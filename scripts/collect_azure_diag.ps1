$APP_NAME = "astrology-engine-central-7387"
$RG = "astrology-rg-migration"
$ACR = "astrologyacr3391"

Write-Host "Getting WebApp Settings..."
$settings = az webapp config appsettings list --name $APP_NAME --resource-group $RG --output json
$settings | Out-File -FilePath diag_azure_settings.json -Encoding utf8

Write-Host "Getting WebApp Container Config..."
$container = az webapp config container show --name $APP_NAME --resource-group $RG --output json
$container | Out-File -FilePath diag_azure_container.json -Encoding utf8

Write-Host "Getting ACR Credentials..."
$creds = az acr credential show --name $ACR --output json
$creds | Out-File -FilePath diag_acr_creds.json -Encoding utf8

Write-Host "Done."
