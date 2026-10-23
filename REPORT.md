# SENTRY SWM-2 Acceptance Test Report

**Test period:** October 19-21, 2026  
**Device:** ESP32-S3 DevKit, COM6, UART 115200 8N1  
**Firmware under test:** 2.1.0 stable and 2.3.0 beta  
**Oracle:** fw_7 `PRD.md`; detailed test design and traceability are in [TEST_CASES.md](./TEST_CASES.md) and [TRACEABILITY_MATRIX.md](./TRACEABILITY_MATRIX.md).  
**Report status:** Final evidence-based report (evidence through 22 Oct 2026). Physical bench, Guard/Alert, OTA, security and 2.1.0 repeat testing were completed; planned coverage is still not 100% (a few cases such as calibrate 5/300 cm boundaries were not run), so unrepresented cases must not be treated as passing.

## 1. Summary and release decision

The board finished the test window running valid 2.3.0 on `ota_1`, logged in with a new test account, Wi-Fi connected. On October 21, after the original account's username could not be recovered, the board was erased and reflashed with 2.1.0, a new test account was registered, Wi-Fi was reconnected, and 2.3.0 was reinstalled by local OTA. A large additional block of account, state, lamp, relay, sonar, telemetry, OTA-server and bonus security testing was then completed on both firmware versions in the same session; see sections 2-5 below.

**Recommendation: NO-GO for promoting 2.3.0 to stable at this time.** Confirmed PRD boundary violations remain present on 2.3.0: `distance 20` is rejected although the accepted range is 1–20 (BUG-01), `relay pulse` accepts most values below the documented 100 ms minimum (BUG-02), and the relay cycle counter miscounts (BUG-04). The documented `distance calibrate reset` is rejected on both versions (BUG-07, low). On 2.3.0 the Guard wrong-PIN attempt counter is never reset, so after three lifetime wrong PINs a single typo raises a full ALARM with the relay open (BUG-06). The 2.3.0 beta also retains the invalid relay/distance behavior found on 2.1.0. Wi-Fi-loss-during-OTA and relay contact behavior under a real load remain unverified.

This is a release recommendation for the tested build, not a statement that 2.3.0 is less stable than 2.1.0 in general. BUG-01, BUG-02 and BUG-04 reproduce on both versions (with different specifics for BUG-04); BUG-03 is a 2.1.0-only boundary defect that was accepted on 2.3.0 and was re-confirmed on October 21 with a fresh device/account.

## 2. Test execution checklist

This checklist summarizes recorded evidence, not every assertion within each requirement. See the traceability matrix for detail. **Partial** means some assertions passed or failed while others remain untested. **Not run** and **Blocked** are not passes.

