# SENTRY SWM-2 Acceptance Test Plan

**Status:** Execution in progress — results and evidence recorded; full coverage and final release recommendation pending  
**Target versions:** 2.1.0 stable and 2.3.0 beta  
**Device:** ESP32-S3 DevKit, expected UART port COM6  
**UART:** 115200 baud, 8 data bits, no parity, 1 stop bit  
**Release target:** October 21, 2026  
**Project defense:** October 22, 2026

**Coursework report:** [`REPORT.md`](./REPORT.md) assembles the per-version checklist, bug matrix, evidence, security-test status, release recommendation, and remaining limitations. It is the final report; planned coverage is not 100% and gaps are listed in its limitations.

## Execution snapshot (updated October 21, 2026)

**Recorded execution-result rows:** 101 across 64 distinct case IDs: 40 full Pass, 47 Partial (including pass-with-limited-scope), 11 Fail, 2 Investigate, and 1 Not run. These are documented-row counts, not a percentage of all planned requirement coverage; the remaining unrepresented cases are mainly the calibrate 5/300 cm boundaries with a target and a few lower-priority 2.1.0 repeats. Lamp, relay, K1–K4 presses, all four state chords including EMERGENCY, and the Guard/CRITICAL alarm path (BUG-06 found) were physically observed on October 21.

- Manual OTA rollback was exercised from valid 2.3.0 to valid 2.1.0 and back twice (once before and once after the October 21 reset), both self-checks passed each time.
- The intentional `ota broken` image failed self-check and automatically returned the board to valid 2.3.0.
- Cross-version checks confirmed `distance 20` is rejected on both versions (BUG-01) and `relay pulse` below 100 ms is accepted down to 10 ms on both (BUG-02), so neither is beta-only. A full local-server OTA fault matrix (garbage/truncated/corrupted/interrupted images) was run on both versions with no partition corruption in any case.
- Health interval 300 seconds is rejected on 2.1.0 but accepted on 2.3.0 (BUG-03; stable-only defect observed, beta behavior conforms at this boundary).
- On 2.3.0, `health now` and health reporting off/on worked; interval limits were checked and the 60-second enabled state was restored.
- New findings from the October 21 extended session: BUG-04 (relay cycle counter over/under-counts on both versions, different symptom per version) and BUG-05 (2.1.0 lamp timer confirmation message prints "ms" instead of "s", cosmetic). A bonus security exploration found a leaked debug `sudo` password in the boot banner's base64 "build tag" and a hidden `selftest` diagnostic command; both are documented and the password is redacted everywhere in the deliverable.
- The device is back on 2.3.0; health interval 60 seconds, relay closed/auto-off, and Guard disarmed at its default 50 cm zone.
- Home-network retesting restored saved Wi-Fi connectivity: default ping returned 4/4 replies (25 ms average), and reconnect obtained an IP with the internet check passing. `disconnect` succeeded; `disconnect` while already disconnected returned W115; `reconnect` while already connected returned W114.
- Custom-host ping to a public test address returned 4/4 replies (11 ms average) on 2.3.0; see `logs/wifi_custom_ping_2.3.0.txt`.
- W106 NTP-sync warning occurred after saved-network reconnect in 2/2 trials on the home network with 2.3.0, matching 2/2 on the earlier test hotspot with 2.1.0. A timestamp was still returned by `time`; later reconnects after OTA restoration synced NTP on both versions. Treat this as intermittent and unresolved, not a confirmed defect.
- The intentional broken-image OTA test temporarily overwrote the inactive `ota_0` image.
- The inactive stable slot has since been restored: forced install of 2.1.0 completed at 100%, booted on `ota_0`, and passed self-check. OTA status showed v2.3.0 on `ota_1` as the previous image; manual rollback returned to 2.3.0 and passed self-check. Both slots are again valid; the final 2.3.0 reconnect passed internet and NTP checks. See `logs/ota_stable_fallback_restore_2026-10-20.txt`.
- On 2.3.0, malformed version input returned E414 and unavailable v9.9.9 returned E415; OTA status confirmed v2.3.0/ota_1 and v2.1.0/ota_0 remained valid. See `logs/ota_install_rejections_2.3.0.txt`.
- Unsupported `ftp://` OTA URL returned E418; the following channel check still reached the default manifest. No slot changed. See `logs/ota_url_scheme_2.3.0.txt`.
- Read-only `ota server` confirmed the default OTA manifest; no custom-server setting was changed. See `logs/ota_server_default_2.3.0.txt`.
- On October 21, read-only UART checks confirmed v2.3.0 is still valid on `ota_1`; saved Wi-Fi reconnect passed, but the logged-out board returned E003 for `ota status`. The account username could not be confirmed, so no OTA actions were attempted. See `logs/device_readonly_state_2026-10-21.txt`. The 53-row snapshot above is unchanged; this state check is not counted as a case result.
- Coverage remains incomplete. Findings are confirmed observations, not a final 2.3.0 release decision.

