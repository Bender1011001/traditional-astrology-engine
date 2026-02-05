# Azure Migration Guide

This guide details how to migrate the Astrology Engine from Render to Azure App Service + Azure Database for PostgreSQL.

## Prerequisites
- Azure CLI installed (`az`)
- GitHub Repository Admin access

## 1. Infrastructure Setup (via Azure CLI)

Run these commands in your local terminal.

### 1.1 Set Variables
```bash
RESOURCE_GROUP="astrology-rg-migration" # Updated to avoid conflict
LOCATION="eastus2" # Updated to eastus2
ACR_NAME="astrologyacr" # Must be globally unique
PLAN_NAME="astrology-plan"
APP_NAME="astrology-engine" # Must be globally unique
DB_SERVER_NAME="astrology-db" # Must be globally unique
DB_USER="astroadmin"
DB_PASS="YourStrongPassword123!" # CHANGE THIS
```

### 1.2 Create Resource Group and Container Registry
```bash
az group create --name $RESOURCE_GROUP --location $LOCATION
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true
```

### 1.3 Create App Service Plan (Linux)
```bash
az appservice plan create --name $PLAN_NAME --resource-group $RESOURCE_GROUP --sku F1 --is-linux
```

### 1.4 Create Web App
```bash
az webapp create --resource-group $RESOURCE_GROUP --plan $PLAN_NAME --name $APP_NAME --deployment-container-image-name $ACR_NAME.azurecr.io/astrology-engine:latest
```

### 1.5 Create PostgreSQL Database
```bash
az postgres flexible-server create --resource-group $RESOURCE_GROUP --name $DB_SERVER_NAME --location $LOCATION --admin-user $DB_USER --admin-password $DB_PASS --sku-name Standard_B1ms --tier Burstable --public-access 0.0.0.0
```
*Note: `public-access 0.0.0.0` allows access from Azure IP addresses (like App Service).*

## 2. Configuration

### 2.1 Get Connection Strings
**Database URL:**
`postgresql://astroadmin:A1!StrongPass123@astrology-db-central-7387.postgres.database.azure.com:5432/postgres`

### 2.2 Configure App Service Environment Variables
Set these via the Azure Portal -> App Service -> Settings -> Environment Variables, or CLI:

```bash
az webapp config appsettings set --resource-group astrology-rg-migration --name astrology-engine-central-7387 --settings \
  DATABASE_URL="postgresql://astroadmin:A1!StrongPass123@astrology-db-central-7387.postgres.database.azure.com:5432/postgres" \
  STRIPE_SECRET_KEY="sk_live_..." \
  STRIPE_WEBHOOK_SECRET="whsec_..." \
  JWT_SECRET="your_jwt_secret" \
  OPENROUTER_API_KEY="sk-or-..." \
  SENDGRID_API_KEY="SG...." \
  SENDER_EMAIL="noreply@traditional-astrology.com" \
  SITE_BASE_URL="https://astrology-engine-central-7387.azurewebsites.net"
```

## 3. GitHub Actions Deployment

1. **ACR Credentials:**
   - **Login Server:** `astrologyacr3391.azurecr.io`
   - **Username:** `astrologyacr3391`
   - **Password:** `COJHm8EKcrWV0qbgkZjDQwMp2zgDoP5GNbbmaCuniNciur69p3ouJQQJ99CBACHYHv6Eqg7NAAACAZCRRXGYl`

2. **Set GitHub Secrets:**
   Go to GitHub Repo -> Settings -> Secrets and variables -> Actions -> New repository secret.
   - `AZURE_WEBAPP_NAME`: `astrology-engine-central-7387`
   - `REGISTRY_LOGIN_SERVER`: `astrologyacr3391.azurecr.io`
   - `REGISTRY_USERNAME`: `astrologyacr3391`
   - `REGISTRY_PASSWORD`: `COJHm8EKcrWV0qbgkZjDQwMp2zgDoP5GNbbmaCuniNciur69p3ouJQQJ99CBACHYHv6Eqg7NAAACAZCRRXGYl`
   - `AZURE_CREDENTIALS`: *(Optional if using Publish Profile or Service Principal, but the workflow uses ACR creds + simple deployment)*

3. **Push to Main:**
   The workflow `.github/workflows/azure-deploy.yml` will automatically build the Docker image, push to ACR, and tell App Service to update.

## 4. Verification

1. Go to `https://astrology-engine-central-7387.azurewebsites.net`.
2. Check logs: `az webapp log tail --resource-group astrology-rg-migration --name astrology-engine-central-7387`.
