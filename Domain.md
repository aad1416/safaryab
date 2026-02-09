
Here’s what each unit in **Domain** does:

---

## 1. **Area** (`Area.h`, `Area-inl.h`, `Area.cpp`)

**Role:** Rectangular region on a slide (pixel or motor units) and its **rows**; also sample-area detection (ONNX + line detection).

- **Area.h** – Declares `Area` (x, y, width, height, `rows_`, id, slide_id), conversion to/from `cv::Rect`, `detect_areas(raw_image)`, row/archive/upload helpers (`add_row`, `find_row`, `get_ready_for_archive_row`, `has_uploadable_row`, etc.), and `Area::Detector` with `Config` (Canny/Hough/model params from YAML), `detect()`, `get_scan_area_manual`, `get_cropped_slide`, line extraction, NMS.
- **Area-inl.h** – Inline: constructors, assign, getters/setters, `is_empty`, `get_rows`, `init`, `set_rows`, `detect_areas` (calls Detector), and all `Area::Detector::Config` getters/initializers from YAML.
- **Area.cpp** – Static Detector state, `Config` ctor, `convert_rect_to_area` / `convert_area_to_rect`, row logic (`add_row`, `are_all_rows_scanned`, `find_row`, archive/upload row selection), and Detector implementation (ONNX inference, post-processing, NMS, line detection, manual area).

**Used by:** Slide (scan areas), Scanner, AreaRepository.

---

## 2. **Barcode** (`Barcode.h`, `Barcode-inl.h`, `Barcode.cpp`)

**Role:** Read and parse barcode (e.g. QR) from a slide image; bridge to barcode reader.

- **Barcode.h** – Declares `AbstractBarcodeReader` with `BarcodeInfo` (slide_id, raw_string, Position with 4 corners → `Area`), `BookZxingBarcodeReader`, `MockBarcodeReader`, and `Barcode` (raw_image, reader, `read()`, `try_parse_string_data_to_barcode_info`, getters, DB id).
- **Barcode-inl.h** – Inline: `set_id`, `get_id`, `set_data`, `get_data`, `init`, `get_position`, `get_slide_id`.
- **Barcode.cpp** – `BarcodeInfo::Position::get_area()` from corner coords; `BookZxingBarcodeReader::read()` using ZXing (QR); `MockBarcodeReader::read()`; `Barcode::read()` and string parsing.

**Used by:** Slide (fetch), Scanner (slide identity).

---

## 3. **Beep** (`Beep.h`, `Beep.cpp`)

**Role:** Domain beep mode and mapping to driver mode.

- **Beep.h** – Declares `Beep::Mode` (e.g. Alert) and `to_driver_mode(Beep::Mode)` → `AbstractBeepDriver::Mode`.
- **Beep.cpp** – Implements `to_driver_mode` (switch on Beep::Mode).

**Used by:** Calibration (beep), DiagnosticController.

---

## 4. **Calibration** (`Calibration.h`, `Calibration-inl.h`, `Calibration.cpp`)

**Role:** System calibration and low-level hardware control: motors, gripper, lights, door, firmware, pixel/step ratio.

- **Calibration.h** – Declares `Calibration` with `Config`, `ConfigDTO`, `MotorPositions`, `RackInformation`; `init(...)` with Stage, PickAndPlace, lights, firmware, etc.; `calibrate_low_quality_camera_pixel_length`, get/apply/save config; motor moves (home, stop, move x/y/z), gripper, beep, door, auto_focus, rack moves, firmware status; and helpers (`IsCalibrationSquareEdgeDetectedResponse`, `LowPictureCalibrationScales`).
- **Calibration-inl.h** – Inline: `init()` assigning all injected dependencies (config, stage, drivers, photographer, focus_handler, logger).
- **Calibration.cpp** – Implements calibration logic, edge detection, pixel-scale calculation, and all motor/gripper/rack/firmware calls via the injected drivers.

**Used by:** RackBoardController, DiagnosticController (via CalibrationRepository).

---

## 5. **Device** (`Device.h`, `Device-inl.h`, `Device.cpp`)

**Role:** Global device mode (idle vs scanning vs live).

