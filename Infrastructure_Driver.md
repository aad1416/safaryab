
Here’s what each unit under **Infrastructure/Driver** does:

---

## Base / device hierarchy

### 1. **AbstractDeviceDriver** (`AbstractDeviceDriver.h`)

**Role:** Base for all hardware drivers; also a lockable resource so only an Accessor can use it.

- Declares pure virtual `health_check(access_token)` and inherits from `commons::AbstractLockableResource` (so drivers get `access_check`, acquire/release).
- No .cpp or -inl; no default implementation.

**Used by:** All other abstract drivers (camera, motor, light, beep, door, gripper, etc.).

---

### 2. **AbstractCameraDriver** (`AbstractCameraDriver.h`)

**Role:** Base for camera drivers: init/release and take picture.

- Declares: `init(access_token)`, `release(access_token)`, `take_picture(access_token)` returning `commons::RawImage`.
- No -inl or .cpp.

**Used by:** AbstractHighQualityCameraDriver, AbstractLowQualityCameraDriver.

---

### 3. **AbstractMotorDriver** (`AbstractMotorDriver.h`, `AbstractMotorDriver-inl.h`)

**Role:** Base for motor drivers: velocity, acceleration, limits, step unit, move/stop.

- **AbstractMotorDriver.h** – Declares: `init`, `home`, `get_min_limit`/`get_max_limit`, `stop`, `set_velocity`/`get_current_velocity`, `set_acceleration`/`get_acceleration`, `set_min_limit`/`set_max_limit`, `set_step_unit`, `move_to`, `move_to_min`, `move_to_max`, `get_position`. Protected: velocity_, acceleration_, step_unit_, should_stop_. Private: min_limit_, max_limit_.
- **AbstractMotorDriver-inl.h** – Inline: default ctor, ctor(velocity, acceleration, min_limit, max_limit, step_unit), all getters/setters and `stop` (sets should_stop_ = true); setters call `access_check(access_token)`.

**Used by:** AbstractHorizontalMotorDriver, AbstractZMotorDriver.

---

### 4. **AbstractHorizontalMotorDriver** (`AbstractHorizontalMotorDriver.h`, `AbstractHorizontalMotorDriver-inl.h`, `AbstractHorizontalMotorDriver.cpp`)

**Role:** Horizontal (XY) motor: adds “named positions” for load/unload and low-quality capture.

- **AbstractHorizontalMotorDriver.h** – Extends AbstractMotorDriver; declares `move_to_load_on_stage_point`, `move_to_unload_to_rackfield_point`, `move_to_low_quality_picture_point`.
- **AbstractHorizontalMotorDriver-inl.h** – Empty (only include guard).
- **AbstractHorizontalMotorDriver.cpp** – Ctor(min_limit, max_limit) forwards to AbstractMotorDriver(0, 0, min_limit, max_limit, 0).

**Used by:** AbstractXMotorDriver, AbstractYMotorDriver.

---

### 5. **AbstractXMotorDriver** (`AbstractXMotorDriver.h`, `AbstractXMotorDriver-inl.h`, `AbstractXMotorDriver.cpp`)

**Role:** X-axis motor: adds “wait for move to finish”.

- **AbstractXMotorDriver.h** – Extends AbstractHorizontalMotorDriver; declares `wait_for_move_to_finish(access_token)`.
- **AbstractXMotorDriver-inl.h** – Empty.
- **AbstractXMotorDriver.cpp** – Ctor(min_limit, max_limit) forwards to AbstractHorizontalMotorDriver(min_limit, max_limit).

**Used by:** ZaberXMotorDriver, MockXMotorDriver.

---

### 6. **AbstractYMotorDriver** (`AbstractYMotorDriver.h`, `AbstractYMotorDriver-inl.h`, `AbstractYMotorDriver.cpp`)

**Role:** Y-axis motor; interface same as horizontal, no extra methods.