| PRD area | 2.1.0 stable | 2.3.0 beta |
|---|---|---|
| Baseline, version, partition, startup, help | Pass for recorded baseline/version/startup/help checks; clean baseline rerun verified; non-Latin-character handling (W006) and malformed command parsing confirmed | Valid image and partition verified after rollback/restoration/reinstall; non-Latin-character handling confirmed |
| Access and account | Valid account/login, `whoami`, duplicate-registration rejection, full lockout/relock cycle, `passwd` change with persistence across logout/reboot, and already-logged-in/logout rules all verified on the new test account | Same full account/lockout/passwd suite verified; format-specific E203/E204/E205 codes could not be exercised on a single-profile device without destroying the active account |
| Wi-Fi and network | Scan/connect, IP/RSSI, internet, network info, default ping, time, and saved reconnect observed; outage produced W110 and three retries; multiple edge cases pending | Saved reconnect, disconnect/reconnect warnings, default and custom-host ping, network info, and time observed; input validation and other network errors pending |
| NTP after reconnect | W106 repeated 2/2 times on test hotspot despite internet check; later reconnect synced | W106 repeated 2/2 times on home network despite IP/internet checks; a later reconnect synced |
| OTA upgrade, rollback, recovery | Upgrade source image and valid rollback slot verified; 2.1.0 restored and self-check passed; later re-registered and re-upgraded to 2.3.0 by local OTA | Upgrade, broken-image automatic rollback, manual rollback (both directions), forced stable restore/downgrade with data persistence, and current-beta no-op verified; final beta and stable slots valid |
| OTA input protection | Downgrade without force returned E408 in the comparison run | E408, malformed-version E414, unavailable-version E415, unsupported-scheme E418, server-unavailable E402, invalid-channel E404/E415, and custom-server persistence/restoration all observed |
| OTA local fault matrix | garbage/truncated/corrupted/drop-at-50% all rejected cleanly (E406/E412/E410); recovery OTA succeeded afterward | Same four faults repeated and rejected cleanly; slow-transfer-with-Wi-Fi-loss attempt did not conclusively interrupt the download (see limitations) |
| Smart Lamp | Boundary/error-code suite passed (color/brightness/mode/scene limits); **timer unit discrepancy found** (ms displayed vs. s actual, BUG-05) | Full boundary/error-code suite passed (on/off/toggle, color, brightness, mode, timer, scenes); physical output checks pending |
| Relay | `relay pulse 99` (and most sub-100 ms values) accepted (BUG-02); rate-limit E602 confirmed; cycle counter double-counts (BUG-04); max duration accepted; relay health reported good; physical contact not verified | Same relay boundary suite passed except pulse-minimum (BUG-02, refined) and cycle counter under-counts after an open-at-reboot (BUG-04); schedule/auto/health all verified; physical contact not verified |
| Distance sensor | `distance 19` accepted; `distance 20` rejected (BUG-01); log interval, concurrent-command rejection (E711), calibrate and alarm boundaries all verified | Same full boundary suite (count, log interval, concurrency, calibrate, alarm, filter, stats, history) verified; `distance 20` rejected (BUG-01) |
| Health telemetry | Health report and periodic report observed; 300 s rejected (BUG-03, re-confirmed Oct 21); interval boundaries, on/off and now all verified | `health now`, auto on/off, interval boundary checks (10/300 accepted, 9/301 rejected), and 60 s restoration observed |
| States / EMERGENCY | EMERGENCY command blocking (E005), rising reported temperature, and reboot-only exit (E304) verified | Full state-machine suite verified: DEBUG/VERBOSE transitions, repeat-state W303, invalid-state E301, EMERGENCY entry/exit rules, logout-to-NORMAL |
| Guard and Alert Center | Planned for a later version; absence is not a defect | Arm/intrusion/ALARM timeout, PANIC, 3-wrong-PIN alarm, PIN change rules (E804/E807), zone E808, critical-alert relay + VERBOSE (AL-5), ack/clear errors all verified with tester-observed relay click and GPIO4 LED; **wrong-PIN counter never resets (BUG-06)**; tamper (no echo), 10 s reminders, K4-hold and logout-does-not-disarm verified; GPIO4 LED is the DS-7 proximity indicator (see limitation 1), not a plain relay-state LED |
| Buttons, physical LEDs | Not run | K1/K2/K3 short and long presses, K4 short and hold, all four state chords (incl. K4+K1 to EMERGENCY) and button blocking in EMERGENCY (E005) verified; lamp RGB colors, status LED, relay click and GPIO4 LED tester-observed; chord negative case (K4+K1 from NORMAL: E302) verified |
| Security / hidden-command exploration | Not run | **Performed:** boot-log build tag decodes to the debug `sudo` password (finding, now redacted everywhere); debug elevation verified correct lockout/already-debug behavior; `selftest` hidden diagnostic command found and exercised; ~15 other guessed command names found nothing further |

Execution-row snapshot from `TEST_CASES.md`: **101 result rows across 64 distinct case IDs** — 40 full Pass, 47 Partial (including pass-with-limited-scope), 11 Fail, 2 Investigate, and 1 Not run (bucketed by the status column; an earlier running tally was replaced by this recount). These rows are not a percentage of total planned coverage; many planned case IDs have no execution row.

## 3. Bug reports

Complete reproductions, prerequisites, PRD expectations, evidence, impact, and triage notes are in [BUG_REPORTS.md](./BUG_REPORTS.md).

| ID | PRD | Severity / priority | 2.1.0 | 2.3.0 | Classification |
|---|---|---|---|---|---|
| BUG-01 — `distance 20` rejected | DS-1: inclusive count 1–20 | Medium / P2 | Fail; re-confirmed on reset device | Fail; 2/2 rejected, re-confirmed | Existing defect on both versions; not a beta regression |
| BUG-02 — `relay pulse` accepts most sub-100 ms values | RL-3: inclusive pulse 100–10,000 ms | Medium / P2 | Fail; only 1 ms rejected | Fail; boundary scan found only 1 ms rejected (101→10 ms all accepted) | Existing defect on both versions; not a beta regression; relay contact operation unverified |
| BUG-03 — health interval 300 s rejected | HL-3: inclusive interval 10–300 s | Medium / P2 | Fail; re-confirmed on reset device | 300 s accepted | Stable-only defect; observed corrected in beta |
| BUG-04 — relay cycle counter miscounts | RL-2: each on/off = +1, stored in NVS | Low / P3 | Fail; every edge counted as +2 | Fail; counter loses 2 across a reboot that leaves the valve open | Different mechanism per version; present on both |

