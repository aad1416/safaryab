
Here’s what each **Service/Controllers** unit (only the controller files in that folder) does:

---

## Service/Controllers — unit files (directly in folder)

Only files under `Source/Core/Service/Controllers/` (not BindingModels/, Exceptions/, ViewModels/) are covered.

---

### **AbstractController**

- **AbstractController.h**  
  Declares the base controller used by all concrete controllers. Defines:
  - Constructor taking `AbstractDeviceRepository` and `AbstractLogger`.
  - `set_context` / `get_context` for request-scoped `Context`.
  - Helpers: `assert_access_token_validity(token)` (throws if token ≠ current user’s local token), `assert_device_mode_validity(valid_modes)` (throws if device mode not in set), and several overloads of `generate_response(action_name, successful, message [, result] [, error])` that build an `ActionResponse`.
  - Members: `context_`, `logger_`, `device_repository_`.
  - RTTR enabled for reflection. Includes `AbstractController-inl.h`.

- **AbstractController-inl.h**  
  Inline implementations: `set_context` / `get_context`; `assert_device_mode_validity` (checks device from repo); `assert_access_token_validity` (throws `InvalidLocalTokenException` when token mismatch); all `generate_response` overloads (build `ActionResponse` with action_name, successful, message, result, error).

- **AbstractController.cpp**  
  None. Logic is in the header and -inl.h.

---

### **DiagnosticController**

- **DiagnosticController.h**  
  Declares the **diagnostic/maintenance** controller: hardware checks, calibration, config, axes, gripper, lights, door, firmware, rack/slide moves. Constructor takes Config, CalibrationRepository, FocusHandlerRepository, PhotographerRepository, DeviceRepository, DiagnosticRepository, RackFieldRepository, StageRepository, Logger. Static `create(DependencyInjector)`. Many action methods (e.g. `get_status`, `get_info`, `is_*_ok`, `calibrate`, `get_config`/`reset_config`/`apply_config`/`save_config`, gripper/axis/light/door/firmware/rack/slide actions). Each action has a matching `get_accessors_<action>()` returning the allowed roles. Includes `DiagnosticController-inl.h`.

- **DiagnosticController-inl.h**  
  Inline implementations of all `get_accessors_*`: they return one of the static lists `CALIBRATE_ACCESS_LIST`, `GET_STATUS_ACCESS_LIST`, or `GET_INFO_ACCESS_LIST` (e.g. status checks → GET_STATUS, calibration/config/motion → CALIBRATE).

- **DiagnosticController.cpp**  
  Constructor and `create`. Each action: `assert_access_token_validity`, then delegates to domain (Diagnostic, Calibration, etc.) and wraps result in `generate_response`. Defines static access lists (all roles for diagnostic). RTTR registration for `DiagnosticController`: constructor(s), all action methods, and all `get_accessors_*` so BasicRouter can discover and call them.

---

### **LiveStreamController**

- **LiveStreamController.h**  
  Declares the **live preview/stream** controller: start/end live, snapshot, focus, stage movement (go_up/down/left/right, stop_x/y/z), zoom in/out, get position, set X/Y/Z velocity, set stream HSL. Constructor takes Logger, RackFieldRepository, PhotographerRepository, VideoStreamerRepository, LiveModeManagerRepository, LiveRequestRepository, DeviceRepository. Static `create(DependencyInjector)`. Each action has `get_accessors_*`. Includes `LiveStreamController-inl.h`.

- **LiveStreamController-inl.h**  
  Inline implementations of all `get_accessors_*`, returning the appropriate static list (PREPARE_LOW_QUALITY, START, END, GET_LIVE_PICTURE, AUTO_FOCUS, MOVEMENT, ZOOM_IN/OUT, GET_POSITION, STOP_Z, SET_VELOCITY, etc.).

- **LiveStreamController.cpp**  
  Constructor and `create`. **request**: token check, get LiveRequest, accept with RackField, start VideoStreamer thread, return slide info/image. **end**: device must be LIVE_IN_PROGRESS, stop VideoStreamer thread, end LiveRequest. **get_live_picture**: Photographer capture, return picture result. **auto_focus**, **go_up/down/left/right**, **stop_x/y/z**, **zoom_in/out**: use LiveModeManager with LiveRequest; all require LIVE_IN_PROGRESS. **get_position**: LiveModeManager pixel position. **set_x/y/z_velocity**, **set_live_stream_feed_hue_saturation_luminance_value**: delegate to LiveModeManager. Static role lists and RTTR registration for all actions and accessors.

