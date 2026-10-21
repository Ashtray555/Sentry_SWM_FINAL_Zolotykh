# SENTRY SWM-2 Bug Reports

**Status:** Confirmed findings from black-box acceptance testing. BUG-01, BUG-02 and BUG-04 reproduce on both versions (BUG-04 with a different symptom per version); BUG-03 is a stable 2.1.0 boundary defect accepted by 2.3.0; BUG-05 is a 2.1.0-only cosmetic unit-label defect; BUG-06 (2.3.0 only, Guard) is a wrong-PIN attempt counter that never resets; BUG-07 (both versions, low) is the documented `distance calibrate reset` being rejected. Retest after fixes before changing the provisional NO-GO recommendation. Evidence logs omit credentials and redact private network addresses and the debug password.

## BUG-01 — `distance 20` rejected although PRD includes 20

- **Severity:** Medium
- **Priority:** P2
- **Found in:** 2.1.0 stable and 2.3.0 beta
- **Reproducibility:** `distance 20` rejected in 2/2 attempts on each version.
- **Other versions:** Confirmed on 2.1.0; not limited to the beta build.
- **Requirement:** PRD DS-1 — `distance <N>` accepts 1–20 measurements, inclusive.
- **Preconditions:** Device connected to Wi-Fi and logged in; 2.3.0 active on `ota_1`; sonar command available.
- **Steps:**
  1. Run `distance 19`.
  2. Observe that measurement begins and completes with an average.
  3. Run `distance 20`.
  4. Repeat `distance 20`.
- **Expected:** Both 19 and 20 are accepted; 20 requests twenty measurements and reports an average.
- **Actual:** On both versions, `distance 19` is accepted while `distance 20` returns `E704 count must be 1-20` without measuring. On 2.1.0 the 19-sample run completed with 19/19 valid echoes.
- **Evidence:** [distance_relay_validation_2.3.0.txt](./logs/distance_relay_validation_2.3.0.txt), [distance_count_upper_bound_retest_2.3.0.txt](./logs/distance_count_upper_bound_retest_2.3.0.txt), [distance_count_validation_2.1.0.txt](./logs/distance_count_validation_2.1.0.txt), [functional_limits_and_errors_2.3.0_2026-10-21.txt](./logs/functional_limits_and_errors_2.3.0_2026-10-21.txt), [functional_limits_and_errors_2.1.0_2026-10-21.txt](./logs/functional_limits_and_errors_2.1.0_2026-10-21.txt).
- **Impact:** The documented maximum sample count is unavailable; a user can work around it with 19, but cannot execute the specified 20-sample measurement.
- **Triage note:** Reproduced on stable and beta; this is not a beta-only regression. A prior 2.3.0 19-sample run had 14/19 valid echoes, while the 2.1.0 comparison had 19/19. Echo variability is separate from the deterministic count-limit rejection. Re-confirmed on October 21 on a freshly reset device/account: `distance 20` returned E704 on both 2.1.0 and 2.3.0.

## BUG-02 — `relay pulse 99` is accepted despite minimum of 100 ms

- **Severity:** Medium
- **Priority:** P2
- **Found in:** 2.1.0 stable and 2.3.0 beta
- **Reproducibility:** `relay pulse 99` accepted in 6/6 attempts on 2.3.0 and 1/1 attempt on 2.1.0.
- **Other versions:** Also reproduced on 2.1.0; not limited to the beta build.
- **Requirement:** PRD RL-3 — pulse duration range is 100–10000 ms; values below 100 ms must return E603.
- **Preconditions:** Device logged in; relay-status check showed closed. Tester reports relay VCC at 3.3 V, direct GPIO8-to-IN wiring, and low-voltage indicator-only load.
- **Steps:**
  1. Run `relay pulse 99`.
  2. Observe the UART output and, only if safe, the relay indicator.
