# setup_vps_env.ps1
# Automates the setup of the Astrology App environment on a fresh Windows VPS

Write-Host "Starting VPS Environment Setup..." -ForegroundColor Cyan

# 1. Install Chocolatey (Package Manager)
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
} else {
    Write-Host "Chocolatey already installed." -ForegroundColor Green
}

# 2. Install Tools via Chocolatey
Write-Host "Installing Python, Git, VS Code, and Cloudflared..." -ForegroundColor Yellow
choco install python --version=3.11.0 -y
choco install git -y
choco install vscode -y
choco install cloudflared -y

# Refreshennv to get new PATH variables
Import-Module $env:ProgramData\chocolatey\helpers\chocolateyProfile.psm1
refreshenv

# 3. Setup OpenSSH Server (For Remote Management)
Write-Host "Setting up OpenSSH Server..." -ForegroundColor Yellow
# Install OpenSSH (if not present)
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# Start Service
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'

# Open Firewall for SSH (Port 22)
if (-not (Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
}

Write-Host "SSH Server Configured. You can now SSH into this machine." -ForegroundColor Green

# 4. Setup Python Virtual Environment (Optional but recommended, skipping for simplicity on dedicated VPS)
# We will install directly to global python for this single-purpose server user
Write-Host "Installing Python Dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r ..\..\requirements.txt

Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "Action Required: Copy your .env file to the project root before running the server." -ForegroundColor Magenta
