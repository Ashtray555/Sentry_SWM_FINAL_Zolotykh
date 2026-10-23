"""Offline checks for the runner; these never open a serial port."""

import io
import unittest

from regression import BenchError, make_suite, require, sanitize


class FakeBench:
    def __init__(self, fixed=False, version="2.3.0"):
        self.fixed = fixed
        self.version = version
        self.interval = 30
        self.commands = []

    def command(self, command, wait=2.5):
        self.commands.append(command)
        responses = {
            "version": f"fw v{self.version}\npartition: ota_0, state: valid",
            "state": "state: 1 NORMAL",
            "relay status": "[VALVE] closed, auto off, cycles 166",
            "guard status": "[WATCH] disarmed, zone 50 cm",
            "distance 1": "[SONAR] 1/1: 50.0 cm",
            "distance stats": "[SONAR] calibration +0.0 cm",
            "relay off": "W601 relay already off",
            "distance 20": "[SONAR] 1/20: 50.0 cm" if self.fixed else "E704 count",
            "distance 21": "E704 count",
            "relay pulse 99": (
                "E603 pulse must be 100-10000 ms" if self.fixed
                else "[VALVE] OPEN (pulse)\n[VALVE] CLOSED (pulse end)"
            ),
            "relay pulse 100": "[VALVE] OPEN (pulse)\n[VALVE] CLOSED (pulse end)",
            "distance calibrate reset": (
                "[SONAR] calibration reset" if self.fixed else "E706 usage"
            ),
        }
        if command == "health":
            return f"[TELEMETRY] auto on, interval {self.interval} s"
        if command.startswith("health interval "):
            value = int(command.split()[-1])
            if value == 301 or (value == 300 and self.version == "2.1.0" and not self.fixed):
                return "E902 interval must be 10-300 s"
            self.interval = value
            return f"[TELEMETRY] interval {value} s"
        return responses[command]


class RunnerTests(unittest.TestCase):
    def run_suite(self, bench):
        return unittest.TextTestRunner(stream=io.StringIO()).run(make_suite(bench))

    def test_known_beta_defects_are_three_real_failures(self):
        bench = FakeBench()
        result = self.run_suite(bench)
        self.assertEqual(result.testsRun, 4)
        self.assertEqual(len(result.failures), 3)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(bench.interval, 30)
        self.assertIn("relay off", bench.commands)

    def test_stable_health_defect_is_also_detected(self):
        result = self.run_suite(FakeBench(version="2.1.0"))
        self.assertEqual(len(result.failures), 4)
        self.assertFalse(result.errors)

    def test_fixed_firmware_passes(self):
        bench = FakeBench(fixed=True)
        self.assertTrue(self.run_suite(bench).wasSuccessful())
        self.assertEqual(bench.interval, 30)

    def test_cleanup_errors_cannot_be_reported_as_success(self):
        class BrokenCleanup(FakeBench):
            def command(self, command, wait=2.5):
                if command == "relay off":
                    raise BenchError("Disconnected during cleanup")
                return super().command(command, wait)

        bench = BrokenCleanup(fixed=True)
        result = self.run_suite(bench)
        self.assertFalse(result.wasSuccessful())
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(bench.interval, 30)

    def test_nonzero_calibration_stops_before_defect_checks(self):
        class Calibrated(FakeBench):
            def command(self, command, wait=2.5):
                if command == "distance stats":
                    return "[SONAR] calibration -2.3 cm"
                return super().command(command, wait)

        bench = Calibrated()
        result = self.run_suite(bench)
        self.assertEqual(result.testsRun, 0)
        self.assertEqual(len(result.errors), 1)
        self.assertNotIn("distance calibrate reset", bench.commands)
        self.assertEqual(bench.interval, 30)

    def test_redaction(self):
        value = sanitize(
            "user: example, access: user\nsecret 192.168.1.5 AA:BB:CC:DD:EE:FF",
            ["secret"],
        )
        for sensitive in ("example", "secret", "192.168.1.5", "AA:BB:CC:DD:EE:FF"):
            self.assertNotIn(sensitive, value)

    def test_missing_required_response_is_error(self):
        with self.assertRaises(BenchError):
            require("", "calibration", "Missing response")


if __name__ == "__main__":
    unittest.main()
