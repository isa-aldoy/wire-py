#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Automated setup and execution script for the Python Network Scanner (rapid-scan.py).
    Installs Python, Nmap (with Npcap), Git, Python dependencies, creates config files,
    and then runs the Python scanner.

.DESCRIPTION
    This script performs the following actions:
    1. Checks for Administrator privileges.
    2. Defines necessary variables and file contents.
    3. Checks for and attempts to install Python 3 using winget, with a fallback to downloading the official installer.
    4. Checks for and attempts to install Nmap (with Npcap) using winget, with a fallback.
    5. (Optional) Checks for and attempts to install Git using winget (if script is to be fetched from Git).
    6. Creates a project directory.
    7. Downloads (or copies) the Python scanner script (rapid-scan.py) and requirements.txt.
    8. Creates default config.json, users.txt, and pass.txt.
    9. Sets up a Python virtual environment and installs dependencies.
    10. Runs the Python network scanner script (rapid-scan.py).

.NOTES
    - Must be run as Administrator.
    - Internet connection required for downloads if $DownloadFiles is $true.
    - PowerShell Execution Policy might need adjustment (e.g., Set-ExecutionPolicy RemoteSigned -Scope Process -Force).
    - Replace placeholder URLs for Python script and requirements.txt if using download method.
#>

# --- Initial Check for Administrator Privileges ---
Write-Host "Checking for Administrator privileges..."
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Administrator privileges are required to run this script. Please re-run as Administrator."
    Read-Host "Press Enter to exit..."
    exit 1
}
Write-Host "Administrator privileges confirmed." -ForegroundColor Green

# --- Script Configuration ---
$ProjectName = "RapidNetworkScanner" # Updated project name slightly for clarity
$ProjectDir = Join-Path $env:USERPROFILE "Documents\$ProjectName" # Or choose a different base path like C:\Tools
$VenvName = "venv_scanner"
$PythonScriptName = "rapid-scan.py" # MODIFIED: Python script name

# Placeholder URLs - REPLACE THESE with your actual raw file URLs (e.g., from GitHub)
$PythonScriptUrl = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/rapid-scan.py" # MODIFIED
$RequirementsUrl = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/requirements.txt"
# If your Python script and requirements.txt are in the same folder as this PowerShell script,
# set $DownloadFiles to $false and ensure they are present.
$DownloadFiles = $false # Set to $false to copy local files instead of downloading

# Python and Nmap target versions (winget might pick latest stable)
$PythonWingetId = "Python.Python.3.9" # Example, adjust as needed (e.g., Python.Python.3.11)
$NmapWingetId = "Nmap.Nmap"
$GitWingetId = "Git.Git"

# --- Helper Functions ---
function Test-CommandExists {
    param($command)
    return (Get-Command $command -ErrorAction SilentlyContinue) -ne $null
}

function Install-WithWinget {
    param(
        [string]$PackageName,
        [string]$WingetId
    )
    Write-Host "[INFO] Attempting to install $PackageName using winget..."
    try {
        winget install -e --id $WingetId --accept-source-agreements --accept-package-agreements
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[SUCCESS] $PackageName installed successfully via winget." -ForegroundColor Green
            return $true
        } else {
            Write-Warning "[WARNING] winget installation for $PackageName may have failed (Exit code: $LASTEXITCODE)."
            return $false
        }
    } catch {
        Write-Warning "[WARNING] winget command failed for $PackageName. $($_.Exception.Message)"
        return $false
    }
}

function Download-File {
    param(
        [string]$Url,
        [string]$OutFile
    )
    Write-Host "[INFO] Downloading $OutFile from $Url..."
    try {
        Invoke-WebRequest -Uri $Url -OutFile $OutFile -UseBasicParsing
        if (Test-Path $OutFile) {
            Write-Host "[SUCCESS] Downloaded $OutFile successfully." -ForegroundColor Green
            return $true
        } else {
            Write-Warning "[WARNING] Failed to download $OutFile."
            return $false
        }
    } catch {
        Write-Warning "[WARNING] Error downloading $OutFile. $($_.Exception.Message)"
        return $false
    }
}

