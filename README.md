# CMS
============================================================
DIGITAL SIGNAGE CMS – BACKEND ARCHITECTURE DOCUMENTATION
============================================================

Project Type:
-------------
Backend CMS for Digital Signage System

Technology Stack:
-----------------
- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy (Async)
- Redis
- WebSocket
- Clean Architecture
- Domain-Driven Design (DDD)

============================================================
1. ARCHITECTURE PHILOSOPHY
============================================================

This backend is built using:

- Clean Architecture
- Domain-Driven Design (DDD)
- Separation of Concerns

The system is organized in independent layers.

Each layer has ONE responsibility.

Main rule:
----------
Outer layers depend on inner layers.
Inner layers NEVER depend on outer layers.

This ensures:
- maintainability
- scalability
- testability
- long-term evolution

============================================================
2. GLOBAL LAYER OVERVIEW
============================================================

Application structure:

Backend/
└── app/
    ├── api/
    ├── common/
    ├── domain/
    ├── use_cases/
    ├── infrastructure/
    └── tests/

Layer responsibilities:

API            → communication (HTTP / WebSocket)
DOMAIN         → business rules
USE CASES      → application workflows
INFRASTRUCTURE → technical implementations
COMMON         → shared utilities
TESTS          → verification and validation

============================================================
3. API LAYER
============================================================

Path:
Backend/app/api/

Purpose:
--------
This layer exposes the application to the outside world.

It is responsible ONLY for:
- receiving requests
- validating input
- calling use cases
- returning responses

It must NEVER contain:
- SQL queries
- business rules
- Redis logic
- filesystem logic

------------------------------------------------------------
3.1 API/REST
------------------------------------------------------------

Path:
Backend/app/api/rest/

Purpose:
--------
Defines HTTP endpoints using FastAPI routers.

Examples:
- POST   /devices/register
- POST   /devices/approve
- GET    /playlists
- POST   /media/upload

Responsibilities:
- route definition
- dependency injection
- authentication dependency
- request → use case mapping

Example flow:
-------------
HTTP Request
→ Router
→ Schema validation
→ Use case execution
→ Response schema

------------------------------------------------------------
3.2 API/SCHEMAS
------------------------------------------------------------

Path:
Backend/app/api/schemas/

Purpose:
--------
Defines Data Transfer Objects (DTO).

Used to:
- validate input data
- serialize output data
- ensure API consistency

Technology:
-----------
Pydantic

Examples:
--------
- DeviceRegisterRequest
- DeviceRegisterResponse
- PlaylistCreateRequest
- MediaOut

Rules:
------
- No SQLAlchemy models
- No business logic
- No database access
- Only data structure

------------------------------------------------------------
3.3 API/WS (WebSocket)
------------------------------------------------------------

Path:
Backend/app/api/ws/

Purpose:
--------
Manages WebSocket entry points.

Used for:
- device live connections
- real-time commands
- heartbeat monitoring
- emergency broadcast

Responsibilities:
------------------
- accept socket connections
- authenticate device
- forward socket to use cases

WebSocket business logic is NEVER implemented here.

============================================================
4. COMMON LAYER
============================================================

Path:
Backend/app/common/

Purpose:
--------
Contains shared utilities used across the system.

Typical content:
----------------
- time utilities
- constants
- configuration helpers
- base exceptions
- logging helpers
- security helpers

Rules:
------
- no database access
- no business logic
- reusable everywhere

Example:
--------
time.py → unified timestamp handling

============================================================
5. DOMAIN LAYER
============================================================

Path:
Backend/app/domain/

This is the CORE of the system.

If FastAPI, PostgreSQL, or Redis disappear,
this layer still works.

The domain layer contains pure business logic.

------------------------------------------------------------
5.1 DOMAIN/ENTITIES
------------------------------------------------------------

Path:
Backend/app/domain/entities/

Purpose:
--------
Represents core business objects.

Examples:
--------
- Device
- Playlist
- Media
- Tenant
- User

Entities contain:
----------------
- business rules
- lifecycle behavior
- state transitions

Example:
--------
A device cannot be approved twice.
A playlist must have at least one item.

Entities DO NOT know:
---------------------
- database
- API
- JSON
- HTTP
- Redis

------------------------------------------------------------
5.2 DOMAIN/ENUMS
------------------------------------------------------------

Path:
Backend/app/domain/enums/

Purpose:
--------
Defines all business states.

Examples:
--------
- DeviceState (PENDING, APPROVED, REVOKED)
- MediaState (DRAFT, PUBLISHED)
- EmergencyLevel (LOW, HIGH, CRITICAL)

Rules:
------
No magic strings allowed in business logic.

------------------------------------------------------------
5.3 DOMAIN/MEDIA
------------------------------------------------------------

