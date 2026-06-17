#!/usr/bin/env python3 # save as simple_processor.py
"""
Simple Bookmark HTML Processor

This script reads a Netscape bookmark HTML file, organizes bookmarks by folders,
removes duplicate URLs, and exports back to HTML format.
"""

import re
from datetime import datetime

def parse_bookmarks(content):
    """Parse bookmarks from HTML content."""
    bookmarks = {}
    seen_urls = set()
    current_folder = "Root"
    
    # Find all DT elements
    dt_pattern = r'<DT>(.*?)</DT>'
    dt_matches = re.findall(dt_pattern, content, re.DOTALL | re.IGNORECASE)
    
    for dt_content in dt_matches:
        # Check if it's a folder (H3)
        h3_match = re.search(r'<H3[^>]*>(.*?)</H3>', dt_content, re.IGNORECASE)
        if h3_match:
            current_folder = h3_match.group(1).strip()
            if current_folder not in bookmarks:
                bookmarks[current_folder] = []
            continue
        
        # Check if it's a bookmark (A tag)
        a_match = re.search(r'<A\s+([^>]*)>(.*?)</A>', dt_content, re.IGNORECASE)
        if a_match:
            attrs = a_match.group(1)
            title = a_match.group(2).strip()
            
            # Extract href attribute
            href_match = re.search(r'HREF=["\'](.*?)["\']', attrs, re.IGNORECASE)
            if href_match:
                url = href_match.group(1)
                
                # Skip empty URLs or duplicates
                if not url or url in seen_urls:
                    continue
                    
                seen_urls.add(url)
                
                # Extract other attributes
                add_date = extract_attribute(attrs, 'ADD_DATE')
                last_modified = extract_attribute(attrs, 'LAST_MODIFIED')
                icon_uri = extract_attribute(attrs, 'ICON_URI')
                icon = extract_attribute(attrs, 'ICON')
                tags = extract_attribute(attrs, 'TAGS')
                
                bookmark = {
                    'url': url,
                    'title': title or url,
                    'add_date': add_date,
                    'last_modified': last_modified,
                    'icon_uri': icon_uri,
                    'icon': icon,
                    'tags': tags
                }
                
                if current_folder not in bookmarks:
                    bookmarks[current_folder] = []
                bookmarks[current_folder].append(bookmark)
    
    return bookmarks, seen_urls

def extract_attribute(attrs, attr_name):
    """Extract attribute value from HTML attributes."""
    pattern = f'{attr_name}=["\'](.*?)["\']'
    match = re.search(pattern, attrs, re.IGNORECASE)
    return match.group(1) if match else ''

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
            html += f'    <DT><H3 ADD_DATE="{now}" LAST_MODIFIED="{now}">{escape_html(folder)}</H3>\n'
            html += '    <DL><p>\n'
            
            for bookmark in bookmark_list:
                html += '        ' + generate_bookmark_html(bookmark)
            
            html += '    </DL><p>\n'
    
    html += '</DL><p>'
    return html

def generate_bookmark_html(bookmark):
    """Generate HTML for a single bookmark."""
    url = escape_html(bookmark['url'])
    title = escape_html(bookmark['title'] or bookmark['url'])
    add_date = bookmark['add_date'] or str(int(datetime.now().timestamp()))
    last_modified = bookmark['last_modified'] or str(int(datetime.now().timestamp()))
    
    html = f'<DT><A HREF="{url}" ADD_DATE="{add_date}" LAST_MODIFIED="{last_modified}"'
    
    if bookmark['icon_uri']:
        html += f' ICON_URI="{escape_html(bookmark["icon_uri"])}"'
    if bookmark['icon']:
        html += f' ICON="{escape_html(bookmark["icon"])}"'
    if bookmark['tags']:
        html += f' TAGS="{escape_html(bookmark["tags"])}"'
    
    html += f'>{title}</A>\n'
    return html

def escape_html(text):
    """Escape HTML special characters."""
    if not text:
        return ''
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))

def main():
    print("Bookmark Processor")
    print("==================")
    
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
    except Exception as e:
        print(f"\u2717 Error writing output file: {e}")
        return

if __name__ == "__main__":
    main()