# Physical evidence

## October 23 RGB lamp photo session

The tester confirmed each colour and took a photo before the next command.
Commands set solid mode, 80% brightness, then red, green and blue; `lamp status`
confirmed each RGB value. The lamp was turned off and its final state read back.

| Observed colour | Firmware status | Original photo |
|---|---|---|
| Red | ON, (255,0,0), solid, 80% | [Red photo](./photo_2026-10-23_20-38-09.jpg) |
| Green | ON, (0,255,0), solid, 80% | [Green photo](./photo_2026-10-23_20-38-05.jpg) |
| Blue | ON, (0,0,255), solid, 80% | [Blue photo](./photo_2026-10-23_20-37-59.jpg) |

Filename timestamps reflect the saved files, not command sequence. Photos are
mapped by visible LED glow and tester confirmations; bright LED cores are
overexposed, so these are qualitative visual evidence, not colour measurements.
Original images have not been edited. This is a manual physical confirmation
supported by UART commands, not an automated optical test.

## October 22 video

[LED and relay video](./video_2026-10-22_00-49-14.mp4) with the
[matching command timeline](../logs/led_video_session_2.3.0_2026-10-22.txt).
The video and photos are included in the complete project ZIP.
