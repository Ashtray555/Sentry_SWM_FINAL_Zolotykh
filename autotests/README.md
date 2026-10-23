# Automated UART regression checks

Four assertion-based `unittest` tests target confirmed, repeatable PRD violations.
Known bugs are **real FAIL results**, not expected failures that turn the suite green.
The suite does not flash firmware or switch OTA slots.

## Setup and run (Windows PowerShell, from the project root)

Use Python 3.9 or newer. Connect the ESP32 on COM6 and close other serial monitors.
Keep the relay unloaded and use only the previously verified low-voltage wiring.
Start in NORMAL, Guard disarmed, relay closed with auto mode off, sonar continuous
logging stopped, and calibration zero. Do not press buttons during a run.
The runner checks state/Guard/relay/calibration prerequisites before defect tests.
No measured target placement is needed.

```powershell
python -m pip install -r autotests\requirements.txt
python autotests\regression.py --port COM6
```

An already authenticated user session needs no credentials. If login is needed:

```powershell
python autotests\regression.py --port COM6 --credentials "D:\Projects\SENTRY_TEST_CREDENTIALS_DELETE_ME.txt"
```

That file is external, not included with the project. It needs `username: VALUE`
and `password: VALUE` fields. Alternatively, set `SENTRY_USERNAME` and
`SENTRY_PASSWORD` locally. Never commit credentials or type them into a recorded
terminal. `--output` selects another evidence directory; the default is `logs`.

## Checks and limitations

| Test | PRD / bug | Assertions |
|---|---|---|
| Distance count upper boundary | DS-1 / BUG-01 | 20 accepted as a measurement request; 21 rejected with E704 |
| Relay pulse lower boundary | RL-3 / BUG-02 | 99 ms rejected with E603 and no OPEN; 100 ms produces OPEN and CLOSED |
| Health interval upper boundary | HL-3 / BUG-03 | 300 s accepted and read back; 301 rejected with E902 |
| Calibration reset syntax | DS-3 / BUG-07 | `distance calibrate reset` acknowledged and zero offset read back |

Distance testing checks CLI count acceptance, **not sonar accuracy or 20 successful
echoes**. E701/E702 can demonstrate that measurement execution was entered, but
are not evidence of accurate readings. Calibration testing starts at zero: it
tests documented reset syntax/idempotence, not clearing a deliberately nonzero
offset. Physical relay contacts and LEDs are not measured automatically.

The relay test briefly actuates the relay; its cycle counter therefore increases.
After assertions, registered cleanup closes the relay and restores the original
health interval, with read-back checks. Auto health on/off is not changed.
Calibration is not deliberately changed. Cleanup failures are errors, not passes.
A power loss or disconnected serial cable can prevent cleanup; inspect the
device before rerunning.

The supported version guard permits 2.1.0 and 2.3.0. The automated suite was
**hardware-validated on 2.3.0 only** on October 23. The older two-version manual/
semi-automated evidence remains separate. No OTA switch is required for a demo.

## Results and exit status

Each run creates timestamped UART `.txt`, unittest `.results.txt`, and JSON summary
files. Secrets supplied through credentials/environment, account names in
`whoami`, IPv4 addresses, and MAC addresses are redacted. The runner only sends
the fixed test/status commands plus login/reconnect when necessary; it does not
invoke debug/help commands that could disclose hidden secrets.

- Exit **0**: assertions and cleanup passed.
- Exit **1**: requirement assertion failures (including known defects).
- Exit **2**: setup, transport or cleanup errors. Missing credentials/files also
  cause a nonzero exit; fix the setup before interpreting defect results.

Firmware 2.3.0 live result: **4 test methods, 1 passing and 3 failing, no errors**.
BUG-01, BUG-02 and BUG-07 reproduced; BUG-03 did not reproduce on beta.
Invalid-input neighbours are subtests, not additional top-level tests.
These results are a supplement to, not a recount of, the original 101 execution rows.

## Offline validation of the runner

```powershell
python -m unittest discover -s autotests -p test_runner.py -v
```

These seven tests use fake command responses and never connect to COM6. They
verify detection of beta/stable defects, success against simulated corrected
responses, cleanup on failures, refusal of nonzero calibration, and redaction.
They validate the test harness, **not actual 2.1.0 firmware**.