### Version bug matrix

| Bug | Stable 2.1.0 | Beta 2.3.0 | Regression status |
|---|---|---|---|
| BUG-01 | Present | Present | Not a beta regression |
| BUG-02 | Present | Present | Not a beta regression |
| BUG-03 | Present | Not reproduced at tested boundary | Beta behavior accepts 300 s; no observed beta regression |
| BUG-04 | Present (double-count) | Present (reboot-loss) | Present on both, different symptom |
| BUG-06 | N/A (Guard planned) | Present | Beta-only feature defect; not a regression |
| BUG-07 | Present | Present | Not a beta regression |

## 4. OTA evidence and operational state

- 2.1.0 → 2.3.0 beta upgrade completed and passed self-check.
- `ota broken` failed self-check and automatically returned the device to valid 2.3.0.
- Manual rollback between valid versions passed self-check in both directions, and was repeated again on October 21 after the device reset (2.3.0→2.1.0, then 2.1.0→2.3.0).
- The broken image had replaced the inactive stable slot. Stable 2.1.0 was subsequently force-installed on `ota_0`, reached 100%, booted, and passed self-check. Manual rollback returned to 2.3.0 on `ota_1`, which also passed self-check.
- Malformed version and unavailable-version requests returned E414/E415; unsupported `ftp://` URL returned E418. Both OTA partitions remained valid.
- `ota server` reported the default update server; a server pointed at a closed port returned E402, overridden invalid stable/beta channel values returned E404/E415, and a custom server persisted across a `reboot` before being restored to default.
- On October 21 the original account username was not recorded, so with authorization the board was erased, reflashed with 2.1.0 and a new test account was registered (credentials kept outside the deliverable). The local-server OTA matrix then ran on both 2.1.0 and 2.3.0 (`logs/ota_local_failure_matrix_2026-10-21.txt`, `logs/ota_local_failure_matrix_2.3.0_2026-10-21.txt`): garbage image E406, truncated and corrupted images E412, interrupted download E410; in every case the running image stayed valid and a later valid local OTA succeeded. Observations: truncated.bin shows 100% progress before failing validation, and failed installs leave the rejected image reported as "previous" in `ota status`.
- A forced downgrade from 2.3.0 to 2.1.0 was used to verify data persistence (lamp color/brightness/mode/scene, relay auto-mode, distance alarm threshold, health interval): all were unchanged after the downgrade (`logs/ota_downgrade_persistence_2026-10-21.txt`).
- A slow-transfer (30 KB/s) local OTA was started and a `disconnect` command was issued partway through, but the download completed and installed successfully; the attempted mid-transfer Wi-Fi loss was not conclusively captured in the log (`logs/ota_slow_wifi_loss_2.1.0_2026-10-21.txt`). This scenario remains open.
- Reinstalling the already-running version (`ota install 2.3.0` without `force`) printed `W409 same version - reinstalling` and completed normally, swapping the running OTA slot; the PRD does not clearly state whether `force` should be required for a same-version reinstall, so this is noted as an observation rather than a bug.
- **Security finding:** the boot banner prints a base64 "build tag" that decodes to a privileged `sudo <password>` command, exposing the debug password in every boot log (credential exposure). The password was used once, with authorization, to confirm the `sudo` elevation path: wrong password returned E213, the decoded password elevated `whoami` to `access: debug`, a repeat `sudo` returned W212, and the elevated access did not survive `logout`. All logs and report text redact this password; it is replaced with `<debugpw>`.
- **Bonus finding:** while in debug access, a hidden `selftest` command runs a 10-point self-check (NVS usage, memory, temperature, link, internet, NTP, sonar echo, valve GPIO readback, buttons, firmware validity) and raises a CIC alert on failure. Sonar failed as expected since no physical transducer is wired in this lab setup. About 15 other plausible hidden command names were tried and found nothing further; unrecognized commands in debug mode return a more verbose parser message (`[DBG] E001 parse error: token '<x>' (len N) not in command table (66 entries)`), a minor information-disclosure note but not a vulnerability by itself.