- **Expected:** `E603 pulse must be 100-10000 ms`; relay remains closed and no pulse is started.
- **Actual:** On 2.3.0, firmware logged `[VALVE] OPEN (pulse)` and `[VALVE] CLOSED (pulse end)` in all six attempts. On 2.1.0, the same below-minimum command also logged OPEN/CLOSED. It did not reject the invalid duration on either version. The tester reports that GPIO4, ESP32 RGB, relay-module, and other LEDs blinked briefly during the latest 2.3.0 pulse. Relay contact switching was not independently observed.
- **Evidence:** [distance_relay_validation_2.3.0.txt](./logs/distance_relay_validation_2.3.0.txt), [relay_pulse_boundary_retest_2.3.0.txt](./logs/relay_pulse_boundary_retest_2.3.0.txt), [relay_pulse_gpio4_observation_2.3.0.txt](./logs/relay_pulse_gpio4_observation_2.3.0.txt), [relay_pulse_boundaries_2.1.0.txt](./logs/relay_pulse_boundaries_2.1.0.txt), [relay_pulse_boundary_2.3.0_2026-10-21.txt](./logs/relay_pulse_boundary_2.3.0_2026-10-21.txt).
- **Impact:** An out-of-range command is accepted and commands the output on both stable and beta. UART timestamps show approximately 110–120 ms between OPEN/CLOSED logs on 2.3.0; multiple LEDs reportedly blinked during the latest beta pulse. Relay contact timing/switching was not observed.
- **Triage note:** This defect is present on both versions, not a beta-only regression. The 10,000 ms maximum was accepted on 2.1.0 and the relay later reported closed; 10,000 ms on 2.3.0 and 100 ms on 2.1.0 remain untested. Tester reports the relay input uses the 3.3 V rail. LED wiring/causality beyond the reported pulse-synchronous blink is not established. On October 21, a boundary scan on 2.3.0 found the real lower limit: 101, 100, 99, 98, 90, 50 and 10 ms were all accepted (pulse width scaled down with the requested value, e.g. ~30 ms open for a 10 ms request), and only 1 ms was rejected with E603. So validation only rejects very small values, not everything below the documented 100 ms minimum.

## BUG-03 — Stable firmware rejects the valid 300-second health interval

- **Severity:** Medium
- **Priority:** P2
- **Found in:** 2.1.0 stable
- **Reproducibility:** 2/2 attempts on 2.1.0
- **Other versions:** 2.3.0 beta accepted 300 seconds.
- **Requirement:** PRD HL-3 — `health interval <10-300>` accepts both endpoints, inclusive.
- **Preconditions:** Device logged in; health reporting enabled with a 60-second interval.
- **Steps:**
  1. Run `health interval 299` and confirm acceptance.
  2. Run `health interval 300`; repeat.
  3. Run `health interval 301`.
  4. Restore `health interval 60` and verify with `health`.
- **Expected:** 299 and 300 are accepted; 301 is rejected with E902. Interval is restored to 60 seconds.
- **Actual:** 299 was accepted, but `health interval 300` returned `E902 interval must be 10-300 s` in both attempts on 2.1.0. The adjacent invalid value 301 was rejected. The same 300-second value was accepted on 2.3.0.
- **Evidence:** [health_interval_boundaries_2.1.0.txt](./logs/health_interval_boundaries_2.1.0.txt), [health_interval_boundaries_2.3.0.txt](./logs/health_interval_boundaries_2.3.0.txt), [functional_limits_and_errors_2.1.0_2026-10-21.txt](./logs/functional_limits_and_errors_2.1.0_2026-10-21.txt).
- **Impact:** Stable users cannot configure the documented maximum telemetry interval; 299 seconds is a workaround. The tested beta accepts the maximum.
- **Triage note:** This is a stable-version defect with evidence that it is corrected in 2.3.0 beta. The configured interval was restored to 60 seconds on both versions. Re-confirmed on October 21 on a freshly reset 2.1.0 device/account: `health interval 300` still returned E902.

## BUG-04 — `relay` cycle counter sometimes increments by 2 instead of 1, and sometimes loses 2 across reboot

- **Severity:** Low
- **Priority:** P3
- **Found in:** 2.1.0 stable and 2.3.0 beta
- **Reproducibility:** The double-increment reproduced on every `relay on`/`off`/`toggle` on 2.1.0 (7/7 commands) and did not reproduce on 2.3.0 (7/7 commands incremented by exactly 1, `relay pulse` by 2, consistent with one open + one close edge).
- **Requirement:** PRD RL-2 — "одне перемикання on або off = +1" (one on or off switch = +1), counter stored in NVS and must survive reboot.
- **Preconditions:** Device logged in, relay idle.
- **Steps:**
  1. Record `relay status` cycle count.
  2. Issue one `relay on`, `relay off`, or `relay toggle`.
  3. Record the new cycle count and compute the delta.
  4. Separately, switch the relay an odd number of times (e.g. 1 or 3), note the count, reboot, and compare.
