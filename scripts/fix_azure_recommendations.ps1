# Azure Advisor Fixes for Astrology Engine
# This script applies the recommendations provided by Azure Advisor.
# WARNING: These changes will increase monthly Azure costs.

$RESOURCE_GROUP = "astrology-rg-migration"
$ACR_NAME = "astrologyacr3391"
$PLAN_NAME = "astrology-plan-central"
$DB_SERVER = "astrology-db-central-7387"
$LOCATION = "centralus" # Primary location from resource list
$REPLICA_LOCATION = "eastus2" 

Write-Host "--- Applying Azure Advisor Recommendations ---" -ForegroundColor Cyan

# 1. Service Health Alert
Write-Host "`n[1/5] Creating Service Health Alert..." -ForegroundColor Yellow
az monitor activity-log alert create --name "ServiceHealthAlert" --resource-group $RESOURCE_GROUP --condition "category=ServiceHealth" --description "Alert for Azure Service Health issues"
Write-Host "Service Health Alert created." -ForegroundColor Green

# 2. ACR Upgrade & Geo-replication
Write-Host "`n[2/5] Upgrading ACR to Premium Tier..." -ForegroundColor Yellow
az acr update --name $ACR_NAME --sku Premium
Write-Host "Creating ACR Replication in $REPLICA_LOCATION..." -ForegroundColor Yellow
az acr replication create --registry $ACR_NAME --location $REPLICA_LOCATION
Write-Host "ACR Premium upgrade and Geo-replication complete." -ForegroundColor Green

# 3. App Service Plan Upgrade (Standard S1 + Zone Redundancy)
Write-Host "`n[3/5] Upgrading App Service Plan to S1 with Zone Redundancy..." -ForegroundColor Yellow
# Note: Zone redundancy requires at least 3 instances to be effective and is set at creation or via specific update.
# Some existing plans cannot enable zoneRedundant=true if not originally created as such. 
# We will upgrade the SKU first.
az appservice plan update --name $PLAN_NAME --resource-group $RESOURCE_GROUP --sku S1
# Attempt to enable zone redundancy (may fail if infra doesn't support transition)
try {
    az appservice plan update --name $PLAN_NAME --resource-group $RESOURCE_GROUP --set zoneRedundant=true
    Write-Host "Zone Redundancy enabled." -ForegroundColor Green
}
catch {
    Write-Host "Warning: Could not enable Zone Redundancy on existing plan. This may require a new plan deployment." -ForegroundColor Red
}

# 4. PostgreSQL Upgrade (Burstable -> GeneralPurpose)
Write-Host "`n[4/5] Upgrading PostgreSQL SKU for HA Support..." -ForegroundColor Yellow
az postgres flexible-server update --resource-group $RESOURCE_GROUP --name $DB_SERVER --sku-name Standard_D2s_v3 --tier GeneralPurpose
Write-Host "PostgreSQL SKU upgraded." -ForegroundColor Green

# 5. PostgreSQL HA & Geo-Backup
Write-Host "`n[5/5] Enabling PostgreSQL HA and Geo-redundant Backup..." -ForegroundColor Yellow
az postgres flexible-server update --resource-group $RESOURCE_GROUP --name $DB_SERVER --high-availability ZoneRedundant --geo-redundant-backup Enabled --yes
Write-Host "PostgreSQL HA and Geo-Backup enabled." -ForegroundColor Green

Write-Host "`n--- All Recommendations Applied ---" -ForegroundColor Cyan
Write-Host "Note: It may take 24-48 hours for Azure Advisor to reflect these changes." -ForegroundColor Gray