- **Device.h** – Declares `Device` with `Mode` (IDLE, SCAN_IN_PROGRESS, LIVE_IN_PROGRESS), `get_id`/`set_id`, `get_mode`/`set_mode`.
- **Device-inl.h** – Inline: all getters/setters for id and mode.
- **Device.cpp** – Any non-inline logic (e.g. persistence-related).

**Used by:** ScannerController, LiveStreamController, Context (device state).

---

## 6. **Diagnostic** (`Diagnostic.h`, `Diagnostic-inl.h`, `Diagnostic.cpp`)

**Role:** Hardware and PC health checks (cameras, lights, motors, gripper, beep, door, disk, CPU, memory).

- **Diagnostic.h** – Declares `Diagnostic` with `DiagnoseResult` (bool per component), `Config` (expected CPU/disk/memory/axis lengths from YAML), ctor/init with Stage, Photographer, PickAndPlace, drivers, logger; `diagnose()` and per-component checks (`is_*_ok`, `has_enough_*`).
- **Diagnostic-inl.h** – Inline: `Diagnostic::Config` getters and initializers.
- **Diagnostic.cpp** – Implements `diagnose()` and each check (driver state, Windows APIs for CPU/memory/disk).

**Used by:** DiagnosticController.

---

## 7. **FocusHandler** (`FocusHandler.h`, `FocusHandler-inl.h`, `FocusHandler.cpp`)

**Role:** Auto-focus at current (x,y): take images at multiple z, score them, find best z.

- **FocusHandler.h** – Declares `FocusHandler` with `Config`, `Frame` (z, score); `init` with Stage, Photographer, FocusScoreCalculator, VideoStreamer; `auto_focus(custom_arguments, initial_point)`; and internal types (`FocusData`, `Direction`) and methods (estimate_focus, step size, thresholds).
- **FocusHandler-inl.h** – Inline: typically config getters and small helpers.
- **FocusHandler.cpp** – Implements focus search (multiple initial points, decreasing step, brute refinement), score calculation via FocusScoreCalculator, and Stage/Photographer interaction.

**Used by:** Calibration, Scanner, LiveModeManager.

---

## 8. **FocusScoreCalculator** (`FocusScoreCalculator.h`, `FocusScoreCalculator-inl.h`, `FocusScoreCalculator.cpp`)

**Role:** Compute a single focus score from a raw image (sharpness measure).

- **FocusScoreCalculator.h** – Declares `FocusScoreCalculator` with `Method` enum (VOLLATH_F5, GAUSSIAN_DERIVATIVE, TENENGRAD, BRENNER, etc.), `calculate_score(raw_image)`, `set_score_calculation_algorithm`.
- **FocusScoreCalculator-inl.h** – Inline: `set_id`, `get_id`, `set_score_calculation_algorithm`, dummy getter/setter.
- **FocusScoreCalculator.cpp** – Implements each algorithm (OpenCV-based; e.g. Vollath F5, Tenengrad, Brenner) and `calculate_score` dispatch.

**Used by:** FocusHandler.

---

## 9. **LiveModeManager** (`LiveModeManager.h`, `LiveModeManager-inl.h`, `LiveModeManager.cpp`)

**Role:** Live view: move stage (up/down/left/right/zoom), auto_focus, velocities, stream HSL; holds current LiveRequest.

- **LiveModeManager.h** – Declares `LiveModeManager` with `init` (Stage, Photographer, Config, FocusHandler); `auto_focus`, `go_up`/`go_down`/`go_left`/`go_right`, `stop_x`/`stop_y`/`stop_z`, `zoom_in`/`zoom_out`; `get_position`, `set_*_velocity`, `set_live_stream_feed_hue_saturation_luminance_value`; `accept_request(LiveRequest)`.
- **LiveModeManager-inl.h** – Inline: usually trivial getters or forwarding.
- **LiveModeManager.cpp** – Implements moves and velocity/HSL calls via Stage/Photographer/StreamDriver.

**Used by:** LiveStreamController.

---

## 10. **LiveRequest** (`LiveRequest.h`, `LiveRequest-inl.h`, `LiveRequest.cpp`)

**Role:** One “live view” session: which RackField/slide, accept/end, and state (loading slide, capturing, etc.).

