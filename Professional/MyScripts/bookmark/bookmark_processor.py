#!/usr/bin/env python3 #save as bookmark_processor.py
"""
Bookmark HTML Processor: bookmark_processor.py


This script reads a Netscape bookmark HTML file, organizes bookmarks by folders,
removes duplicate URLs across the entire collection, and exports back to HTML format.
"""

import re
from html.parser import HTMLParser
from datetime import datetime
import html

class BookmarkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_folder = "Root"
        self.folder_stack = ["Root"]
        self.bookmarks = {}  # folder_name: [list of bookmark_dicts]
        self.all_urls = set()  # Track all URLs to remove duplicates
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == 'h3':
            # This is a folder name
            self.current_folder = None
        elif tag == 'a':
            # This is a bookmark
            url = attrs_dict.get('href', '')
            title = attrs_dict.get('title', '')
            add_date = attrs_dict.get('add_date', '')
            last_modified = attrs_dict.get('last_modified', '')
            icon_uri = attrs_dict.get('icon_uri', '')
            icon = attrs_dict.get('icon', '')
            tags = attrs_dict.get('tags', '')
            
            # Only add if URL is not empty and not already seen
            if url and url not in self.all_urls:
                self.all_urls.add(url)
                
                bookmark = {
                    'url': url,
                    'title': title,
                    'add_date': add_date,
                    'last_modified': last_modified,
                    'icon_uri': icon_uri,
                    'icon': icon,
                    'tags': tags
                }
                
                if self.current_folder not in self.bookmarks:
                    self.bookmarks[self.current_folder] = []
                self.bookmarks[self.current_folder].append(bookmark)
    
    def handle_data(self, data):
        # If we're in an H3 tag, this is the folder name
        if self.current_folder is None:
            folder_name = data.strip()
            if folder_name:
                self.current_folder = folder_name
                # Update the folder stack
                if len(self.folder_stack) > 0:
                    self.folder_stack[-1] = folder_name
                else:
                    self.folder_stack = [folder_name]
                
                # Initialize the folder in bookmarks if not exists
                if self.current_folder not in self.bookmarks:
                    self.bookmarks[self.current_folder] = []

def parse_bookmark_file(file_path):
    """Parse the bookmark HTML file and return organized bookmarks."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    parser = BookmarkParser()
    parser.feed(content)
    
    return parser.bookmarks

def generate_html(bookmarks):
    """Generate HTML content from organized bookmarks."""
    html_content = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
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
    
    # Add bookmarks by folder
    for folder, bookmark_list in bookmarks.items():
        if folder == "Root":
            # Add root bookmarks without folder header
            for bookmark in bookmark_list:
                html_content += generate_bookmark_html(bookmark)
        else:
            # Add folder header and its bookmarks
            html_content += f'    <DT><H3 ADD_DATE="{int(datetime.now().timestamp())}" LAST_MODIFIED="{int(datetime.now().timestamp())}">{html.escape(folder)}</H3>\n'
            html_content += '    <DL><p>\n'
            
            for bookmark in bookmark_list:
                html_content += '        ' + generate_bookmark_html(bookmark)
            
            html_content += '    </DL><p>\n'
    
    html_content += '</DL><p>'
    return html_content

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

def process_bookmarks(input_file, output_file):
    """Main function to process bookmarks."""
    print(f"Reading bookmarks from: {input_file}")
    bookmarks = parse_bookmark_file(input_file)
    
    # Print summary
    total_urls = sum(len(bookmark_list) for bookmark_list in bookmarks.values())
    print(f"Total unique bookmarks: {total_urls}")
    print(f"Total folders: {len(bookmarks)}")
    
    for folder, bookmark_list in bookmarks.items():
        print(f"  {folder}: {len(bookmark_list)} bookmarks")
    
    # Generate HTML
    html_content = generate_html(bookmarks)
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Processed bookmarks written to: {output_file}")

def main():
    input_file = "bookmarks20250627.html"
    output_file = "processed_bookmarks.html"
    
    print("Bookmark Processor")
    print("==================")
    process_bookmarks(input_file, output_file)
    print("\nProcessing complete!")

if __name__ == "__main__":
    main()