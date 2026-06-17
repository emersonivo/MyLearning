#!/bin/bash
# Quick setup script for DOCX to PDF converters

echo "======================================"
echo "DOCX to PDF Converter Setup"
echo "======================================"
echo

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
echo "Checking Python installation..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Found: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command_exists python; then
    PYTHON_VERSION=$(python --version)
    echo "✓ Found: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    echo "✗ Python not found! Please install Python 3.6 or higher."
    exit 1
fi
echo

# Check LibreOffice
echo "Checking LibreOffice installation..."
if command_exists libreoffice; then
    LO_VERSION=$(libreoffice --version 2>&1 | head -n1)
    echo "✓ Found: $LO_VERSION"
    LO_INSTALLED=true
elif command_exists soffice; then
    LO_VERSION=$(soffice --version 2>&1 | head -n1)
    echo "✓ Found: $LO_VERSION"
    LO_INSTALLED=true
else
    echo "✗ LibreOffice not found!"
    echo
    echo "Please install LibreOffice:"
    echo
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "  Ubuntu/Debian: sudo apt-get install libreoffice"
        echo "  Fedora/RHEL:   sudo dnf install libreoffice"
        echo "  Arch:          sudo pacman -S libreoffice-fresh"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  macOS: brew install --cask libreoffice"
    fi
    echo "  Or download from: https://www.libreoffice.org/download"
    echo
    LO_INSTALLED=false
fi
echo

# Make scripts executable
echo "Making scripts executable..."
chmod +x docx_to_pdf.py 2>/dev/null && echo "✓ docx_to_pdf.py"
chmod +x simple_docx_to_pdf.py 2>/dev/null && echo "✓ simple_docx_to_pdf.py"
chmod +x test_converters.py 2>/dev/null && echo "✓ test_converters.py"
echo

# Optional: Install docx2pdf
echo "Optional: Install docx2pdf library? (for simple_docx_to_pdf.py) [y/N]"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Installing docx2pdf..."
    $PYTHON_CMD -m pip install docx2pdf
    echo
fi

# Optional: Install python-docx for test script
echo "Optional: Install python-docx? (for creating test documents) [y/N]"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Installing python-docx..."
    $PYTHON_CMD -m pip install python-docx
    echo
fi

# Summary
echo "======================================"
echo "Setup Summary"
echo "======================================"
echo "Python:      ✓ Installed"
echo "LibreOffice: $([ "$LO_INSTALLED" = true ] && echo "✓ Installed" || echo "✗ Not installed")"
echo
echo "Available scripts:"
echo "  1. docx_to_pdf.py        - Main converter (recommended)"
echo "  2. simple_docx_to_pdf.py - Simple alternative"
echo "  3. test_converters.py    - Test suite"
echo
echo "Quick test:"
echo "  $PYTHON_CMD test_converters.py"
echo
echo "Usage examples:"
echo "  $PYTHON_CMD docx_to_pdf.py document.docx"
echo "  $PYTHON_CMD docx_to_pdf.py folder/ --batch"
echo
echo "See README.md for complete documentation."
echo "======================================"
