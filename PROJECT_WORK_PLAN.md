# SENTRY SWM-2 Project Work Plan

## Updated project information

- **ESP32 serial port:** COM6
- **Board connection check (October 19, 2026):** COM6 is detected as USB-Enhanced-SERIAL CH343 and opens at 115200 8N1.
- **Current firmware:** SENTRY SWM-2 fw_7 v2.3.0 on `ota_1 @ 0x1A0000`, state `valid`; stable v2.1.0 is restored and boot-validated on `ota_0`. See `logs/ota_stable_fallback_restore_2026-10-20.txt`.
- **Baseline setup:** with user authorization, erased the previous station_WiFi v1.5.0 image/NVS and flashed the supplied fw_7 merged v2.1.0 image. esptool verified the written image hash.
- **Wi-Fi:** test-hotspot and home-network connectivity, network info, time, disconnect and saved-network reconnect verified. The home-network retest produced 4/4 default-ping replies (25 ms average); saved reconnect obtained an IP and passed the internet check. W106 NTP warning recurred after reconnect in 2/2 trials on each network across the tested versions, despite successful connectivity; `time` returned a timestamp after the latest warning. A later reconnect after OTA restoration synced NTP on both 2.1.0 and 2.3.0. Credentials and network identifiers are excluded from evidence. Treat the warning as intermittent pending isolation, not a confirmed defect.
- **Wi-Fi outage:** hotspot was intentionally interrupted. Firmware emitted W110 and exactly three retries; after the hotspot returned, link remained down until manual `reconnect`, which restored internet. See sanitized `logs/wifi_outage_2.1.0.txt` and `logs/wifi_outage_recovery_2.1.0.txt`; characterize against WF-5 and retest before filing a defect.
- **Account/OTA checks:** the existing disposable account was used only to authenticate OTA queries and recovery actions; its identifier and password remain excluded from logs. The test session was logged out after verification; the account remains configured on the device.
- **Test-state reset (user authorized, historical):** flash/NVS was erased and fw_7 2.1.0 reinstalled to clear an earlier temporary account and saved hotspot configuration. `logs/baseline_after_account_reset_2.1.0.txt` verifies that baseline on ota_0, NORMAL, and logged out. A disposable account and the home network were configured afterward; the account remains configured and the test session is now logged out. Earlier-run evidence remains sanitized and valid for its recorded state.
- **October 21 read-only check:** COM6 reports v2.3.0 valid on `ota_1`; saved Wi-Fi reconnect and internet check succeeded. The board is logged out; OTA status requires login, and the existing account username could not be confirmed. No OTA settings or partitions were changed. See `logs/device_readonly_state_2026-10-21.txt`.
- **Current test state:** v2.3.0 beta is valid on `ota_1`, and stable v2.1.0 is restored and valid on `ota_0`. Both passed OTA self-check after the restoration cycle; final 2.3.0 reconnect passed internet check and NTP sync. Health interval is 60 s, relay is closed/auto off, and Guard is disarmed at its original 50 cm zone. Cross-version findings: BUG-01 (distance count 20 rejected on both versions), BUG-02 (`relay pulse 99` accepted on both versions), and BUG-03 (stable 2.1.0 rejects health interval 300 s; beta 2.3.0 accepts it). User reported multiple LEDs blinked briefly during the latest 2.3.0 pulse; relay contact switching itself remains unobserved. See `BUG_REPORTS.md`; keep low-voltage-only relay setup.
- **Release target:** October 21 (updated information from the project owner; this supersedes the October 20 work/presentation date shown in the coursework PDF)
- **Demo day:** October 22
- **LMS submission deadline:** October 24, 23:59, if not presenting at demo day
- **Product under test:** SENTRY SWM-2 firmware 2.1.0 stable and 2.3.0 beta
- **Test approach:** Black-box acceptance and regression testing against the firmware PRD

## Project materials

The coursework requirements are in `requirnments/Курсовий_проєкт_SENTRY_SWM_2.pdf`.

Supporting firmware and QA materials are in:

`D:\Projects\EMBEDDED-QA-ENGINEER\EMBEDDED-QA-ENGINEER\forGit\fw_7`

Key references:

- `PRD.md` — expected product behavior and acceptance requirements
- `HW-17.md` — required test activities and report contents
- `README.md` — firmware flashing and startup instructions
- `WIRING.md` — HIL bench wiring and safety instructions
- `tools/README.md` — local OTA server and OTA failure-test instructions
- `sentry_fw7_v2.1.0_merged.bin` — initial 2.1.0 firmware image

