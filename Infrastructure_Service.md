
Here’s a concise description of each unit under **Infrastructure/Service** and what it does.

---

## 1. **AbstractSerialCommunication** (`AbstractSerialCommunication.h`)

**Role:** Abstract interface for serial I/O (open/close, send/receive, flow control).

- Declares enums: `FlowControl` (NONE, SOFTWARE, HARDWARE), `Parity` (NONE, ODD, EVEN), `StopBits` (ONE, ONE_POINT_FIVE, TWO).
- Pure virtuals: `is_open()`, `open(device_path, baud, flow_control, size, parity, stop_bits)`, `flush()`, `cancel()`, `close()`, `receive()` (returns `future<string>`), `transmit(data)` (returns `future<size_t>`), `transmit_receive(data)` (returns `future<pair<size_t,string>>`).
- No .cpp or -inl.

**Used by:** ScopedSerialCommunication; referenced by SlidescopeFirmwareCommunication (actual serial type may be abstract).

---

## 2. **ScopedSerialCommunication** (`ScopedSerialCommunication.h`, `ScopedSerialCommunication-pimpl.h`, `ScopedSerialCommunication.cpp`)

**Role:** Concrete serial implementation over Boost.Asio; RAII open/close.

- **ScopedSerialCommunication.h** – Class implementing AbstractSerialCommunication. Ctor takes `serial_port_name` and opens. Methods: `is_open`, `open`, `flush`, `cancel`, `close`, `receive`, `transmit`, `transmit_receive` (each returns a `future` that runs the real I/O asynchronously). Pimpl: `std::unique_ptr<BoostAsio> io_`.
- **ScopedSerialCommunication-pimpl.h** – Defines `ScopedSerialCommunication::BoostAsio`: `boost::asio::io_context`, `boost::asio::serial_port`, open/close/flush/cancel, `read()`, `write(data)`, `write_read(data)`; maps FlowControl/Parity/StopBits to Boost types. Include guard restricts inclusion to ScopedSerialCommunication.cpp.
- **ScopedSerialCommunication.cpp** – Ctor creates BoostAsio and calls `open(serial_port_name)`. Destructor calls `close()`. Public methods forward to `io_`. `receive`/`transmit`/`transmit_receive` wrap BoostAsio read/write/write_read in `std::async`. BoostAsio ctors/dtors and open/read/write implementation (serial_port_.open, async_read, etc.) live here.

**Used by:** SlidescopeFirmwareCommunication (or similar) for serial to device firmware; not used by Zaber (Zaber uses its own SDK).

---

## 3. **AbstractHttpClient** (`AbstractHttpClient.h`, `AbstractHttpClient-inl.h`)

**Role:** Abstract HTTP client: host/path/body and generic request interface; extends lockable resource.

- **AbstractHttpClient.h** – Declares `StringPairVector` (vector of string pairs for headers). Pure virtuals: `get`, `put`, `del`, `post(body, headers)`, `patch(body, headers)`, `request(method, content_type, body, headers)`, `request_file_upload(file_path, headers)`. Protected: `host_`, `path_`, `body_`. Setters: `set_host`, `set_path`, `set_body`. Nested `HttpMethod` with enum (GET, PUT, POST, DELETE, PATCH), constructors/assignments from enum or string, `operator==`, `operator std::string()`.
- **AbstractHttpClient-inl.h** – Inline: HttpMethod ctor/assign/compare and string conversion; `set_host`/`set_path`/`set_body` (assign to host_/path_/body_). String→HttpMethod throws RunTimeException on unknown method name.

**Used by:** HttpClient (core implementation); service consumers use HttpClient.

---

## 4. **HttpClient** (`HttpClient.h`, `HttpClient-inl.h`, `HttpClient.cpp`)

**Role:** Concrete HTTP client: REST (cpprest) and file upload (curlpp).

