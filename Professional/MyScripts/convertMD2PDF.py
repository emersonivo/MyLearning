"""
Markdown to PDF Converter
Converts .md files to PDF while preserving formatting and styling

Linux dependencies:
sudo apt-get install python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

Required Libraries:
- markdown
- weasyprint
Usage Examples:
1. Convert a single file:
   convert_md_to_pdf("example.md")
2. Convert with custom output path:
   convert_md_to_pdf("example.md", "output/example.pdf")
3. Convert all .md files in a directory:
   batch_convert_md_to_pdf("./markdown_files", "./pdf_output")
"""

import glob
import os
import sys
import markdown
from weasyprint import HTML, CSS
from pathlib import Path

def convert_md_to_pdf(md_file_path, output_pdf_path=None, custom_css=None):
    """
    Convert a Markdown file to PDF with preserved formatting.
    
    Args:
        md_file_path (str): Path to the input .md file
        output_pdf_path (str, optional): Path for output PDF. If None, uses same name as input
        custom_css (str, optional): Custom CSS styling. If None, uses default styling
    
    Returns:
        str: Path to the generated PDF file
    """
    
    # Read the markdown file
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML with extensions for better formatting
    html_content = markdown.markdown(
        md_content,
        extensions=[
            'extra',           # Tables, fenced code blocks, etc.
            'codehilite',      # Syntax highlighting
            'toc',             # Table of contents
            'nl2br',           # Newline to break
            'sane_lists'       # Better list handling
        ]
    )
    
    # Default CSS styling
    default_css = """
        @page {
            margin: 2cm;
            size: A4;
        }
        
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            font-weight: 600;
        }
        
        h1 { font-size: 2em; border-bottom: 2px solid #3498db; padding-bottom: 0.3em; }
        h2 { font-size: 1.5em; border-bottom: 1px solid #bdc3c7; padding-bottom: 0.3em; }
        h3 { font-size: 1.3em; }
        h4 { font-size: 1.1em; }
        
        p {
            margin: 0.8em 0;
            text-align: justify;
        }
        
        a {
            color: #3498db;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #e74c3c;
        }
        
        pre {
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
            line-height: 1.4;
        }
        
        pre code {
            background-color: transparent;
            color: #ecf0f1;
            padding: 0;
        }
        
        blockquote {
            border-left: 4px solid #3498db;
            padding-left: 1em;
            margin-left: 0;
            color: #555;
            font-style: italic;
            background-color: #f9f9f9;
            padding: 0.5em 1em;
        }
        
        ul, ol {
            margin: 1em 0;
            padding-left: 2em;
        }
        
        li {
            margin: 0.3em 0;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }
        
        table th {
            background-color: #3498db;
            color: white;
            padding: 0.8em;
            text-align: left;
            font-weight: 600;
        }
        
        table td {
            border: 1px solid #ddd;
            padding: 0.8em;
        }
        
        table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1em auto;
        }
        
        hr {
            border: none;
            border-top: 2px solid #bdc3c7;
            margin: 2em 0;
        }
    """
    
    # Use custom CSS if provided, otherwise use default
    css_to_use = custom_css if custom_css else default_css
    
    # Wrap HTML content with proper structure
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Markdown to PDF</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Determine output path
    if output_pdf_path is None:
        output_pdf_path = Path(md_file_path).with_suffix('.pdf')
    
    # Convert HTML to PDF
    html = HTML(string=full_html)
    css = CSS(string=css_to_use)
    html.write_pdf(output_pdf_path, stylesheets=[css])
    
    print(f"✓ PDF created successfully: {output_pdf_path}")
    return str(output_pdf_path)


def batch_convert_md_to_pdf(directory_path, output_dir=None):
    """
    Convert all .md files in a directory to PDF.
    
    Args:
        directory_path (str): Directory containing .md files
        output_dir (str, optional): Output directory for PDFs. If None, saves in same directory
    
    Returns:
        list: Paths to all generated PDF files
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        raise ValueError(f"Directory not found: {directory_path}")
    
    # Find all .md files
    md_files = list(directory.glob("*.md"))
    
    if not md_files:
        print(f"No .md files found in {directory_path}")
        return []
    
    # Create output directory if specified
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    
    pdf_files = []
    
    for md_file in md_files:
        try:
            if output_dir:
                pdf_path = Path(output_dir) / md_file.with_suffix('.pdf').name
            else:
                pdf_path = None
            
            result = convert_md_to_pdf(str(md_file), str(pdf_path) if pdf_path else None)
            pdf_files.append(result)
        except Exception as e:
            print(f"✗ Error converting {md_file.name}: {str(e)}")
    
    print(f"\n✓ Converted {len(pdf_files)} out of {len(md_files)} files")
    return pdf_files

if len(sys.argv) == 2:
    infile = sys.argv[1]


# Example usage
if __name__ == "__main__":
    # Example 1: Convert a single file
    if len(sys.argv) == 2:
        infile = sys.argv[1]
        if os.path.exists(infile) and infile.endswith(".md"):
            outfile = infile.replace(".md", ".pdf").replace(" ", "_")
            convert_md_to_pdf(infile, outfile)
            print(f"Converted {infile} to {outfile}")
        else:
            print(f"File not found or not a markdown file: {infile}")
    else:
        mdfiles = glob.glob("**/*.md", recursive=True)
        if mdfiles:
            print(f"Found {len(mdfiles)} markdown files.")
            for mdfile in mdfiles:
                mdbase = os.path.basename(mdfile)
                pfbase = mdbase.replace(".md", ".pdf").replace(" ", "_")
                pdffile = os.path.join(os.path.dirname(mdfile), pfbase)
                convert_md_to_pdf(mdfile, pdffile)
                if os.path.exists(pdffile):
                    print(f"- {mdfile}\n -> {pdffile}")
                # convert_md_to_pdf(mdfiles[0])
        
                # Example 2: Convert with custom output path
            
    
    # Example 3: Convert all .md files in a directory
    # batch_convert_md_to_pdf("./markdown_files", "./pdf_output")
    
    # Example 4: With custom CSS
    custom_style = """
        body { font-family: Georgia, serif; }
        h1 { color: #c0392b; }
    """
    # convert_md_to_pdf("example.md", custom_css=custom_style)
    
    # print("Markdown to PDF Converter Ready!")
    # print("Uncomment the examples above to use.")