## Work plan

### 1. Prepare test documentation

- Review the PRD and convert its requirements into individually identifiable test cases.
- Build a traceability matrix linking each PRD requirement to test case(s), firmware version, result, and bug ID where applicable.
- Include normal, boundary, invalid-input, persistence-after-reboot, OTA, and regression scenarios.
- Treat Guard, Alert Center, and K4 as features introduced in 2.3.0; their absence in 2.1.0 is expected, not a defect.

**Deliverables:** test plan, test cases, traceability matrix.

**Status:** Completed as living documents; keep updating execution records and coverage as evidence is added.

### 2. Specify the HIL test bench

- Document the ESP32-S3, HC-SR04, relay, indicator LED, buttons, UART connection, and a future CI integration.
- Use COM6 for serial-console and flashing procedures.
- Follow `WIRING.md`: power peripherals from 3.3 V only; do not connect 5 V to ESP32 GPIO.
- List what must be observed physically (sensor response, relay/LED behavior, button actions) in addition to UART output.

**Deliverable:** HIL bench description and connection/signal diagram.

### 3. Set up and test firmware 2.1.0

- Confirm the ESP32 is available on COM6 and establish UART at 115200 8N1. Done.
- Flash the supplied 2.1.0 merged image following the fw_7 README. Done with authorization; written image hash verified.
- Save the boot/version output and confirm the device reaches its expected ready state. Baseline version, valid partition, NORMAL state, no saved network/profile, and help output captured; see `logs/baseline_2.1.0.txt` and `logs/baseline_readonly_checks_2.1.0.txt`.
- Register and log in as required by the PRD, then execute the 2.1.0 test cases.
- Capture full logs and physical observations; redact Wi-Fi credentials as `***`.
- Wi-Fi scan/connect, status, network details, default ping/time and saved-network disconnect/reconnect have started; see sanitized `logs/wifi_*.txt`. Deliberate outage/reconnect-count tests remain pending.
- **Current execution status:** baseline, account, Wi-Fi, selected OTA, health, distance and relay cases have results; many remain partial and BUG-01/02 are confirmed. Wi-Fi outage produced W110 and three retries; after the hotspot returned, manual reconnect was required. Remaining 2.1.0 boundaries and state/actuator coverage are pending or not run.

### 4. Upgrade to and test firmware 2.3.0

- Check the OTA channels, then upgrade from 2.1.0 to beta 2.3.0 using the device's OTA flow.
- Verify the new firmware version and self-check result.
- Check persistence of Wi-Fi/account and other PRD-listed data across the upgrade.
- Repeat applicable 2.1.0 tests for regression coverage.
- Test 2.3.0 Guard, Alert Center, and K4 behavior.
- **Status:** Upgrade, OTA recovery, health, Wi-Fi, distance/relay, selected Guard-zone and noncritical Alert Center cases have results, plus (October 21) the full account/state/lamp/relay/sensor/telemetry regression suite (136 expectations) on both versions, manual rollback both directions repeated, and non-Latin-input/reboot-persistence checks. The 2.1.0 fallback has been restored after `ota broken`; current state is 2.3.0 on `ota_0` with 2.1.0 last verified valid on `ota_1`. Guard alarm, critical alert, button chords and physical-output observation remain pending (deliberately deferred for relay safety and bench access).

### 5. Test OTA protection, errors, and recovery

- Check stable/beta update behavior, already-current behavior, downgrade protection with and without `force`, and rollback using the broken image.
- Use the provided local OTA server for interrupted/slow downloads and invalid, truncated, or corrupted images as specified in `HW-17.md`.
- After each failed update, verify the device remains usable on the current firmware and that a subsequent OTA succeeds.
- Restore the default OTA server and record the final server setting.
- **Status:** Upgrade, current-beta no-op, no-force downgrade protection (plus a forced downgrade with settings-persistence checks), forced stable restore, broken-image auto rollback, manual rollback both directions, malformed/unavailable versions and invalid URL scheme have evidence. Default and custom OTA servers are confirmed, including custom-server persistence across reboot and restoration to default. The full local-server fault matrix (interrupted, invalid, truncated and corrupted images) has been run on **both** 2.1.0 and 2.3.0 with the device remaining valid and a subsequent OTA succeeding each time. A slow-transfer-plus-Wi-Fi-loss attempt did not conclusively interrupt the transfer (UART console is blocked during OTA) and remains an open/inconclusive case.

