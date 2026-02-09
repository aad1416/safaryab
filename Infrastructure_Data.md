
Here’s what each unit under **Infrastructure/Data** does:

---

## 1. **AbstractDatabaseFactory** (`AbstractDatabaseFactory.h`, `AbstractDatabaseFactory.cpp`)

**Role:** Abstract factory for getting a DB connection; single “lockable resource” so only one Accessor holds the DB at a time.

- **AbstractDatabaseFactory.h** – Declares `AbstractDatabaseFactory` extending `commons::AbstractLockableResource`. Pure virtual `get_database(commons::Accessor* access_token)` returning `shared_ptr<Storage>`. Protected static `create(path)` to build a `Storage`.
- **AbstractDatabaseFactory.cpp** – Implements `create(path)` by calling `InlineCreateDatabase::create(path)` and wrapping the result in a `shared_ptr<Storage>`.

**Used by:** All repositories (via `BasicRepository`), DependencyInjection (DatabaseFactory vs TestDatabaseFactory).

---

## 2. **DatabaseFactory** (`DatabaseFactory.h`, `DatabaseFactory-inl.h`, `DatabaseFactory.cpp`)

**Role:** Concrete factory: one shared SQLite `Storage`, created from `DATABASE_FILE_PATH`; access only after acquiring the factory (Accessor).

- **DatabaseFactory.h** – Declares `DatabaseFactory` extending `AbstractDatabaseFactory`: ctor with optional `connection_string`, override `get_database(access_token)`.
- **DatabaseFactory-inl.h** – Inline: `get_database` calls `access_check(access_token)` then returns `storage_`.
- **DatabaseFactory.cpp** – Ctor: `storage_ = AbstractDatabaseFactory::create(DATABASE_FILE_PATH)` (path from global), stores `connection_string_`.

**Used by:** DI in production; test build uses `TestDatabaseFactory` instead.

---

## 3. **InlineCreateDatabase** (`InlineCreateDatabase.h`)

**Role:** Defines the SQLite schema and the `Storage` type (sqlite_orm storage with all tables). No .cpp.

- **InlineCreateDatabase.h** – Defines `InlineCreateDatabase::create(path)`: builds a sqlite_orm storage with every `*Configuration::create_configuration()` (Area, Barcode, FocusHandler, Plane, FocusScoreCalculator, LiveRequest, Diagnostic, Photographer, PickAndPlace, RackBoard, RackField, ScanRequest, Row, Device, Slide, Stage, User, VideoStreamer). Calls `sync_schema(true)`, `busy_timeout(500)`, `open_forever()`. Under `TESTING`, clears all entity tables then inserts `domain::User::get_built_in_user()`. Defines `CreateDatabase` (friend of AbstractDatabaseFactory) and `Storage` as an alias for the storage type. No Calibration/Rack table – those entities are either non-persisted or handled elsewhere.

**Used by:** `AbstractDatabaseFactory::create`, so every `Storage` is created through this schema.

---

## 4. **Repository – AbstractRepository** (`Repository/AbstractRepository.h`)

**Role:** Generic repository interface: CRUD by entity reference.

- **AbstractRepository.h** – Template `AbstractRepository<Entity>` with pure virtuals: `add(const_reference)`, `update(const_reference)`, `add_or_update(const_reference)`, `remove(const_reference)`. Typedefs for value_type, reference, const_reference.

**Used by:** Every concrete repository (implements or extends this).

---

## 5. **Repository – BasicRepository** (`Repository/BasicRepository.h`, `Repository/BasicRepository-inl.h`)

**Role:** Default implementation of `AbstractRepository<Entity>` using the lockable `AbstractDatabaseFactory` and sqlite_orm `Storage`. All DB access goes through an `Accessor` (wait_for_acquire / get_database / release).

