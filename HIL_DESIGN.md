# SENTRY SWM-2 Hardware-in-the-Loop Bench Design

**Status:** Proposed HIL design with partial manual/semi-automated execution completed through October 20, 2026; hardware compatibility and physical-output gaps remain.
**Purpose:** Satisfy the coursework requirement to describe a theoretical HIL bench for future automation while using available equipment for safe manual/semi-automated acceptance tests.

**October 23 automation supplement:** A delivered [UART regression suite](./autotests/README.md)
now automates four PRD checks with assertions and cleanup. Real 2.3.0 execution:
one test passed, three reproduced known firmware defects. Seven offline tests
validate the runner itself. This is host-side CLI automation, not automated
physical measurement or a completed CI/HIL station.

## Current bench connection

COM6 is detected as USB-Enhanced-SERIAL CH343 and is readable at 115200 8N1. With user authorization, the prior station_WiFi v1.5.0 image/NVS was erased and the fw_7 v2.1.0 merged image installed; esptool verified the written image hash. The device has since been tested on both firmware versions. Final verified state is 2.3.0 valid on `ota_1`, with restored 2.1.0 valid on `ota_0`; both passed OTA self-check. It is connected to saved Wi-Fi and was logged out after testing. Health reporting is auto-on at 60 s, relay closed/auto-off, and Guard disarmed at 50 cm. Evidence is in the project `logs/` folder; account identifiers, credentials, private network addresses and build-tag values are omitted or redacted.

The tester reports that the US-100 is wired with mode/echo level verified, four buttons are wired to the fw_7 inputs, and the relay is powered from 3.3 V with GPIO8 directly connected to IN and only a low-voltage indicator load. These are tester-reported setup details, not independently measured; the relay module's exact model is still unclear. During the latest 99 ms pulse the tester reports brief blinking of the GPIO4 breadboard indicator, ESP32 RGB LED, relay-module indicator, and other LEDs, in addition to UART OPEN/CLOSED logs. The cause of the other LEDs' behavior and relay contact switching were not independently verified. Keep the low-voltage-only setup and verify the module input requirements before connecting another load.

## 1. Bench concept

The ESP32-S3 running the unmodified SENTRY firmware is the device under test (DUT). A host computer connects over USB/UART on COM6, sends CLI commands, captures logs and can host the supplied local OTA server. Physical controls and actuators are observed by a tester; safe, verified signals may later be driven or measured by a dedicated I/O controller.

```text
                  2.4 GHz Wi-Fi / internet
                            |
                 +----------+-----------+
                 | Host PC              |
                 | - UART test runner   |
                 | - log/evidence store |
                 | - local OTA server  |
                 +----------+-----------+
                            | USB, COM6
                  UART 115200 8N1
                            |
                 +----------v-----------+
                 | ESP32-S3 DUT          |
                 | SENTRY fw_7 2.1/2.3  |
                 +--+--------+--------+--+
                    |        |        |
            GPIO 5/18     GPIO 8/4  GPIO 41/40/39/38
             Sonar I/O   Relay/LED    K1-K4 controls
                    |        |        |
             Target/fixture  Safe     Push buttons or
             (manual now;    indicator  verified interface
              actuator later) LEDs
```

The ESP32's onboard RGB LED is GPIO48. The board has no physical depth, hull-pressure or battery sensors for this coursework setup; the PRD says those telemetry values come from a simulator and do not drive module logic.

## 2. Available parts and compatibility gates

The inventory PDF lists an ESP32-S3 DevKit, 2.4 GHz antenna, 1×4 keypad, three LEDs, two breadboards, US-100 ultrasonic sensor, 5 V low-level relay, wires and USB cable. Resistors and additional LEDs are also available. The fw_7 [WIRING.md] specifies a particular setup: HC-SR04 TRIG GPIO5/ECHO GPIO18, relay input GPIO8, external indicator LED GPIO4, buttons K1–K4 on GPIO41/40/39/38, and 3.3 V supply.

Resolve these differences before wiring:

