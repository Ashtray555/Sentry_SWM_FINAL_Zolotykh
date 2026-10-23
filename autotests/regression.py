"""PRD-based UART checks. Known firmware defects remain failing tests."""

import argparse
import datetime
import io
import json
import os
from pathlib import Path
import re
import sys
import time
import unittest

import serial


class BenchError(RuntimeError):
    pass


def sanitize(text, secrets):
    for value in sorted(filter(None, secrets), key=len, reverse=True):
        text = text.replace(value, "<redacted>")
    text = re.sub(r"user:\s*[^,\r\n]+", "user: <redacted>", text)
    text = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "<ip>", text)
    text = re.sub(r"\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b", "<mac>", text)
    return text


def require(text, pattern, description):
    if not re.search(pattern, text):
        raise BenchError(description)


class Bench:
    def __init__(self, port, credentials):
        self.port = port
        self.connection = None
        self.secrets = []
        self.username = os.environ.get("SENTRY_USERNAME")
        self.password = os.environ.get("SENTRY_PASSWORD")
        self.version = None
        if credentials:
            text = Path(credentials).read_text(encoding="utf-8")
            user = re.search(r"(?im)(?:username|user|login)\s*[:=]\s*(\S+)", text)
            password = re.search(r"(?im)password\s*[:=]\s*(\S+)", text)
            if not user or not password:
                raise BenchError("Credentials file needs username and password fields.")
            self.username, self.password = user[1], password[1]
            self.secrets.extend(
                match[1] for match in re.finditer(r"[:=]\s*(\S+)", text)
            )
        self.secrets.extend([self.username, self.password])
        self.transcript = []

    def command(self, command, wait=2.5):
        self.connection.reset_input_buffer()
        self.connection.write((command + "\r\n").encode())
        deadline = time.monotonic() + wait
        data = bytearray()
        while time.monotonic() < deadline:
            data.extend(self.connection.read(4096))
        text = data.decode("utf-8", errors="replace")
        safe = sanitize(text, self.secrets)
        timestamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        self.transcript.append(
            f"{timestamp} > {sanitize(command, self.secrets)}\n{safe}"
        )
        # An echo alone is not evidence that the firmware processed a command.
        if not re.search(r"[IWE] \(\d+\)", text):
            raise BenchError(f"No firmware response to {command.split()[0]}.")
        return safe

    def connect(self):
        self.connection = serial.Serial(
            self.port, 115200, timeout=0.2, write_timeout=2
        )
        response = self.command("whoami")
        if re.search(r"\bE00[23]\b|not logged", response, re.I):
            if not self.username or not self.password:
                raise BenchError("Login required: supply credentials or environment variables.")
            self.command("reconnect", wait=10)
            self.command(f"login {self.username} {self.password}", wait=4)
            response = self.command("whoami")
        require(response, r"user:.*access: user", "Authenticated user session required.")

    def close(self):
        if self.connection:
            self.connection.close()