### 6. Report results and make the release recommendation

- Write a complete bug report for every confirmed defect: ID, title, version(s), severity, priority, prerequisites, reproduction steps, expected behavior with PRD reference, actual behavior, evidence, and reproducibility.
- Produce a per-version pass/fail checklist and a bug/regression matrix.
- Include sanitized logs and physical evidence where relevant.
- Recommend **GO** or **NO-GO** for promoting 2.3.0 to stable, supported by test results and unresolved risks.

**Deliverables:** bug reports, logs, version/regression matrix, release recommendation.

**Status:** [REPORT.md](./REPORT.md) now assembles the per-version checklist, evidence summary, BUG-01 to BUG-07 matrix, performed security-exploration findings, limitations, and provisional NO-GO. It is explicitly interim because full physical-observation and Guard/critical-alert coverage remains pending (user-bench items).

### 7. Package and present

- Assemble the required `HW-17_<Surname>.zip` with `REPORT.md` and `logs/`, plus the supporting test plan, cases, traceability, HIL design, bug reports, and presentation.
- Include a test framework and a README with run instructions if automation is implemented.
- Complete the release package and presentation by **October 21**.
- Prepare and defend the project at the **October 22** demo.
- Build the presentation around the project goal, test scope and method, HIL design, version coverage, key defects/evidence, and the 2.3.0 release recommendation.
- Rehearse a concise talk of up to 10 minutes and prepare for follow-up questions about coverage, limitations, evidence, and the GO/NO-GO decision.
- If the demo defense cannot be attended, submit through LMS by **October 24, 23:59**; the coursework states that this route has a lower maximum score.

**Status (October 21, extended session):** Interim report, seven-slide outline and deck are complete at the previous evidence level; the October 21 extended authorized session added the full account/OTA/functional/security regression pass (87/61 rows) and two new bugs (BUG-04, BUG-05), documented in `REPORT.md`, `BUG_REPORTS.md` and `TRACEABILITY_MATRIX.md`. **Update (Oct 22):** the deck and ZIP were refreshed, and the physical bench, Guard/Alert and 2.1.0 repeat testing was completed (BUG-06, BUG-07 found); only rehearsal and LMS upload remain.

## Presentation and defense

The presentation is a required project deliverable, not an optional extra. It should communicate:

1. What SENTRY SWM-2 is and what versions were tested.
2. How the PRD was converted into test cases and traceability.
3. The physical test bench and proposed future HIL/CI automation.
4. Test execution and coverage across 2.1.0 and 2.3.0.
5. The most important confirmed bugs, with evidence and impact.
6. The release recommendation for 2.3.0 and any test limitations.

Keep slides visual and evidence-led. Rehearse within the 10-minute limit and prepare answers on test selection, boundary coverage, OTA safety/recovery, physical-vs-automated checks, and unresolved risks.

## Next actions

1. **Needs account name and a renewed live-hardware window:** the October 21 read-only check confirmed the board state and Wi-Fi, but local OTA commands require login. The existing account username could not be confirmed; do not guess credentials. No OTA fault matrix was run.
2. **Needs physical tester involvement:** verify US-100/HC-SR04 compatibility, button wiring, exact relay module, and safe output observation. Do not use mains or hazardous loads; do not run Guard alarms/critical alerts until relay output safety is established.
3. **Can proceed without hardware:** review evidence, maintain the report/traceability, finish the visual presentation, and audit/package final deliverables after execution status is frozen.
4. **Packaging:** surname `Zolotykh` confirmed; interim archive `HW-17_Zolotykh.zip` created with the report, supporting docs, deck, and logs. Remaining unrun tests are explicitly identified; do not describe coverage as complete.

## Execution constraints and notes

- This is firmware black-box testing; the supplied fw_7 folder provides a 2.1.0 binary and OTA path to 2.3.0, not the firmware source code.
- Hardware-dependent test results require the ESP32 and peripherals to be connected. The expected serial port is COM6.
- Keep passwords and other credentials out of submitted logs. Replace any Wi-Fi password with `***`.
- Base pass/fail decisions only on the PRD. Behavior explicitly marked as planned for a later firmware version is not a defect in the earlier version.