Evidence: [read-only state check](./logs/device_readonly_state_2026-10-21.txt), [upgrade](./logs/ota_2.1.0_to_2.3.0_beta.txt), [broken-image recovery](./logs/ota_broken_auto_rollback_2.3.0.txt), [fallback restoration](./logs/ota_stable_fallback_restore_2026-10-20.txt), [install rejections](./logs/ota_install_rejections_2.3.0.txt), [URL validation](./logs/ota_url_scheme_2.3.0.txt), [default server](./logs/ota_server_default_2.3.0.txt), [local fault matrix 2.1.0](./logs/ota_local_failure_matrix_2026-10-21.txt), [local fault matrix 2.3.0](./logs/ota_local_failure_matrix_2.3.0_2026-10-21.txt), [server unavailable/channel/persistence](./logs/ota_server_unavailable_channel_persistence_2.3.0_2026-10-21.txt), [downgrade persistence](./logs/ota_downgrade_persistence_2026-10-21.txt), [slow transfer + Wi-Fi loss attempt](./logs/ota_slow_wifi_loss_2.1.0_2026-10-21.txt), [security/hidden commands](./logs/security_sudo_hidden_commands_2.3.0_2026-10-21.txt).

## 5. Security and evidence handling

A bonus hidden-command and security exploration **was performed** on October 21, with authorization. Findings: (1) the debug `sudo` password is exposed in plaintext (via base64) in every boot log — a credential-exposure defect; (2) a hidden `selftest` diagnostic command exists and was exercised safely (read-only self-check); (3) no other hidden commands were found among ~15 guessed names. This is a limited exploration, not a full security audit; absence of further findings must not be read as evidence that no other hidden commands or vulnerabilities exist.