def make_suite(bench):
    class Regression(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            version = bench.command("version")
            require(version, r"fw v2\.(?:1|3)\.0", "Unsupported firmware version.")
            require(version, r"state: valid", "Running OTA image must be valid.")
            cls.version = re.search(r"fw v([\d.]+)", version)[1]
            bench.version = cls.version
            require(bench.command("state"), r"state: 1 NORMAL", "NORMAL state required.")
            require(
                bench.command("relay status"),
                r"\[VALVE\] closed, auto off",
                "Start with relay closed and auto mode off.",
            )
            if cls.version == "2.3.0":
                require(
                    bench.command("guard status"), r"\[WATCH\] disarmed\b",
                    "Disarm Guard before testing.",
                )
            health = bench.command("health")
            match = re.search(r"auto (?:on|off), interval (\d+) s", health)
            if not match:
                raise BenchError("Cannot determine original health interval.")
            cls.interval = int(match[1])
            # Preserve the original interval, including when an assertion fails.
            cls.addClassCleanup(cls.restore_health)
            cls.addClassCleanup(cls.close_relay)
            bench.command("distance 1", wait=4)
            require(
                bench.command("distance stats"), r"calibration \+0\.0 cm",
                "Start with zero calibration; this suite does not overwrite a nonzero offset.",
            )

        @classmethod
        def close_relay(cls):
            bench.command("relay off")
            require(
                bench.command("relay status"), r"\[VALVE\] closed, auto off",
                "Cleanup failed: relay is not closed with auto mode off.",
            )

        @classmethod
        def restore_health(cls):
            bench.command(f"health interval {cls.interval}")
            require(
                bench.command("health"), rf"interval {cls.interval} s",
                "Cleanup failed: health interval was not restored.",
            )

        def test_distance_upper_boundary_bug01(self):
            """DS-1 / BUG-01: 20 is accepted; 21 is rejected with E704."""
            for count in (20, 21):
                with self.subTest(count=count):
                    response = bench.command(f"distance {count}", wait=8)
                    if count == 20:
                        self.assertNotRegex(response, r"\bE704\b")
                        self.assertRegex(response, r"/20:|/20 ok|E701|E702")
                    else:
                        self.assertRegex(response, r"\bE704\b")

        def test_relay_lower_boundary_bug02(self):
            """RL-3 / BUG-02: 99 ms rejected; 100 ms completes a pulse."""
            for duration in (99, 100):
                with self.subTest(duration=duration):
                    response = bench.command(f"relay pulse {duration}")
                    if duration == 99:
                        self.assertRegex(response, r"\bE603\b")
                        self.assertNotRegex(response, r"\[VALVE\] OPEN")
                    else:
                        self.assertRegex(response, r"\[VALVE\] OPEN \(pulse\)")
                        self.assertRegex(response, r"\[VALVE\] CLOSED \(pulse end\)")

        def test_health_upper_boundary_bug03(self):
            """HL-3 / BUG-03: 300 s accepted; 301 s rejected with E902."""
            with self.subTest(interval=300):
                response = bench.command("health interval 300")
                self.assertNotRegex(response, r"\bE902\b")
                self.assertRegex(response, r"\[TELEMETRY\] interval 300 s")
                self.assertRegex(bench.command("health"), r"interval 300 s")
            with self.subTest(interval=301):
                self.assertRegex(bench.command("health interval 301"), r"\bE902\b")

        def test_calibration_reset_syntax_bug07(self):
            """DS-3 / BUG-07: documented reset command is accepted."""
            response = bench.command("distance calibrate reset")
            self.assertNotRegex(response, r"\bE706\b")
            self.assertRegex(response, r"\[SONAR\] calibration reset")
            self.assertRegex(bench.command("distance stats"), r"calibration \+0\.0 cm")

    return unittest.defaultTestLoader.loadTestsFromTestCase(Regression)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", default="COM6")
    parser.add_argument("--credentials", help="External credentials file; never committed.")
    parser.add_argument("--output", type=Path, default=Path("logs"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    prefix = args.output / f"autotest_{stamp}"
    bench = Bench(args.port, args.credentials)
    report = io.StringIO()
    try:
        bench.connect()
        result = unittest.TextTestRunner(stream=report, verbosity=2).run(make_suite(bench))
        summary = {
            "firmware": bench.version,
            "port": args.port,
            "started_local": stamp,
            "tests": result.testsRun,
            "failure_entries": len(result.failures),
            "error_entries": len(result.errors),
            "successful": result.wasSuccessful(),
            "note": "Failure entries include subtests; counts are not coverage percentages.",
        }
        exit_code = 0 if result.wasSuccessful() else (2 if result.errors else 1)
    except (BenchError, serial.SerialException, OSError) as error:
        report.write(f"SETUP/TRANSPORT ERROR: {sanitize(str(error), bench.secrets)}\n")
        summary = {"successful": False, "setup_error": True}
        exit_code = 2
    finally:
        bench.close()
        prefix.with_suffix(".txt").write_text(
            "\n\n".join(bench.transcript), encoding="utf-8"
        )
    prefix.with_suffix(".results.txt").write_text(report.getvalue(), encoding="utf-8")
    prefix.with_suffix(".json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(report.getvalue())
    print(f"Evidence: {prefix}.*")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