- **AbstractYMotorDriver.h** – Extends AbstractHorizontalMotorDriver; ctor(min_limit, max_limit) in header.
- **AbstractYMotorDriver-inl.h** – Empty.
- **AbstractYMotorDriver.cpp** – Empty (only includes).

**Used by:** ZaberYMotorDriver, MockYMotorDriver.

---

### 7. **AbstractZMotorDriver** (`AbstractZMotorDriver.h`, `AbstractZMotorDriver-inl.h`, `AbstractZMotorDriver.cpp`)

**Role:** Z-axis motor: jog move, hardware trigger, step-pass and move-finished checks; config from YAML.

- **AbstractZMotorDriver.h** – Declares nested `Config` (FieldRange, serial number, limits, velocities, accelerations, step_unit, poll time, jog step, timeouts; all from YAML). Declares: `init`, `is_step_passed`, `is_move_finished`, `move_jog_to`, `move_absolute_to`, `get_last_checked_position`, `enable_hardware_trigger_mode`, `disable_hardware_trigger_mode`. Protected: config_, is_move_done_, last_checked_position_.
- **AbstractZMotorDriver-inl.h** – Inline: `get_last_checked_position`, all Config getters/setters and `initialize*` from YAML.
- **AbstractZMotorDriver.cpp** – Config ctor loads YAML section `Z_MOTOR_DRIVER`.

**Used by:** ZaberZMotorDriver, MockZMotorDriver.

---

### 8. **AbstractLightDriver** (`AbstractLightDriver.h`, `AbstractLightDriver-inl.h`)

**Role:** Base for light drivers: on/off and state.

- **AbstractLightDriver.h** – Declares: `is_on()`, `turn_on(access_token)`, `turn_off(access_token)`.
- **AbstractLightDriver-inl.h** – Empty.

**Used by:** AbstractTopLightDriver, AbstractBottomLightDriver.

---

### 9. **AbstractTopLightDriver** / **AbstractBottomLightDriver** (each `.h` only)

**Role:** Markers for “top” and “bottom” light; no extra API beyond AbstractLightDriver.

- **AbstractTopLightDriver.h** – `class AbstractTopLightDriver : public AbstractLightDriver {}`.
- **AbstractBottomLightDriver.h** – Same for bottom.

**Used by:** TopLightDriver, BottomLightDriver and their mocks.

---

### 10. **AbstractBeepDriver** (`AbstractBeepDriver.h`, `AbstractBeepDriver-inl.h`)

**Role:** Beep with a mode (e.g. Alert).

- **AbstractBeepDriver.h** – Declares `Mode::Alert` and `beep(access_token, mode)`.
- **AbstractBeepDriver-inl.h** – Typically empty or trivial inlines.

**Used by:** BeepDriver, MockBeepDriver.

---

### 11. **AbstractDoorDriver** (`AbstractDoorDriver.h`, `AbstractDoorDriver-inl.h`)

**Role:** Door lock/unlock and locked state.

- **AbstractDoorDriver.h** – Declares: `is_locked()`, `lock(access_token)`, `unlock(access_token)`.
- **AbstractDoorDriver-inl.h** – Empty or trivial.

**Used by:** DoorDriver, MockDoorDriver.

---

### 12. **AbstractGripperDriver** (`AbstractGripperDriver.h`, `AbstractGripperDriver-inl.h`)

**Role:** Gripper: move (forward/backward, up/down) and hold/release.

- **AbstractGripperDriver.h** – Declares: `move_forward`, `move_backward`, `move_up`, `move_down`, `hold`, `release`.
- **AbstractGripperDriver-inl.h** – Empty or trivial.

**Used by:** GripperDriver, MockGripperDriver.

---

### 13. **AbstractPickAndPlaceDriver** (`AbstractPickAndPlaceDriver.h`)

**Role:** Load/unload slide to/from stage and rack positions; health check.

