
# Azure Setup Script for Astrology Engine
# Usage: .\setup_azure.ps1

$ErrorActionPreference = "Stop"

# Ensure Azure CLI is in Path
$env:Path += ";C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin"



# --- Configuration ---
$RESOURCE_GROUP = "astrology-rg-migration" # Changed to avoid conflict with existing 'eastus' RG
$LOCATION = "eastus2" 
$ACR_NAME = "astrologyacr" + (Get-Random -Minimum 1000 -Maximum 9999) 
$PLAN_NAME = "astrology-plan"
$APP_NAME = "astrology-engine-" + (Get-Random -Minimum 1000 -Maximum 9999) 
$DB_SERVER_NAME = "astrology-db-" + (Get-Random -Minimum 1000 -Maximum 9999) 
$DB_USER = "astroadmin"

# --- Provider Registration ---
Write-Host "Registering Resource Providers..."
az provider register --namespace Microsoft.ContainerRegistry
az provider register --namespace Microsoft.Web
az provider register --namespace Microsoft.DBforPostgreSQL
Write-Host "Waiting 30 seconds for registration to propagate..."
Start-Sleep -Seconds 30


# Generate a strong password
$DB_PASS = -join ((33..126) | Get-Random -Count 16 | % {[char]$_})
# Ensure password meets Azure complexity (3 categories)
$DB_PASS = "A1!" + $DB_PASS 

Write-Host "=== Configuration ==="
Write-Host "Resource Group: $RESOURCE_GROUP"
Write-Host "App Name: $APP_NAME"
Write-Host "DB Server: $DB_SERVER_NAME"
Write-Host "DB User: $DB_USER"
Write-Host "DB Password: $DB_PASS"
Write-Host "====================="

# --- Checks ---
Write-Host "Checking Azure CLI..."
try {
    az --version | Out-Null
} catch {
    Write-Error "Azure CLI (az) is not installed. Please install it first."
    exit 1
}

Write-Host "Checking Login Status..."
try {
    $account = az account show --output json | ConvertFrom-Json
    Write-Host "Logged in as: $($account.user.name) (Subscription: $($account.name))"
} catch {
    Write-Error "You are not logged in. Please run 'az login' first."
    exit 1
}

# --- Infrastructure ---

Write-Host "`n1. Creating Resource Group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

Write-Host "`n2. Creating Container Registry..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true


Write-Host "`n3. Creating App Service Plan (Linux)..."
# Using F1 (Free) tier to avoid "Basic" quota limits. 
# Note: F1 has CPU limits (60 mins/day) and no Always On. 
# If needed, upgrade to B1 in portal later.
az appservice plan create --name $PLAN_NAME --resource-group $RESOURCE_GROUP --sku F1 --is-linux


Write-Host "`n4. Creating Web App..."
# Uses a dummy image first, we will deploy later
az webapp create --resource-group $RESOURCE_GROUP --plan $PLAN_NAME --name $APP_NAME --deployment-container-image-name "$ACR_NAME.azurecr.io/astrology-engine:latest"

Write-Host "`n5. Creating PostgreSQL Flexible Server (this takes a few minutes)..."
az postgres flexible-server create --resource-group $RESOURCE_GROUP --name $DB_SERVER_NAME --location $LOCATION --admin-user $DB_USER --admin-password $DB_PASS --sku-name Standard_B1ms --tier Burstable --public-access 0.0.0.0 --yes

# --- Outputs ---
$DB_URL = "postgresql://$($DB_USER):$($DB_PASS)@$($DB_SERVER_NAME).postgres.database.azure.com:5432/postgres"
$ACR_LOGIN_SERVER = "$ACR_NAME.azurecr.io"

Write-Host "`n=== SETUP COMPLETE ==="
Write-Host "Save these values for your GitHub Secrets:"
Write-Host "AZURE_WEBAPP_NAME: $APP_NAME"
Write-Host "REGISTRY_LOGIN_SERVER: $ACR_LOGIN_SERVER"
Write-Host "DB_CONNECTION_STRING: $DB_URL"
Write-Host ""
Write-Host "Get ACR Credentials:"
Write-Host "Run: az acr credential show --name $ACR_NAME"
Write-Host ""
Write-Host "Next Steps:"
Write-Host "1. Configure GitHub Secrets"
Write-Host "2. Set App Service Environment Variables using: az webapp config appsettings set ..."
