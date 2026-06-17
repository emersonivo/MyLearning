#!/usr/bin/env python3
"""
Simple DOCX to PDF Converter using docx2pdf library

This is a simpler alternative that uses the docx2pdf Python library.
On Windows, it uses Microsoft Word if available. On Linux/Mac, it uses LibreOffice.

Installation:
    pip install docx2pdf

Usage:
    python simple_docx_to_pdf.py input.docx
    python simple_docx_to_pdf.py input.docx output.pdf
    python simple_docx_to_pdf.py /path/to/folder --all  # Convert all .docx in folder
"""

import argparse
import sys
from pathlib import Path

try:
    from docx2pdf import convert
except ImportError:
    print("ERROR: docx2pdf library not found!")
    print("\nPlease install it with:")
    print("  pip install docx2pdf")
    print("\nNote: This library requires:")
    print("  - Windows: Microsoft Word installed")
    print("  - macOS/Linux: LibreOffice installed")
    sys.exit(1)


def convert_single(input_file, output_file=None):
    """Convert a single .docx file to PDF"""
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"ERROR: File not found: {input_file}")
        return False
    
    if input_path.suffix.lower() != '.docx':
        print(f"ERROR: File must be .docx: {input_file}")
        return False
    
    if output_file:
        output_path = Path(output_file)
    else:
        output_path = input_path.with_suffix('.pdf')
    
    print(f"Converting: {input_path}")
    print(f"Output:     {output_path}")
    
    try:
        convert(str(input_path), str(output_path))
        print(f"✓ Success! PDF created: {output_path}")
        return True
    except Exception as e:
        print(f"ERROR: Conversion failed: {e}")
        return False


def convert_multiple(input_dir, output_dir=None):
    """Convert all .docx files in a directory"""
    input_path = Path(input_dir)
    
    if not input_path.is_dir():
        print(f"ERROR: Not a directory: {input_dir}")
        return False
    
    docx_files = list(input_path.glob("*.docx"))
    
    if not docx_files:
        print(f"No .docx files found in: {input_dir}")
        return False
    
    print(f"Found {len(docx_files)} .docx file(s)")
    print("-" * 60)
    
    success_count = 0
    
    for docx_file in docx_files:
        if output_dir:
            out_file = Path(output_dir) / docx_file.with_suffix('.pdf').name
        else:
            out_file = docx_file.with_suffix('.pdf')
        
        if convert_single(docx_file, out_file):
            success_count += 1
        print("-" * 60)
    
    print(f"\nConverted {success_count}/{len(docx_files)} files successfully")
    return success_count == len(docx_files)


def main():
    parser = argparse.ArgumentParser(
        description="Simple DOCX to PDF converter using docx2pdf library"
    )
    
    parser.add_argument("input", help="Input .docx file or directory")
    parser.add_argument("output", nargs="?", help="Output PDF file or directory")
    parser.add_argument("--all", action="store_true", 
                       help="Convert all .docx files in directory")
    
    args = parser.parse_args()
    
    if args.all:
        success = convert_multiple(args.input, args.output)
    else:
        success = convert_single(args.input, args.output)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