- Declares: `load_on_scanning_stage(access_token, rack, field)`, `load_on_overview_stage(...)`, `load_from_overview_to_scanning_stage(access_token)`, `unload_to_rackfield(access_token)`, `health_check(access_token)`.
- No -inl or .cpp.

**Used by:** PickAndPlaceDriver, MockPickAndPlaceDriver.

---

### 14. **AbstractRackBoardDriver** (`AbstractRackBoardDriver.h`)

**Role:** Rack board: rack/field presence, rack info, slide detection, move rack to stations.

- Defines `NUMBER_OF_RACKS = 12`, `NUMBER_OF_RACK_SLIDES = 20`. Declares: `has_rack`, `has_field`, `get_rack_information` (returns RackInfoFirmwareResponse), `detect_slides_in_rack`, `move_to_loading_station`, `move_to_slide_gripper_station`, `move_to_slide_detection_station`, `move_to_overview_imaging_station` (all with rack_index and direction string).
- No -inl or .cpp.

**Used by:** RackBoardDriver, MockRackBoardDriver.

---

### 15. **AbstractSlidescopeFirmwareDriver** (`AbstractSlidescopeFirmwareDriver.h`)

**Role:** Firmware “status” driver: get status string, get structured state (racks, lights, door), check, init.

- Declares `StateResult` (racks_occupied_, is_top_light_on_, is_bottom_light_on_, is_door_open_). Declares: `get_status(access_token)`, `get_info(access_token)`, `check(access_token)`, `initialize(access_token)`.
- No -inl or .cpp.

**Used by:** SlidescopeFirmwareDriver, MockSlidescopeFirmwareDriver.

---

### 16. **AbstractSlideSensorBoardDriver** (`AbstractSlideSensorBoardDriver.h`, `AbstractSlideSensorBoardDriver-inl.h`)

**Role:** Slide sensor board: move forward/backward.

- **AbstractSlideSensorBoardDriver.h** – Declares: `move_backward(access_token)`, `move_forward(access_token)`.
- **AbstractSlideSensorBoardDriver-inl.h** – Empty or trivial.

**Used by:** SlideSensorBoardDriver, MockSlideSensorBoardDriver.

---

### 17. **AbstractStageDriver** (`AbstractStageDriver.h`)

**Role:** Placeholder base for “stage” as a single device; no methods beyond AbstractDeviceDriver.

- **AbstractStageDriver.h** – `class AbstractStageDriver : public AbstractDeviceDriver {}`.

**Used by:** Domain Stage uses X/Y/Z motor drivers directly; MockStageDriver implements this for tests.

---

### 18. **AbstractStreamDriver** (`AbstractStreamDriver.h`, `AbstractStreamDriver-inl.h`, `AbstractStreamDriver.cpp`)

**Role:** Live video stream: open/close connection and send compressed frame data; config (port, ip, packet rate, fps).

- **AbstractStreamDriver.h** – Declares nested `Config` (port, ip, packet_transfer_rate, fps from YAML). Declares: ctor(Config), `open(access_token)`, `stream(access_token, data)`, `close(access_token)`, `get_fps()`.
- **AbstractStreamDriver-inl.h** – Inline: ctor, Config getters and `initialize*` from YAML.
- **AbstractStreamDriver.cpp** – Config ctor loads YAML `LIVE_STREAM` section.

**Used by:** StreamDriver (UDP/Boost.Asio implementation).

---

### 19. **AbstractHighQualityCameraDriver** (`AbstractHighQualityCameraDriver.h`, `AbstractHighQualityCameraDriver-inl.h`, `AbstractHighQualityCameraDriver.cpp`)

**Role:** High-quality (scanning) camera: init, take/get picture, RGB, pixel format, HSL, hardware trigger.