- **Expected:** Each `on`/`off`/`toggle` adds exactly 1 to the counter; the counter is unchanged by a reboot.
- **Actual:** On 2.1.0, every single edge (`on`, `off`, or `toggle`) added 2 to the counter instead of 1, and `relay pulse 200` added 4 instead of 2. On 2.3.0 the per-command delta was correct (+1 per edge, +2 per pulse), but after an odd number of switches (1 or 3) left the relay open at reboot, the counter read 2 lower after the reboot than immediately before it; an even number of switches (leaving it closed) was unaffected.
- **Evidence:** [relay_cycles_delta_per_command_2.1.0_2026-10-21.txt](./logs/relay_cycles_delta_per_command_2.1.0_2026-10-21.txt), [relay_cycles_persistence_2.1.0_2026-10-21.txt](./logs/relay_cycles_persistence_2.1.0_2026-10-21.txt), [relay_cycles_delta_per_command_2.3.0_2026-10-21.txt](./logs/relay_cycles_delta_per_command_2.3.0_2026-10-21.txt), [relay_cycles_persistence_2.3.0_2026-10-21.txt](./logs/relay_cycles_persistence_2.3.0_2026-10-21.txt).
- **Impact:** The wear counter (used by `relay health` against the 100,000-cycle contact life budget) is unreliable: it over-counts on stable and loses counts across a reboot that ends with the valve open on beta. Both directions make the reported wear level inaccurate rather than conservative.
- **Triage note:** Two distinct behaviors, so possibly two causes: a NVS/debounce double-count path active only on 2.1.0, and a save-on-close-only persistence path active only on 2.3.0 (an open relay state is not flushed to NVS before reboot, so the last open-transition increment is lost). Logout also closes the relay (PRD RL-7) and was not tested as a save trigger; not enough data to confirm the mechanism. Rated low severity because it does not affect valve operation, only the reported wear statistic.

## BUG-05 — `lamp timer` countdown message reports milliseconds instead of seconds on 2.1.0

- **Severity:** Low
- **Priority:** P3
- **Found in:** 2.1.0 stable only
- **Reproducibility:** 2/2 (`lamp timer 10` and `lamp timer 60`).
- **Requirement:** PRD LM-5 — `lamp timer <1-3600>` is in seconds, and `[BEACON] auto-off in N s` must report seconds; `lamp status` shows `timer N s left`.
- **Preconditions:** Device logged in, lamp on.
- **Steps:**
  1. `lamp on`, then `lamp timer 10`.
  2. Observe the confirmation message.
  3. Poll `lamp status` over several seconds and observe when the lamp actually turns off.
- **Expected:** Confirmation reads `auto-off in 10 s`; the lamp turns off after approximately 10 seconds, matching `lamp status`'s decreasing `timer N s left`.
- **Actual:** On 2.1.0, the confirmation read `auto-off in 10 ms` (and `auto-off in 60 ms` for the second case) — a unit label defect — but the actual behavior used seconds: `lamp status` correctly counted down in seconds (`timer 7 s left`, then `timer 3 s left`) and the lamp turned off after the configured number of seconds, not milliseconds. On 2.3.0 the same commands correctly printed `auto-off in 10 s`.
- **Evidence:** [lamp_timer_unit_and_misc_2.1.0_2026-10-21.txt](./logs/lamp_timer_unit_and_misc_2.1.0_2026-10-21.txt), [functional_limits_and_errors_2.3.0_2026-10-21.txt](./logs/functional_limits_and_errors_2.3.0_2026-10-21.txt).
- **Impact:** Cosmetic/documentation-facing only — the actual timer behavior is correct and matches the PRD; only the one-line confirmation message on 2.1.0 shows the wrong unit, which could mislead an operator reading the console log.
- **Triage note:** Fixed in 2.3.0 (not a beta regression); likely a leftover string-format bug from stable, worth a one-line fix before any further 2.1.0 patch release.