- **LiveRequest.h** – Declares `LiveRequest` with optional RackField, `init` (Config, logger, Photographer, Device, Stage); `is_acceptable`, `accept`, `end`; getters for slide data, compressed image, device, rackfield; `set_is_critical_process_in_progress`.
- **LiveRequest-inl.h** – Inline: id/rackfield/velocity getters-setters and DB-related accessors.
- **LiveRequest.cpp** – Implements accept (load slide to stage, capture), end (unload), and helpers (move_to_slide_middle_point, fetch_slide, save_current_configs).

**Used by:** LiveModeManager, LiveStreamController.

---

## 11. **Photographer** (`Photographer.h`, `Photographer-inl.h`, `Photographer.cpp`)

**Role:** Use high/low quality cameras and lights to capture images (raw/compressed, preview, gray/color).

- **Photographer.h** – Declares `Photographer` with init (camera configs, drivers, lights, logger); `init_camera`, `prepare_for_low_quality_capture`, `prepare_for_high_quality_capture`, `prepare_for_gray_imaging`, `prepare_for_color_imaging`; `take_compressed_picture`, `take_raw_picture`, `take_rgb_raw_picture`, `get_slide_preview`; HSL for high-quality camera; camera state getters.
- **Photographer-inl.h** – Inline: simple getters or state flags.
- **Photographer.cpp** – Implements prepare/capture by driving AbstractHighQualityCameraDriver, AbstractLowQualityCameraDriver, and light drivers.

**Used by:** Scanner, FocusHandler, Calibration, Diagnostic, LiveRequest, VideoStreamer.

---

## 12. **PickAndPlace** (`PickAndPlace.h`, `PickAndPlace-inl.h`, `PickAndPlace.cpp`)

**Role:** Load/unload slides between RackField and stage (overview and scanning).

- **PickAndPlace.h** – Declares `PickAndPlace` with init (AbstractPickAndPlaceDriver, Stage, logger); `load_on_scanning_stage`, `load_on_overview_stage`, `load_from_overview_to_scanning_stage`, `unload_to_rackfield`; `check_health_status`.
- **PickAndPlace-inl.h** – Inline: id/get_id, idle_state getter/setter.
- **PickAndPlace.cpp** – Implements load/unload sequences and prepare/check logic via driver and Stage.

**Used by:** Calibration, RackField, Scanner (slide handling).

---

## 13. **Plane** (`Plane.h`, `Plane-inl.h`, `Plane.cpp`)

**Role:** Focal plane model z = f(x,y) (slope/bias or point set) for focus height at (x,y).

- **Plane.h** – Declares `Plane` with `Config`, `Point`, `Mode`; constructors from (x_slope, y_slope, bias) or Config/Stage/Photographer/FocusHandler; `get_z_at`, estimation strategies (NEAREST_POINT, SINGLE_PLANE, etc.), auto-detection strategies (SAMPLE_POINTS_AND_SPIRAL, GRID, etc.); id getter.
- **Plane-inl.h** – Inline: slope/bias/id getters and Config initializers.
- **Plane.cpp** – Implements plane fitting, point sampling, and z-at-(x,y) calculation.

**Used by:** Slide (focus plane), Scanner.

---

## 14. **Rack** (`Rack.h`, `Rack-inl.h`, `Rack.cpp`)

**Role:** One physical rack: index on RackBoard and list of RackFields.

- **Rack.h** – Declares `Rack` with index, max_fields, `get_field_indexes`, `get_id`, `init(PickAndPlace)`.
- **Rack-inl.h** – Inline: id/index getters-setters.
- **Rack.cpp** – Builds/returns field list; init stores PickAndPlace for later load/unload.

**Used by:** RackBoard, RackField.

---

## 15. **RackBoard** (`RackBoard.h`, `RackBoard-inl.h`, `RackBoard.cpp`)

**Role:** Top-level rack holder: talks to hardware (AbstractRackBoardDriver) and exposes list of Racks.

- **RackBoard.h** – Declares `RackBoard` with `get_racks()`, `init(AbstractRackBoardDriver)`.
- **RackBoard-inl.h** – Inline: `set_id`, `get_id`, `init`.
- **RackBoard.cpp** – Implements `get_racks()` via driver (sensor state, rack positions).

