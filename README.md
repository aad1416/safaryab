
Here’s a concise overview of the **cennalab** codebase so you can ask follow-up questions.

---

## **cennalab – High-Level Overview**

**cennalab** is a **Slidescope** system: hardware and software for automated **slide scanning** (microscope slides), with racks, motors, cameras, grippers, and firmware.

---

## **Repository Layout**

| Component | Role |
|----------|------|
| **Slidescope-Core** | Main C++ backend: Thrift RPC server, business logic, hardware drivers, SQLite DB. |
| **Slidescope-UI** | WPF (C#) desktop UI that talks to Core via Thrift. |
| **Slidescope-Client** | C++ Thrift client used for testing / scripting Core (login, motors, scan, rack, firmware, etc.). |
| **Slidescope-Firmware** | Python mock that emulates firmware over serial (COM port), same protocol as real hardware. |
| **Slidescope-Documents** | Docs and diagrams (Persian: “محل قرارگیری مستندات پروژه”), including sequence diagrams (login, scan, live mode, rack, etc.). |

---

## **Slidescope-Core (Main Backend)**

- **Entry point:** `Source/Mobayyen.Slidescope.cpp`  
  - Loads config (optional path in `argv[1]`), sets up **DependencyInjection**, **AmazonWebStorageClient**, **TaskScheduler**, and **FrontEndController**, then starts the Thrift server. The process then runs until shutdown (the `return EXIT_FAILURE` at the end looks like a bug; it never returns success).

- **API surface:** One Thrift service, **BasicRequestor**, with a single method:
  - `request(ControllerType controller_type, string action_name, string data)`  
  Controllers: **UserManager**, **LiveStream**, **RackBoard**, **Scanner**, **Diagnostic**.

- **Request flow:**  
  **FrontEndController** (Thrift `TThreadPoolServer`) → **BasicRouter** (implements `BasicRequestorIf`) → selects controller by `controller_type`, checks lock/access, then invokes the matching **action_name** with JSON **data**. Controllers live under `Core/Service/Controllers/` (e.g. **ScannerController**, **DiagnosticController**, **RackBoardController**, **UserManagerController**, **LiveStreamController**).

- **Architecture (Core):**
  - **Commons:** Logging, exceptions, image utilities, base64, token generator, task scheduler, web storage (e.g. Amazon), ONNX model wrapper.
  - **Domain:** Scanner, ScanRequest, Row, Area, Slide, Stage, Rack, RackBoard, RackField, Photographer, FocusHandler, FocusScoreCalculator, LiveRequest, LiveModeManager, PickAndPlace, Barcode, Diagnostic, User, VideoStreamer, Calibration, Beep, Device, Plane, SampleDetector.
  - **Infrastructure/Driver:** Abstract drivers + real/mock implementations: cameras (high/low quality, Pylon), XY/Z motors (Zaber), lights (top/bottom), door, beep, slide sensor board, gripper, **SlidescopeFirmwareDriver** (serial protocol to firmware). **SlidescopeFirmwareCommunication** implements the serial protocol (e.g. `/I`, `/C`, ...).
  - **Infrastructure/Data:** SQLite via sqlite_orm, repositories for the domain entities above, **DatabaseFactory**, **Config** (from YAML).
  - **Infrastructure/Service:** HTTP client, binding models/view models for external services (login, roles, upload, barcode, etc.), **CoreServiceConsumer**, **SlideServiceConsumer**, **UserServiceConsumer**, **ScannerServiceConsumer**.

- **Config:** `Config/Config.yml` drives system and hardware: server URLs, auth paths, firmware port (`SLIDESCOPE_FIRMWARE_PORT`), motor limits (X/Y/Z), focus handler, cameras, live stream, scan/sample/area detection, Zaber, firmware speeds/positions, diagnostics, calibration, etc. Config is injected and used across drivers and controllers.

- **Libraries (Core):** Thrift, Boost (date_time, log, regex, thread, filesystem), cpprest, nlohmann-json, OpenCV, Pylon (Basler), libjpeg-turbo, GraphicsMagick, Zaber Motion, NuBook ZXing (barcode), ONNX Runtime, marl (scheduler), 7zip-cpp, AWS SDK (S3, etc.), sqlite3 + sqlite_orm, yaml-cpp, RTTR, TBB, vcpkg for many of these.

- **Build:** CMake (vcpkg toolchain), produces executable **Mobayyen.Slidescope** and **Mobayyen.Slidescope.Lib**. Post-build copies Config, Assets (e.g. ONNX models), Zaber DLLs, ONNX DLLs, SamplePicture. **Test** subdirectory builds with **Mobayyen.Slidescope.Test.Lib** (same sources + `TESTING` define, test DB path).

---

## **Slidescope-Client**

- C++ app that uses Thrift to call Core. Defines an **Action** enum (LOGIN, motors, lights, door, gripper, scan, rack movements, firmware status, etc.) and implements a CLI/script that sends corresponding `request(controller_type, action_name, data)` calls. Useful to see how the API is used and for manual/automated testing.

---

## **Slidescope-Firmware (Mock)**

- **mock-server.py** opens a serial port (e.g. COM6), listens for the same command strings Core sends (e.g. `/I`, `/S`, `/G`, …), and replies with fixed payloads and checksum so Core can run without real hardware.

---

## **Data & External Systems**

- **Local:** SQLite DB (path from CMake, e.g. `slidescope.db` next to the executable). Repositories map domain entities to this DB.
- **External:** Config points to a **SERVER_HOST_URI** (e.g. `http://192.168.21.12:80`) for auth (login, roles), slide info, automation state, scanning start/stop/fail, upload overview. **WEB_STORAGE_CLIENT** (e.g. MinIO at `http://192.168.21.15:9000`) is used for storage (e.g. uploads).

---

## **Domain in One Sentence**

The system **loads slides from racks**, moves them to a **stage**, uses **cameras** and **focus** (Z) to scan tiles, runs **barcode** and **scan-area** logic (including ONNX models), and coordinates with an **external server** and **web storage**; all of this is driven by the **UI** and **Client** via the Thrift **BasicRequestor** API and configured by **Config.yml**.

---


## **Document Of C++ Sources (Slidescope-Core/Source/Core)**

1. [Core Directory](./CoreRoot.md) 

2. [Commons](./Commons.md)

3. [Domain](./Domain.md)

4. Infrastructure
4.1. [Infrastructure/Data](./Infrastructure_Data.md)
4.2. [Infrastructure/Driver](./Infrastructure_Driver.md)
4.3 [Infrastructure/Service](./Infrastructure_Service.md)

4. [Service/Controllers](./Service_Controllers.md)