- **BasicRepository.h** – Template `BasicRepository<Entity>` extending `AbstractRepository<Entity>`. Ctor takes `shared_ptr<AbstractDatabaseFactory>`. Overrides `add`, `update`, `add_or_update`, `remove`. Protected: `database_factory_`.
- **BasicRepository-inl.h** – Template impl: `add` acquires factory, calls `storage->insert(entity)`, sets entity id, releases. `update` acquires, `storage->update(entity)`. `add_or_update` acquires, `get_no_throw<Entity>(entity.get_id())`; if found then `update`, else `add`. `remove` acquires, `storage->remove<Entity>(entity.get_id())`. All paths use a temporary `Accessor` and `wait_for_acquire`; on timeout throw `RunTimeException`.

**Used by:** All concrete repositories that persist entities to the same SQLite DB (Area, Barcode, Device, Row, Slide, Stage, etc.). CalibrationRepository does not extend BasicRepository (no DB table for Calibration).

---

## 6. **Configurations** (e.g. `AreaConfiguration.h`, `DeviceConfiguration.h` + `.cpp`, …)

**Role:** Map each domain entity to a sqlite_orm table: table name, columns, getters/setters, primary/unique. For enums, some configs also specialize sqlite_orm traits (type_printer, statement_binder, field_printer, row_extractor) so the enum is stored as TEXT.

**Pattern:** Each `*Configuration` has a static `create_configuration()` that returns the result of `sqlite_orm::make_table(...)` with `make_column(...)` for each field. Columns use domain getters/setters (e.g. `&domain::Area::get_id`, `&domain::Area::set_id`). Primary key and optional unique are set per table.

**Configurations present:**

| File | Entity | Notes |
|------|--------|--------|
| **AreaConfiguration.h** | Area | id (PK), slide_id, x, y, width, height. |
| **BarcodeConfiguration.h** | Barcode | id (PK), data. |
| **DeviceConfiguration.h** + **.cpp** | Device | id (PK), mode. .cpp: enum↔string for Device::Mode + sqlite_orm traits. |
| **DiagnosticConfiguration.h** | Diagnostic | Table + Config; Diagnostic has nested Config. |
| **FocusHandlerConfiguration.h** | FocusHandler | Table for FocusHandler entity. |
| **FocusScoreCalculatorConfiguration.h** | FocusScoreCalculator | Table for calculator entity. |
| **LiveRequestConfiguration.h** | LiveRequest | Table for live request. |
| **PhotographerConfiguration.h** | Photographer | Table (likely minimal; photographer may be singleton-like). |
| **PickAndPlaceConfiguration.h** | PickAndPlace | Table. |
| **PlaneConfiguration.h** | Plane | Table for Plane. |
| **RackBoardConfiguration.h** | RackBoard | Table. |
| **RackConfiguration.h** | Rack | Table for Rack. |
| **RackFieldConfiguration.h** | RackField | id (PK), rack_index, field_index, slide_id. |
| **RowConfiguration.h** + **RowConfiguration.cpp** | Row | id (PK), area, layer, row, state. .cpp: Row::State enum↔string + sqlite_orm traits. |
| **ScanRequestConfiguration.h** + **ScanRequestConfiguration.cpp** | ScanRequest | id (PK), rackfield_id, mode, area_detection_mode, state. .cpp: enum↔string for State/Mode/AreaDetectionMode + traits. |
| **SlideConfiguration.h** | Slide | id (PK), image_preview_path, barcode, focus_plane, surrounding_area_id (FKs as ids). |
| **StageConfiguration.h** | Stage | Table for Stage. |
| **UserConfiguration.h** + **UserConfiguration.cpp** | User | id (PK), username (unique), password, display_name, role, last_validation. .cpp: User::Role enum↔string + sqlite_orm traits. |
| **VideoStreamerConfiguration.h** | VideoStreamer | Table. |

**When a config has a .cpp:** It implements string conversion for enums and the sqlite_orm specializations so those enums can be read/written as TEXT.

---

## 7. **Repositories** (e.g. `AreaRepository`, `DeviceRepository`, `SlideRepository`, …)

