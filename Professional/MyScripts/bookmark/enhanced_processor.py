#!/usr/bin/env python3 #save as enhanced_processor.py
"""
Enhanced Bookmark HTML Processor

This script reads a Netscape bookmark HTML file, organizes bookmarks by folders,
removes duplicate URLs across the entire collection, and exports back to HTML format.
"""

import re
from datetime import datetime
import html

def parse_bookmarks(content):
    """Parse bookmarks from HTML content using a more robust approach."""
    bookmarks = {}
    seen_urls = set()
    current_folder = "Root"
    
    # Split content into lines for processing
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for folder (H3 tag)
        if '<DT><H3' in line:
            # Extract folder name
            folder_match = re.search(r'<DT><H3[^>]*>(.*?)</H3>', line, re.IGNORECASE)
            if folder_match:
                current_folder = folder_match.group(1).strip()
                if current_folder not in bookmarks:
                    bookmarks[current_folder] = []
            i += 1
            continue
        
        # Check for bookmark (A tag)
        if '<DT><A' in line:
            # This might be a multi-line bookmark, collect all attributes
            bookmark_line = line
            
            # If the line doesn't end with </A>, collect continuation lines
            j = i + 1
            while j < len(lines) and not bookmark_line.strip().endswith('</A>'):
                bookmark_line += ' ' + lines[j].strip()
                j += 1
            
            # Extract bookmark data
            bookmark = extract_bookmark_data(bookmark_line)
            if bookmark and bookmark['url'] and bookmark['url'] not in seen_urls:
                seen_urls.add(bookmark['url'])
                
                if current_folder not in bookmarks:
                    bookmarks[current_folder] = []
                bookmarks[current_folder].append(bookmark)
            
            i = j
            continue
        
        i += 1
    
    return bookmarks, seen_urls

def extract_bookmark_data(line):
    """Extract bookmark data from a line containing an A tag."""
    # Extract the entire A tag
    a_match = re.search(r'<A\s+([^>]*)>(.*?)</A>', line, re.IGNORECASE | re.DOTALL)
    if not a_match:
        return None
    
    attrs = a_match.group(1)
    title = a_match.group(2).strip()
    
    # Extract href attribute
    href_match = re.search(r'HREF=["\'](.*?)["\']', attrs, re.IGNORECASE)
    if not href_match:
        return None
    
    url = href_match.group(1)
    
    # Extract other attributes
    add_date = extract_attr(attrs, 'ADD_DATE')
    last_modified = extract_attr(attrs, 'LAST_MODIFIED')
    icon_uri = extract_attr(attrs, 'ICON_URI')
    icon = extract_attr(attrs, 'ICON')
    tags = extract_attr(attrs, 'TAGS')
    
    return {
        'url': url,
        'title': title or url,
        'add_date': add_date,
        'last_modified': last_modified,
        'icon_uri': icon_uri,
        'icon': icon,
        'tags': tags
    }

def extract_attr(attrs, attr_name):
    """Extract attribute value from HTML attributes string."""
    # More robust regex that handles quotes properly
    pattern = f'{attr_name}=(["\'])(.*?)\\1'
    match = re.search(pattern, attrs, re.IGNORECASE)
    return match.group(2) if match else ''

def generate_html(bookmarks):
    """Generate HTML content from bookmarks."""
    html = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self'; script-src 'none'; img-src data: *; object-src 'none'"></meta>
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks Menu</H1>

<DL><p>
"""
    
    now = str(int(datetime.now().timestamp()))
    
    for folder, bookmark_list in bookmarks.items():
        if folder == "Root":
            # Add root bookmarks without folder header
            for bookmark in bookmark_list:
                html += generate_bookmark_html(bookmark)
        else:
            # Add folder header and its bookmarks
            html += f'    <DT><H3 ADD_DATE="{now}" LAST_MODIFIED="{now}">{html.escape(folder)}</H3>\n'
            html += '    <DL><p>\n'
            
            for bookmark in bookmark_list:
                html += '        ' + generate_bookmark_html(bookmark)
            
            html += '    </DL><p>\n'
    
    html += '</DL><p>'
    return html

def generate_bookmark_html(bookmark):
    """Generate HTML for a single bookmark."""
    url = html.escape(bookmark['url'])
    title = html.escape(bookmark['title'] or bookmark['url'])
    add_date = bookmark['add_date'] or str(int(datetime.now().timestamp()))
    last_modified = bookmark['last_modified'] or str(int(datetime.now().timestamp()))
    
    html_str = f'<DT><A HREF="{url}" ADD_DATE="{add_date}" LAST_MODIFIED="{last_modified}"'
    
    if bookmark['icon_uri']:
        html_str += f' ICON_URI="{html.escape(bookmark["icon_uri"])}"'
    if bookmark['icon']:
        html_str += f' ICON="{html.escape(bookmark["icon"])}"'
    if bookmark['tags']:
        html_str += f' TAGS="{html.escape(bookmark["tags"])}"'
    
    html_str += f'>{title}</A>\n'
    return html_str

def main():
    print("Enhanced Bookmark Processor")
    print("==========================")
    
    # Read input file
    try:
        with open('bookmarks20250627.html', 'r', encoding='utf-8') as f:
            content = f.read()
        print("\u2713 Read bookmark file successfully")
    except FileNotFoundError:
        print("\u2717 Error: Could not find bookmarks20250627.html")
        return
    except Exception as e:
        print(f"\u2717 Error reading file: {e}")
        return
    
    # Parse bookmarks
    bookmarks, seen_urls = parse_bookmarks(content)
    
    # Count total bookmarks
    total_bookmarks = sum(len(bookmark_list) for bookmark_list in bookmarks.values())
    
    print(f"\nProcessing Results:")
    print(f"Total unique bookmarks: {total_bookmarks}")
    print(f"Total folders: {len(bookmarks)}")
    print(f"Unique URLs processed: {len(seen_urls)}")
    
    print(f"\nFolders found:")
    for folder, bookmark_list in bookmarks.items():
        print(f"  {folder}: {len(bookmark_list)} bookmarks")
    
    # Generate HTML
    html_content = generate_html(bookmarks)
    
    # Write output file
    try:
        with open('processed_bookmarks.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\n\u2713 Processed bookmarks written to: processed_bookmarks.html")
        print("\u2713 You can now import this file into your browser")
        print("\nTo import into your browser:")
        print("1. Open your browser's bookmark manager")
        print("2. Look for 'Import bookmarks' or 'Import and Export' option")
        print("3. Select the processed_bookmarks.html file")
    except Exception as e:
        print(f"\u2717 Error writing output file: {e}")
        return

if __name__ == "__main__":
    main()