
Here’s the **unit-file documentation for the root Core** (files directly under `Source/Core`, not in Commons/Domain/Infrastructure/Service), in the same style as the rest of the project.

---

## Root Core units (directly under `Source/Core`)

These are the only units whose files sit directly under `Source/Core` (no subfolder). There is no `Context.cpp`; Context is header-only with inline implementation.

---

### **BasicRouter**

- **BasicRouter.h**  
  Declares `BasicRouter` as the Thrift request router: implements `thrift::BasicRequestorIf`, holds static `Context`, `DependencyInjector`, `Config`, and logger. Declares `request(return_val, controller_type, action_name, data)` and `set_context` / `get_context`. Includes `BasicRouter-inl.h` for inline members.

- **BasicRouter-inl.h**  
  Inline definitions for `set_context(const Context&)` and `get_context() const`.

- **BasicRouter.cpp**  
  Defines static `BasicRouter::context_`. Constructor builds DI via `DependencyInjection::make()`, creates `Config` and logger from injector. `request()`: maps Thrift `controller_type` to RTTR type name (e.g. `XController`), creates controller with injector, parses JSON into action parameter, checks access via `get_accessors_<method>` and `Context::current_user_` role, sets/gets context on controller, invokes action, returns JSON from `ActionResponse::json_serialize()`. Also defines `check_method_access()` (role-based) and `check_lock()` (auto-lock after idle using `Config::get_auto_lock_after()`).

---

### **Config**

- **Config.h**  
  Declares `Config`: YAML-based system config. Typedefs `ConfigObject` (YAML::Node) and `ConstRefrenceConfigObject`. Static `CONFIG_FILE_PATH`. Many getters for server URI, API paths (login, roles, slide info, automation, scanning, upload), thread count, organization/local-login/auto-lock settings, action delimiter, firmware port, save path, z-step, layer count, calibration/crop and motor-origin settings; a few setters that also persist to YAML. Private `initialize(ConstRefrenceConfigObject)` and per-field `initialize_*` / `persist`. Includes `Config-inl.h`.

- **Config-inl.h**  
  Inline implementations: all getters, `initialize()` (calling all `initialize_*`), each `initialize_*` (reading from YAML keys), `persist()` (writing YAML to `CONFIG_FILE_PATH` or `"Config.yml"`), and the setters that reload file, update member, and call `persist()`.

- **Config.cpp**  
  Defines `Config::CONFIG_FILE_PATH` and `Config::Config()`: loads YAML from that path, then calls `initialize(config["SYSTEM"])`.

---

### **Context**

- **Context.h**  
  Declares `Context`: runtime state struct with default ctor, `boost::optional<time_t> last_system_access_time_`, `std::shared_ptr<domain::User> current_user_`, and `domain::User::LoginState login_state_`. Includes `Context-inl.h`.

- **Context-inl.h**  
  Inline definition of `Context::Context()` (initializes optional to none, user to nullptr, login state to NOT_LOGGED_IN).

- **Context.cpp**  
  Does not exist; Context is header-only.

---

### **DependencyInjection**

- **DependencyInjection.h**  
  Single file (no `-inl.h` or `.cpp`). Uses Boost.DI. Defines:
  - **InlineDependencyInjection::make()**  
    Builds the injector: repositories (Calibration, Area, Barcode, User, RackBoard, etc.), `Config`, domain/device configs, logger, web storage, `SlidescopeFirmwareCommunication`, driver configs, `SlidescopeFirmwareDriverSet`. Uses `AbstractDatabaseFactory` → `DatabaseFactory` (or `TestDatabaseFactory` when `TESTING`). Driver bindings depend on `MOCK_MODE` vs real (e.g. RackBoard, Stage, PickAndPlace, cameras, lights, motors, firmware, etc.).
  - **DependencyInjection**  
    Exposes `make()` and the injector type.
  - **DependencyInjector**  
    Type alias / wrapper over that injector type for move semantics.

---

### **FrontEndController**

- **FrontEndController.h**  
  Declares `FrontEndController`: holds worker count, init flag, Thrift `ThreadManager`, and `TThreadPoolServer`. Constructors (default and `explicit FrontEndController(size_t worker_count)`), `initialize()`, `start()`, `is_initialized()`. Also declares `BasicRequestorCloneFactory` implementing `BasicRequestorIfFactory` with `getHandler` / `releaseHandler`. Includes `FrontEndController-inl.h`.

- **FrontEndController-inl.h**  
  Inline definition of `is_initialized()`.

- **FrontEndController.cpp**  
  Default ctor delegates to `FrontEndController(2)`. `initialize()`: creates simple thread manager with `worker_count_`, `TThreadPoolServer` on port 9090 with `BasicRequestorProcessorFactory(BasicRequestorCloneFactory())`, buffered transport, binary protocol. `start()` serves and throws if not initialized. `BasicRequestorCloneFactory::getHandler()` returns a new `BasicRouter()`; `releaseHandler()` deletes it.

---

## Summary table

| Unit                 | .h | -inl.h | .cpp | Role |
|----------------------|----|--------|------|------|
| **BasicRouter**      | ✓  | ✓      | ✓    | Thrift request router; RTTR controller dispatch, access checks, JSON response. |
| **Config**           | ✓  | ✓      | ✓    | YAML system config (paths, hardware, auth, automation). |
| **Context**          | ✓  | ✓      | —    | Runtime state: last access time, current user, login state. |
| **DependencyInjection** | ✓ | —      | —    | Boost.DI bindings for repos, drivers, config, logger. |
| **FrontEndController**  | ✓ | ✓   | ✓    | Thrift server on 9090; thread pool; handler = BasicRouter. |

This is the full set of root Core units (not in any subfolder like Commons or Infrastructure), with the same “what each file does” level of detail as in the rest of the Slidescope-Core docs.