Evidence hygiene: credentials and account identifiers are excluded from the new logs. Private IPv4 and MAC values found in legacy text evidence were redacted. The debug password and its base64-encoded form (found unredacted in two files during this session's work) were located and redacted on October 21. The final audit found no raw private IPv4 or MAC values, no account credentials, and no unredacted debug password in the text logs. Evidence references in project Markdown were checked.

## 6. Limitations and items requiring physical access

1. **Relay/module safety and physical output:** on October 21 the tester observed on the bench (low voltage, 3.3 V, no load) that the 5 V low-level relay module clicked in step with `relay on`/`off`/pulse and that the GPIO4 LED followed it ([log](./logs/physical_bench_observations_2.3.0_2026-10-21.txt)). Contact continuity and any real load were not measured, and the module is driven from 3.3 V instead of its rated 5 V, so contact behaviour under load remains unverified. Do not use mains or hazardous loads.
2. **Sensors, buttons, and indicators:** the RGB lamp (red/green/blue), the NORMAL status LED with the lamp off, K1/K2/K3, K4 short and hold, and all four state chords (K2+K3, K1+K2, K3+K4, K4+K1 into EMERGENCY, with E005 button blocking and reboot-only exit) were verified on 2.3.0 ([log](./logs/button_chords_emergency_2.3.0_2026-10-21.txt)). Sonar readings with a ruler-placed flat target (10/20/30/50 cm → 13.0/21.4/30.9/48.6 cm, stable; the earlier 13.3/16.3/30.3/42.5 run was a placement error) show +3 cm at 10 cm and within about ±1.6 cm from 20 to 50 cm; the PRD sets no tolerance and offset calibration was not exercised ([log](./logs/sonar_accuracy_2.3.0_2026-10-22.txt)). Also verified: the K4+K1 negative case from NORMAL (E302). A phone video of the RGB lamp (red/green/blue/off), the relay click and the GPIO4 proximity LED was recorded on Oct 22 (`evidence/video_2026-10-22_00-49-14.mp4`, about 78 MB, supplied separately from the ZIP) with a matching command timeline ([log](./logs/led_video_session_2.3.0_2026-10-22.txt)).
3. **Guard alarm and CRITICAL alert paths:** run on October 21 at low voltage after relay behaviour was observed (log: [guard_alert_critical](./logs/guard_alert_critical_2.3.0_2026-10-21.txt)). Also run: K4-hold PANIC (relay click and RGB red/blue seen; 10 s ALARM reminder in the log; the GPIO4 LED stayed off, which is consistent with DS-7: it is a proximity indicator that only blinks while the valve is open and measuring, see [log](./logs/gpio4_proximity_indicator_2.3.0_2026-10-22.txt)), sensor tamper (no echo gave ALARM, CRITICAL and relay OPEN), logout-does-not-disarm and the alert edge cases (E855, W852, retention of 20) ([log](./logs/guard_tamper_alert_edge_2.3.0_2026-10-21.txt)). A reboot was confirmed to clear the BUG-06 counter (RAM-only, 9/3 to 1/3).
4. **Wi-Fi/OTA fault injection:** drop, garbage, truncated and corrupted image cases ran on both 2.1.0 and 2.3.0 on October 21. The slow-transfer-plus-Wi-Fi-loss scenario was attempted but did not conclusively interrupt the transfer; it remains open.
5. **Broader behavioral coverage:** The 2.1.0 repeats were done on Oct 22 via `ota rollback` and back ([log](./logs/stable_2.1.0_repeat_and_calibrate_2026-10-22.txt)): Guard/Alert commands return E099 (planned in 2.3.0), K1–K3 and chords, lamp colours and relay click were physically confirmed, and `distance calibrate 20` with a ruler-placed target set -2.0 cm (invalid values E706, no target E707). This found BUG-07 (`distance calibrate reset` rejected on both versions; `distance reset` works). Still open (skipped by choice): calibrate 5/300 cm boundaries with a target (the 2.3.0 calibrate-with-target run was repeated validly: 20 cm target, measured 22.3 cm, offset -2.3 cm, readings then 20.0 cm; [log](./logs/calibrate_with_target_2.3.0_2026-10-22.txt)). The GPIO4 LED was confirmed on Oct 22 as the DS-7 proximity indicator (blinks with the valve open and sonar measuring; wiring relay GPIO8, LED GPIO4); an earlier bench note that it simply "followed the relay" is superseded, and a lit-without-measuring observation on Oct 21 versus off-without-measuring on Oct 22 was not reconciled (background sonar activity is a possible cause). One unexplained observation: the alert "unacknowledged" counter dropped without a command (logged, not classified).
6. **Intermittent NTP warning:** W106 occurred after reconnect in 2/2 trials on each of two networks/firmware combinations despite internet success; subsequent reconnects synced. This remains an unresolved intermittent observation, not a confirmed defect.
7. **Hardware-dependent work:** the renewed 20-minute authorization on October 21 was used for read-only checks; a later authorized 30-minute window (which ran longer, with explicit continued authorization) covered the reset, new account, local OTA fault tests, OTA-server edge cases, downgrade persistence, the account/state/lamp/relay/sonar/telemetry boundary suite, and the bonus security exploration. The board now runs 2.3.0 (`ota_0`, valid) with 2.1.0 last verified valid on `ota_1` during the same session. Any further hardware work requires renewed authorization; do not guess credentials.

## 7. Evidence index and related deliverables

### October 23 automated-regression supplement

A reusable [UART regression suite](./autotests/README.md) now provides automatic
PRD assertions for BUG-01, BUG-02, BUG-03 and BUG-07. A real COM6 run on firmware
2.3.0 produced **4 test methods: 1 Pass, 3 Fail, 0 errors**. The health interval
boundary passed; distance count 20, relay pulse 99 ms and documented calibration
reset failed. Invalid-input neighbours are checked as subtests. These additional
results do not change the earlier 101-row manual/semi-automated snapshot.
The suite restores the starting health interval and closes the relay. It does
not automate physical observations or change firmware versions; 2.1.0 has not
been hardware-validated with this new runner. Final run evidence:
[assertion results](./logs/autotest_2026-10-23_20-24-07.results.txt),
[UART transcript](./logs/autotest_2026-10-23_20-24-07.txt), and
[JSON summary](./logs/autotest_2026-10-23_20-24-07.json).

- [Test cases and execution records](./TEST_CASES.md)
- [Requirements traceability matrix](./TRACEABILITY_MATRIX.md)
- [Bug reports](./BUG_REPORTS.md)
- [Test strategy and safety](./TEST_PLAN.md)
- [HIL bench design](./HIL_DESIGN.md)
- [Project work plan](./PROJECT_WORK_PLAN.md)
- [Defense presentation outline](./PRESENTATION_OUTLINE.md)
- Sanitized UART and execution evidence: [`logs/`](./logs/)
- [Physical photo/video evidence index](./evidence/README.md): October 23
  [red](./evidence/photo_2026-10-23_20-38-09.jpg),
  [green](./evidence/photo_2026-10-23_20-38-05.jpg), and
  [blue](./evidence/photo_2026-10-23_20-37-59.jpg) lamp photos, with tester
  confirmations and firmware RGB status. Qualitative evidence only; not an
  automated colour measurement. Final lamp state was off.

This report and its supporting evidence have been packaged as `HW-17_Zolotykh.zip`. Some planned cases have no execution row and relay contact/load behaviour was not measured; do not present this package as full coverage. Update the report and archive if further authorized test evidence is collected before formal submission.
