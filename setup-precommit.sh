#!/bin/bash
# Setup script for pre-commit hooks (Linux/Mac)
# Run this once to set up automatic markdown formatting

echo "Setting up pre-commit hooks for markdown files..."

# Check if Python is installed
if command -v python3 &> /dev/null; then
    echo "✓ Python found: $(python3 --version)"
else
    echo "✗ Python not found. Please install Python first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo -e "\nCreating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created at .venv"
else
    echo -e "\n✓ Virtual environment already exists"
fi

# Activate virtual environment
echo -e "\nActivating virtual environment..."
source .venv/bin/activate

# Install pre-commit
echo -e "\nInstalling pre-commit in virtual environment..."
pip install pre-commit

# Install the git hook scripts
echo -e "\nInstalling git hooks..."
pre-commit install

# Run against all files (optional first run)
read -p "Do you want to run pre-commit on all existing files now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\nRunning pre-commit on all files..."
    pre-commit run --all-files
fi

echo -e "\n✓ Pre-commit setup complete!"
echo -e "\nNow every time you commit, your markdown files will be automatically formatted."
echo -e "\nTo manually run pre-commit:"
echo "  source .venv/bin/activate     # Activate virtual environment first"
echo "  pre-commit run --all-files    # Run on all files"
echo "  pre-commit run                # Run on staged files"
echo -e "\nNote: Virtual environment is at .venv/ (add to .gitignore)"
