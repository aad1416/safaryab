
Here’s what each unit in **Commons** does:

---

## 1. **Accessor** (`Accessor.h`, `Accessor-inl.h`, `Accessor.cpp`)

**Role:** RAII “token” for exclusive access to a lockable resource.

- **Accessor.h** – Declares the class: constructor from `shared_ptr<AbstractLockableResource>`, `acquire`, `wait_for_acquire`, `release`. One accessor can hold one resource at a time.
- **Accessor-inl.h** – Inline impl: constructor calls `acquire` and throws `RunTimeException` on failure; destructor calls `release` (so releasing is automatic).
- **Accessor.cpp** – Non-inline impl: `acquire`/`wait_for_acquire` ask the resource to take this accessor; `release` asks the resource to release it and clears the stored pointer. Used with `AbstractLockableResource` (e.g. DB factory) so only the holder of the accessor can use the resource.

---

## 2. **AbstractLockableResource** (`AbstractLockableResource.h`, `AbstractLockableResource-inl.h`, `AbstractLockableResource.cpp`)

**Role:** Base for resources that can be locked by a single **Accessor** at a time (mutex + condition variable).

- **AbstractLockableResource.h** – Declares: `is_locked()`, protected `access_check(token)`, and (private) `acquire` / `wait_for_acquire` / `release` used by **Accessor**.
- **AbstractLockableResource-inl.h** – Inline: `is_locked()` returns whether `token_` is non-null.
- **AbstractLockableResource.cpp** – Locking logic: `acquire`/`release` via atomic compare-exchange; `wait_for_acquire` waits on a condition variable until the resource is free, then sets `token_`. `access_check` throws if the caller’s token is not the current holder. Used so code must hold an **Accessor** to use the resource (e.g. get DB from factory).

---

## 3. **AbstractJsonSerializable** (`AbstractJsonSerializable.h`, `AbstractJsonSerializable.cpp`)

**Role:** Common interface for types that serialize/deserialize to/from **nlohmann::json**, plus free functions and RTTR registration.

- **AbstractJsonSerializable.h** – Pure interface: `json_serialize()` and `json_deserialize(json)`. Declares `to_json`/`from_json` for the type and for `shared_ptr<AbstractJsonSerializable>`. RTTR_ENABLE for reflection.
- **AbstractJsonSerializable.cpp** – Constructor from json calls `from_json`. Implements `to_json`/`from_json` by calling the virtual methods (and handles null `shared_ptr`). Registers the class with RTTR so controllers/binding models can be deserialized by name.

---

## 4. **RawImage** (`RawImage.h`, `RawImage-inl.h`)

**Role:** Simple holder for raw pixel buffer and dimensions (no .cpp).

- **RawImage.h** – Declares: constructor from `vector<uint8_t>`, width, height, channels; getters for data, width, height, channels.
- **RawImage-inl.h** – All methods implemented inline: store/copy data and dimensions, return them. Used wherever raw image buffers are passed (e.g. into **ImageUtilities**).

---

## 5. **ThreadManager** (`ThreadManager.h` only)

**Role:** Static, thread-safe map from index → object + thread; start/stop/join threads by index.

- **ThreadManager.h** – Template `ThreadManager<T>`: static `add(index, shared_ptr<T>)`, `start(index)` (runs `*object` as `std::thread`), `remove(index)`, `get(index)`, `join(index)`, `detach(index)`. Uses a static mutex and two maps (object_list, thread_list). All in header (template + static members defined in same file). Used to manage long-lived worker objects and their threads by ID.

---

## 6. **Exceptions** (`Commons/Exceptions/`)

**Role:** Exception hierarchy and domain-specific exception types.

- **AbstractException.h** – Base: extends `std::exception`, holds a `std::string` message, `what()` returns it. All custom exceptions derive from this (or, in one case, `std::runtime_error`).
- **RunTimeException.h** – `RunTimeException` and `UnprivilegedAccessException` (both take a message string).
- **RunTimeException.cpp** – Only includes the header (ensures the TU is compiled; no extra logic).
- **InvalidControllerActionArguments.h** – Thrown when controller name, action name, or arguments are invalid (e.g. in **BasicRouter**).
- **JsonParsingException.h** – Thrown when JSON parsing fails.
- **ORMRelatedException.h** – Thrown for DB/ORM errors (e.g. sqlite_orm).
- **UserManagementExceptions.h** – Set of user/auth exceptions: `GetRolesFailureException` (extends `std::runtime_error`), `InvalidRoleIdException`, `LogOutNotAllowedException`, `OrganizationNotValidException`, `SetRoleFailureException`, `UserDataNotValidException` (all extend **AbstractException**).

---

## 7. **Utilities – Logger** (`AbstractLogger.h`, `Logger.h`, `Logger.cpp`)

**Role:** Pluggable logging API and Boost.Log-based implementation.

- **AbstractLogger.h** – Interface: `warning`, `trace`, `info`, `error`, `fatal`, `debug`, `exception`; each in two overloads (message only, or message + file/function/line). Macros: `LOG`, `LOGP`, `PURE_LOGP` for convenience.
- **Logger.h** – Declares **Logger** implementing **AbstractLogger**, backed by `boost::log::sources::logger_mt`.
- **Logger.cpp** – Sets up file logging (rotation, format), implements every method by forwarding to Boost.Log. Used everywhere for tracing, errors, and exceptions.

---

## 8. **Utilities – Base64** (`Base64.h`, `Base64.cpp`)

**Role:** Encode/decode strings to/from Base64 (URL-safe alphabet).