- **HttpClient.h** – Implements AbstractHttpClient: `get`, `post`, `del`, `put`, `patch`, `request`, `request_file_upload`. `DEFAULT_CONTENT_TYPE = "application/json"`.
- **HttpClient-inl.h** – Inline: `get`/`post`/`patch` call `request` with the right HttpMethod; `del`/`put` return empty string (not implemented).
- **HttpClient.cpp** – `request`: build `web::http::client::http_client`, `http_request` (method, uri, body, content-type, headers), then `client.request(request).then(extract_utf8string).get()`. `request_file_upload`: curlpp Easy, URL = host+path, form with file part, custom headers, perform and return response stream as string.

**Used by:** CoreServiceConsumer (and thus UserServiceConsumer, ScannerServiceConsumer, SlideServiceConsumer) for all HTTP calls to the backend.

---

## 5. **ServiceRequest** (`ServiceRequest.h`, `ServiceRequest.cpp`)

**Role:** DTO for one HTTP request: host, path, method, body, content-type, headers.

- **ServiceRequest.h** – Fields: `method_`, `host_`, `path_`, `body_`, `content_type_`, `headers_`. Ctor(host, path, method). Getters/setters for all. `set_request_body` overloads: from string or from `AbstractBindingModel` (body = model.json_serialize().dump()). `get_request_headers` returns the vector of pairs; `set_request_headers(key, value)` appends one header.
- **ServiceRequest.cpp** – Ctor sets default content_type_ to "application/json". All getters/setters implemented; `set_request_body(AbstractBindingModel)` calls `body.json_serialize().dump()`.

**Used by:** CoreServiceConsumer, UserServiceConsumer, ScannerServiceConsumer, SlideServiceConsumer to build the request before calling HttpClient.

---

## 6. **ServiceResponse** (`ServiceResponse.h`, `ServiceResponse.cpp`)

**Role:** Wrapper around backend JSON response: parse once, then access Result/Infos/Warns/Errors/Fatals/Traces.

- **ServiceResponse.h** – Ctor takes `json_string`; `is_ok()` (Result non-null); `get_result()`, `get_infos()`, `get_warns()`, `get_errors()`, `get_fatals()`, `get_traces()` return `const nlohmann::json&`. Private: `nlohmann::json json_`.
- **ServiceResponse.cpp** – Ctor: `json_ = nlohmann::json::parse(json_string)`. `is_ok()`: true iff `json_["Result"]` exists and is not null. Getters use `json_.at("/Result"_json_pointer)` etc.; throw JsonParsingException if key missing.

**Used by:** All service consumers to interpret HTTP response body and get result/errors.

---

## 7. **CoreServiceConsumer** (`CoreServiceConsumer.h`, `CoreServiceConsumer.cpp`)

**Role:** Base for calling the Core backend over HTTP: build request, send via HttpClient, return ServiceResponse.

- **CoreServiceConsumer.h** – Ctor(system_config, logger). `service_consumer_request(ServiceRequest)` returns ServiceResponse (GET/POST/PATCH etc.). Overload `service_consumer_request(ServiceRequest, file_name)` for file upload. Protected: `system_config_`, `logger_`.
- **CoreServiceConsumer.cpp** – Both overloads: create `service::HttpClient`, set host/path from ServiceRequest; first overload calls `client.request(method, content_type, body, headers)` and logs response; second calls `client.request_file_upload(file_name, headers)`. Return `ServiceResponse(response_string)`.

**Used by:** UserServiceConsumer, ScannerServiceConsumer, SlideServiceConsumer as base; they add specific methods (login, get_roles, upload, get_slide_info, etc.).

---

## 8. **UserServiceConsumer** (`UserServiceConsumer.h`, `UserServiceConsumer.cpp`)

**Role:** User/auth API: login (user/pass), get roles, set role (login to organization).

- **UserServiceConsumer.h** – Extends CoreServiceConsumer. `request_login(username, password)` → token string. `request_get_roles(token)` → `vector<UserMemberShip>`. `request_set_role(token, role_id)` → new token string.
- **UserServiceConsumer.cpp** – `request_login`: CredentialBindingModel body, POST to get_login_userpass_path, parse TokenViewModel from result. `request_get_roles`: GET get_get_roles_path, Authorization header, parse RolesViewModel. `request_set_role`: RoleBindingModel body (organization_id, role_id), PATCH get_login_role_path, Authorization, parse TokenViewModel. On !is_ok() uses ErrorViewModel from get_errors().