## 1. Objective

Assess the supplied SENTRY SWM-2 firmware against `fw_7/PRD.md`, verify the beta's new features and regression behavior, exercise OTA recovery, and provide an evidence-based GO/NO-GO recommendation for promoting 2.3.0 to stable.

This is a black-box acceptance test. The firmware source is not included; the supplied 2.1.0 merged image is the starting release and 2.3.0 is obtained through OTA.

## 2. References

- Coursework requirements: `requirnments/Курсовий_проєкт_SENTRY_SWM_2.pdf`
- Product requirements: `D:\Projects\EMBEDDED-QA-ENGINEER\EMBEDDED-QA-ENGINEER\forGit\fw_7\PRD.md`
- Test assignment: `D:\Projects\EMBEDDED-QA-ENGINEER\EMBEDDED-QA-ENGINEER\forGit\fw_7\HW-17.md`
- Flash/startup: `D:\Projects\EMBEDDED-QA-ENGINEER\EMBEDDED-QA-ENGINEER\forGit\fw_7\README.md`
- Wiring and safety: `D:\Projects\EMBEDDED-QA-ENGINEER\EMBEDDED-QA-ENGINEER\forGit\fw_7\WIRING.md`
- OTA fault server: `D:\Projects\EMBEDDED-QA-ENGINEER\EMBEDDED-QA-ENGINEER\forGit\fw_7\tools\README.md`

## 3. Scope

### In scope

- Boot, version, flash-slot and system state
- Access-control annotations, Wi-Fi, account lifecycle and lockout
- NORMAL, DEBUG, VERBOSE and EMERGENCY state transitions and restrictions
- Stable/beta update flow, persistence, downgrade protection, rollback and OTA failures
- Smart Lamp, relay, sonar/distance, health telemetry, buttons and physical outputs
- Guard and Alert Center features introduced in 2.3.0
- Regression checks of applicable 2.1.0 behavior after upgrading to 2.3.0
- Exploratory testing for undocumented commands/secrets; report safely and do not publish credentials

### Version-specific expectations

- **2.1.0:** Guard, Alert Center and K4 are planned for 2.3.0. Their documented `E099 ... planned in v2.3.0` response is expected, not a defect.
- **2.3.0:** Includes previous functionality plus Guard, Alert Center and K4; earlier behavior must not regress.
- Compare behavior with the PRD for the version under test. Do not report informational simulator messages or documented warnings as firmware bugs.

## 4. Test strategy

1. **Static preparation:** derive tests and requirement links from the PRD before execution.
2. **Baseline:** connect on COM6, capture boot output, verify firmware/version/partition/state, then establish Wi-Fi and account access.
3. **Version 2.1.0:** execute its applicable functional, boundary, error, persistence, physical and OTA cases.
4. **Upgrade:** use `ota update beta` to reach 2.3.0; capture the complete transition and post-boot self-check; verify data persistence.
5. **Version 2.3.0:** run new Guard/Alert/K4 coverage and repeat applicable baseline tests for regression.
6. **OTA resilience:** test rollback, downgrade controls, server fault modes and successful recovery after failures.
7. **Evidence and decision:** save sanitized UART logs and physical observations; classify defects; assess release blockers and residual coverage risks.

Use the detailed cases in `TEST_CASES.md` and requirement mapping in `TRACEABILITY_MATRIX.md`. Cases begin as **Not run** and are updated only when evidence is recorded; never infer a pass from a command response alone when the PRD requires physical verification.

## 5. Test environment and safety