1. **US-100 vs HC-SR04:** confirm sensor mode and pinout. Verify echo output voltage is safe for the ESP32 GPIO. Do not assume US-100 wiring or mode matches the firmware configuration.
2. **5 V low-level relay vs 3.3 V guide:** verify the module input compatibility and safe supply requirements. Do not feed 5 V to an ESP32 GPIO. If uncertain, leave it disconnected; use serial state and a safe, resistor-limited indicator only if electrically appropriate.
3. **1×4 keypad vs four buttons:** fw_7 expects each button input to be pulled up and pressed to GND. Confirm the keypad exposes four independent switches compatible with that arrangement; a matrix requiring scanned rows/columns is not automatically interchangeable.
4. **External LEDs:** use a series resistor and correct polarity. Follow the fw_7 guide's GPIO4 wiring for its diode indicator. Do not parallel an LED directly across a GPIO and a supply rail without a current-limiting resistor.
5. Assemble with USB power disconnected. Inspect for shorts and wiring errors before connecting the board. No mains or high-current relay load is required.

If any gate cannot be verified, mark dependent tests **Blocked** and preserve the board; do not experiment with unsafe voltage levels. Refer to the component documentation or instructor for confirmation.

The previous DZ-16 bench run reported mostly sensor timeouts with its US-100/assumed wiring and an active-low relay response. These are useful setup risks to investigate, **not fw_7 test results**. Recheck sensor mode, wiring, voltage and relay polarity against fw_7 before attributing any observation to this firmware.

## 3. Test stimulus and observation

| Firmware area | Stimulus | Observation / oracle |
|---|---|---|
| UART CLI, auth, states | Host sends commands and records responses | PRD output/error codes, access behavior and state |
| Wi-Fi and OTA | Host network/hotspot; local OTA server fault modes | UART logs, server request log, version/slot/self-check after reboot |
| Sonar | Move a suitable target to known measured distances; remove target for no-echo check | Reported distance, PRD threshold/error behavior; compare to ruler |
| Buttons | Press/hold each correctly wired input and documented button pairs | UART press/action logs and resulting state |
| Relay and external indicator | Safe relay command with no hazardous load | Relay state from CLI plus observed click/indicator where module compatibility permits |
| RGB lamp | Commands and LED priority events | Visually observe color/mode/brightness/on-off; compare with `lamp status` |
| Guard/alerts (2.3.0) | Commands, target motion, button events and controlled sensor fault | Guard state/timers, alert IDs/acknowledgement, relay and LED effects |
| Simulated carrier telemetry | System time and firmware-driven simulator | Check format/cadence; do not treat modelled depth/pressure/battery as real sensor measurements |

For physical outputs, save a dated note/photo/video when useful and record the matching UART log. A command acknowledgement alone does not prove the physical output changed.

## 4. Host software and CI extension

### Initial, deadline-appropriate setup

- Use a serial terminal or a small Python `pyserial` runner on COM6 to send one command at a time, capture timestamped responses and save logs.
- Keep credentials out of scripts and logs. Redact any echoed Wi-Fi password as `***`.
- Run the provided fw_7 local OTA server on the host for drop/slow/invalid-image scenarios. The ESP32 and host must be on the same network. Return the device to `ota server default` at the end.
- Keep visual/physical checks manual, with explicit evidence and a tester sign-off.

### Future CI-capable HIL

1. A dedicated runner claims the bench and verifies the DUT identity/version before running.
2. CI flashes the known 2.1.0 merged image only when a safe, documented recovery/erase procedure is available; it then performs smoke and UART CLI tests.
3. A serial adapter/logger provides timestamped transcripts; test assertions map to the requirement IDs in `TRACEABILITY_MATRIX.md`.
4. A local OTA service supplies pinned firmware and deterministic failure modes on an isolated test network.
5. A safe fixture may later emulate button closures and sonar echo timing and may monitor GPIO outputs. Add voltage-level protection/isolation before any automated electrical connection.
6. CI uploads sanitized logs, versions, test results and bug evidence. Secrets are injected securely and never printed.
7. Human approval remains required for destructive OTA/rollback tests and visual color checks until the fixture has validated sensing and recovery.

Do not claim these future automation components exist in the current bench. The present deliverable is a design plus manual/semi-automated tests using verified hardware.