**Used by:** Domain User (login_to_service, get_roles, login_to_organization).

---

## 9. **ScannerServiceConsumer** (`ScannerServiceConsumer.h`, `ScannerServiceConsumer.cpp`)

**Role:** Scan/upload API: request upload URL, upload file to S3, confirm upload.

- **ScannerServiceConsumer.h** – Extends CoreServiceConsumer. Ctor(system_config, logger, amazon_web_storage_client). `request_upload(token, archive_path, slide_id, layer, row, is_last_row)` → JSON string (upload request info) or "". `try_to_upload(upload_request_info_dump, archive_path)` → bool (calls AbstractWebStorageClient::put). `confirm_upload(token, archive_path, slide_id, layer, row, is_last_row)` → result JSON or "".
- **ScannerServiceConsumer.cpp** – `request_upload`: build path `/api/Processing/Slides/{id}/Layer/{layer}/Row/{row}`, POST with UploadRequestBindingModel (file_extension, is_last_row), return get_result().dump() or "". `try_to_upload`: delegate to amazon_web_storage_client_->put. `confirm_upload`: same path, PATCH with same body, return get_result().dump() or "".

**Used by:** Row (upload), Scanner (request_upload/confirm), Area (init with scanner service); AmazonWebStorageClient used for actual S3 put.

---

## 10. **SlideServiceConsumer** (`SlideServiceConsumer.h`, `SlideServiceConsumer.cpp`)

**Role:** Slide/scan lifecycle API: slide info, automation state, start/stop/fail scanning, upload overview.

- **SlideServiceConsumer.h** – Extends CoreServiceConsumer. `get_slide_info(token, barcode_id)`, `get_automation_state(token, barcode_id)` (returns int), `start_scanning(barcode_id, number_of_scan_layers)`, `stop_scanning(barcode_id)`, `fail_scanning(barcode_id, fail_message)`, `upload_slide_overview(barcode_id, path)`. `set_requesting_user(user)` for Authorization (global token). Private: `requesting_user_`.
- **SlideServiceConsumer.cpp** – Paths from Config, with _ID_ / _LAYERS_ replaced by barcode_id/layers. GET for slide info and automation state; POST for start/stop/fail/upload overview. Authorization from requesting_user_->get_global_token(). get_automation_state returns SlideStatus from result or -1 on permission denied; others throw or log on error.

**Used by:** Slide (get_server_state, etc.), Scanner (start/stop/fail scanning, upload overview), ScanRequest (sync with server).

---

## 11. **AbstractBarcodeReader** (`AbstractBarcodeReader.h`) — Infrastructure/Service

**Role:** Abstract barcode reader in infrastructure::service: one method that returns BarcodeInfo from a RawImage; lockable.

- Declares `BarcodeInfo`: slide_id, raw_string, position (x1..y4). Pure virtual `read(raw_image)` returning BarcodeInfo.
- Note: Domain also has its own AbstractBarcodeReader and BookZxingBarcodeReader in Domain/Barcode.h and Barcode.cpp; Domain/Barcode uses the domain types. Infrastructure/Service provides a separate abstraction (e.g. for Slide or other callers that use the service layer).

**Used by:** BookZxingBarcodeReader (Infrastructure/Service); Slide.cpp includes this header.

---

## 12. **BookZxingBarcodeReader** (`BookZxingBarcodeReader.h`, `BookZxingBarcodeReader.cpp`) — Infrastructure/Service

**Role:** Barcode reading via ZXing; implements Infrastructure/Service AbstractBarcodeReader.

