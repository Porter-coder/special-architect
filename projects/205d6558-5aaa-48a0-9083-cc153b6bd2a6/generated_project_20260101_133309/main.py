"""
Markdown to HTML Converter
==========================

This script converts Markdown formatted text to HTML using simple regex-based replacements.
It supports basic Markdown elements including:
- Headers (#, ##, etc.)
- Paragraphs
- Bold and italic text
- Links
- Images
- Lists (ordered and unordered)
- Code blocks
- Blockquotes
- Horizontal rules

Usage:
------
    python main.py input.md output.html
    cat input.md | python main.py > output.html
"""

import re
import sys

def escape_html(text):
    """Escape special HTML characters to prevent XSS and ensure proper rendering."""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def convert_markdown_to_html(markdown_text):
    """
    Convert Markdown text to HTML.

    Args:
        markdown_text (str): The input Markdown text.

    Returns:
        str: The converted HTML string.
    """
    html = markdown_text

    # Convert headers (from largest to smallest to avoid nested matching)
    for level in range(1, 7):
        pattern = r'^' + ('#' * level) + r'\s+(.+)$'
        html = re.sub(pattern, r'<h' + str(level) + r'>\1</h' + str(level) + r'>', html, flags=re.MULTILINE)

    # Convert bold text
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # Convert italic text
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Convert links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

    # Convert images
    html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', html)

    # Convert unordered lists (handling multiline lists)
    html = re.sub(r'^\s*-\s+(.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    # Wrap consecutive list items in <ul> tags
    html = re.sub(r'(<li>.*</li>\n?)+', lambda m: '<ul>\n' + m.group(0) + '</ul>\n', html)

    # Convert ordered lists
    html = re.sub(r'^\s*\d+\.\s+(.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    # Wrap consecutive list items in <ol> tags
    html = re.sub(r'(<li>.*</li>\n?)+', lambda m: '<ol>\n' + m.group(0) + '</ol>\n', html)

    # Convert code blocks
    html = re.sub(r'