**Used by:** RackBoardController, Calibration.

---

## 16. **RackField** (`RackField.h`, `RackField-inl.h`, `RackField.cpp`)

**Role:** One slot in a Rack: may hold a Slide; load to overview/scanning stage and unload.

- **RackField.h** – Declares `RackField` with rack_index, field_index, optional Slide; `get_slide`, `set_slide`, `load_to_scanning_stage`, `load_to_overview_stage`, `move_from_overview_to_scanning_stage`, `unload_from_stage`; `init(PickAndPlace)`.
- **RackField-inl.h** – Inline: constructors, `get_slide`, `set_slide`, id/rack_index/field_index/slide_id getters-setters.
- **RackField.cpp** – Implements load/unload by delegating to PickAndPlace and Stage.

**Used by:** ScanRequest, LiveRequest, Rack, Calibration.

---

## 17. **Row** (`Row.h`, `Row-inl.h`, `Row.cpp`)

**Role:** One row inside an Area: layer/row index, state (initiated → scan → archive → upload), archive and upload to backend.

- **Row.h** – Declares `Row` with State enum (INITIATED, SCAN_STARTED, … UPLOAD_COMPLETED); ctor from Config, ScannerServiceConsumer, area_id, layer, row; `archive(slide_id)`, `upload(slide_id, token)`; state/layer/row getters and `change_state`.
- **Row-inl.h** – Inline: id, area_id, layer, row, state getters-setters.
- **Row.cpp** – Implements archive (package images) and upload (call ScannerServiceConsumer); state transitions.

**Used by:** Area, Scanner (per-row scan and upload).

---

## 18. **SampleDetector** (`SampleDetector.h`, `SampleDetector-inl.h`, `SampleDetector.cpp`)

**Role:** From a slide thumbnail (+ optional barcode area), compute sample points (e.g. for focus or tile centers).

- **SampleDetector.h** – Declares static `calculate_sample_points(raw_image, barcode_area, visualize)` returning `vector<StagePoint>`; internal contour/preprocess/result types and helpers (preprocess, detect_contours, filter, convert to points, quantile/outlier).
- **SampleDetector-inl.h** – Inline: Config getters/initializers if any.
- **SampleDetector.cpp** – Implements preprocessing, contour detection, filtering by size/circularity/outliers, conversion to StagePoints.

**Used by:** Plane (sample points for focus plane), scanning pipeline.

---

## 19. **Scanner** (`Scanner.h`, `Scanner-inl.h`, `Scanner.cpp`)

**Role:** Orchestrate scanning of one ScanRequest: prepare, scan rows (move, focus, capture, queue archive/upload), stop.

- **Scanner.h** – Declares `Scanner` with init (Stage, Photographer, Config, FocusHandler, Plane config, ScannerServiceConsumer, logger); `process(scan_request, prepare_only, do_archive_and_upload)`, `stop()`; `set_requesting_user`, `set_report_progress`; internal prepare/scan and `ArchiveAndUploadDTO`.
- **Scanner-inl.h** – Inline: flag getters/setters and small helpers.
- **Scanner.cpp** – Implements process (state machine: slide fetch, area detection, focus plane, per-row scan with Stage/Photographer/FocusHandler/Plane, schedule Row archive/upload via TaskScheduler and ScannerServiceConsumer).

**Used by:** ScannerController.

---

## 20. **ScanRequest** (`ScanRequest.h`, `ScanRequest-inl.h`, `ScanRequest.cpp`)

**Role:** One user scan job: RackField, mode (FOCUSED/LAYERED), area detection mode (AUTO/MANUAL), state machine (STARTED → SLIDE_CREATED → AREA_DETECTED → … → COMPLETED / failure states).

- **ScanRequest.h** – Declares `ScanRequest` with Mode, AreaDetectionMode, State enum; ctor from RackField; sync with server, prepare, start_scan, stop, get state, get scan area info; id/rackfield getters.
- **ScanRequest-inl.h** – Inline: state/id/rackfield getters-setters and DB-related accessors.
- **ScanRequest.cpp** – Implements state transitions, server sync (ScannerServiceConsumer), and delegation to Scanner.

