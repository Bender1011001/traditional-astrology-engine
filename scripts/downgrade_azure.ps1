# Azure Downgrade Script for Astrology Engine
# This script reverts high-cost infrastructure to economical tiers.
# Estimated Monthly Cost: $30 (down from $400)

$RESOURCE_GROUP = "astrology-rg-migration"
$ACR_NAME = "astrologyacr3391"
$PLAN_NAME = "astrology-plan-central"
$DB_SERVER = "astrology-db-central-7387"

Write-Host "--- Initiating Azure Cost Downgrade ---" -ForegroundColor Cyan

# 1. ACR Downgrade
Write-Host "`n[1/3] Removing ACR Replications and Downgrading to Basic..." -ForegroundColor Yellow
# Remove replications (Premium feature)
$replications = az acr replication list --registry $ACR_NAME --query "[].location" -o tsv
foreach ($loc in $replications) {
    if ($loc -ne "centralus") {
        Write-Host "Removing replication in $loc..."
        az acr replication delete --registry $ACR_NAME --location $loc --yes
    }
}
# Downgrade SKU
az acr update --name $ACR_NAME --sku Basic
Write-Host "ACR Downgraded to Basic." -ForegroundColor Green

# 2. App Service Plan Downgrade
Write-Host "`n[2/3] Downgrading App Service Plan to B1..." -ForegroundColor Yellow
# B1 is the cheapest "Basic" plan for Linux that supports Always On (if needed) and no artificial CPU limits.
# F1 (Free) is also an option but has tight limits.
az appservice plan update --name $PLAN_NAME --resource-group $RESOURCE_GROUP --sku B1
# Force-disable Zone Redundancy if set
try {
    az appservice plan update --name $PLAN_NAME --resource-group $RESOURCE_GROUP --set zoneRedundant=false
} catch {
    Write-Host "Note: Plan was already non-zone-redundant or could not be toggled."
}
Write-Host "App Service Plan Downgraded to B1." -ForegroundColor Green

# 3. PostgreSQL Downgrade
Write-Host "`n[3/3] Downgrading PostgreSQL to Burstable Tier..." -ForegroundColor Yellow
# Disable HA First (Critical)
az postgres flexible-server update --resource-group $RESOURCE_GROUP --name $DB_SERVER --high-availability Disabled --yes
# Disable Geo-Redundant Backup
az postgres flexible-server update --resource-group $RESOURCE_GROUP --name $DB_SERVER --geo-redundant-backup Disabled --yes
# Downgrade SKU to Burstable B1ms
az postgres flexible-server update --resource-group $RESOURCE_GROUP --name $DB_SERVER --sku-name Standard_B1ms --tier Burstable
Write-Host "PostgreSQL Downgraded to Burstable B1ms." -ForegroundColor Green

Write-Host "`n--- Downgrade Sequence Complete ---" -ForegroundColor Cyan
Write-Host "Resources are now at minimal development cost tiers." -ForegroundColor Gray