# --- Ensure Winget is available ---
$WingetAvailable = Test-CommandExists winget
if ($WingetAvailable) {
    Write-Host "[INFO] winget package manager found." -ForegroundColor Green
} else {
    Write-Warning "[WARNING] winget package manager not found. Installations for Python/Nmap/Git will rely on downloading official installers (may require more user interaction) or manual installation."
}

# --- 1. Python Installation ---
Write-Host "`n--- Checking/Installing Python 3 ---"
$PythonInstalled = $false
if (Test-CommandExists python) {
    $pyVersion = (python --version 2>&1)
    if ($pyVersion -match "Python 3") {
        Write-Host "[INFO] Python 3 already installed: $pyVersion" -ForegroundColor Green
        $PythonInstalled = $true
    }
}

if (-not $PythonInstalled) {
    if ($WingetAvailable) {
        if (Install-WithWinget "Python 3" $PythonWingetId) {
            # Refresh PATH environment variables for the current session
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            $PythonInstalled = (Test-CommandExists python) # Re-check
            if (-not $PythonInstalled) { Write-Warning "Python might be installed but not yet in current session's PATH. A new PowerShell session might be required, or check PATH manually."}
        }
    }
    if (-not $PythonInstalled) { # Fallback if winget failed or not available
        Write-Warning "[ACTION] Python 3 not found. Attempting to download official installer."
        $PythonInstallerUrl = "https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe" # Example: Python 3.9.13, find latest appropriate version
        $PythonInstallerPath = Join-Path $env:TEMP "python_installer.exe"
        if (Download-File $PythonInstallerUrl $PythonInstallerPath) {
            Write-Host "[ACTION] Python installer downloaded. Starting setup..."
            Write-Host "         Please ensure you check 'Add Python to PATH' during installation."
            Start-Process -FilePath $PythonInstallerPath -Wait
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            if ((Test-CommandExists python) -and ((python --version 2>&1) -match "Python 3")) { $PythonInstalled = $true }
        }
    }
}
if (-not $PythonInstalled) {
    Write-Error "Python 3 installation failed or not added to PATH. Please install Python 3 manually and ensure it's in PATH."
    Read-Host "Press Enter to exit..."; exit 1
}

