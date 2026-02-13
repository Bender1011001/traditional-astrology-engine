# 02. Setup and Run Guide

## 1. The "Golden Path" (Local Development)
This comes from verifying `README.md` and `requirements.txt`.

### Prerequisites
- Python 3.10+
- PostgreSQL (optional, defaults to SQLite `users.db` locally)
- Stripe/OpenRouter API Keys (for full functionality)

### Quick Start
```bash
# 1. Clone & Enter
git clone <repo_url>
cd astrology

# 2. Virtual Environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Environment Configuration
cp .env.example .env
# Edit .env with your keys (JWT_SECRET, OPENROUTER_API_KEY, STRIPE_...)

# 5. Run Web Server
uvicorn src.app:app --reload
```
**Access**: Open `http://localhost:8000/docs` for Swagger UI.

## 2. Docker Execution (Production-Like)
Based on `Dockerfile`.

```bash
# 1. Build
docker build -t codex-engine .

# 2. Run
docker run -p 8000:8000 --env-file .env codex-engine
```

## 3. Entry Points

| Entry Point | Purpose | Usage |
|-------------|---------|-------|
| `src/app.py` | **Main Web Server** | Production entry point. Initializes FastAPI, DB, and Middleware. |
| `src/main.py` | **Testing/CLI Audit** | Runs a hardcoded "Universal Causation Audit" (Dev tool). |
| `src/mcp_server.py` | **Agent Protocol** | Exposes engine via Model Context Protocol for AI agents. |
| `src/scripts/generate_premium_report.py`| **CLI Report** | Generates premium Markdown reports from command line. |

## 4. Environment Variables
See `.env.example` for full list.
- **Critical**: `JWT_SECRET`, `STRIPE_SECRET_KEY`, `OPENROUTER_API_KEY`.
- **Optional**: `App Service` handles these in Azure.

## 5. Deployment Scripts
- `setup_azure.ps1`: Automates Azure infrastructure provisioning (Resource Group, App Service Plan, Web App, Postgres).
- `setup_deployment.ps1`: Local Windows setup for Cloudflare Tunnel exposure (Hybrid/Dev access).
