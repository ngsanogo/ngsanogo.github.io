# Setup script for pre-commit hooks
# Run this once to set up automatic markdown formatting

Write-Host "Setting up pre-commit hooks for markdown files..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python first." -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "✓ Virtual environment created at .venv" -ForegroundColor Green
} else {
    Write-Host "`n✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1

# Install pre-commit
Write-Host "`nInstalling pre-commit in virtual environment..." -ForegroundColor Yellow
pip install pre-commit

# Install the git hook scripts
Write-Host "`nInstalling git hooks..." -ForegroundColor Yellow
pre-commit install

# Run against all files (optional first run)
$runAll = Read-Host "`nDo you want to run pre-commit on all existing files now? (y/n)"
if ($runAll -eq 'y' -or $runAll -eq 'Y') {
    Write-Host "`nRunning pre-commit on all files..." -ForegroundColor Yellow
    pre-commit run --all-files
}

Write-Host "`n✓ Pre-commit setup complete!" -ForegroundColor Green
Write-Host "`nNow every time you commit, your markdown files will be automatically formatted." -ForegroundColor Cyan
Write-Host "`nTo manually run pre-commit:" -ForegroundColor Cyan
Write-Host "  .\.venv\Scripts\Activate.ps1   # Activate virtual environment first" -ForegroundColor White
Write-Host "  pre-commit run --all-files     # Run on all files" -ForegroundColor White
Write-Host "  pre-commit run                 # Run on staged files" -ForegroundColor White
Write-Host "`nNote: Virtual environment is at .venv/ (add to .gitignore)" -ForegroundColor Yellow