---

### **RackBoardController**

- **RackBoardController.h**  
  Declares the **rack board** controller: single action `get_rackfields(BaseBindingModel)`. Constructor takes Logger and AbstractRackBoardRepository (device_repository is passed as `nullptr` to base). Static `create(DependencyInjector)` and `get_accessors_get_rackfields()`. Includes `RackBoardController-inl.h`.

- **RackBoardController-inl.h**  
  Inline implementation of `get_accessors_get_rackfields()` returning `GET_RACKFIELDS_ACCESS_LIST`.

- **RackBoardController.cpp**  
  `create`. **get_rackfields**: token check, get RackBoard from repo, collect field indexes from all racks into `GetRackFieldsActionResult`, return success/failure response. Defines `GET_RACKFIELDS_ACCESS_LIST` and RTTR registration.

---

### **ScannerController**

- **ScannerController.h**  
  Declares the **slide scanning** controller: `start_scan`, `prepare_scan`, `stop_scan`, `add_scan_request`, `remove_scan_request`, `get_scan_state`, `get_scan_info`, `set_scan_area`. Constructor takes ScannerRepository, ScanRequestRepository, RackFieldRepository, RowRepository, DeviceRepository, Config, Logger. Private helpers: `fetch_scanner`, `scan`, `stop_all_scan_requests`, `get_scan_request_state`, `get_scan_request_info`, `is_device_mode_idle`, `check_and_add_scan_request_id_to_processed_set`. Static `is_scan_stopped_` and per-action access lists. Includes `ScannerController-inl.h`.

- **ScannerController-inl.h**  
  Inline implementations of all `get_accessors_*` (start_scan, prepare_scan, stop_scan, add/remove_scan_request, get_scan_state, get_scan_info, set_scan_area), each returning the corresponding static access list.

- **ScannerController.cpp**  
  Constructor and `create`. **add_scan_request**: token and device mode (IDLE/SCAN_IN_PROGRESS), create ScanRequests from binding model, add to repo, return scan IDs. **remove_scan_request**: remove by IDs (skip if state ≥ FOCUS_PLANE_DETECTING). **prepare_scan**: run scanner’s preparation for each “next scan preparation” request. **set_scan_area**: set areas on ScanRequest when state is AREA_DETECTED. **start_scan**: bind TaskScheduler, loop over scan requests, set device SCAN_IN_PROGRESS, call `scan()` (Scanner::process), respect `is_scan_stopped_` and stop all on stop. **stop_scan**: set `is_scan_stopped_`, wait, reset scanner. **get_scan_state**: for given scan IDs return state + row states. **get_scan_info**: slide areas, barcode, preview image for one scan ID. Defines all static access lists and RTTR registration.

---

### **UserManagerController**

- **UserManagerController.h**  
  Declares the **auth/session** controller: `login`, `logout`, `get_user_roles`, `set_role`, `lock`, `unlock`, `get_user_status`. Constructor takes Logger, UserRepository, DeviceRepository. Static `create(DependencyInjector)` and `get_accessors_*` for each action. Includes `UserManagerController-inl.h`.

- **UserManagerController-inl.h**  
  Inline implementations of all `get_accessors_*`, each returning the corresponding static list (LOGIN, LOGOUT, GET_USER_ROLES, SET_ROLE, LOCK, UNLOCK, GET_CURRENT_STATUS).

- **UserManagerController.cpp**  
  Constructor and `create`. **login**: reject if LOCKED or already logged in; get user by username/password, `login_to_service()`, validate (online), store in context, return local token. **logout**: reject if LOCKED; token check; device must be IDLE; user logout then clear context. **get_user_roles**: token check; currently returns a fixed “ADMIN” membership (TODO: real backend). **set_role**: token check; `login_to_organization(role_id)`, update user, return token. **lock**: token check; set context to LOCKED. **unlock**: password check; set LOGGED_IN and last access time. **get_user_status**: token check; return login state. Defines all static access lists (LOGIN empty; others list roles). RTTR registration for `AbstractController` (set_context, get_context) and for `UserManagerController` (all actions and accessors).

---

Documentation for **all subfolders** under `Service/Controllers`: BindingModels, Exceptions, and ViewModels.

---

# Service/Controllers — All subfolders

## 1. BindingModels/