- **AbstractHighQualityCameraDriver.h** – Declares `PixelFormat` (MONO8, BAYERRG8), nested `Config` (frame rate, width, height, timeout, stream compression, internal config path, stream format/tool). Declares: `init`, `take_picture`, `get_picture`, `is_image_available`, `enable/disable_hardware_trigger_mode`, `take_rgb_picture`, `change_pixel_format`, `set_hue_saturation_luminance_value`.
- **AbstractHighQualityCameraDriver-inl.h** – Inline: Config getters and `initialize*` from YAML.
- **AbstractHighQualityCameraDriver.cpp** – Config ctor loads YAML `HIGH_QUALITY_CAMERA`.

**Used by:** HighQualityCameraDriver (Pylon/Basler USB), MockHighQualityCameraDriver.

---

### 20. **AbstractLowQualityCameraDriver** (`AbstractLowQualityCameraDriver.h`, `AbstractLowQualityCameraDriver-inl.h`, `AbstractLowQualityCameraDriver.cpp`)

**Role:** Low-quality (overview) camera; config for size, compression, brightness, contrast, exposure, etc.

- **AbstractLowQualityCameraDriver.h** – Declares nested `Config` (width, height, compression_rate, brightness_offset/factor, contrast, exposure, average_intensity_threshold, output_format, image_processing_tool from YAML). No extra methods beyond AbstractCameraDriver in header; concrete drivers add take_picture etc.
- **AbstractLowQualityCameraDriver-inl.h** – Inline: Config getters and `initialize*` (note: one getter pair is swapped brightness_offset/factor in -inl).
- **AbstractLowQualityCameraDriver.cpp** – Config ctor loads YAML `LOW_QUALITY_CAMERA`.

**Used by:** LowQualityCameraDriver, MockLowQualityCameraDriver.

---

## Communication layers

### 21. **ZaberCommunication** (`ZaberCommunication.h`, `ZaberCommunication-inl.h`, `ZaberCommunication.cpp`)

**Role:** Shared serial link to Zaber XY (and Z) hardware: open/close, send/receive, axis limits/speeds/accelerations from YAML. Lockable resource.

- **ZaberCommunication.h** – Declares `Config` (serial port, length/velocity/acceleration units, per-axis min/max limits, max speed, acceleration). Declares open/close, send_command, get_reply, position/velocity/acceleration per axis (X/Y/Z). `MAXIMUM_ZABER_REPLAY_SIZE = 256`.
- **ZaberCommunication-inl.h** – Inline: Config getters and `initialize*` from YAML.
- **ZaberCommunication.cpp** – Config ctor, serial open/close, Zaber ASCII protocol (zaber::motion::ascii), command/reply handling.

**Used by:** ZaberXMotorDriver, ZaberYMotorDriver, ZaberZMotorDriver (shared singleton in DI).

---

### 22. **SlidescopeFirmwareCommunication** (`SlidescopeFirmwareCommunication.h`, `SlidescopeFirmwareCommunication-inl.h`, `SlidescopeFirmwareCommunication.cpp`)

**Role:** Serial (or similar) protocol to device firmware: send commands, parse responses (status, door, rack info, slide detection, etc.). Lockable resource.

- **SlidescopeFirmwareCommunication.h** – Defines `FirmwareStatus` (READY, HAS_ERROR, BUSY, UNKNOWN), helpers (convert_enum_to_string, split_base_response_and_data, hex_to_bits). Declares response types: AbstractFirmwareResponse (StatusCode, deserialize), BasicFirmwareResponse, DoorFirmwareResponse, SlideDetectionFirmwareResponse, RackInfoFirmwareResponse, StatusFirmwareResponse, etc. Declares SlidescopeFirmwareCommunication class: open/close, send_command, get_status, get_door_state, get_rack_info, detect_slides, move_rack, gripper/beep/light/slide-sensor commands, direction enum. Uses Config (e.g. firmware port from YAML) and AbstractSerialCommunication.
- **SlidescopeFirmwareCommunication-inl.h** – Inline: Config getters and response parsing helpers if any.
- **SlidescopeFirmwareCommunication.cpp** – Implements serial open/close, command encoding, response parsing (hex, status bits), all command/response handling (large file ~845 lines).