## BUG-06 — Guard wrong-PIN attempt counter is never reset by `guard arm` or a correct PIN

- **Severity:** Medium
- **Priority:** P2
- **Found in:** 2.3.0 beta (Guard is not available in 2.1.0)
- **Reproducibility:** 4/4 sequences (one initial run plus three isolation cases).
- **Requirement:** PRD GD-4 — the attempt counter starts from zero at every `guard arm` and resets after a correct PIN; the 3rd wrong PIN raises ALARM.
- **Preconditions:** Logged in, Guard disarmed, default PIN 1234, at least 3 wrong PIN attempts earlier since boot.
- **Steps:**
  1. Enter wrong `guard disarm 0000` twice (`Attempts: 1/3`, `2/3`), then `guard disarm 1234` (disarmed).
  2. `guard arm`, wait for INTRUSION (or the arming countdown), then send one wrong `guard disarm 0000`.
  3. Repeat the arm / correct-PIN / single-wrong-PIN cycle.
- **Expected:** A single wrong PIN after a fresh arm reports `Attempts: 1/3` and does not alarm.
- **Actual:** The counter is cumulative since boot. The single wrong PIN after a fresh arm reported `Attempts: 3/3` and raised a GENERAL ALARM (CRITICAL alert, relay OPEN, state VERBOSE). Later cycles reported `6/3`, `7/3`, `8/3`, each raising ALARM again, and wrong PINs during an alarm printed `4/3`, `5/3`.
- **Evidence:** [guard_alert_critical_2.3.0_2026-10-21.txt](./logs/guard_alert_critical_2.3.0_2026-10-21.txt).
- **Impact:** After the first three lifetime wrong PINs, one typing mistake by the operator triggers a full ALARM with the relay open. This is a false alarm risk on the safety/actuator path. A reboot clears the counter (9/3 before reboot, 1/3 after), so it is RAM-only, not persisted; a reboot is the only workaround.
- **Triage note:** Neither `guard arm` nor a successful disarm resets the counter, so likely the reset code is missing. Retest after the fix.

## BUG-07 — `distance calibrate reset` (documented syntax) is rejected with E706

- **Severity:** Low
- **Priority:** P3
- **Found in:** 2.1.0 stable and 2.3.0 beta
- **Reproducibility:** 3/3 on 2.1.0 and 2/2 on 2.3.0 (original Oct 21 suite logs plus the Oct 22 reruns).
- **Requirement:** PRD DS-3 — `distance calibrate reset` clears the calibration offset; errors are E706/E707.
- **Steps:**
  1. `distance calibrate 20` with a target at 20 cm (offset is set, e.g. -2.0 cm).
  2. `distance calibrate reset`.
  3. `distance stats`.
- **Expected:** The calibration is reset to +0.0 cm.
- **Actual:** `E706 usage: distance calibrate <ref 5-300 cm>`; the offset stays (`calibration -2.0 cm`). The firmware help even prints `distance calibrate <cm> - calibrate by reference object ('reset')`. Undocumented `distance reset` does clear the offset (`calibration reset`, then `+0.0 cm`). `calibrate clear`, `off` and `0` are also rejected.
- **Evidence:** [functional_limits_and_errors_2.1.0_2026-10-21.txt](./logs/functional_limits_and_errors_2.1.0_2026-10-21.txt), [functional_limits_and_errors_2.3.0_2026-10-21.txt](./logs/functional_limits_and_errors_2.3.0_2026-10-21.txt), [stable_2.1.0_repeat_and_calibrate_2026-10-22.txt](./logs/stable_2.1.0_repeat_and_calibrate_2026-10-22.txt).
- **Impact:** A documented command does not work; the operator cannot clear a wrong calibration as the PRD specifies, and the offset otherwise stays until `distance reset` (undocumented) or presumably a reboot (not tested).
- **Triage note:** Either the parser is missing the `reset` sub-command or the PRD syntax is wrong. Correction: an earlier test row recorded `calibrate reset` as accepted; the original logs show it was rejected because the old test only expected E706/E707 for invalid input.
