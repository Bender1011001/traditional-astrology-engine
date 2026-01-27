# Astrology Project Deployment & Security Script

Write-Host "--- Astrology Project Deployment & Security ---" -ForegroundColor Cyan

# 1. Security Check: Firewall
Write-Host "[1/3] Configuring Firewall..." -ForegroundColor Yellow
$RuleName = "Block External Astrology Port"
if (Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue) {
    Write-Host "Firewall rule already exists." -ForegroundColor Green
} else {
    try {
        New-NetFirewallRule -DisplayName $RuleName -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Block -Description "Blocks external access to the local astrology backend (port 8000). Access is only permitted via Localhost (Cloudflare Tunnel)."
        Write-Host "Firewall rule created: Public access to port 8000 is now BLOCKED." -ForegroundColor Green
    } catch {
        Write-Host "Failed to create firewall rule. Ensure you are running as Administrator." -ForegroundColor Red
    }
}

# 2. Cloudflare Tunnel Setup
Write-Host "`n[2/3] Checking Cloudflare Tunnel (cloudflared)..." -ForegroundColor Yellow
if (!(Get-Command cloudflared -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: cloudflared not found in PATH. Please install it from: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/install-run/" -ForegroundColor Red
    return
}

$ConfigPath = Join-Path $PWD "cloudflared_config.yml"
$CredentialsDir = Join-Path $PWD ".cloudflared"

if (!(Test-Path $CredentialsDir)) {
    New-Item -ItemType Directory -Path $CredentialsDir | Out-Null
}

Write-Host "Next steps for you:" -ForegroundColor White
Write-Host "1. Run: cloudflared tunnel login" -ForegroundColor Cyan
Write-Host "2. Run: cloudflared tunnel create astrology-tunnel" -ForegroundColor Cyan
Write-Host "3. Run: cloudflared tunnel route dns astrology-tunnel traditional-astrology.com" -ForegroundColor Cyan
Write-Host "4. Move the generated JSON credential file to: $CredentialsDir\tunnel-credentials.json" -ForegroundColor Cyan

# 3. Running the App
Write-Host "`n[3/3] Backend Status..." -ForegroundColor Yellow
$Port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($Port8000) {
    Write-Host "Backend is already RUNNING on port 8000." -ForegroundColor Green
} else {
    Write-Host "Backend is NOT running. Run 'python src/api.py' to start it." -ForegroundColor Red
}

Write-Host "`nOnce configured, start the tunnel with:" -ForegroundColor White
Write-Host "cloudflared tunnel --config cloudflared_config.yml run" -ForegroundColor Cyan
