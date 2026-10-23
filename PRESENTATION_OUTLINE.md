# SENTRY SWM-2 Project Defense — Presentation Outline

**Target defense:** October 23, 2026  
**Target duration:** up to 10 minutes  
**Status:** Eight-slide, high-contrast deck `SENTRY_SWM2_Defense.pptx` includes October 23 live automated results (4 tests: 1 Pass, 3 Fail) separately from the original 101 rows. The matching spoken text is also in PowerPoint speaker notes: [`SPEAKER_SCRIPT.md`](./SPEAKER_SCRIPT.md).
**Report source:** [`REPORT.md`](./REPORT.md); do not present its result-row counts as a planned-coverage percentage.

## Suggested 8-slide talk

| Slide | Time | Content and evidence |
|---|---:|---|
| 1. Project and decision question | 0:45 | SENTRY SWM-2; compare 2.1.0 stable with 2.3.0 beta; question: is 2.3.0 ready for stable? |
| 2. Requirements and strategy | 1:00 | 67 defined cases; 101 original result rows across 64 case IDs: 40 Pass, 47 Partial, 11 Fail, 2 Investigate, 1 Not run. Not a coverage percentage. Four automated tests are a separate supplement. |
| 3. Test bench / HIL design | 1:00 | ESP32-S3 on COM6, UART, Wi-Fi/OTA host, sensor/relay/buttons/LED. Physical observations, measured targets and low-voltage safety limits. |
| 4. OTA and version coverage | 1:15 | Upgrade, manual rollback (both directions, repeated) and `ota broken` automatic recovery verified; downgrade/force protection and persistence checked; full local-server fault matrix (garbage/truncated/corrupted/interrupted images) run on **both** 2.1.0 and 2.3.0 with no corruption; custom-server selection/persistence/restoration and server-unavailable/invalid-channel errors confirmed; slow-transfer-plus-Wi-Fi-loss remains inconclusive (UART blocked during OTA) |
| 5. Product-feature coverage | 1:00 | Auth/states, sonar/relay/lamp/health and 2.3.0 Guard/Alert; manual/semi-automated functional regression on both versions. Physical buttons, EMERGENCY, PANIC and tamper were tested; relay load verification remains open. |
| 6. Highest-impact findings | 2:00 | BUG-01, BUG-02 and BUG-04 occur on both versions (not beta regressions); BUG-03 rejects 300 s on stable 2.1.0 but passes on 2.3.0; BUG-05 is a cosmetic stable-only lamp timer label bug. Bonus: a leaked debug `sudo` password was found and disclosed responsibly (redacted everywhere) along with a hidden `selftest` command. Show PRD boundaries and sanitized UART evidence. |
| 7. Automated regression tests | 1:30 | Four live UART tests on 2.3.0: 1 Pass, 3 Fail, no errors. BUG-01/02/07 reproduced; health boundary passed. Assertions, sanitized logs/JSON, verified cleanup; seven offline harness checks passed. No live 2.1.0 validation with the new runner. |
| 8. Release recommendation and lessons | 1:00 | NO-GO: PRD violations plus BUG-06 Guard false-alarm risk. Remaining limits: calibration at 5/300 cm, relay contacts under load and Wi-Fi interruption during OTA. Fix and retest. |

The slide budgets total 9:30. Reserve the remaining 30 seconds for transitions
or an optional short LED video excerpt. Rehearse aloud; questions are outside
this 10-minute budget.

## Evidence checklist before slides are finalized

- Verified firmware versions and test dates
- Result-row snapshot from `TEST_CASES.md`; clearly distinguish executed rows from planned total coverage
- OTA upgrade, self-check, failure/retry and rollback evidence
- Physical bench photo/diagram and confirmation of which components actually worked
- Confirmed bug IDs, reproducibility, severity and version matrix
- Cross-version boundary results: `distance 20` rejected on both; `relay pulse 99` accepted on both; `health interval 300` rejected on 2.1.0 and accepted on 2.3.0
- Explicit distinction between firmware defects and hardware/setup limitations
- Final GO/NO-GO recommendation based on complete results, not assumptions
- Sanitized screenshots/log excerpts; no Wi-Fi password, account password or sudo secret

## Likely defense questions

- How did each test derive from a PRD requirement?
- Which boundaries and invalid inputs were tested, and why?
- How did you distinguish firmware faults from sensor/relay/wiring issues?
- How did OTA failure tests establish that the old image remained safe and usable?
- What does the proposed HIL setup automate, and what still needs a human?
- Which coverage gaps remain and how do they affect your release recommendation?
- What specific evidence supports each reported bug and its severity?
