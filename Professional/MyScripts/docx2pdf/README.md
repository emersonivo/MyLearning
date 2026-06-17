# DOCX to PDF Converter

Two Python scripts for converting .docx files to PDF while preserving all formatting, styles, tables, images, and document elements.

## Overview

This package provides two conversion approaches:

1. **`docx_to_pdf.py`** - Direct LibreOffice integration (recommended)
   - No additional Python dependencies
   - Works on all platforms with LibreOffice
   - Better control over conversion process
   - Detailed progress reporting

2. **`simple_docx_to_pdf.py`** - Using docx2pdf library
   - Requires `docx2pdf` pip package
   - Simpler code
   - Uses Microsoft Word on Windows, LibreOffice on Linux/Mac

## Installation

### Option 1: Using docx_to_pdf.py (Recommended)

**Requirements:**
- Python 3.6 or higher
- LibreOffice (free and open source)

**Install LibreOffice:**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install libreoffice

# Fedora/RHEL/CentOS
sudo dnf install libreoffice

# Arch Linux
sudo pacman -S libreoffice-fresh

# macOS (using Homebrew)
brew install --cask libreoffice

# Or download from: https://www.libreoffice.org/download
```

**Windows:**
Download and install from: https://www.libreoffice.org/download

**No Python dependencies needed!**

### Option 2: Using simple_docx_to_pdf.py

**Requirements:**
- Python 3.6 or higher
- docx2pdf library
- LibreOffice (Linux/Mac) or Microsoft Word (Windows)

```bash
pip install docx2pdf
```

On Linux/Mac, also install LibreOffice (see above).

## Usage

### Method 1: docx_to_pdf.py

**Convert a single file:**
```bash
python docx_to_pdf.py document.docx
# Creates: document.pdf (in same directory)
```

**Specify output filename:**
```bash
python docx_to_pdf.py document.docx -o report.pdf
python docx_to_pdf.py document.docx --output /path/to/output.pdf
```

**Convert all .docx files in a directory:**
```bash
python docx_to_pdf.py /path/to/documents --batch
# Creates PDFs in same directory
```

**Batch convert to different output directory:**
```bash
python docx_to_pdf.py /path/to/documents --batch -o /path/to/output
```

**Quiet mode (minimal output):**
```bash
python docx_to_pdf.py document.docx -q
python docx_to_pdf.py document.docx --quiet
```

**Complete options:**
```bash
usage: docx_to_pdf.py [-h] [-o OUTPUT] [--batch] [-q] input

positional arguments:
  input                 Input .docx file or directory (with --batch)

optional arguments:
  -h, --help            Show help message
  -o OUTPUT, --output OUTPUT
                        Output PDF file or directory (for batch mode)
  --batch               Convert all .docx files in the input directory
  -q, --quiet           Suppress verbose output
```

### Method 2: simple_docx_to_pdf.py

**Convert a single file:**
```bash
python simple_docx_to_pdf.py document.docx
# Creates: document.pdf

python simple_docx_to_pdf.py document.docx output.pdf
# Creates: output.pdf
```

**Convert all .docx files in a directory:**
```bash
python simple_docx_to_pdf.py /path/to/documents --all
python simple_docx_to_pdf.py /path/to/documents /path/to/output --all
```

## Features

### Preserves All Formatting

Both scripts preserve:
- ✓ Text formatting (bold, italic, underline, colors)
- ✓ Font families and sizes
- ✓ Headings and styles
- ✓ Paragraphs and line spacing
- ✓ Tables with borders and shading
- ✓ Lists (bulleted and numbered)
- ✓ Images and graphics
- ✓ Headers and footers
- ✓ Page numbers
- ✓ Hyperlinks
- ✓ Table of contents
- ✓ Footnotes and endnotes
- ✓ Comments (as annotations in PDF)
- ✓ Tracked changes (rendered as final)
- ✓ Page layout and margins

### Error Handling

- Validates input files exist and are .docx format
- Checks LibreOffice/Word installation
- Clear error messages
- Exit codes (0 = success, 1 = failure)
- Timeout protection (120 seconds per file)

### Batch Processing

- Process entire directories of .docx files
- Summary statistics
- Individual file success/failure tracking
- Continues on error (doesn't stop batch on single failure)

## Examples

### Example 1: Convert technical documentation
```bash
# Single file with custom output
python docx_to_pdf.py "Technical_Guide.docx" -o "Technical_Guide_v1.0.pdf"
```

### Example 2: Process curriculum documents
```bash
# Convert all curriculum files
python docx_to_pdf.py ./curriculum_docs --batch -o ./curriculum_pdfs
```

### Example 3: Automated workflow
```bash
#!/bin/bash
# Convert all .docx files in current directory
for file in *.docx; do
    python docx_to_pdf.py "$file"
done
```

### Example 4: Python script integration
```python
from pathlib import Path
import subprocess

def convert_docx_to_pdf(docx_file):
    """Convert a docx file to PDF"""
    result = subprocess.run(
        ["python", "docx_to_pdf.py", str(docx_file)],
        capture_output=True,
        text=True
    )
    return result.returncode == 0

# Use it
if convert_docx_to_pdf("report.docx"):
    print("Conversion successful!")
else:
    print("Conversion failed!")
