# Project Structure

## Folder Layout

```
rfpgl-api/
├── main.py                  # App factory — router registration, middleware setup
├── requirements.txt
├── Dockerfile
├── alembic.ini
├── _staging.env             # Env vars for staging (DB_CONFIG, OAUTH2_URL, etc.)
├── _prod.env                # Env vars for production
│
├── configs/                 # App-wide configuration
│   ├── configs.py           # Pydantic Settings — loads env vars
│   ├── permission.py        # OAuth2 permission dependency classes
│   ├── generator_pdf.py     # PDF generation config/helpers
│   └── report_generator_pdf.py
│
├── models/                  # SQLModel table definitions
│   ├── base_model.py        # BaseUUIDModel, BaseCodeModel, BaseMasterModelFull
│   └── *_model.py
│
├── schemas/                 # Pydantic request/response schemas
│   ├── common_sch.py        # Shared enums (WorkflowLastStatusEnum, RfpTypeEnum, etc.)
│   ├── response_sch.py      # Generic response wrappers (GetResponseBaseSch, etc.)
│   └── *_sch.py
│
├── crud/                    # Database access layer
│   ├── __init__.py          # Exports singleton instances of all CRUD classes
│   ├── base_crud.py         # CRUDBase generic class
│   └── *_crud.py
│
├── services/                # Business logic layer
│   └── *_service.py
│
├── routes/
│   ├── api.py               # Router aggregation — defines the 5 router groups
│   └── endpoints/           # One file per resource domain
│       └── *.py
│
├── common/                  # Shared utilities and exceptions
│   ├── enum.py              # Domain enums
│   ├── exceptions.py        # HTTPException subclasses (IdNotFoundException, etc.)
│   └── partial.py
│
├── utils/
│   ├── common_helper.py     # Static utility functions (formatting, string ops)
│   └── exceptions/
│       └── common_exception.py
│
├── views/                   # Read-only composite views (non-ORM query helpers)
│
├── migrations/
│   └── versions/            # Alembic migration files
│
├── tasks/                   # Cloud Task payload definitions
│
└── docs/
    └── db_functions.md      # Full documentation of all PostgreSQL stored functions
```

## Architecture Pattern

The codebase follows a strict 4-layer architecture:

```
Route (endpoint) → Service → CRUD → Model
```

- **Routes** (`routes/endpoints/*.py`) — Handle HTTP concerns: request parsing, auth dependencies, response wrapping. Must stay thin.
- **Services** (`services/*_service.py`) — Orchestrate business logic across multiple CRUD calls, manage transactions, call external APIs.
- **CRUD** (`crud/*_crud.py`) — Database access only. Each CRUD class extends `CRUDBase` and is exported as a singleton in `crud/__init__.py`.
- **Models** (`models/*_model.py`) — SQLModel table definitions. Relationships default to `noload` or `joined`; use `selectinload` in CRUD when eager loading is needed.

## Key Conventions

### Models

- All tables inherit `BaseUUIDModel` (UUID primary key, `created_at`, `updated_at`, `created_by_id`, `updated_by_id`).
- Table names are auto-generated via `stringcase.snakecase(ClassName)` — no manual `__tablename__` needed.
- Master entities with a code field inherit `BaseCodeModel`; `code` is always stored uppercase.
- Separate `Base` / `FullBase` / `table=True` classes per model:
  - `XBase(SQLModel)` — field definitions only
  - `XFullBase(XBase, BaseUUIDModel)` — adds ID and audit fields
  - `X(XFullBase, table=True)` — actual table, adds relationships and `@property` computed fields

### Schemas

- `CreateSch` extends the model's `Base` class.
- `UpdateSch` is a separate class (often just `pass` to inherit base).
- `ByIdSch` is the rich response schema for single-record fetches.
- `Sch` (no suffix) is the lighter list/paginated response schema.
- All API responses use the generic wrappers from `schemas/response_sch.py`:
  - `create_response(data=obj)` — returns `{"data": ..., "message": ...}`
  - `GetResponseBaseSch[T]`, `PostResponseBaseSch[T]`, `GetResponsePaginatedSch[T]`

### CRUD

- All CRUD instances are singletons exported from `crud/__init__.py`. Import and use as `crud.rfp_header`, `crud.jlheader`, etc.
- `db_session` is always optional — defaults to `db.session` from the middleware. Pass it explicitly only when batching operations without intermediate commits.
- Use `with_commit=False` for multi-step operations; call `await db_session.commit()` manually at the end in the service layer.
- `DuplicateException` is raised automatically on `IntegrityError` inside `create`/`update`.

### Services

- Services are instantiated per-call: `await RfpService().create_rfp(...)`.
- Multi-step DB operations (create header → create lines → create banks → commit) are wrapped in `try/except` with `await db_session.rollback()` on failure.
- External HTTP calls use the synchronous `requests` library (not `httpx`).

### Routes

- Each router file defines `router = APIRouter()` at the top.
- Auth dependency is applied at the router group level in `routes/api.py`, not per endpoint.
- Client-facing routes use a separate `router_client` in the same file.
- Raise `IdNotFoundException(Model, id)` for 404s on missing records.

### Enums

- All string enums used in models and schemas live in `schemas/common_sch.py`.
- Domain-specific enums that don't belong to a schema live in `common/enum.py`.

### Migrations

- Migration files are named: `{hash}_{date_description}.py`
- Always use `alembic revision --autogenerate` to generate; review before applying.
