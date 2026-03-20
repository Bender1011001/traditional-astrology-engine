#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Deploy Astrology Engine to Google Cloud Run.

.DESCRIPTION
    This script deploys the astrology engine to Cloud Run using source-based
    deployment (Cloud Build builds the Docker image from Dockerfile automatically).

.PARAMETER ProjectId
    Google Cloud project ID to deploy to.

.PARAMETER Region
    Cloud Run region (default: us-central1).

.PARAMETER ServiceName
    Cloud Run service name (default: astrology-engine).

.EXAMPLE
    .\deploy_gcp.ps1 -ProjectId "my-project-123"
    .\deploy_gcp.ps1 -ProjectId "my-project-123" -Region "us-east1"
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$ProjectId = "",

    [Parameter(Mandatory=$false)]
    [string]$Region = "us-central1",

    [Parameter(Mandatory=$false)]
    [string]$ServiceName = "astrology-engine"
)

$ErrorActionPreference = "Stop"

# ── Preflight Checks ──────────────────────────────────────────────────────────
Write-Host "`n🔍 Preflight checks..." -ForegroundColor Cyan

# Check gcloud
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "❌ gcloud CLI not found. Install: https://cloud.google.com/sdk/install" -ForegroundColor Red
    exit 1
}

# Check authentication
$account = gcloud auth list --filter="status:ACTIVE" --format="value(account)" 2>$null
if (-not $account) {
    Write-Host "❌ Not authenticated. Run: gcloud auth login" -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ Authenticated as: $account" -ForegroundColor Green

# Get or set project
if (-not $ProjectId) {
    $ProjectId = gcloud config get-value project 2>$null
}
if (-not $ProjectId) {
    Write-Host "❌ No project set. Use -ProjectId or run: gcloud config set project PROJECT_ID" -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ Project: $ProjectId" -ForegroundColor Green
Write-Host "  ✅ Region: $Region" -ForegroundColor Green
Write-Host "  ✅ Service: $ServiceName" -ForegroundColor Green

# ── Enable Required APIs ──────────────────────────────────────────────────────
Write-Host "`n⚙️  Enabling required APIs..." -ForegroundColor Cyan
$apis = @(
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com"
)
foreach ($api in $apis) {
    gcloud services enable $api --project=$ProjectId 2>$null
    Write-Host "  ✅ $api" -ForegroundColor Green
}

# ── Check for .env file (extract required env vars) ───────────────────────────
Write-Host "`n📋 Checking environment variables..." -ForegroundColor Cyan

$envFile = Join-Path $PSScriptRoot ".env"
$envVars = @{}
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
            $parts = $line -split "=", 2
            $envVars[$parts[0].Trim()] = $parts[1].Trim().Trim('"').Trim("'")
        }
    }
    Write-Host "  ✅ Found .env with $($envVars.Count) variables" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  No .env file found. You'll need to set env vars manually." -ForegroundColor Yellow
    Write-Host "     Required: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, JWT_SECRET, SENDER_EMAIL" -ForegroundColor Yellow
}

# ── Deploy to Cloud Run ───────────────────────────────────────────────────────
Write-Host "`n🚀 Deploying to Cloud Run ($Region)..." -ForegroundColor Cyan
Write-Host "   This will build the Docker image via Cloud Build and deploy it." -ForegroundColor Gray
Write-Host "   First deploy takes 3-5 minutes (building C extensions)." -ForegroundColor Gray

$deployArgs = @(
    "run", "deploy", $ServiceName,
    "--source", ".",
    "--project", $ProjectId,
    "--region", $Region,
    "--platform", "managed",
    "--allow-unauthenticated",
    "--memory", "1Gi",
    "--cpu", "1",
    "--min-instances", "0",
    "--max-instances", "3",
    "--timeout", "300",
    "--port", "8080"
)

# Add env vars if we have them
if ($envVars.Count -gt 0) {
    $envString = ($envVars.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ","
    $deployArgs += @("--set-env-vars", $envString)
}

gcloud @deployArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Deployment successful!" -ForegroundColor Green
    
    # Get the service URL
    $url = gcloud run services describe $ServiceName --region=$Region --project=$ProjectId --format="value(status.url)" 2>$null
    Write-Host "`n🌐 Service URL: $url" -ForegroundColor Cyan
    Write-Host "📖 API Docs:    $url/docs" -ForegroundColor Cyan
    
    Write-Host "`n📝 Next steps:" -ForegroundColor Yellow
    Write-Host "   1. Set env vars if not done: gcloud run services update $ServiceName --region=$Region --set-env-vars KEY=VALUE" -ForegroundColor White
    Write-Host "   2. Map custom domain: gcloud beta run domain-mappings create --service=$ServiceName --domain=traditional-astrology.com --region=$Region" -ForegroundColor White
    Write-Host "   3. Update Stripe webhook URL to: $url/api/v1/billing/webhook" -ForegroundColor White
    Write-Host "   4. Update DNS to point to Cloud Run" -ForegroundColor White
} else {
    Write-Host "`n❌ Deployment failed. Check the logs above." -ForegroundColor Red
    exit 1
}