Path:
Backend/app/domain/media/

Purpose:
--------
Contains media-specific business logic.

Examples:
--------
- supported formats
- duration rules
- media compatibility
- resolution validation

This is NOT filesystem logic.

------------------------------------------------------------
5.4 DOMAIN/POLICIES
------------------------------------------------------------

Path:
Backend/app/domain/policies/

Purpose:
--------
Defines business authorization rules.

Examples:
--------
- who can approve devices
- who can publish content
- who can trigger emergency mode

This is BUSINESS permission logic,
not JWT or authentication.

------------------------------------------------------------
5.5 DOMAIN/VALUE_OBJECTS
------------------------------------------------------------

Path:
Backend/app/domain/value_object/

Purpose:
--------
Represents immutable validated values.

Examples:
--------
- Email
- PasswordHash
- DeviceFingerprint
- MediaDuration

Characteristics:
----------------
- immutable
- validated at creation
- used inside entities

============================================================
6. USE CASES LAYER
============================================================

Path:
Backend/app/use_cases/

Purpose:
--------
Implements application workflows.

One use case = one business action.

Examples:
--------
- RegisterDevice
- ApproveDevice
- AssignPlaylistToDevice
- FetchPlaylistForDevice
- UploadMedia
- TriggerEmergency

Use cases:
----------
- orchestrate domain logic
- call repositories
- coordinate services

They do NOT:
-----------
- handle HTTP
- handle JSON
- depend on FastAPI

------------------------------------------------------------
6.1 USE_CASES/AUTH
------------------------------------------------------------

Handles:
--------
- authentication workflows
- login
- token generation
- refresh tokens

Uses:
-----
- domain policies
- infrastructure auth services

------------------------------------------------------------
6.2 USE_CASES/CONTENT
------------------------------------------------------------

Handles:
--------
- media upload
- versioning
- publishing
- validation

Coordinates:
-------------
- domain media rules
- filesystem storage
- database persistence

------------------------------------------------------------
6.3 USE_CASES/PLAYLIST
------------------------------------------------------------

Handles:
--------
- playlist creation
- ordering
- assignment to devices
- device playlist retrieval

Critical layer for digital signage playback.

------------------------------------------------------------
6.4 USE_CASES/EMERGENCY
------------------------------------------------------------

Handles:
--------
- emergency override
- instant content replacement
- priority playback

Usually bypasses normal playlists.

------------------------------------------------------------
6.5 USE_CASES/AUDIT
------------------------------------------------------------

Handles:
--------
- system audit logs
- user actions
- traceability
- security tracking

Usually executed internally by other use cases.

============================================================
7. INFRASTRUCTURE LAYER
============================================================

Path:
Backend/app/infrastructure/

Purpose:
--------
Contains technical implementations.

This layer is replaceable.

------------------------------------------------------------
7.1 INFRASTRUCTURE/DB
------------------------------------------------------------

Contains:
---------
- SQLAlchemy models
- repositories
- database sessions
- migrations

Repositories implement interfaces expected by use cases.

------------------------------------------------------------
7.2 INFRASTRUCTURE/AUTH
------------------------------------------------------------

Contains:
---------
- JWT implementation
- password hashing
- token verification

This is technical authentication,
not business authorization.

------------------------------------------------------------
7.3 INFRASTRUCTURE/FILESYSTEM
------------------------------------------------------------

Handles:
---------
- file storage
- path resolution
- upload management

Allows future replacement:
- local storage
- S3
- NAS

------------------------------------------------------------
7.4 INFRASTRUCTURE/REDIS
------------------------------------------------------------

Handles:
---------
- cache
- online devices
- heartbeat tracking
- pub/sub communication

Critical for real-time dashboards.

------------------------------------------------------------
7.5 INFRASTRUCTURE/WEBSOCKET
------------------------------------------------------------

Handles:
---------
- socket manager
- connected clients
- broadcast system

Used by use cases indirectly.

============================================================
8. TESTS
============================================================

Path:
Backend/app/tests/

Purpose:
--------
Ensures correctness and stability.

Test types:
-----------
- domain unit tests
- use case tests
- API integration tests

Priority:
---------
Domain tests → fastest
Use case tests → medium
API tests → limited

============================================================
9. DATA FLOW EXAMPLE
============================================================

Device Registration Flow:

API REST
→ Schema validation
→ RegisterDeviceUseCase
→ Device entity validation
→ Database repository
→ Redis registration
→ Response schema

============================================================
10. FINAL PRINCIPLES
============================================================

- Domain is king
- Use cases coordinate logic
- Infrastructure is replaceable
- API is only a gateway
- Time and state are explicit
- No magic strings
- Clear boundaries

============================================================
END OF DOCUMENT
============================================================
