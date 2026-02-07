# Deployment Guide

This guide details the deployment process for Codex Caelestis on a Windows VPS environment.

## Infrastructure

The application is designed to run on a **Windows VPS** (Virtual Private Server) to support the specific astrological calculation engines.

*   **OS**: Windows Server 2019/2022 or Windows 10/11 Pro
*   **Runtime**: Python 3.11+
*   **Reverse Proxy**: Cloudflare Tunnel (cloudflared)

## Initial Setup

An automated PowerShell script is provided to bootstrap a fresh VPS.

1.  **Clone the Repository**:
    ```powershell
    git clone https://github.com/your-repo/codex-caelestis.git C:\TraditionalAstrology
    cd C:\TraditionalAstrology
    ```

2.  **Run Setup Script**:
    This script installs Chocolatey, Python, Git, VS Code, and Cloudflared. It also configures OpenSSH.
    ```powershell
    .\src\scripts\setup_vps_env.ps1
    ```

3.  **Environment Variables**:
    Create a `.env` file in the project root (`C:\TraditionalAstrology\.env`) with the following keys:
    ```ini
    STRIPE_SECRET_KEY=sk_live_...
    STRIPE_WEBHOOK_SECRET=whsec_...
    JWT_SECRET=your_secure_random_string
    ADMIN_SECRET_KEY=your_admin_key
    OWNER_EMAILS=owner@example.com
    ```

4.  **Database Seeding**:
    Initialize the database and seed subscription plans.
    ```bash
    python -m src.scripts.omnibus rehydrate
    ```

## Running the Application

Use `uvicorn` to start the ASGI server.

```bash
uvicorn src.app:app --host 0.0.0.0 --port 8000 --workers 4
```

## Updates & Maintenance

To update the application:

1.  **Pull latest changes**:
    ```bash
    git pull origin main
    ```

2.  **Apply Database Migrations**:
    ```bash
    python -m src.scripts.omnibus migrate
    ```

3.  **Restart Server**:
    Stop and restart the `uvicorn` process.
