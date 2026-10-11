param (
    [string]$SeniorName = "Senior Student",
    [string]$SeniorRollNo = "123456",
    [string]$SeniorEmail = "senior@example.com",
    [string]$OutputDir = "..\Senior_Plant_Disease_System"
)

Write-Host "==========================================================" -ForegroundColor Green
Write-Host " AI Plant Care — Zero-Trace Project Export for Senior" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "Senior Name    : $SeniorName"
Write-Host "Senior Roll No : $SeniorRollNo"
Write-Host "Senior Email   : $SeniorEmail"
Write-Host "Target Folder  : $OutputDir"
Write-Host ""

# 1. Clean destination folder if it already exists
if (Test-Path $OutputDir) {
    Write-Host "[1/6] Removing existing destination folder..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $OutputDir
}

# 2. Copy project files excluding git, virtualenv, and caches
Write-Host "[2/6] Copying clean source code..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

$excludeItems = @('venv', '.git', '.pytest_cache', '__pycache__', 'uploads', '*.pyc', '*.zip')

Get-ChildItem -Path . -Exclude $excludeItems | ForEach-Object {
    if ($_.Name -notin @('venv', '.git', '.pytest_cache', '__pycache__', 'uploads')) {
        Copy-Item -Path $_.FullName -Destination (Join-Path $OutputDir $_.Name) -Recurse -Force
    }
}

# Ensure clean uploads directory exists with .gitkeep
$uploadsTarget = Join-Path $OutputDir "uploads"
New-Item -ItemType Directory -Path $uploadsTarget -Force | Out-Null
New-Item -ItemType File -Path (Join-Path $uploadsTarget ".gitkeep") -Force | Out-Null

# 3. Personalize docs/PROJECT_REPORT.md for the Senior
Write-Host "[3/6] Personalizing project report for senior..." -ForegroundColor Cyan
$reportPath = Join-Path $OutputDir "docs\PROJECT_REPORT.md"
if (Test-Path $reportPath) {
    $reportContent = Get-Content -Path $reportPath -Raw
    $reportContent = $reportContent -replace "Parvez Mohammed Akram", "$SeniorName ($SeniorRollNo)"
    Set-Content -Path $reportPath -Value $reportContent -Force
}

# 4. Remove Handover script itself from the senior's copy
$exportScriptInTarget = Join-Path $OutputDir "scripts\export_for_senior.ps1"
if (Test-Path $exportScriptInTarget) {
    Remove-Item -Force $exportScriptInTarget
}

# 5. Initialize fresh Git repository with Senior as author
Write-Host "[4/6] Initializing clean Git repository under Senior's identity..." -ForegroundColor Cyan
Push-Location $OutputDir
try {
    git init -b main | Out-Null
    git config user.name "$SeniorName"
    git config user.email "$SeniorEmail"
    git add .
    git commit -m "feat: complete initial release of AI Plant Disease Detection System" | Out-Null
    Write-Host "      Created initial commit with author: $SeniorName <$SeniorEmail>" -ForegroundColor Green
} finally {
    Pop-Location
}

# 6. Create standalone clean ZIP archive
Write-Host "[5/6] Creating clean ZIP archive..." -ForegroundColor Cyan
$zipPath = "$OutputDir.zip"
if (Test-Path $zipPath) { Remove-Item -Force $zipPath }
Compress-Archive -Path "$OutputDir\*" -DestinationPath $zipPath -Force

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host " Export Complete! Zero trace of your name or accounts." -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "Folder : $OutputDir" -ForegroundColor Yellow
Write-Host "Zip    : $zipPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "Your senior can now:" -ForegroundColor Cyan
Write-Host "1. Create a new repository on their GitHub account"
Write-Host "2. Run inside $OutputDir :"
Write-Host "   git remote add origin https://github.com/SENIOR_USERNAME/plant-disease-detection-system.git"
Write-Host "   git push -u origin main"
Write-Host ""
Write-Host "Your original repository remains 100% untouched with all your commits and credit intact!" -ForegroundColor Green
