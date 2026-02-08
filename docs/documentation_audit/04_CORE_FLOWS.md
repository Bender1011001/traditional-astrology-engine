# 04. Core Flows (The Nervous System)

## 1. Authentication Flow (Login)
**Goal**: Securely authenticate a user and issue a JWT for session management.

```mermaid
sequenceDiagram
    participant Client
    participant API as AuthEndpoint (/api/v1/auth/login)
    participant UM as UserManager
    participant DB as Database (Users)
    participant JWT as TokenFactory

    Client->>API: POST /login {email, password}
    API->>UM: authenticate(email, password)
    UM->>DB: Query User by email
    DB-->>UM: User Record (pw_hash, salt)
    UM->>UM: Verify Password (bcrypt + salt)
    
    alt Invalid Credentials
        UM-->>API: {success: False, message: "Invalid credentials"}
        API-->>Client: 401 Unauthorized
    else Valid Credentials
        UM-->>API: {success: True, user: {...}}
        API->>JWT: create_access_token(user_id, tier)
        JWT-->>API: JWT String
        API-->>Client: {success: True, token: "ey...", user: {...}}
    end
```

## 2. Chart Calculation & Forensic Audit
**Goal**: Calculate high-precision planetary positions and perform a forensic astrological audit.

```mermaid
sequenceDiagram
    participant Client
    participant API as ChartsEndpoint (/api/v1/calculate)
    participant Bridge as EngineBridge
    participant Calc as ChartCalculator
    participant Swe as SwissEphemeris
    participant Auditor as ForensicAuditor
    participant DB as DelineationDB
    participant Cache as Redis/Cache

    Client->>API: POST /calculate {date, time, city}
    
    %% Cache Check
    API->>Cache: get(chart_hash)
    opt Cache Hit
        Cache-->>API: Cached Result
        API-->>Client: JSON Result
    end

    %% Calculation
    API->>Bridge: generate_full_nativity_async()
    Bridge->>Calc: calculate_chart_data(input)
    Calc->>Swe: calc_ut(julian_day, planets)
    Swe-->>Calc: Positions (Long, Lat, Speed)
    Calc->>Swe: houses()
    Swe-->>Calc: House Cusps
    Calc->>Calc: Compute Derived (Antiscia, Lots, Phasis)
    Calc-->>Bridge: Technical Chart Object

    %% Audit
    Bridge->>Auditor: perform_audit(Chart)
    Auditor->>Auditor: Calculate Almutens & Dignities
    Auditor->>Auditor: Check Kakosis (Maltreatment)
    Auditor->>DB: Fetch Text (Planets in Signs/Houses)
    DB-->>Auditor: Delineation Text
    Auditor-->>Bridge: Audit Report (Technical + Narrative)

    %% Response
    Bridge-->>API: Full Result
    API->>Cache: set(chart_hash, result)
    API-->>Client: Full JSON {meta, planets, analysis...}
```

## 3. Subscription Verification (Middleware)
**Goal**: Verify request entitlements before allowing processing.

```mermaid
sequenceDiagram
    participant Client
    participant Middleware as QuotaMiddleware
    participant DB as Database
    participant API as ProtectedResource

    Client->>Middleware: Request with JWT or API Key
    
    alt No Credentials
        Middleware-->>Client: 401 Unauthorized
    end

    Middleware->>DB: Fetch Subscription/Usage
    
    alt Quota Exceeded
        Middleware-->>Client: 429 Too Many Requests
    else Quota Available
        Middleware->>API: Forward Request
        API-->>Middleware: Response
        Middleware->>DB: Increment Usage Count
        Middleware-->>Client: Response
    end
```

## 4. Key Components Interaction

| Component | Responsibility | Dependencies |
|-----------|----------------|--------------|
| `src.engine.chart_calculator` | **Physics Engine**: Pure astronomical calculation. | `pyswisseph`, `geopy`, `timezonefinder` |
| `src.engine.forensic_engine` | **Logic Engine**: Applies traditional rules (e.g., Bonatti/Valens). | `chart_calculator`, `database` |
| `src.database.db_manager` | **Knowledge Base**: Retrieves interpretative text. | `SQLAlchemy` |
| `src.api.v1.endpoints` | **Gateway**: Validation, Auth, Response formatting. | `fastapi`, `pydantic` |