# --- 2. Nmap (and Npcap) Installation ---
Write-Host "`n--- Checking/Installing Nmap (with Npcap) ---"
$NmapInstalled = $false
if (Test-CommandExists nmap) {
    Write-Host "[INFO] Nmap already installed." -ForegroundColor Green
    $NmapInstalled = $true
} else {
    if ((Test-Path (Join-Path $env:ProgramFiles "Nmap\nmap.exe")) -or `
        (Test-Path (Join-Path ${env:ProgramFiles(x86)} "Nmap\nmap.exe"))) {
        Write-Host "[INFO] Nmap found in Program Files. Ensure it's in PATH if 'nmap' command fails." -ForegroundColor Green
        $NmapInstalled = $true 
    }
}

if (-not $NmapInstalled) {
    if ($WingetAvailable) {
        if (Install-WithWinget "Nmap" $NmapWingetId) {
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            $NmapInstalled = (Test-CommandExists nmap)
            if (-not $NmapInstalled) { Write-Warning "Nmap might be installed but not yet in current session's PATH. A new PowerShell session might be required, or check PATH manually."}
        }
    }
    if (-not $NmapInstalled) { # Fallback
        Write-Warning "[ACTION] Nmap not found. Attempting to download official installer."
        $NmapInstallerUrl = "https://nmap.org/dist/nmap-7.95-setup.exe" # Check nmap.org for the latest stable version
        $NmapInstallerPath = Join-Path $env:TEMP "nmap_installer.exe"
        if (Download-File $NmapInstallerUrl $NmapInstallerPath) {
            Write-Host "[ACTION] Nmap installer downloaded. Starting setup..."
            Write-Host "         Please ensure Npcap is included during installation."
            Start-Process -FilePath $NmapInstallerPath -Wait
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            if (Test-CommandExists nmap) { $NmapInstalled = $true }
        }
    }
}
if (-not $NmapInstalled) {
    Write-Error "Nmap installation failed or not in PATH. Please install Nmap (with Npcap) manually."
    Read-Host "Press Enter to exit..."; exit 1
}

# --- 3. Git Installation (Optional) ---
# (Keeping this section commented as per previous script, enable if needed)
# Write-Host "`n--- Checking/Installing Git ---"
# if (-not (Test-CommandExists git)) {
#     if ($WingetAvailable) { Install-WithWinget "Git" $GitWingetId }
#     if (-not (Test-CommandExists git)) { Write-Warning "Git not installed. If you need to clone a repository, please install Git manually." }
# } else { Write-Host "[INFO] Git already installed." -ForegroundColor Green }

# --- 4. Create Project Directory ---
Write-Host "`n--- Setting up Project Directory: $ProjectDir ---"
if (-not (Test-Path $ProjectDir)) {
    New-Item -ItemType Directory -Force -Path $ProjectDir | Out-Null
    Write-Host "[SUCCESS] Created project directory: $ProjectDir" -ForegroundColor Green
} else {
    Write-Host "[INFO] Project directory already exists: $ProjectDir"
}
Set-Location $ProjectDir

# --- 5. Get Python Script and requirements.txt ---
Write-Host "`n--- Obtaining Python script ($PythonScriptName) and requirements.txt ---"
if ($DownloadFiles) {
    if (-not (Download-File $PythonScriptUrl $PythonScriptName)) {
        Write-Error "Failed to download Python script '$PythonScriptName'. Exiting." # MODIFIED message
        Read-Host "Press Enter to exit..."; exit 1
    }
    if (-not (Download-File $RequirementsUrl "requirements.txt")) {
        Write-Error "Failed to download requirements.txt. Exiting."
        Read-Host "Press Enter to exit..."; exit 1
    }
} else {
    Write-Host "[INFO] Attempting to copy local files..."
    $SourceDir = Split-Path $MyInvocation.MyCommand.Path # Directory of the PowerShell script
    $LocalPythonScript = Join-Path $SourceDir $PythonScriptName
    $LocalRequirements = Join-Path $SourceDir "requirements.txt"

    if (Test-Path $LocalPythonScript) {
        Copy-Item $LocalPythonScript -Destination .
        Write-Host "[SUCCESS] Copied $PythonScriptName" -ForegroundColor Green
    } else {
        Write-Error "Local file $PythonScriptName not found in script directory '$SourceDir'. Exiting." # MODIFIED message
        Read-Host "Press Enter to exit..."; exit 1
    }
    if (Test-Path $LocalRequirements) {
        Copy-Item $LocalRequirements -Destination .
        Write-Host "[SUCCESS] Copied requirements.txt" -ForegroundColor Green
    } else {
        Write-Error "Local file requirements.txt not found in script directory '$SourceDir'. Exiting. Please create it."
        Read-Host "Press Enter to exit..."; exit 1
    }
}

# --- 6. Create Default Files (config.json, users.txt, pass.txt) ---
Write-Host "`n--- Creating default configuration files ---"
# config.json (content remains the same)
@"
{
  "nmap_scan_mode": "aggressive",
  "local_network_subnet_override": null,
  "nmap_arguments_custom": "-T4 -A -Pn --script=default,vuln,http-enum,banner",
  "enable_brute_force": false,
  "brute_force_scripts": "ftp-brute,ssh-brute,telnet-brute",
  "brute_force_userdb": "users.txt",
  "brute_force_passdb": "pass.txt",
  "brute_force_stop_on_success": true,
  "nmap_scan_timeout_per_host": 700,
  "max_nmap_threads": 5,
  "log_file": "network_scanner_advanced.log",
  "log_level": "INFO",
  "credentials": {
    "ssh": { "username": "", "password": "", "key_path": "" },
    "smb": { "username": "", "password": "", "domain": "" }
  },
  "external_db_urls": {
    "nvd_cve": "https://nvd.nist.gov/vuln/detail/",
    "exploitdb_search": "https://www.exploit-db.com/search?q="
  }
}
"@ | Set-Content -Path "config.json" -Encoding UTF8
Write-Host "[SUCCESS] Created default config.json" -ForegroundColor Green

# users.txt
"admin`r`nroot`r`ntest" | Set-Content -Path "users.txt" -Encoding UTF8
Write-Host "[SUCCESS] Created default users.txt" -ForegroundColor Green

# pass.txt
"password`r`n123456`r`nadmin" | Set-Content -Path "pass.txt" -Encoding UTF8
Write-Host "[SUCCESS] Created default pass.txt" -ForegroundColor Green

# scan_outputs directory
$OutputDir = "scan_outputs"
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
    Write-Host "[SUCCESS] Created '$OutputDir' directory." -ForegroundColor Green
}

# --- 7. Setup Python Virtual Environment & Install Dependencies ---
Write-Host "`n--- Setting up Python virtual environment ($VenvName) ---"
try {
    python -m venv $VenvName
    Write-Host "[SUCCESS] Virtual environment '$VenvName' created." -ForegroundColor Green
} catch {
    Write-Error "Failed to create Python virtual environment. $($_.Exception.Message)"
    Read-Host "Press Enter to exit..."; exit 1
}

Write-Host "[INFO] Installing Python dependencies from requirements.txt..."
$PipExe = Join-Path $VenvName "Scripts\pip.exe"
if (-not (Test-Path $PipExe)) { $PipExe = Join-Path $VenvName "Scripts\pip3.exe" } 

if (Test-Path $PipExe) {
    try {
        & $PipExe install -r requirements.txt
        Write-Host "[SUCCESS] Python dependencies installed." -ForegroundColor Green
    } catch {
        Write-Error "Failed to install Python dependencies using $PipExe. $($_.Exception.Message)"
        Write-Host "Try running manually: '$ProjectDir\$VenvName\Scripts\Activate.ps1' then 'pip install -r requirements.txt'"
        Read-Host "Press Enter to exit..."; exit 1
    }
} else {
    Write-Error "pip.exe (or pip3.exe) not found in virtual environment. Cannot install dependencies."
    Read-Host "Press Enter to exit..."; exit 1
}

# --- 8. Run the Python Scanner Script ---
Write-Host "`n--- Setup Complete. Preparing to run $PythonScriptName ---" # MODIFIED message
Write-Host "Please review 'config.json', 'users.txt', and 'pass.txt' in '$ProjectDir' and customize them if needed."
Write-Host "The Python script ($PythonScriptName) will now be executed." # MODIFIED message
Read-Host "Press Enter to start the Python network scanner..."

$PythonExe = Join-Path $VenvName "Scripts\python.exe"
if (Test-Path $PythonExe) {
    Write-Host "[INFO] Running: $PythonExe $PythonScriptName" # MODIFIED message
    Write-Host "Output from the Python script will follow:"
    Write-Host "--------------------------------------------"
    try {
        # To pass arguments to the Python script from PowerShell, list them after the script name
        # Example: & $PythonExe $PythonScriptName "192.168.1.0/24"
        # Example: & $PythonExe $PythonScriptName $args # If PowerShell script takes args
        & $PythonExe $PythonScriptName # Runs without additional arguments by default
        Write-Host "--------------------------------------------"
        Write-Host "[SUCCESS] Python script ($PythonScriptName) finished execution." -ForegroundColor Green # MODIFIED message
    } catch {
        Write-Error "Error running the Python script ($PythonScriptName): $($_.Exception.Message)" # MODIFIED message
    }
} else {
    Write-Error "python.exe not found in virtual environment. Cannot run the script."
    Write-Host "To run manually: '$ProjectDir\$VenvName\Scripts\Activate.ps1' then 'python $PythonScriptName'" # MODIFIED message
}

Read-Host "PowerShell setup script finished. Press Enter to exit..."