**Role:** Implement persistence and loading for one entity (or a small set of related ones). They use `AbstractDatabaseFactory` (and often `BasicRepository`) and, when needed, other repositories (e.g. SlideRepository uses AreaRepository, PlaneRepository, BarcodeRepository). Access to the DB is always via an `Accessor` and `get_database()`.

**Common pattern:**

- **Abstract*Repository** – Extends `AbstractRepository<Entity>`, adds entity-specific methods (e.g. `get(id)`, `get_first()`, `get_all_by_slide_id(id)`).
- ***Repository** – Implements the abstract repository; often extends `BasicRepository<Entity>` for standard add/update/add_or_update/remove, and overrides when behavior differs (e.g. cascading to child entities). Constructor takes `AbstractDatabaseFactory` and any other repos/config/logger/drivers needed to build or hydrate the entity.

**Examples:**

- **AreaRepository** – `AbstractAreaRepository` + `AreaRepository`. `get(id)`: load Area from DB, then load rows via RowRepository, call `area.init(...)`. `add`/`update`: persist rows first, then call BasicRepository. `get_all_by_slide_id`, `delete_all_by_slide_id` for slide-scoped queries.
- **DeviceRepository** – `AbstractDeviceRepository` + `DeviceRepository`. `get_first()`: single “device” record (min id or create new); ctor ensures one device row exists and is IDLE. No Calibration table; Device is the global mode record.
- **SlideRepository** – `AbstractSlideRepository` + `SlideRepository`. `get(id)`: load Slide, then load areas (AreaRepository), focus plane (PlaneRepository), barcode (BarcodeRepository), init slide with logger/config/service_consumer. `add`/`update`: persist surrounding_area, focus_plane, barcode first and set FKs, then insert/update Slide.
- **CalibrationRepository** – `AbstractCalibrationRepository` + `CalibrationRepository`. Does **not** extend BasicRepository; Calibration is not in the DB. `get_first()` returns a fully built `domain::Calibration` from injected StageRepository, PhotographerRepository, FocusHandlerRepository, SlidescopeFirmwareDriverSet, config, logger. Optional static `calibration_` for caching one instance.
- **ScanRequestRepository** – `AbstractScanRequestRepository` + `ScanRequestRepository`. Implements get, add, get_first_scan_request, get_first_scan_preparation, has_next_scan, has_next_scan_preparation, stop_all, get_report_progress_method, etc., using DB + RackFieldRepository, StageRepository, PhotographerRepository, DeviceRepository, service consumers.
- **StageRepository** – `AbstractStageRepository` + `StageRepository`. Holds a single logical Stage (static `stage_`). `get_first()` / `get_new()` return that stage instance, built from motor drivers and config; `update` persists it. Stage is effectively a singleton for the app.

Other repositories (Barcode, Diagnostic, FocusHandler, FocusScoreCalculator, LiveModeManager, LiveRequest, Photographer, PickAndPlace, Plane, RackBoard, RackField, Rack, Row, Scanner, User, VideoStreamer) follow the same idea: abstract interface + concrete class, optional use of BasicRepository, and use of DatabaseFactory + Accessor for any DB access. Repositories that build complex domain objects (e.g. Slide, Area, ScanRequest) inject and use other repositories and/or drivers.

---

## Summary

- **AbstractDatabaseFactory** + **DatabaseFactory** (+ **DatabaseFactory-inl.h**) + **InlineCreateDatabase**: provide a single lockable SQLite “connection” (Storage) and define the full schema and Storage type.
- **AbstractRepository** + **BasicRepository** (+ **BasicRepository-inl.h**): generic repository interface and default CRUD implementation with Accessor-based locking.
- **Configurations**: one (or two) files per persisted entity to define the sqlite_orm table and, when needed, enum serialization (in the .cpp).
- **Repositories**: one abstract and one concrete class per entity (or logical aggregate); they use the factory and, when applicable, BasicRepository and other repos to load/save and fully construct domain objects. Calibration and Stage are special (no or minimal DB table; built from drivers and other repos).