```

## Troubleshooting

### LibreOffice not found

**Problem:** "ERROR: LibreOffice not found!"

**Solution:**
1. Ensure LibreOffice is installed (see Installation section)
2. Check it's in your PATH: `which libreoffice` (Linux/Mac) or `where soffice.exe` (Windows)
3. Try running: `libreoffice --version`

### Permission errors

**Problem:** "Permission denied" errors

**Solution:**
```bash
chmod +x docx_to_pdf.py
# Then run:
./docx_to_pdf.py document.docx
```

### Timeout errors

**Problem:** "Conversion timed out"

**Solution:** Large files may take longer. The default timeout is 120 seconds. For very large files, you can modify the timeout in the script (search for `timeout=120`).

### File format errors

**Problem:** "Input file must be .docx"

**Solution:** Only .docx format is supported. If you have legacy .doc files, convert them first:
```bash
# Using LibreOffice
libreoffice --headless --convert-to docx file.doc
```

### Dependencies for docx2pdf

**Problem:** "ModuleNotFoundError: No module named 'docx2pdf'"

**Solution:**
```bash
pip install docx2pdf
# or
pip3 install docx2pdf
```

## Platform-Specific Notes

### Linux
- Works with any LibreOffice version (tested on 6.x, 7.x, 24.x)
- May need to install additional fonts for best results:
  ```bash
  sudo apt-get install fonts-liberation fonts-crosextra-carlito
  ```

### macOS
- LibreOffice from Homebrew works perfectly
- May need to grant Terminal permissions in System Preferences → Security & Privacy

### Windows
- LibreOffice is recommended over Microsoft Word for automation
- If using docx2pdf with MS Word, ensure Word is properly licensed
- Path to LibreOffice: `C:\Program Files\LibreOffice\program\soffice.exe`

## Performance

**Conversion speeds** (approximate):
- Small document (<10 pages): 1-3 seconds
- Medium document (10-50 pages): 3-10 seconds
- Large document (50-200 pages): 10-30 seconds
- Very large document (200+ pages): 30-60 seconds

**Batch processing:**
- 10 documents: ~30-60 seconds
- 100 documents: ~5-15 minutes

## Technical Details

### How it works

**docx_to_pdf.py:**
1. Locates LibreOffice installation
2. Invokes LibreOffice in headless mode
3. Uses LibreOffice's native conversion engine
4. Ensures all formatting is preserved through native rendering

**simple_docx_to_pdf.py:**
1. Uses docx2pdf library as wrapper
2. On Windows: Uses COM interface to Microsoft Word
3. On Linux/Mac: Uses LibreOffice via subprocess
4. Delegates actual conversion to the office application

### Comparison

| Feature | docx_to_pdf.py | simple_docx_to_pdf.py |
|---------|----------------|----------------------|
| Dependencies | None (just LibreOffice) | Requires pip install |
| Code complexity | Medium | Simple |
| Progress reporting | Detailed | Basic |
| Error handling | Comprehensive | Basic |
| Batch processing | Full-featured | Basic |
| Platform support | All | All (with caveats) |
| Recommended for | Production use | Quick scripts |

## License

These scripts are provided as-is for converting .docx files to PDF format. LibreOffice is licensed under MPL 2.0.

## Support

For issues with:
- **LibreOffice installation**: https://www.libreoffice.org/get-help/
- **docx2pdf library**: https://github.com/AlJohri/docx2pdf

## Advanced Usage

### Making the script executable

```bash
chmod +x docx_to_pdf.py
# Add shebang if not present (first line of script)
# Then run directly:
./docx_to_pdf.py document.docx
```

### Adding to PATH for system-wide use

```bash
# Copy to a directory in PATH
sudo cp docx_to_pdf.py /usr/local/bin/docx2pdf
sudo chmod +x /usr/local/bin/docx2pdf

# Now use from anywhere:
docx2pdf document.docx
```

### Integration with file managers

**Nautilus (Ubuntu) - Right-click context menu:**

Create `~/.local/share/nautilus/scripts/Convert to PDF`:
```bash
#!/bin/bash
python3 /path/to/docx_to_pdf.py "$1"
```

Make it executable:
```bash
chmod +x ~/.local/share/nautilus/scripts/Convert\ to\ PDF
```

Now you can right-click any .docx file and convert it!

## FAQ

**Q: Does this work with .doc (legacy) files?**
A: No, only .docx. Convert .doc to .docx first using LibreOffice.

**Q: Can I convert multiple files at once?**
A: Yes! Use `--batch` mode to convert entire directories.

**Q: Will this work without internet?**
A: Yes! All conversion happens locally.

**Q: Does it require Microsoft Office?**
A: No! Works with free LibreOffice on all platforms.

**Q: Is the output identical to the .docx?**
A: Virtually identical. LibreOffice's PDF export is very accurate.

**Q: Can I customize PDF settings (compression, quality)?**
A: The scripts use LibreOffice's default settings. For custom settings, you'd need to modify the LibreOffice command parameters.

**Q: Does it preserve hyperlinks?**
A: Yes! All hyperlinks are preserved as clickable links in the PDF.

**Q: What about password-protected .docx files?**
A: These cannot be converted without first removing the password.

---

**Enjoy your document conversions!** 📄 → 📕
