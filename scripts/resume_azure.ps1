# Azure Resume Script for Astrology Engine
# Brings parked resources back online for testing/migration work.

$ErrorActionPreference = "Continue"

$RESOURCE_GROUP = "astrology-rg-migration"
$WEBAPP_NAME = "astrology-engine-central-7387"
$DB_SERVER = "astrology-db-central-7387"

Write-Host "--- Resuming Azure Resources ---" -ForegroundColor Cyan

Write-Host "`n[1/2] Starting PostgreSQL..." -ForegroundColor Yellow
try {
    $dbState = az postgres flexible-server show --resource-group $RESOURCE_GROUP --name $DB_SERVER --query "state" -o tsv
    if ($dbState -eq "Stopped") {
        az postgres flexible-server start --resource-group $RESOURCE_GROUP --name $DB_SERVER
        Write-Host "PostgreSQL start requested." -ForegroundColor Green
    } else {
        Write-Host "PostgreSQL is '$dbState' (no start needed)." -ForegroundColor Green
    }
} catch {
    Write-Host "Warning: PostgreSQL start step failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n[2/2] Starting Web App..." -ForegroundColor Yellow
try {
    az webapp start --resource-group $RESOURCE_GROUP --name $WEBAPP_NAME
    Write-Host "Web App started." -ForegroundColor Green
} catch {
    Write-Host "Warning: Web App start step failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n--- Resume Sequence Complete ---" -ForegroundColor Cyan