Input DTOs for controller actions: inherit `AbstractJsonSerializable`, have `token_` (or extend `BaseBindingModel`), and implement `json_serialize` / `json_deserialize`. RTTR registration is in the `.cpp` files. **No `*-inl.h`** in this folder.

| Unit | .h | .cpp | Purpose |
|------|----|------|--------|
| **BaseBindingModel** | ✓ | ✓ | Base for all binding models: `token_`; JSON serialize/deserialize Token. |
| **LoginBindingModel** | ✓ | ✓ | Login input: `username_`, `password_`. |
| **UnlockBindingModel** | ✓ | ✓ | Unlock input: `password_`. |
| **SetRoleBindingModel** | ✓ | ✓ | Set-role input: extends BaseBindingModel; `role_id_`. |
| **MoveBindingModel** | ✓ | ✓ | Manual axis move: `position_`, `is_relative_`. |
| **PickAndPlaceBindingModel** | ✓ | ✓ | Pick/place location: `rack_id_`, `field_id_`. |
| **RackBindingModel** | ✓ | ✓ | Single rack: `rack_index_`. |
| **RackMoveBindingModel** | ✓ | ✓ | Rack move: `rack_index_`, `direction_`. |
| **GetRackFieldsBindingModel** | ✓ | ✓ | Get rack fields: `rack_id_`. |
| **ScanRequestBindingModel** | ✓ | ✓ | Add scan requests: `requests_` (vector of `ScanRequestObject`: rack_id, field_id, mode, area_detection_mode). |
| **ScanIdBindingModel** | ✓ | ✓ | Single scan: `scan_id_`. |
| **ScanIdsBindingModel** | ✓ | ✓ | Multiple scans: `scan_ids_` (vector). |
| **ScanAreaBindingModel** | ✓ | ✓ | Set scan area: extends ScanIdBindingModel; `areas_` (vector of `domain::Area`). |
| **SetConfigBindingModel** | ✓ | ✓ | Calibration/config: many fields (x/y/z speeds, limits, pick/place positions, etc.). |
| **SetMotorVelocityBindingModel** | ✓ | ✓ | Motor velocity: `velocity_`. |
| **SetStreamFeedHueSaturationLuminanceBindingModel** | ✓ | ✓ | Stream image: `hue_value_`, `saturation_value_`, `luminance_value_`. |

**Per-file role (same pattern for all BindingModels):**

- **`.h`** — Declares the struct (extends `BaseBindingModel` or `AbstractJsonSerializable`), members, and `json_serialize` / `json_deserialize`; `RTTR_ENABLE(...)`.
- **`.cpp`** — Implements `json_serialize` / `json_deserialize` (map members to/from JSON keys) and `RTTR_REGISTRATION` so BasicRouter can construct and deserialize the type from JSON.

---

## 2. Exceptions/

Controller-specific exceptions; all inherit `Commons/Exceptions/AbstractException`. **Header-only**, no `.cpp` or `-inl.h`.

| Unit | .h | Purpose |
|------|----|--------|
| **InvalidLocalTokenException** | ✓ | Thrown when the request token does not match the current user’s local token (e.g. in `assert_access_token_validity`). |
| **LoginNotAllowedException** | ✓ | Thrown when login is not allowed (e.g. someone already logged in). |
| **PasswordNotValidForUnlockException** | ✓ | Thrown when unlock password does not match current user. |
| **SystemLockedException** | ✓ | Thrown when the system is locked and the action (login, logout, etc.) is not allowed. |

Each **`.h`** declares a class with an `explicit X(const std::string& message)` constructor that forwards to `AbstractException(message)`.

---

## 3. ViewModels/

Output DTOs for controller actions: payload of `ActionResponse` (action_name, message, successful, result, error). Most types extend `AbstractActionResult` and implement `json_serialize` / `json_deserialize`. **No `*-inl.h`** in this folder.

### Base types

| Unit | .h | .cpp | Purpose |
|------|----|------|--------|
| **AbstractActionError** | ✓ | — | Base for error payloads in `ActionResponse`; extends `AbstractJsonSerializable`. |
| **AbstractActionResult** | ✓ | — | Base for result payloads; extends `AbstractJsonSerializable`. |
| **ActionResponse** | ✓ | ✓ | Full response: `action_name_`, `message_`, `successful_`, `result_` (AbstractActionResult), `error_` (AbstractActionError); `json_serialize` / `json_deserialize`; used by `AbstractController::generate_response` and returned as JSON by BasicRouter. |

