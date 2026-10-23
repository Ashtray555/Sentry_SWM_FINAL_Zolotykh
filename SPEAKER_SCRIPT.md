# SENTRY SWM-2 — 10-minute speaker script

Slide numbers follow `SENTRY_SWM2_Defense.pptx` (7 slides). About 130 words per minute; the timings add up to 9:30, which leaves about 30 seconds of buffer. Bracketed text is a stage direction, not spoken.

## Slide 1 — Project and decision question (0:45)

Good day. My project is acceptance and regression testing of the SENTRY SWM-2 firmware, a sonar watch module running on an ESP32-S3, connected over UART on COM6.

The question I had to answer is simple: **is firmware 2.3.0 beta ready to replace 2.1.0 stable?** To answer it I tested both versions on the same real board, against the same requirements document, and compared the results.

## Slide 2 — Requirements and test strategy (1:15)

Everything starts from the PRD. I built a traceability matrix from the requirements to 67 defined test cases, so every test can be traced back to a requirement.

I ran acceptance and regression tests on both versions: normal behaviour, boundary values, invalid input, persistence after reboot, and OTA failures.

By the end I had **101 recorded result rows across 64 distinct case IDs**: 40 Pass, 47 Partial, 11 Fail, 2 Investigate and 1 Not run. I want to be honest about what this means: these are execution records, **not** a percentage of total planned coverage. Partial means it passed within a limited scope, not a full pass.

The testing found seven bugs, and I will show the most important ones.

## Slide 3 — Test bench (1:15)

[Show the bench photo or diagram; if you want, play 15–20 s of the LED video here.]

This is the bench. An ESP32-S3 board connected over UART at 115200 baud, a Wi-Fi network with a local OTA server, an ultrasonic sonar, a relay module on GPIO8, an RGB lamp on GPIO48, four buttons on GPIO41, 40, 39 and 38, and a proximity LED on GPIO4.

Safety came first. The relay was only used at low voltage with no load, and I did not use mains or hazardous loads. I also automated the command side with a small Python helper that logs in, sends commands and captures the output, while a human was needed for physical observation: LED colours, the relay click, button presses and placing the sonar target with a ruler.

I also added four assertion-based UART regression tests for recurring defects.
On 2.3.0, one passed and three failed against the PRD, reproducing known bugs.
They generate logs and restore settings; the new runner was validated on 2.3.0 only.
Physical observations remain manual. All logs were sanitised.

## Slide 4 — OTA and version coverage (1:15)

OTA is the riskiest part of a firmware release, so I tested it deeply.

Upgrade from 2.1.0 to 2.3.0 worked and passed the self-check. A deliberately broken image failed the self-check and the device rolled back automatically. Manual rollback worked in both directions, and I used it again to switch versions safely for the final repeat tests.

I also ran a local-server fault matrix on **both** versions: garbage, truncated, corrupted and interrupted images. They were all rejected cleanly, with no corruption, and the device recovered each time. Downgrade protection (E408) and error codes for a bad URL or version also worked.

One thing I could not prove: Wi-Fi loss in the middle of a transfer. UART is blocked during OTA, so that case stays inconclusive, and I list it as a limitation.

## Slide 5 — Product features (1:30)

Next, the features: login and states, sonar, relay, lamp, health reports, and in 2.3.0 the new Guard and Alert Center.

I ran a full account and password boundary matrix and a 136-expectation functional regression suite on both versions.

On the hardware, I physically confirmed the RGB colours, the relay click, all four buttons and every state chord, including EMERGENCY, where buttons are blocked and the only exit is a reboot.

Guard worked end to end: arming with a countdown, intrusion, a 15-second disarm window and then ALARM. ALARM opens the relay and raises a CRITICAL alert. I also tested the K4-hold PANIC, sensor tamper, and alert retention capped at 20.

On 2.1.0 these Guard and Alert commands correctly report that they are planned for 2.3.0.

## Slide 6 — Findings (2:00)

[This is the most important slide; slow down.]

Seven bugs. The key point is that most are **not** beta regressions.

- **BUG-01:** `distance 20` is rejected, although the PRD range is 1 to 20. Both versions.
- **BUG-02:** `relay pulse` accepts values below the PRD minimum of 100 ms. Both versions.
- **BUG-04:** the relay cycle counter miscounts. On 2.1.0 every switch adds two; on 2.3.0 the last increment is lost across a reboot.
- **BUG-03:** a health interval of 300 seconds is rejected on 2.1.0 but accepted on 2.3.0. This is stable-only, so 2.3.0 actually fixes it.
- **BUG-05:** a cosmetic one on 2.1.0: the lamp timer message says "ms" but the timing is in seconds.
- **BUG-06:** new in 2.3.0 Guard. The wrong-PIN counter never resets. After three wrong PINs over the device's lifetime since boot, a single typo raises ALARM. A reboot clears it.
- **BUG-07:** the documented command `distance calibrate reset` returns an error on both versions. The undocumented `distance reset` works.

As a bonus, during authorised security exploration I found a leaked debug sudo password and a hidden selftest command. I reported them responsibly and redacted them everywhere in my evidence.

## Slide 7 — Recommendation and lessons (1:00)

My recommendation is **NO-GO for promoting 2.3.0 to stable at this time.**

BUG-01, BUG-02 and BUG-04 violate PRD limits on both versions, and BUG-06 adds a real false-alarm risk in the new Guard feature. This is a recommendation about this specific build, not a claim that 2.3.0 is generally worse than 2.1.0. Retest after fixes.

Gaps remain, and I state them openly: the calibrate boundaries of 5 and 300 cm were not run, relay contact behaviour under real load was not measured, and Wi-Fi loss during OTA is inconclusive.

Lessons: test against the requirements, not against assumptions; run the same boundaries on every version, because that is how you separate old defects from regressions; and keep evidence sanitised and reproducible. I corrected one of my own early mistakes along the way, a calibrate-reset result I had first misread, which is why re-checking matters.

Thank you. I am ready for questions.

## Likely questions — short answers

- **How were tests derived from the PRD?** Each PRD requirement ID maps to test case IDs in the traceability matrix, with boundaries and invalid values for each.
- **Firmware fault or hardware fault?** I repeated each failing case on both versions and checked the error codes. I used a ruler-placed target for sonar tests, and discarded two invalid runs where the target moved.
- **Why is it NO-GO if 2.1.0 has the same bugs?** The bugs break PRD limits in the build that would be promoted, and 2.3.0 adds BUG-06. Promoting means shipping known violations plus a new one.
- **How did OTA tests keep the device safe?** Each fault run was followed by a version and partition check. Rollback and self-check recovered the device every time.
- **What is still not covered?** The three gaps on slide 7. They do not change the NO-GO, since it rests on confirmed defects.
- **What does 'Partial' mean?** A pass within a limited scope, for example the logic was checked but not under real load.
- **Why a ruler for the sonar?** The PRD sets no accuracy tolerance, so I only reported measured values: 10, 20, 30 and 50 cm read 13.0, 21.4, 30.9 and 48.6 cm, and I did not claim a defect.
