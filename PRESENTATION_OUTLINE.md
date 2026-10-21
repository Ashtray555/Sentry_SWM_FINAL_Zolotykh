# SENTRY SWM-2 Project Defense — Presentation Outline

**Target defense:** October 23, 2026  
**Target duration:** up to 10 minutes  
**Status:** Seven-slide deck `SENTRY_SWM2_Defense.pptx` is refreshed to the Oct 22 evidence (101 rows, BUG-01 to BUG-07). Full spoken text: [`SPEAKER_SCRIPT.md`](./SPEAKER_SCRIPT.md).
**Report source:** [`REPORT.md`](./REPORT.md); do not present its result-row counts as a planned-coverage percentage.

## Suggested 7-slide talk

| Slide | Time | Content and evidence |
|---|---:|---|
| 1. Project and decision question | 0:45 | SENTRY SWM-2; compare 2.1.0 stable with 2.3.0 beta; question: is 2.3.0 ready for stable? |
| 2. Requirements and test strategy | 1:15 | PRD-driven traceability, two versions, acceptance + regression, boundary/error cases; 101 recorded result rows across 64 distinct case IDs (40 Pass, 47 Partial, 11 fail, 2 investigate, 1 not run; not total planned coverage); seven bugs incl. BUG-06 Guard attempt counter and BUG-07 calibrate reset |
| 3. Test bench / HIL design | 1:15 | ESP32-S3 on COM6, UART, Wi-Fi/OTA host, sensor/relay/buttons/LED; show bench diagram and compatibility/safety gates |
| 4. OTA and version coverage | 1:15 | Upgrade, manual rollback (both directions, repeated) and `ota broken` automatic recovery verified; downgrade/force protection and persistence checked; full local-server fault matrix (garbage/truncated/corrupted/interrupted images) run on **both** 2.1.0 and 2.3.0 with no corruption; custom-server selection/persistence/restoration and server-unavailable/invalid-channel errors confirmed; slow-transfer-plus-Wi-Fi-loss remains inconclusive (UART blocked during OTA) |
| 5. Product-feature coverage | 1:30 | Auth/states, sonar/relay/lamp/health and 2.3.0 Guard/Alert; full account/password boundary matrix and a 136-expectation functional regression suite on both versions; summarize coverage and remaining physical-observation gaps |
| 6. Highest-impact findings | 2:00 | BUG-01, BUG-02 and BUG-04 occur on both versions (not beta regressions); BUG-03 rejects 300 s on stable 2.1.0 but passes on 2.3.0; BUG-05 is a cosmetic stable-only lamp timer label bug. Bonus: a leaked debug `sudo` password was found and disclosed responsibly (redacted everywhere) along with a hidden `selftest` command. Show PRD boundaries and sanitized UART evidence. |
| 7. Release recommendation and lessons | 1:00 | NO-GO for promoting 2.3.0 to stable: BUG-01, BUG-02 and BUG-04 violate PRD limits on both versions; BUG-03 is a stable-only regression risk if not already tracked; remaining risk is mainly physical-observation and Guard/critical-alert coverage requiring bench access. |

Reserve approximately one minute for transitions/questions within the instructor's timing guidance. If the talk is strictly capped at 10 minutes before questions, use a timed rehearsal and trim detail rather than rushing.

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