### ActionResult types (all .h + .cpp unless noted)

| Unit | Purpose |
|------|--------|
| **LoginActionResult** | Login response: `local_token_`. |
| **SetRoleActionResult** | Set-role response: `local_token_`. |
| **GetUserRolesActionResult** | User roles: `member_ships_` (e.g. UserMemberShip list). |
| **GetUserStatusActionResult** | User status: `login_state_` (User::LoginState). |
| **DiagnosticActionResult** | Diagnostic status: many booleans (is_low_quality_camera_ok_, is_high_quality_camera_ok_, is_top_light_ok_, …, has_enough_available_cpu_usage_, etc.). |
| **GetInfoActionResult** | Device info: `racks_occupied_`, `is_top_light_on_`, `is_bottom_light_on_`, `is_door_open_`. |
| **GetConfigActionResult** | Calibration config: x/y/z speeds, limits, pick/place positions (with bounds). |
| **GetMotorPositionsActionResult** | Motor positions: `x_axis_`, `y_axis_`, `z_axis_`. |
| **GetFirmwareStatusActionResult** | Firmware status string: `firmware_status_`. |
| **GetRackInfoActionResult** | Rack info: `slides_occupied_`, `is_rack_available_`. |
| **GetRackFieldsActionResult** | Rack layout: `rackfield_ids_` (vector of field index vectors). |
| **GetRacksActionResult** | Racks list (if used). |
| **GetFieldsActionResult** | Fields list (if used). |
| **PictureActionResult** | Single image: `picture_` (vector of bytes). |
| **SlideInfoActionResult** | Slide info + image: `slide_info_`, `image_`. |
| **GetPositionActionResult** | Stage position: `x_`, `y_`. |
| **ScanAreaActionResult** | Scan areas + slide: `scan_areas_`, `slide_info_`, `warning_`, `slide_image_preview_`. |
| **ScanStateActionResult** | Scan state(s): `scan_state_details_` (id, ScanRequest::State, rows_state_). |
| **AddScanRequestActionResult** | Added scan requests: `scan_requests_` (id, rack_number, field_number per item). |
| **StageStateActionResult** | Stage state (if used). |

**Per-file role:**

- **`.h`** — Declares the struct (extends `AbstractActionResult` or `AbstractActionError`), data members, and `json_serialize` / `json_deserialize`.
- **`.cpp`** — Implements `json_serialize` / `json_deserialize` and, where present, RTTR registration (e.g. `ActionResponse`).

---

## Summary table

| Unit | .h | -inl.h | .cpp | Purpose |
|------|----|--------|------|--------|
| **AbstractController** | ✓ | ✓ | — | Base controller: context, token/device checks, response building. |
| **DiagnosticController** | ✓ | ✓ | ✓ | Hardware diagnostic, calibration, config, axes, gripper, lights, door, firmware, rack/slide. |
| **LiveStreamController** | ✓ | ✓ | ✓ | Live preview: start/end, snapshot, focus, move, zoom, velocity, stream HSL. |
| **RackBoardController** | ✓ | ✓ | ✓ | Expose rack board field layout (get_rackfields). |
| **ScannerController** | ✓ | ✓ | ✓ | Scan workflow: add/remove requests, prepare, start/stop scan, state, info, set scan area. |
| **UserManagerController** | ✓ | ✓ | ✓ | Login, logout, roles, set role, lock, unlock, user status. |

All concrete controllers inherit `AbstractController`, use BindingModels for input and ViewModels (ActionResult types) for output, and register with RTTR so `BasicRouter` can invoke them by Thrift controller type and action name and enforce role via `get_accessors_<action>`.


| Subfolder | Contents | -inl.h |
|-----------|----------|--------|
| **BindingModels/** | 16 input DTOs for controller actions (token, login, move, scan, config, etc.); .h + .cpp, RTTR in .cpp | None |
| **Exceptions/** | 4 controller exceptions (invalid token, login not allowed, bad unlock password, system locked); header-only | None |
| **ViewModels/** | 1 response wrapper (ActionResponse) + 2 abstract bases + many ActionResult/error types for controller outputs; .h + .cpp where needed | None |

So **for all subfolders** under Service/Controllers: BindingModels and ViewModels follow the same “.h declares, .cpp implements JSON + RTTR” pattern; Exceptions are header-only; none of these subfolders use `*_inl.h` or `*-inl.h`.