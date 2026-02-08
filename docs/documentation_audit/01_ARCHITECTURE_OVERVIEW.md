# 01. Architecture Overview

## 1. High-Level Concept
**Codex Caelestis** (Project Astrology) is a specialized engine for traditional astrology (pre-1700s), capable of generating high-precision natal reports, forensic audits of charts, and mundane astrological analysis. It distinguishes itself by adhering strictly to traditional doctrines (e.g., Egyptian Terms, Sect-based dignity) and using a "Forensic" approach to chart analysis.

## 2. Technology Stack

### Core Runtime
- **Language**: Python 3.10+ (via Docker `python:3.10-slim`)
- **Web Framework**: FastAPI
- **Server**: Uvicorn
- **Containerization**: Docker

### Computational Engine
- **Ephemeris**: Swiss Ephemeris (`pyswisseph`) - The gold standard for astronomical calculation.
- **Location/Time**: `geopy`, `timezonefinder`, `pytz`.

### Data & Persistence
- **ORM**: SQLAlchemy
- **Database**:
    - **Local**: SQLite (`users.db`)
    - **Production**: PostgreSQL Flexible Server (Azure)
- **Caching**: Redis (implied by requirements, likely for rate limiting/session storage).
- **Data Source**: JSON files in `src/database/data/` seeded into DB.

### AI & Generation
- **LLM Provider**: OpenRouter (Google Gemini Flash)
- **PDF Generation**: `reportlab`

### Integrations
- **Payments**: Stripe (Checkout & Webhooks)
- **Auth**: PyJWT (Custom implementation with `bcrypt`)
- **Email**: SendGrid or SMTP

## 3. Directory Map (Mental Model)

```text
/
├── .env.example          # Template for environment variables
├── Dockerfile            # Container definition
├── CONTEXT.md            # Critical operational context & tribal knowledge
├── requirements.txt      # Python dependencies
├── src/                  # Application Source Code
│   ├── app.py            # Main Web Application Entry Point
│   ├── main.py           # Alternate Entry Point (CLI/Script?)
│   ├── mcp_server.py     # Model Context Protocol Server (Agent Interface)
│   ├── api/              # API Routes & Endpoints
│   ├── core/             # Core Configuration & Constants
│   ├── database/         # DB Models, Managers, and Data Seeding
│   ├── engine/           # The specialized Astrology Logic (Calculators, Auditors)
│   ├── services/         # Business Logic Layers (Auth, Stripe, Email)
│   ├── static/           # Frontend Assets (JS, CSS, HTML)
│   └── templates/        # Jinja2 Templates (if used) or HTML fragments
├── scripts/              # Utility scripts (Migrations, Extraction, Setup)
├── tests/                # Pytest Suite
└── docs/                 # Project Documentation (MkDocs source)
```

## 4. "Load Bearing" Components
Removing these causes immediate system collapse:
1.  **`pyswisseph`**: The astronomical kernel. Without it, no charts are calculated.
2.  **`src/engine/`**: Contains the unique value proposition (Forensic logic, Dignity calculations).
3.  **`CONTEXT.md`**: The brain of the project for AI development.
4.  **`src/database/data/`**: The traditional astrological ruleset (delineations).

## 5. Architectural Patterns
- **Monolith**: Single service handling API, Static Files, and Logic.
- **Service Layer**: Separation between API (`src/api`) and Business Logic (`src/services`, `src/engine`).
- **Data-Driven Logic**: Heavily reliant on structured JSON/DB data for delineations rather than hardcoded strings.
- **Hybrid AI**: Deterministic calculation engine + GenAI synthesis layer.
