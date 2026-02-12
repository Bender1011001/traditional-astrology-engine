# Azure Downgrade Script for Astrology Engine
# This script reverts high-cost infrastructure to economical tiers.
# Also parks compute resources to minimize idle burn while there are no users.

$ErrorActionPreference = "Continue"

$RESOURCE_GROUP = "astrology-rg-migration"
$ACR_NAME = "astrologyacr3391"
$PLAN_NAME = "astrology-plan-central"
$WEBAPP_NAME = "astrology-engine-central-7387"
$DB_SERVER = "astrology-db-central-7387"

Write-Host "--- Initiating Azure Cost Downgrade ---" -ForegroundColor Cyan

# 1. ACR Downgrade
Write-Host "`n[1/5] Removing ACR Replications and Downgrading to Basic..." -ForegroundColor Yellow
try {
    $acrSku = az acr show --resource-group $RESOURCE_GROUP --name $ACR_NAME --query "sku.name" -o tsv
    if ($acrSku -eq "Premium") {
        # Remove non-home replications (Premium feature).
        $registryLocation = az acr show --resource-group $RESOURCE_GROUP --name $ACR_NAME --query "location" -o tsv
        $replications = az acr replication list --registry $ACR_NAME --query "[].name" -o tsv
        foreach ($repName in $replications) {
            if ($repName -ne $registryLocation) {
                Write-Host "Removing replication '$repName'..."
                az acr replication delete --registry $ACR_NAME --name $repName
            }
        }
    }
    az acr update --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic
    Write-Host "ACR downgraded to Basic." -ForegroundColor Green
} catch {
    Write-Host "Warning: ACR downgrade step failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 2. App Service Plan Downgrade
Write-Host "`n[2/5] Downgrading App Service Plan to B1..." -ForegroundColor Yellow
# B1 is the cheapest "Basic" plan for Linux that supports Always On (if needed) and no artificial CPU limits.
# F1 (Free) is also an option but has tight limits.
try {
    az appservice plan update --name $PLAN_NAME --resource-group $RESOURCE_GROUP --sku B1
    # Force-disable Zone Redundancy if set
    az appservice plan update --name $PLAN_NAME --resource-group $RESOURCE_GROUP --set zoneRedundant=false
} catch {
    Write-Host "Note: Plan was already non-zone-redundant or could not be toggled."
}
Write-Host "App Service Plan Downgraded to B1." -ForegroundColor Green

# 3. Web App Stop (compute hibernation)
Write-Host "`n[3/5] Stopping Web App to eliminate runtime compute..." -ForegroundColor Yellow
try {
    az webapp stop --resource-group $RESOURCE_GROUP --name $WEBAPP_NAME
    Write-Host "Web App stopped." -ForegroundColor Green
} catch {
    Write-Host "Warning: Web App stop failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 4. PostgreSQL Downgrade
Write-Host "`n[4/5] Downgrading PostgreSQL to Burstable Tier..." -ForegroundColor Yellow
try {
    $dbState = az postgres flexible-server show --resource-group $RESOURCE_GROUP --name $DB_SERVER --query "state" -o tsv
    if ($dbState -eq "Ready") {
        # Disable HA first (required prior to lower-cost SKU changes).
        az postgres flexible-server update --resource-group $RESOURCE_GROUP --name $DB_SERVER --high-availability Disabled --yes
        # Downgrade SKU to Burstable B1ms.
        az postgres flexible-server update --resource-group $RESOURCE_GROUP --name $DB_SERVER --sku-name Standard_B1ms --tier Burstable
        Write-Host "PostgreSQL downgraded to Burstable B1ms." -ForegroundColor Green
    } else {
        Write-Host "PostgreSQL is '$dbState'; skipping compute downgrade updates." -ForegroundColor Yellow
    }
} catch {
    Write-Host "Warning: PostgreSQL downgrade step failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 5. PostgreSQL Stop (compute hibernation)
Write-Host "`n[5/5] Stopping PostgreSQL compute..." -ForegroundColor Yellow
try {
    $dbStateBeforeStop = az postgres flexible-server show --resource-group $RESOURCE_GROUP --name $DB_SERVER --query "state" -o tsv
    if ($dbStateBeforeStop -eq "Ready") {
        az postgres flexible-server stop --resource-group $RESOURCE_GROUP --name $DB_SERVER
        Write-Host "PostgreSQL stop requested." -ForegroundColor Green
    } else {
        Write-Host "PostgreSQL is already '$dbStateBeforeStop'." -ForegroundColor Green
    }
} catch {
    Write-Host "Warning: PostgreSQL stop step failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n--- Downgrade Sequence Complete ---" -ForegroundColor Cyan
Write-Host "Resources are now parked at minimal development cost tiers." -ForegroundColor Gray