**Used by:** SlidescopeFirmwareDriver, RackBoardDriver, PickAndPlaceDriver, BeepDriver, DoorDriver, GripperDriver, TopLightDriver, BottomLightDriver, SlideSensorBoardDriver (all firmware-backed drivers share this).

---

## Concrete drivers (real hardware)

### 23. **ZaberXMotorDriver** (`ZaberXMotorDriver.h`, `ZaberXMotorDriver-inl.h`, `ZaberXMotorDriver.cpp`)

**Role:** X-axis motor via Zaber: move, limits, named positions (load/unload, low-quality picture, fix slide); uses ZaberCommunication.

- **ZaberXMotorDriver.h** – Declares nested Config (axis_speed, axis_acceleration, min/max limit, load_on_stage_x, unload_to_rack_field_x, low_quality_picture_position_x, fix_slide_position_x with FieldRange). Implements AbstractXMotorDriver: init, home, move_to, move_to_min/max, move_to_load_on_stage_point, move_to_unload_to_rackfield_point, move_to_low_quality_picture_point, wait_for_move_to_finish, get_position.
- **ZaberXMotorDriver-inl.h** – Inline: Config getters/setters and `initialize*` from YAML.
- **ZaberXMotorDriver.cpp** – Config ctor, all move/position logic via ZaberCommunication (serial commands, units, blocking wait).

**Used by:** Stage (X axis); DI in production when not MOCK_MODE.

---

### 24. **ZaberYMotorDriver** / **ZaberZMotorDriver**

**Role:** Same idea as ZaberXMotorDriver for Y and Z: YAML Config, ZaberCommunication (or Z-specific channel), implement AbstractYMotorDriver / AbstractZMotorDriver (move_to, move_to_min/max, jog, hardware trigger for Z, etc.).

- **ZaberYMotorDriver.h / -inl.h / .cpp** – Config (Y limits, speeds), implement AbstractYMotorDriver and horizontal “named position” methods.
- **ZaberZMotorDriver.h / -inl.h / .cpp** – Config (Z limits, velocities, jog, homing), implement AbstractZMotorDriver (move_jog_to, move_absolute_to, is_step_passed, is_move_finished, enable/disable_hardware_trigger_mode).

**Used by:** Stage (Y and Z axes).

---

### 25. **HighQualityCameraDriver** (`HighQualityCameraDriver.h`, `HighQualityCameraDriver.cpp`)

**Role:** High-quality camera using Pylon/Basler USB (e.g. scanning).

- Implements AbstractHighQualityCameraDriver: init/release, take_picture, take_rgb_picture, get_picture, is_image_available, enable/disable_hardware_trigger_mode, change_pixel_format, set_hue_saturation_luminance_value, health_check. Uses Pylon includes and CBaslerUsbInstantCamera.
- No -inl; config from AbstractHighQualityCameraDriver::Config.

**Used by:** Photographer (scanning images).

---

### 26. **LowQualityCameraDriver** (`LowQualityCameraDriver.h`, `LowQualityCameraDriver.cpp`)

**Role:** Low-quality (overview) camera; different hardware/config than high-quality.

- Implements AbstractLowQualityCameraDriver (and AbstractCameraDriver): init, take_picture, get_slide_preview-style output, brightness/contrast from Config.
- No -inl.

**Used by:** Photographer (overview/preview).

---

### 27. **StreamDriver** (`StreamDriver.h`, `StreamDriver-inl.h`, `StreamDriver.cpp`)

**Role:** Send compressed video frames over UDP for live preview (Boost.Asio).

- **StreamDriver.h** – open/close socket, stream(data) (chunked UDP), get_fps; DEFAULT_CHUNK_SIZE, syn_/fin_ packets, io_service_, socket_, remote_, logger_.
- **StreamDriver-inl.h** – Inline: `get_fps()` returns live_stream_config_->get_fps().
- **StreamDriver.cpp** – open (bind/connect), stream (split into chunks, send), close, health_check.