- **Base64.h** – Declares `base64_encode(in)` and `base64_decode(in)`.
- **Base64.cpp** – Implements encode/decode using a fixed alphabet; used for encoding binary or strings (e.g. for APIs or storage).

---

## 9. **Utilities – StringExtensions** (`StringExtensions.h`, `StringExtensions.cpp`)

**Role:** String helpers.

- **StringExtensions.h** – Declares `string_split(source, delimiter)` returning `vector<string>`.
- **StringExtensions.cpp** – Implements split with `std::regex` and `sregex_token_iterator`. Used e.g. in **BasicRouter** for action parameters when a delimiter is configured.

---

## 10. **Utilities – ImageUtilities** (`ImageUtilities.h`, `ImageUtilities-inl.h`, `ImageUtilities.cpp`)

**Role:** Image I/O, compression, conversion (OpenCV + GraphicsMagick), and geometry helpers.

- **ImageUtilities.h** – Declares static API: `compress`, `save` (several overloads), `decompress`, Bayer→RGB, `convert_raw_picture_to_mat`, line/angle/distance helpers, and nested types (Line, Config, enums like SaveMode, CompressMode, ImageProcessingTool).
- **ImageUtilities-inl.h** – Inline implementations for **ImageUtilities::Config**: getters and `initialize` from YAML (compression rate/mode/tool for low-quality save). Only included from **ImageUtilities.h**.
- **ImageUtilities.cpp** – Implements compress/save/decompress and conversions using OpenCV and Magick++; reads config from YAML. Used by scanning/photographer pipeline for saving and compressing slide images.

---

## 11. **Utilities – TaskScheduler** (`TaskScheduler.h`, `TaskScheduler-inl.h`, `TaskScheduler.cpp`)

**Role:** Single global **marl** scheduler for scheduling tasks (e.g. scan jobs).

- **TaskScheduler.h** – Declares: `bind(worker_thread_count)` (returns `marl::Scheduler*`), `add_task(Functor)`, `add_parallel_task(Functor)`. Macro `UNBIND_AT_THE_END_OF_THIS_THREAD`.
- **TaskScheduler-inl.h** – Template impl: `add_task` / `add_parallel_task` call `bind()` and `marl::schedule` (and `marl::blocking_call` for parallel); catch std::exception and print. Only included from **TaskScheduler.h**.
- **TaskScheduler.cpp** – Defines static mutex and scheduler; `bind()` creates the **marl** scheduler once and binds the current thread. Used in **main** and by controllers to run work on the marl thread pool.

---

## 12. **Utilities – TokenGenerator** (`TokenGenerator.h`, `TokenGenerator.cpp`)

**Role:** Generate random string “tokens” (e.g. for IDs or temp names).

- **TokenGenerator.h** – Declares static `generate_random_string(n)`.
- **TokenGenerator.cpp** – Fills a string with random chars from a fixed alphabet (letters, digits, symbols). Note: uses `srand(time(0))`, so not suitable for security-critical tokens.

---

## 13. **Utilities – AbstractWebStorageClient / AmazonWebStorageClient** (`AbstractWebStorageClient.h`, `.cpp`, `AmazonWebStorageClient.h`, `.cpp`)

**Role:** Abstract client for “upload file to cloud” and AWS S3 implementation.

- **AbstractWebStorageClient.h** – Interface: nested **Config** (loads from YAML, provides endpoint), `init()`, `put(upload_request_info_dump, file_path)`, `shutdown()`, `set_logger`, `set_config`.
- **AbstractWebStorageClient.cpp** – **Config** loads from `Config.yml` / **Config::CONFIG_FILE_PATH**; implements getters and `initialize` for endpoint.
- **AmazonWebStorageClient.h** – Declares **AmazonWebStorageClient** implementing the abstract interface, with AWS SDK options and logger.
- **AmazonWebStorageClient.cpp** – `init`/`shutdown` call AWS InitAPI/ShutdownAPI; `put` parses JSON upload request (bucket, key, credentials), creates S3 client, and uploads the file. Used from **main** and scan/upload flow to send files to S3-compatible storage.

---

## 14. **Utilities – OnnxModel** (`OnnxModel.h`, `OnnxModel.cpp`)

**Role:** Load and run ONNX models (e.g. for detection/classification on images).

- **OnnxModel.h** – Declares: `init(model_path, num_threads)` returning `Ort::Session`, `prepare_and_predict(session, images)`, `unload()`; inner **Input** struct; static env and session metadata.
- **OnnxModel.cpp** – Uses ONNX Runtime to create session, build input/output names and shapes, convert `Image` (vector of vector of float) to tensors, run inference, return outputs. Used by domain code that does ML inference (e.g. **SampleDetector**).

---

## 15. **Utilities – StagePoint** (`StagePoint.h` only)

**Role:** 2D integer point for stage/motor coordinates, with comparison and distance.

- **StagePoint.h** – Struct with `x_`, `y_`; default (-1,-1); `operator==`; static `compare(p1,p2)` (y then x) for ordering; static `distance(p1,p2)` (Euclidean). Used by stage/scan logic for positions and ordering.

---

**Summary:** Commons provides locking (Accessor + AbstractLockableResource), JSON serialization base (AbstractJsonSerializable), raw image type (RawImage), threading (ThreadManager, TaskScheduler), logging (AbstractLogger + Logger), string/base64 helpers, image utilities, web storage abstraction (with S3 implementation), ONNX inference, and a small stage-point type. Exceptions are centralized under **AbstractException** and domain-specific headers in **Commons/Exceptions**.