#!/usr/bin/env python3
"""
DOCX to PDF Converter with Formatting Preservation

This script converts .docx files to PDF while preserving all formatting,
styles, tables, images, and other document elements.

Dependencies:
    - LibreOffice (installed and accessible via command line)
    - Python 3.6+

Usage:
    python docx_to_pdf.py input.docx
    python docx_to_pdf.py input.docx -o output.pdf
    python docx_to_pdf.py /path/to/folder --batch  # Convert all .docx files in folder
"""

import argparse
import os
import subprocess
import glob
import sys
from pathlib import Path
import platform
from tabnanny import verbose


class DocxToPdfConverter:
    """Convert .docx files to PDF using LibreOffice"""
    
    def __init__(self):
        self.libreoffice_path = self._find_libreoffice()
        
    def _find_libreoffice(self):
        """Find LibreOffice installation path"""
        system = platform.system()
        
        # Common LibreOffice paths by OS
        possible_paths = []
        
        if system == "Linux":
            possible_paths = [
                "libreoffice",
                "/usr/bin/libreoffice",
                "/usr/local/bin/libreoffice",
                "soffice"
            ]
        elif system == "Darwin":  # macOS
            possible_paths = [
                "/Applications/LibreOffice.app/Contents/MacOS/soffice",
                "libreoffice",
                "soffice"
            ]
        elif system == "Windows":
            possible_paths = [
                r"C:\Program Files\LibreOffice\program\soffice.exe",
                r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
                "soffice.exe"
            ]
        
        # Try each path
        for path in possible_paths:
            try:
                # Test if command exists
                result = subprocess.run(
                    [path, "--version"],
                    capture_output=True,
                    timeout=5,
                    text=True
                )
                if result.returncode == 0:
                    return path
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        
        return None
    
    def check_libreoffice(self):
        """Check if LibreOffice is available"""
        if not self.libreoffice_path:
            print("ERROR: LibreOffice not found!")
            print("\nPlease install LibreOffice:")
            if platform.system() == "Linux":
                print("  Ubuntu/Debian: sudo apt-get install libreoffice")
                print("  Fedora/RHEL:   sudo dnf install libreoffice")
                print("  Arch:          sudo pacman -S libreoffice-fresh")
            elif platform.system() == "Darwin":
                print("  macOS: brew install --cask libreoffice")
                print("  or download from: https://www.libreoffice.org/download")
            elif platform.system() == "Windows":
                print("  Download from: https://www.libreoffice.org/download")
            return False
        return True
    
    def convert_file(self,input_file, output_file):
        """
        Convert a single .docx file to PDF
        
        Args:
            input_file (str): Path to input .docx file
            output_file (str): Path to output PDF file (optional)
            verbose (bool): Print progress messages
            
        Returns:
            bool: True if successful, False otherwise
        """
        print("input", input_file)
        print("output", output_file)
        input_path = Path(input_file).resolve()
        
        # Validate input file
        if not input_path.exists():
            print(f"ERROR: Input file not found: {input_file}")
            return False
        
        if not input_path.suffix.lower() == '.docx':
            print(f"ERROR: Input file must be .docx: {input_file}")
            return False
        
        # Determine output path
        if output_file:
            output_path = Path(output_file).resolve()
            output_dir = output_path.parent
        else:
            output_dir = input_path.parent
            output_path = output_dir / f"{input_path.stem}.pdf"
        
        # Create output directory if needed
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if verbose:
            print(f"Converting: {input_path.name}")
            print(f"Output to:  {output_path}")
        
        try:
            # LibreOffice command for conversion
            # --headless: run without GUI
            # --convert-to pdf: output format
            # --outdir: output directory
            cmd = [
                self.libreoffice_path,
                "--headless",
                "--convert-to", "pdf",
                "--outdir", str(output_dir),
                str(input_path)
            ]
            
            if verbose:
                print(f"Running: {' '.join(cmd)}")
            
            # Run conversion
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode != 0:
                print(f"ERROR: Conversion failed!")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                return False
            
            # LibreOffice creates PDF with same name as input
            # If we want a custom output name, rename it
            default_output = output_dir / f"{input_path.stem}.pdf"
            if output_file and default_output != output_path:
                if default_output.exists():
                    default_output.rename(output_path)
            
            if output_path.exists():
                if verbose:
                    print(f"✓ Success! PDF created: {output_path}")
                return True
            else:
                print(f"ERROR: PDF file was not created")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"ERROR: Conversion timed out (>120 seconds)")
            return False
        except Exception as e:
            print(f"ERROR: Conversion failed: {e}")
            return False
    
def main():
#     parser = argparse.ArgumentParser(
#         description="Convert .docx files to PDF with formatting preservation",
#         formatter_class=argparse.RawDescriptionHelpFormatter,
#         epilog="""
# Examples:
#   # Convert single file
#   python docx_to_pdf.py document.docx
  
#   # Convert with custom output name
#   python docx_to_pdf.py document.docx -o report.pdf
  
#   # Convert all .docx files in a directory
#   python docx_to_pdf.py /path/to/documents --batch
  
#   # Batch convert to different output directory
#   python docx_to_pdf.py /path/to/documents --batch -o /path/to/output
#         """
#     )
    
#     parser.add_argument(
#         "input",
#         help="Input .docx file or directory (with --batch)"
#     )
    
#     parser.add_argument(
#         "-o", "--output",
#         help="Output PDF file or directory (for batch mode)"
#     )
    
#     parser.add_argument(
#         "--batch",
#         action="store_true",
#         help="Convert all .docx files in the input directory"
#     )
    
#     parser.add_argument(
#         "-q", "--quiet",
#         action="store_true",
#         help="Suppress verbose output"
#     )
    
#     args = parser.parse_args()
    
#     # Initialize converter
#     converter = DocxToPdfConverter()
    
#     # Check LibreOffice availability
#     if not converter.check_libreoffice():
#         sys.exit(1)
    
#     verbose = not args.quiet
    
#     # Perform conversion
#     if args.batch:
#         stats = converter.convert_batch(args.input, args.output, verbose=verbose)
#         if stats and stats["failed"] > 0:
#             sys.exit(1)
#     elif args.input:
#         stats = converter.convert_batch(args.input, args.output, verbose=verbose)
#         if stats and stats["failed"] > 0:
#             sys.exit(1)            
#     elif not args.input and not args.batch:
    docxfiles = glob.glob("**/*.docx", recursive=True)
    if docxfiles:
        print(f"Found {len(docxfiles)} docx files.")
        for docxfile in docxfiles:
            docxbase = os.path.basename(docxfile)
            pfbase = docxbase.replace(".docx", ".pdf").replace(" ", "_")
            pdffile = os.path.join(os.path.dirname(docxfile), pfbase)

            if os.path.exists(pdffile):
                print(f"- {docxfile}\n -> {pdffile}")      
    
            success = DocxToPdfConverter().convert_file(docxfile, pdffile)
            if not success:
                sys.exit(1)
    
    print("\nAll done! ✓")


if __name__ == "__main__":
    main()