**Used by:** VideoStreamer (live view).

---

### 28. **SlidescopeFirmwareDriver** (`SlidescopeFirmwareDriver.h`, `SlidescopeFirmwareDriver.cpp`)

**Role:** Single driver that exposes firmware status and state (racks, lights, door) via SlidescopeFirmwareCommunication.

- Implements AbstractSlidescopeFirmwareDriver: get_status, get_info (fills StateResult), check, initialize, health_check by calling SlidescopeFirmwareCommunication.
- No -inl.

**Used by:** Calibration, DiagnosticController; also aggregated in SlidescopeFirmwareDriverSet.

---

### 29. **SlidescopeFirmwareDriverSet** (`SlidescopeFirmwareDriverSet.h`)

**Role:** Holds shared_ptrs to all firmware-backed drivers (pick_and_place, slide_sensor_board, beep, door, bottom_light, top_light, rackboard, slidescope_firmware, gripper) so one place can inject them (e.g. CalibrationRepository, DI).

- Struct with one shared_ptr per driver type; no methods.
- No -inl or .cpp.

**Used by:** CalibrationRepository, DependencyInjection (singleton).

---

### 30. **RackBoardDriver** (`RackBoardDriver.h`, `RackBoardDriver-inl.h`, `RackBoardDriver.cpp`)

**Role:** Rack board operations via firmware: has_rack, has_field, get_rack_information, detect_slides_in_rack, move rack to loading/gripper/detection/overview stations.

- **RackBoardDriver.h** – Takes SlidescopeFirmwareCommunication in ctor; implements all AbstractRackBoardDriver methods; health_check.
- **RackBoardDriver-inl.h** – Inline: health_check calls access_check and returns true.
- **RackBoardDriver.cpp** – Forwards each method to SlidescopeFirmwareCommunication (command/response parsing).

**Used by:** RackBoard (domain), Calibration; DI in production when not MOCK_MODE.

---

### 31. **PickAndPlaceDriver** (`PickAndPlaceDriver.h`, `PickAndPlaceDriver.cpp`)

**Role:** Load/unload slide to/from overview and scanning stage via firmware; tracks SlidePositionState (NO_SLIDE_ON_STAGE, SLIDE_ON_OVERVIEW_STAGE, SLIDE_ON_SCANNING_STAGE).

- Implements AbstractPickAndPlaceDriver: load_on_scanning_stage, load_on_overview_stage, load_from_overview_to_scanning_stage, unload_to_rackfield, health_check using SlidescopeFirmwareCommunication.
- No -inl.

**Used by:** PickAndPlace (domain), Calibration.

---

### 32. **BeepDriver** (`BeepDriver.h`, `BeepDriver.cpp`)

**Role:** Beep (e.g. alert) via firmware.

- Implements AbstractBeepDriver: beep(access_token, mode), health_check; ctor takes SlidescopeFirmwareCommunication; init() in ctor.
- No -inl.

**Used by:** Calibration, Diagnostic.

---

### 33. **DoorDriver** (`DoorDriver.h`, `DoorDriver-inl.h`, `DoorDriver.cpp`)

**Role:** Door lock/unlock via firmware.

- **DoorDriver.h** – Implements AbstractDoorDriver: is_locked, lock, unlock, health_check; holds is_locked_; ctor takes SlidescopeFirmwareCommunication.
- **DoorDriver-inl.h** – Empty or trivial.
- **DoorDriver.cpp** – Forwards lock/unlock to firmware; updates is_locked_.

**Used by:** Calibration, Diagnostic.

---

### 34. **GripperDriver** (`GripperDriver.h`, `GripperDriver.cpp`)

**Role:** Gripper move (forward/backward, up/down) and hold/release via firmware.