- ESP32-S3 DevKit connected to the test computer on COM6.
- **Connection check (October 19, 2026):** COM6 is detected as USB-Enhanced-SERIAL CH343 and opens at 115200 8N1.
- **Initial DUT firmware:** station_WiFi v1.5.0 was present before baseline setup.
- **Baseline installed:** with user authorization, erased flash/NVS and wrote `sentry_fw7_v2.1.0_merged.bin` to COM6. esptool verified the image hash. A UART query confirmed SENTRY SWM-2 v2.1.0 on `ota_0 @ 0x20000`, state `valid`; help lists the expected fw_7 commands and Guard/Alert as planned for v2.3.0.
- **Baseline state after latest authorized reset (historical):** SENTRY SWM-2 2.1.0 on `ota_0`, NORMAL, with no saved Wi-Fi network or account profile. The earlier hotspot credentials and disposable account were erased from DUT NVS. Subsequent tests recreated a disposable account and saved the home network; the device is now running 2.3.0, connected, and logged out after test cleanup.
- The post-reset version/state check is captured in `logs/baseline_after_account_reset_2.1.0.txt`; it verifies that historical baseline. Later account tests used a disposable QA account; its password is not included in project files or evidence.
- **Wi-Fi checks:** scan/connect, status/IP/RSSI, net, default ping, time, disconnect, saved-network reconnect, and a deliberate hotspot outage were exercised. The saved-network reconnect NTP warning reproduced 2/2 times on both the earlier test hotspot (2.1.0) and the home network (2.3.0) despite successful internet checks. Isolate NTP server/retry behavior before classifying it as a defect. The outage produced W110 and three attempts; after hotspot restoration manual reconnect was required.
- 2.4 GHz Wi-Fi with internet for default OTA; local test computer and board must share a network for local OTA fault tests.
- UART terminal/logger at 115200 8N1. Record command, complete response, firmware version and timestamp.
- Physical peripherals: HC-SR04-compatible distance sensor, relay module, indicator LED and resistor, buttons, wiring/breadboard; onboard RGB LED is on GPIO48.
- Follow the fw_7 wiring guide, not pin assumptions from prior coursework.
- **Do not apply 5 V to ESP32 GPIO.** The supplied hardware inventory lists a 5 V low-level relay and US-100, while fw_7's guide specifies 3.3 V peripheral supply and HC-SR04 TRIG/ECHO. Verify module voltage, signal levels, mode/jumpers, and button wiring before connecting. If compatibility is uncertain, leave that component disconnected and mark dependent tests Not run/Blocked; do not risk the board.
- Do not connect mains or a hazardous load to the relay. The relay contacts are not needed to test firmware logic.
- Redact Wi-Fi passwords and account secrets from all submitted evidence (`***`).
- Preserve original evidence; do not modify or delete existing work without authorization.

## 6. Entry and exit criteria

### Entry

- Firmware image and tools are available; port COM6 opens reliably.
- Wiring is checked against fw_7 pin and voltage requirements.
- Wi-Fi credentials are available to the tester but are not recorded in submitted logs.
- Baseline test cases and log naming are prepared.

### Exit

- All feasible mandatory tests have an explicit result: Pass, Fail (bug ID), Not run, or Blocked with reason.
- Both firmware versions have versioned checklists; 2.3.0 regression and new-feature checks are represented.
- OTA transition, rollback, and each attempted fault/recovery scenario have evidence.
- Every confirmed failure has a reproducible bug report and severity/priority.
- Limitations and untested items are visible; no unexecuted test is presented as passing.
- A reasoned 2.3.0 GO/NO-GO recommendation, final package and defense presentation are prepared.

## 7. Result and defect conventions

- **Pass:** observed behavior matches the applicable PRD requirement and evidence is saved.
- **Fail:** behavior conflicts with the PRD; create a unique bug ID and link it to the case and requirement.
- **Not run:** not executed yet.
- **Partial:** some assertions passed or failed, but the case includes untested assertions or boundary conditions.
- **Investigate:** observation is inconclusive and requires isolation before defect classification.
- **Blocked:** cannot safely or practically execute; explain dependency and impact.
- **N/A:** requirement explicitly does not apply to that version.

For each defect record firmware version, severity, priority, preconditions, numbered reproduction steps, expected behavior and PRD reference, actual behavior, evidence path, reproduction count, and whether it is fixed/regressed in the other version.

## 8. Presentation and defense

Prepare a visual, evidence-led presentation for a defense of up to 10 minutes. Cover the product and versions, requirements-based test approach, physical bench and future HIL/CI design, coverage, highest-impact findings, limitations, and the 2.3.0 release decision. Rehearse and prepare for questions about boundaries, OTA safety, physical-vs-automated evidence, and residual risks. Release package and presentation target: October 21; defense: October 22.
