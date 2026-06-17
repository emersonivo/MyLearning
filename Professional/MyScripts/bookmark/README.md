# Bookmark Processor # Save as README.md

A set of tools to clean up and organize browser bookmarks by removing duplicates and organizing them by folders.

## Problem

Browser bookmarks often accumulate duplicates over time, especially when:
- Importing bookmarks from multiple sources
- Syncing across different devices
- Bookmarking the same pages multiple times

This tool helps clean up your bookmarks by:
- Removing duplicate URLs across all folders
- Organizing bookmarks by their folder structure
- Generating a clean HTML file ready for import

## Files Included

1. **enhanced_processor.py** - Python script for processing bookmarks
2. **browser_processor.html** - Browser-based version (no installation required)
3. **bookmarks20250627.html** - Sample bookmark file

## How to Use

### Method 1: Browser Version (Recommended)

1. Open `browser_processor.html` in your web browser
2. Export your bookmarks from your browser as HTML file:
   - **Chrome**: Bookmarks Manager \u2192 Export bookmarks
   - **Firefox**: Library \u2192 Import and Backup \u2192 Export Bookmarks to HTML
   - **Safari**: File \u2192 Export Bookmarks
3. Upload your bookmarks file to the browser tool
4. Click "Process Bookmarks"
5. Download the cleaned bookmarks file
6. Import the cleaned file back into your browser

### Method 2: Python Script

1. Install Python 3.x if not already installed
2. Place your bookmark file in the same folder as the script
3. Run the script:
   ```bash
   python enhanced_processor.py
   ```
4. The script will generate `processed_bookmarks.html`
5. Import this file back into your browser

## Features

- \u2705 Removes duplicate URLs across all folders
- \u2705 Preserves folder structure
- \u2705 Maintains bookmark metadata (dates, icons, tags)
- \u2705 Handles large bookmark files
- \u2705 Works offline (browser version)
- \u2705 No data sent to external servers

## Technical Details

The processor works by:

1. **Parsing**: Reading the Netscape bookmark HTML format
2. **Deduplication**: Using a Set to track unique URLs
3. **Organization**: Grouping bookmarks by their folder structure
4. **Export**: Generating clean HTML in the same format

### Supported Bookmark Attributes

- URL (href)
- Title
- Add date
- Last modified date
- Icon URI
- Icon data
- Tags

## Browser Import Instructions

### Chrome/Edge:
1. Open Bookmarks Manager (Ctrl+Shift+O)
2. Click menu (\u22ee) \u2192 "Import bookmarks"
3. Select the processed HTML file

### Firefox:
1. Open Library (Ctrl+Shift+B)
2. Click "Import and Backup" \u2192 "Import Bookmarks from HTML"
3. Select the processed HTML file

### Safari:
1. File \u2192 Import From \u2192 Bookmarks HTML File
2. Select the processed HTML file

## Sample Output

After processing, you'll see:
```
Processing Results:
Total unique bookmarks: 847
Total folders: 12
Unique URLs processed: 847

Folders found:
  AI: 15 bookmarks
  EB2NIW: 25 bookmarks
  Homebrewing: 18 bookmarks
  Root: 789 bookmarks
```

## Notes

- The original bookmark file is not modified
- The processed file contains only unique URLs
- Folder structure is preserved
- Bookmarks without titles will use the URL as the title
- Large bookmark files (1MB+) may take a few seconds to process

## Troubleshooting

**"File not found" error**: Make sure your bookmark file is in the same directory as the script

**"Invalid format" error**: Ensure you're using the HTML export format, not JSON

**Processing takes too long**: The browser version may be slower for very large files (>10,000 bookmarks)

## Privacy

- All processing happens locally on your device
- No data is sent to external servers
- The browser version uses JavaScript to process files client-side