- Implements AbstractGripperDriver; internal enums VerticalPosition, HorizontalPosition, ClampState; maps to firmware commands (char/position encoding).
- No -inl.

**Used by:** Calibration, PickAndPlace (domain).

---

### 35. **TopLightDriver** / **BottomLightDriver** (each `.h`, `.cpp`)

**Role:** Top/bottom light on/off via firmware.

- **TopLightDriver** – Ctor(SlidescopeFirmwareCommunication); is_on, turn_on, turn_off, health_check; init() in ctor.
- **BottomLightDriver** – Same pattern.
- No -inl.

**Used by:** Photographer, Calibration, Diagnostic.

---

### 36. **SlideSensorBoardDriver** (`SlideSensorBoardDriver.h`, `SlideSensorBoardDriver.cpp`)

**Role:** Slide sensor board move forward/backward via firmware.

- Implements AbstractSlideSensorBoardDriver: move_forward, move_backward, health_check; ctor takes SlidescopeFirmwareCommunication.
- No -inl.

**Used by:** Calibration, Diagnostic.

---

## Mock drivers (`MockDrivers/`)

**Role:** Implement the same abstract driver interfaces but without real hardware: no serial/camera/UDP, return fixed or empty results for tests and MOCK_MODE.

- **MockRackBoardDriver** (.h, -inl.h, .cpp) – has_rack/has_field return false or test data; get_rack_information/detect_slides_in_rack return empty/fixed arrays; move_* return true; health_check returns true. -inl: health_check inline.
- **MockXMotorDriver, MockYMotorDriver, MockZMotorDriver** – Implement AbstractX/Y/ZMotorDriver; move_to/get_position return 0 or stored value; wait_for_move_to_finish, is_step_passed, is_move_finished, etc. no-op or true.
- **MockHighQualityCameraDriver, MockLowQualityCameraDriver** – Implement camera interface; take_picture/get_picture return empty or test image; init/release no-op.
- **MockPickAndPlaceDriver, MockStageDriver** – Load/unload and stage operations no-op or return true.
- **MockBeepDriver, MockDoorDriver, MockGripperDriver, MockTopLightDriver, MockBottomLightDriver, MockSlideSensorBoardDriver** – Beep, door, gripper, lights, slide sensor: methods no-op or return fixed state (e.g. door locked, light off).
- **MockSlidescopeFirmwareDriver** – get_status/get_info return fixed StateResult; check/initialize return true.

DependencyInjection (or build flags) switches between real and mock implementations per driver (e.g. RackBoardDriver vs MockRackBoardDriver, Zaber* vs Mock*MotorDriver).

---

## Summary

- **Abstract*Driver** – Define the interface per device type (motor, camera, light, beep, door, gripper, pick-and-place, rack board, firmware, slide sensor, stage, stream). All extend **AbstractDeviceDriver** (lockable, health_check). Many have **-inl.h** for Config getters and small inlines; some have **.cpp** only for Config ctor or non-inline helpers.
- **ZaberCommunication** – Shared serial/Zaber protocol for X/Y/Z motors (config, open/close, send/receive).
- **SlidescopeFirmwareCommunication** – Serial (or similar) protocol to device firmware (commands, response types, status/door/rack/slide detection).
- **Concrete drivers** – **Zaber*MotorDriver**, **HighQualityCameraDriver**, **LowQualityCameraDriver**, **StreamDriver**, **SlidescopeFirmwareDriver**, **RackBoardDriver**, **PickAndPlaceDriver**, **BeepDriver**, **DoorDriver**, **GripperDriver**, **TopLightDriver**, **BottomLightDriver**, **SlideSensorBoardDriver** talk to real hardware (Zaber, Pylon, UDP, firmware).
- **SlidescopeFirmwareDriverSet** – Aggregates all firmware-backed driver instances for injection.
- **MockDrivers/** – One mock per abstract driver for tests and MOCK_MODE; same interface, no hardware.