- **BookZxingBarcodeReader.h** – Declares `read(raw_image)` override.
- **BookZxingBarcodeReader.cpp** – Uses ZXing::ReadBarcode on raw_image dimensions and buffer; fills BarcodeInfo (raw_string, position from result points); throws RunTimeException if invalid.

**Used by:** Wherever the infrastructure::service AbstractBarcodeReader is injected; Domain Barcode uses domain::BookZxingBarcodeReader in Domain/Barcode.cpp.

---

## BindingModels

**Role:** Request/response DTOs that serialize to/from JSON for HTTP (extend AbstractJsonSerializable / AbstractBindingModel).

| File | Purpose |
|------|--------|
| **AbstractBindingModel.h** | Empty struct extending AbstractJsonSerializable; base for request bodies. |
| **CredentialBindingModel** (.h, .cpp) | username, password, login_as_different_role; JSON keys Username, Password, LoginAsADifferentRole. Used by UserServiceConsumer::request_login. |
| **RoleBindingModel** (.h, .cpp) | organization_id, role_id, remember_me; for set-role PATCH. |
| **BarcodeBindingModel** (.h, -inl.h, .cpp) | barcode_id; -inl: ctor(unsigned long). Used where barcode id is sent. |
| **UploadRequestBindingModel** (.h, .cpp) | file_extention, last_row; for upload request/confirm body. |
| **UploadRequestResultBindingModel** (.h, .cpp) | key, bucket, access_key, secret_key, session_token, endpoint, expiration, is_object_priviledged; for parsing presigned upload response (S3). Used by AmazonWebStorageClient::put. |
| **FailScanningBindingModel** (.h, .cpp) | fail_message; for fail_scanning POST body. |
| **CoreLoginViewModel** (.h, .cpp) | token_; for parsing login response (alternate to TokenViewModel if used). |

---

## ViewModels

**Role:** Parsed response shapes (extend AbstractViewModel or AbstractJsonSerializable).

| File | Purpose |
|------|--------|
| **AbstractViewModel.h** | Empty struct extending AbstractJsonSerializable; base for response DTOs. |
| **ErrorViewModel** (.h, .cpp) | Holds JSON; get_message_text(), get_message_code() (from /0/Message/MessageText, MessageCode). Used when service_response.is_ok() is false. |
| **TokenViewModel** (.h, .cpp) | token_; get_token(); JSON key "Token". Used for login/set-role response. |
| **RolesViewModel** (.h, -inl.h, .cpp) | roles_ (vector<UserMemberShip>); get_roles(). -inl: inline get_roles. Used for get_roles response. |
| **UserMemberShip** (.h, .cpp) | display_name_, role_user_id_, role_id_, role_title_, organization_id_, organization_name_. Used inside RolesViewModel. |
| **LoginResponseJwtPayload** (.h, .cpp) | role_id_, user_display_name_; for JWT payload parsing if needed. |

---

## Summary

- **Serial:** AbstractSerialCommunication (interface), ScopedSerialCommunication (Boost.Asio impl, pimpl in -pimpl.h, async via futures in .cpp).
- **HTTP:** AbstractHttpClient (interface + HttpMethod helpers in -inl), HttpClient (cpprest + curlpp in .cpp; get/post/patch in -inl).
- **Request/response:** ServiceRequest (host, path, method, body, headers), ServiceResponse (Result/Infos/Warns/Errors/Fatals/Traces).
- **Consumers:** CoreServiceConsumer (base; one or two HTTP calls), UserServiceConsumer (login, get_roles, set_role), ScannerServiceConsumer (request_upload, try_to_upload, confirm_upload), SlideServiceConsumer (slide info, automation state, start/stop/fail scanning, upload overview).
- **Barcode (Infrastructure/Service):** AbstractBarcodeReader (interface + BarcodeInfo), BookZxingBarcodeReader (ZXing impl).
- **BindingModels:** Request DTOs (Credential, Role, Barcode, UploadRequest, FailScanning, etc.) for request bodies.
- **ViewModels:** Response DTOs (Error, Token, Roles, UserMemberShip, LoginResponseJwtPayload) for parsing backend JSON.