**Used by:** ScannerController, Scanner.

---

## 21. **Slide** (`Slide.h`, `Slide-inl.h`, `Slide.cpp`)

**Role:** One physical slide: barcode, image, areas, focus plane, surrounding area, sync state with backend.

- **Slide.h** – Declares `Slide` with State enum; `fetch(image)` (barcode + detect), `detect_areas`, `get_focus_plane`/`set_focus_plane`, `get_surrounding_area`, `find_surrounding_area`; image/preview path, barcode string; `get_server_state(token)`; init with CoreServiceConsumer.
- **Slide-inl.h** – Inline: getters/setters for image, areas, barcode, focus_plane, id.
- **Slide.cpp** – Implements fetch (Barcode + Area::detect_areas), detect_areas, server state via CoreServiceConsumer.

**Used by:** RackField, ScanRequest, LiveRequest.

---

## 22. **Stage** (`Stage.h`, `Stage-inl.h`, `Stage.cpp`)

**Role:** XY and Z stage: move in steps or pixels, velocity/acceleration/limits, hardware trigger for Z, current position.

- **Stage.h** – Declares `Stage` with init_motors (X/Y/Z driver configs); move_x_to, move_x_to_pixel, move_x_to_min/max; move_y_to, move_y_to_pixel, move_y_to_min/max; move_z_to, move_z_jog_to, move_z_to_min/max; enable/disable_z_hardware_trigger_mode; stop_x/y/z; get position/velocity; set_z_velocity/acceleration/min/max limit; rack_field_id; pixel/step conversion (Config).
- **Stage-inl.h** – Inline: accessors and small wrappers.
- **Stage.cpp** – Implements all moves and queries via AbstractXMotorDriver, AbstractYMotorDriver, AbstractZMotorDriver (Zaber or mock).

**Used by:** Scanner, FocusHandler, Calibration, Diagnostic, LiveModeManager, PickAndPlace, Plane.

---

## 23. **User** (`User.h`, `User-inl.h`, `User.cpp`)

**Role:** Logged-in user: credentials, tokens (local/global), role, membership; login/logout and role selection via backend.

- **User.h** – Declares `User` with Role and LoginState enums; constructors; `validate`, `login_to_service`, `get_roles`, `login_to_organization(role_id)`, `logout`; `get_role`, `get_local_token`, `get_global_token`; optional last_validation_date and UserServiceConsumer.
- **User-inl.h** – Inline: token/role/date getters-setters.
- **User.cpp** – Implements login/validate/get_roles/login_to_organization/logout via UserServiceConsumer (HTTP), token and role handling.

**Used by:** Context (current_user), UserManagerController, BasicRouter (accessors).

---

## 24. **VideoStreamer** (`VideoStreamer.h`, `VideoStreamer-inl.h`, `VideoStreamer.cpp`)

**Role:** Loop that grabs frames from Photographer and pushes them to AbstractStreamDriver (live preview).

- **VideoStreamer.h** – Declares `VideoStreamer` as callable (`operator()()`); `start`, `stop`, `pause`, `unpause`; init(Photographer, AbstractStreamDriver, logger).
- **VideoStreamer-inl.h** – Inline: id getter/setter, is_streaming.
- **VideoStreamer.cpp** – Implements run loop: take frame from Photographer, send via StreamDriver, FPS throttling.

**Used by:** LiveStreamController, FocusHandler (optional).

---

**Summary:** Domain contains the core business types and behavior for the slidescope: **Device** (mode), **User** (auth/roles), **RackBoard / Rack / RackField / Slide** (inventory and slide handling), **ScanRequest / Scanner / Area / Row** (scan workflow and upload), **Plane / FocusHandler / FocusScoreCalculator** (focus), **Photographer / Stage / PickAndPlace** (hardware abstraction), **Calibration** (calibration and low-level control), **Diagnostic** (health), **LiveRequest / LiveModeManager / VideoStreamer** (live view), **Barcode / SampleDetector / Beep** (support). The `-inl.h` files hold inline getters/setters and small helpers; `.cpp` files hold non-inline logic and driver/API calls.