import os
from pathlib import Path
import markdown
from markdown.extensions import fenced_code, tables, toc, attr_list, def_list, footnotes
from markdown.extensions.codehilite import CodeHiliteExtension
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
import yaml
from bs4 import BeautifulSoup, Comment
import re
from typing import Optional, Dict, List, Tuple, Any
from config import SECTION_ORDER, PDF_CONFIG
from pydantic import BaseModel

class PDFSection(BaseModel):
    """Model for a section in the PDF."""
    id: str
    title: str
    content: str # Raw Markdown content
    html_content: str = "" # Processed HTML content
    intro: str = ""
    key_topics: List[str] = []
    metadata: Dict[str, Any] = {}
    reading_time: int = 0 # Estimated reading time in minutes
    subsections: List[Any] = [] # Subsections of this section

class EnhancedPDFGenerator:
    """Enhanced PDF Generator with better markdown support and styling."""
    
    def __init__(self, template_path: Optional[str] = None):
        """Initialize the PDF generator with an optional custom template path."""
        if template_path:
            self.template_dir = str(Path(template_path).parent)
            self.template_name = Path(template_path).name
        else:
            self.template_dir = str(Path(__file__).parent / 'templates')
            self.template_name = 'enhanced_report_template.html'
        
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.template = self.env.get_template(self.template_name)
        
        # Initialize markdown with an expanded set of extensions
        self.md = markdown.Markdown(extensions=[
            'extra',  # Includes tables, fenced_code, footnotes, etc.
            'meta',
            'codehilite',
            'admonition',
            'attr_list',
            'toc',
            'def_list',  # Definition lists
            'footnotes',  # Footnotes support
            'abbr',  # Abbreviation support
            'md_in_html',  # Markdown inside HTML
            'sane_lists',  # Better list handling
            'nl2br',  # Convert newlines to <br> tags for proper line breaks
        ], extension_configs={
            'codehilite': {'css_class': 'highlight', 'guess_lang': False},
            'toc': {'permalink': False},  # Disable permalinks to remove ¶
            'footnotes': {'BACKLINK_TEXT': '↩'}
        })

    def _extract_section_metadata(self, content: str) -> Tuple[Dict, str]:
        """Extract YAML frontmatter and content from a markdown section."""
        metadata = {}
        content = content.lstrip()  # Remove leading whitespace
        if content.startswith('---'):
            try:
                # Split carefully, expecting '---', yaml block, '---', content
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    markdown_content = parts[2]
                    loaded_meta = yaml.safe_load(frontmatter)
                    # Ensure it's a dict, handle empty frontmatter gracefully
                    metadata = loaded_meta if isinstance(loaded_meta, dict) else {}
                    return metadata, markdown_content.strip()
            except (yaml.YAMLError, IndexError, ValueError) as e:
                # If debugging needed: print(f"Failed to parse YAML frontmatter: {e}")
                pass
        return metadata, content.strip()

    def _estimate_reading_time(self, content: str) -> int:
        """Estimate reading time in minutes based on word count."""
        words = len(content.split())
        # Assuming faster reading speed (300 words per minute) and capping at 5 minutes
        estimated_time = min(5, max(1, round(words / 300)))
        return estimated_time

    def _extract_key_topics(self, content: str, max_topics: int = None) -> List[str]:
        """Extract key topics from the content based on headings."""
        # First convert the markdown to HTML to get proper heading structure
        temp_html = self._convert_markdown_to_html(content)
        soup = BeautifulSoup(temp_html, 'html.parser')
        
        # Only consider h2 and h3 headings for key topics
        headings = soup.find_all(['h2', 'h3'])
        topics = []
        
        # Skip the first h2 if it exists and looks like a title
        starting_index = 0
        if headings and headings[0].name == 'h2':
            # Check if it's the section title (usually matches the section.title)
            starting_index = 1
        
        for heading in headings[starting_index:]:
            # Get the clean text without numbers
            text = heading.get_text().strip()
            
            # Remove any leading numbers like "1. " or "1.1. " that might be present
            clean_text = re.sub(r'^\d+(\.\d+)*\.\s+', '', text)
            
            topics.append(clean_text)
            
            # Only limit if max_topics is specified
            if max_topics and len(topics) >= max_topics:
                break
        
        return topics

    def _cleanup_raw_markdown(self, content: str) -> str:
        """Clean up common LLM formatting issues like literal '\n'."""
        # Replace literal '\n' with actual newlines
        content = content.replace('\\n', '\n')
        # Remove any trailing whitespace
        content = content.strip()
        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        # Ensure consistent spacing around headers
        content = re.sub(r'(\n#{1,6}.*?)(?:\n(?!\n))', r'\1\n\n', content)
        
        # Fix table formatting issues
        # 1. Find potential table patterns (lines with multiple |)
        lines = content.split('\n')
        in_table = False
        table_start_index = -1
        for i, line in enumerate(lines):
            pipe_count = line.count('|')
            
            # Check if this line looks like a table row (has 2+ pipes)
            if pipe_count >= 2:
                # If we weren't in a table before, mark this as the start
                if not in_table:
                    in_table = True
                    table_start_index = i
            # If we were in a table but current line doesn't look like one
            elif in_table:
                # We've reached the end of a table
                in_table = False
                # Process the table we just found
                table_lines = lines[table_start_index:i]
                
                # Check if we have a header row and separator row
                if len(table_lines) >= 2:
                    header_row = table_lines[0]
                    separator_row = table_lines[1]
                    
                    # Fix separator row if needed (it should contain only |, -, and :)
                    if not all(c in '|:-' for c in separator_row.strip()):
                        # Create a proper separator row based on the header
                        cols = header_row.strip('|').split('|')
                        separator_row = '|' + '|'.join(['-' * len(col.strip()) for col in cols]) + '|'
                        table_lines[1] = separator_row
                
                # Update the original lines with fixed table
                lines[table_start_index:i] = table_lines
                
        # Ensure proper spacing around tables
        content = '\n'.join(lines)
        content = re.sub(r'(\n\|.*\|\n)(?!\n)', r'\1\n', content)  # Add newline after table
        content = re.sub(r'\n\n(\|.*\|)', r'\n\1', content)  # Remove extra newline before table
        
        return content

    def _convert_markdown_to_html(self, markdown_content):
        """Convert markdown content to HTML with enhanced styling."""
        # Pre-process markdown to handle tables properly
        lines = markdown_content.split('\n')
        processed_lines = []
        i = 0
        
        # Check if this is a key findings section and apply special preprocessing
        key_findings_section = False
        key_findings_start_idx = -1
        key_findings_end_idx = -1
        
        for i, line in enumerate(lines):
            if "### Key Findings" in line or "## Key Findings" in line:
                key_findings_section = True
                key_findings_start_idx = i
            elif key_findings_section and line.strip().startswith('###'):
                # Found the end of key findings section (next heading)
                key_findings_end_idx = i
                break
        
        # If we found the end of key findings by another heading
        if key_findings_end_idx == -1 and key_findings_section:
            key_findings_end_idx = len(lines)  # Set to end of file
        
        # Special preprocessing for key findings section
        if key_findings_section and key_findings_start_idx >= 0:
            # Create a new array for the processed key findings
            key_findings_lines = []
            key_findings_lines.append('<div id="key-findings">')
            key_findings_lines.append(f'<h3>Key Findings</h3>')
            key_findings_lines.append('<ol>')
            
            # Now process the content items
            idx = key_findings_start_idx + 1
            item_count = 0
            extracted_items = []  # Store all items here first
            
            while idx < key_findings_end_idx:
                line = lines[idx].strip()
                
                # Skip empty lines
                if not line:
                    idx += 1
                    continue
                
                # Match lines starting with a number followed by a period
                if re.match(r'^\d+\.\s+', line):
                    # This is a numbered item like "1. **Title:** Content"
                    # Extract the content after the number
                    # Check if it contains bold text and description
                    match = re.match(r'^\d+\.\s+\*\*(.*?):\*\*(.*?)$', line)
                    if match:
                        title = match.group(1)
                        content = match.group(2).strip()
                        extracted_items.append((title, content))
                    else:
                        # Try another pattern where the colon is outside the bold marks
                        match = re.match(r'^\d+\.\s+\*\*(.*?)\*\*:(.*?)$', line)
                        if match:
                            title = match.group(1)
                            content = match.group(2).strip()
                            extracted_items.append((title, content))
                        else:
                            # Just add as is if no pattern matches
                            content = line[line.find(' ')+1:]  # Everything after the number+period+space
                            extracted_items.append((None, content))
                
                idx += 1
            
            # Now create the list items with sequential numbering
            for i, (title, content) in enumerate(extracted_items, 1):
                if title:
                    key_findings_lines.append(f'<li><strong>{title}</strong><span class="content">{content}</span></li>')
                else:
                    key_findings_lines.append(f'<li><span class="content">{content}</span></li>')
            
            # Close the ordered list and div
            key_findings_lines.append('</ol>')
            key_findings_lines.append('</div>')
            
            # Replace the key findings section in the original content
            lines[key_findings_start_idx:key_findings_end_idx] = key_findings_lines
        
        # First pass: identify and fix table formatting, preserve list formatting
        in_table = False
        table_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            
            # Check if this line might be a table row (contains at least 2 pipe characters)
            if '|' in line and line.count('|') >= 2:
                # If not already in a table, this could be the start of a table
                if not in_table:
                    in_table = True
                    table_lines = [line]
                else:
                    # Continue collecting table lines
                    table_lines.append(line)
            elif in_table:
                # If we're in a table but current line doesn't look like a table row,
                # we might have reached the end of the table
                
                # Process the collected table
                if len(table_lines) >= 2:
                    # Ensure the table has a proper separator row (second row)
                    if not all(c in '|:-' for c in table_lines[1].strip() if c not in ' '):
                        # Create a proper separator row based on the number of columns in the header row
                        column_count = table_lines[0].count('|') - 1
                        separator_row = '|' + '|'.join(['---' for _ in range(column_count)]) + '|'
                        table_lines.insert(1, separator_row)
                    
                    # Add an empty line before the table for proper Markdown parsing
                    if processed_lines and processed_lines[-1].strip():
                        processed_lines.append('')
                    
                    # Add all table lines
                    processed_lines.extend(table_lines)
                    
                    # Add an empty line after the table
                    processed_lines.append('')
                else:
                    # If it doesn't look like a valid table, just add the lines as regular text
                    processed_lines.extend(table_lines)
                
                # Reset table tracking
                in_table = False
                table_lines = []
                
                # Don't forget to add the current line
                processed_lines.append(line)
            else:
                # Check if this is a list item (numbered or bulleted)
                is_list_item = False
                
                # Check for numbered list patterns (e.g., "1. ")
                if re.match(r'^\s*\d+\.\s', line):
                    is_list_item = True
                # Check for bulleted list patterns (e.g., "* ", "- ")
                elif re.match(r'^\s*[\*\-\+]\s', line):
                    is_list_item = True
                
                # Process list items carefully to preserve formatting
                if is_list_item:
                    # Ensure there's appropriate spacing for proper list rendering
                    # If the previous line wasn't blank and wasn't a list item, add a blank line
                    if (processed_lines and processed_lines[-1].strip() and 
                            not re.match(r'^\s*(\d+\.|[\*\-\+])\s', processed_lines[-1])):
                        processed_lines.append('')
                
                # Regular line, not part of a table
                processed_lines.append(line)
            
            i += 1
        
        # If we ended while still in a table, add those lines too
        if in_table and table_lines:
            if len(table_lines) >= 2:
                # Ensure the table has a proper separator row
                if not all(c in '|:-' for c in table_lines[1].strip() if c not in ' '):
                    column_count = table_lines[0].count('|') - 1
                    separator_row = '|' + '|'.join(['---' for _ in range(column_count)]) + '|'
                    table_lines.insert(1, separator_row)
                
                # Add an empty line before the table
                if processed_lines and processed_lines[-1].strip():
                    processed_lines.append('')
                
                processed_lines.extend(table_lines)
                processed_lines.append('')
            else:
                processed_lines.extend(table_lines)
        
        # Join the processed lines back into a single string
        processed_content = '\n'.join(processed_lines)
        
        # Additional preprocessing for numbered lists with bold/italic formatting
        # Ensure proper spacing around formatting markers
        processed_content = re.sub(r'(\d+\.\s+)(\*\*|\*)([^*]+)(\*\*|\*)(\S)', r'\1\2\3\4 \5', processed_content)
        
        # Ensure proper spacing before formatting markers in lists
        processed_content = re.sub(r'(\d+\.\s+)(\S)(\*\*|\*)([^*]+)(\*\*|\*)', r'\1\2 \3\4\5', processed_content)
        
        # Reset the markdown processor and convert to HTML
        self.md.reset()
        html = self.md.convert(processed_content)
        
        # Use BeautifulSoup to further enhance the HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Process all ordered lists (ol) to ensure they have proper structure
        for ol in soup.find_all('ol'):
            # Check if we need to clean up formatting inside list items
            for li in ol.find_all('li'):
                # Check if the list item contains both text and formatted elements
                # Sometimes the parser doesn't correctly combine formatted elements
                if len(li.contents) > 1:
                    # Look for text nodes that might contain asterisks
                    for idx, child in enumerate(li.contents[:]):
                        if isinstance(child, str) and ('*' in child or '**' in child):
                            # We need to properly parse this fragment
                            md_temp = markdown.Markdown(extensions=['extra'])
                            html_fragment = md_temp.convert(child)
                            
                            # Create a temporary soup to parse the HTML fragment
                            temp_soup = BeautifulSoup(html_fragment, 'html.parser')
                            
                            # Create a placeholder to replace the text node
                            placeholder = soup.new_tag('span')
                            child.replace_with(placeholder)
                            
                            # Insert the parsed content before the placeholder
                            # Check if body exists and has contents before trying to access them
                            if temp_soup.body and temp_soup.body.contents:
                                for element in temp_soup.body.contents:
                                    placeholder.insert_before(element)
                            
                            # Remove the placeholder
                            placeholder.extract()
        
        # Second pass: look for table-like content in paragraphs
        for p in soup.find_all('p'):
            text = p.get_text()
            # Check if paragraph text contains multiple | characters that might indicate a table
            if '|' in text and text.count('|') >= 2:
                table_lines = text.split('\n')
                # Check if we have multiple lines and they look like table rows
                table_line_count = sum(1 for line in table_lines if '|' in line and line.count('|') >= 2)
                
                if table_line_count >= 2:
                    # This looks like a table that wasn't properly parsed
                    table = soup.new_tag('table')
                    table['class'] = ['enhanced-table', 'manual-table']
                    
                    # Create thead and tbody
                    thead = soup.new_tag('thead')
                    tbody = soup.new_tag('tbody')
                    
                    # Process each line as a table row
                    in_header = True
                    for line in table_lines:
                        line = line.strip()
                        if not line or line.count('|') < 2:
                            continue
                        
                        # Skip separator rows (those with only |, -, and :)
                        if all(c in '|:-' for c in line if c not in ' '):
                            in_header = False
                            continue
                        
                        # Create a table row
                        tr = soup.new_tag('tr')
                        
                        # Process cells
                        cells = line.split('|')
                        if line.startswith('|'):
                            cells = cells[1:]
                        if line.endswith('|'):
                            cells = cells[:-1]
                        
                        for cell in cells:
                            cell_content = cell.strip()
                            if in_header:
                                cell_tag = soup.new_tag('th')
                            else:
                                cell_tag = soup.new_tag('td')
                            
                            # Set content
                            cell_tag.string = cell_content
                            tr.append(cell_tag)
                        
                        # Add row to the appropriate section
                        if in_header:
                            thead.append(tr)
                            in_header = False
                        else:
                            tbody.append(tr)
                    
                    # Add thead and tbody to the table if they have content
                    if thead.find('tr'):
                        table.append(thead)
                    if tbody.find('tr'):
                        table.append(tbody)
                    
                    # Replace the paragraph with the table if we created a valid table
                    if table.find('tr'):
                        table_div = soup.new_tag('div')
                        table_div['class'] = ['table-responsive']
                        table_div.append(table)
                        p.replace_with(table_div)
        
        # Process all standard tables
        for table in soup.find_all('table'):
            self._process_table(table, soup)
        
        # Process headings for better navigation
        self._process_headings(soup)
        
        # Process lists for better styling
        for ul in soup.find_all(['ul', 'ol'], recursive=False):
            self._process_list(ul, level=1)
        
        # Process nested lists inside containers
        for container in soup.find_all(['div', 'blockquote', 'td']):
            for ul in container.find_all(['ul', 'ol'], recursive=False):
                self._process_list(ul, level=1)
        
        return str(soup)

    def _process_headings(self, soup):
        """Add classes and IDs to headings for better navigation."""
        used_ids = set()  # Track used IDs to avoid duplicates
        
        for h_tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            # Add classes based on heading level
            h_tag['class'] = h_tag.get('class', []) + [f'heading-{h_tag.name}']
            
            # Check if this is the key findings heading
            if h_tag.get_text().strip().lower() == 'key findings':
                # Find the parent section
                parent = h_tag.parent
                while parent and parent.name != 'div':
                    parent = parent.parent
                
                # If we found a parent section, mark it with an ID
                if parent:
                    parent['id'] = 'key-findings'
                
                # Also add an ID to this heading itself
                h_tag['id'] = 'key-findings-heading'
                
                # Process the ordered list that follows
                next_ol = h_tag.find_next('ol')
                if next_ol:
                    next_ol['class'] = next_ol.get('class', []) + ['key-findings-list']
            
            # Add ID for navigation if not already present
            if not h_tag.get('id'):
                # Generate ID from text content
                text = h_tag.get_text().strip()
                # Convert to lowercase and replace spaces with hyphens
                id_base = re.sub(r'[^\w\s-]', '', text.lower())
                id_base = re.sub(r'[\s-]+', '-', id_base)
                
                # Ensure unique ID
                id_text = id_base
                count = 1
                while id_text in used_ids:
                    id_text = f"{id_base}-{count}"
                    count += 1
                
                h_tag['id'] = id_text
                used_ids.add(id_text)
            else:
                # If ID already exists, still track it to avoid duplicates
                original_id = h_tag['id']
                if original_id in used_ids:
                    # Append a number to make it unique
                    count = 1
                    while f"{original_id}-{count}" in used_ids:
                        count += 1
                    h_tag['id'] = f"{original_id}-{count}"
                
                used_ids.add(original_id)

    def _process_list(self, list_tag, level=1):
        """Process a list and its nested lists recursively."""
        # Add appropriate classes based on level
        if level == 1:
            list_tag['class'] = list_tag.get('class', []) + ['enhanced-list']
        else:
            list_tag['class'] = list_tag.get('class', []) + ['nested-list']
            
            # For deep nesting (3+), add a level indicator class
            if level > 2:
                list_tag['class'] = list_tag['class'] + [f'level-{level}']
        
        # Process all list items at this level
        for li in list_tag.find_all('li', recursive=False):
            # Add appropriate classes to list items
            if level == 1:
                li['class'] = li.get('class', []) + ['enhanced-list-item']
            else:
                li['class'] = li.get('class', []) + ['nested-list-item']
                
                # For deep nesting, add a level indicator class
                if level > 2:
                    li['class'] = li['class'] + [f'item-level-{level}']
            
            # Process nested lists recursively
            for nested_list in li.find_all(['ul', 'ol'], recursive=False):
                self._process_list(nested_list, level=level+1)
                
            # Fix empty bullet points that might be followed by numbers in key findings
            if (li.get_text().strip() == '' or li.get_text().strip() == '•') and list_tag.name == 'ol':
                # Try to get the next sibling which might contain the actual content
                next_li = li.find_next_sibling('li')
                if next_li and not next_li.find(['ul', 'ol'], recursive=False):
                    # Move content from the next li to this one
                    for content in next_li.contents:
                        li.append(content.copy())
                    # Remove the now-duplicated li
                    next_li.extract()
            
            # Ensure specially formatted content within list items is preserved
            # Look for bold or italic markers that might be part of the text node
            for text_node in li.find_all(text=True, recursive=False):
                # Skip if this is just whitespace
                if not text_node.strip():
                    continue
                    
                # Check if there are unprocessed markdown formatting markers
                if '**' in text_node or '*' in text_node or '__' in text_node or '_' in text_node:
                    # We need to properly parse this markdown text
                    # Create a temporary markdown processor to handle just this fragment
                    md_temp = markdown.Markdown(extensions=['extra'])
                    html_fragment = md_temp.convert(text_node)
                    
                    # Create a temporary soup to parse the HTML fragment
                    temp_soup = BeautifulSoup(html_fragment, 'html.parser')
                    
                    # Make sure we can create a new tag and soup.body exists
                    if hasattr(li, 'new_tag') and callable(li.new_tag) and temp_soup.body and temp_soup.body.contents:
                        # Replace the text node with the parsed content
                        # Need to use a placeholder tag to replace the text node
                        placeholder = li.new_tag('span')
                        text_node.replace_with(placeholder)
                        
                        # Replace the placeholder with the parsed content
                        for element in temp_soup.body.contents:
                            placeholder.insert_before(element)
                        
                        # Remove the placeholder
                        placeholder.extract()

    def _process_table(self, table, soup):
        """Enhance table styling and structure."""
        # Wrap table in a responsive div if not already wrapped
        if table.parent.get('class') != ['table-responsive']:
            table_div = soup.new_tag('div')
            table_div['class'] = ['table-responsive']
            table.wrap(table_div)
        
        # Add enhanced styling to table
        table['class'] = table.get('class', []) + ['enhanced-table']
        
        # Add zebra striping and header styling
        if table.find('thead'):
            table['class'] = table['class'] + ['has-header']
        else:
            # Create thead from first row if it doesn't exist
            first_row = table.find('tr')
            if first_row:
                thead = soup.new_tag('thead')
                thead.append(first_row.extract())
                table.insert(0, thead)
                # Convert td to th in thead
                for td in thead.find_all('td'):
                    th = soup.new_tag('th')
                    th.attrs = td.attrs
                    if td.string:
                        th.string = td.string
                    else:
                        # Copy all contents if not just a string
                        for content in td.contents:
                            th.append(content.copy())
                    td.replace_with(th)
                table['class'] = table['class'] + ['has-header']
        
        table['class'] = table['class'] + ['zebra-stripe']
        
        # Align number cells to the right
        for td in table.find_all('td'):
            if td.string and td.string.strip() and re.match(r'^[\d,.$%]+$', td.string.strip()):
                td['class'] = td.get('class', []) + ['text-right']

    def _extract_intro(self, content: str) -> str:
        """Extract the introduction paragraph from the content."""
        # Split content into lines
        lines = content.strip().split('\n')
        intro_lines = []
        
        # Skip metadata and empty lines at the start
        i = 0
        while i < len(lines) and (not lines[i].strip() or lines[i].strip().startswith('---')):
            i += 1
            
        # Skip headers
        while i < len(lines) and (not lines[i].strip() or lines[i].strip().startswith('#')):
            i += 1
            
        # Collect first paragraph (until we hit an empty line or another header)
        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('#'):
            intro_lines.append(lines[i])
            i += 1
            
        if not intro_lines:
            return "<p>This section provides detailed analysis and insights.</p>"
            
        # Convert the intro lines to HTML
        intro_content = ' '.join(intro_lines)
        
        # Use a clean markdown processor
        md = markdown.Markdown(extensions=['extra'])
        intro_html = md.convert(intro_content)
        
        return intro_html

    def _generate_toc(self, sections):
        """Generate a properly formatted and hyperlinked table of contents."""
        if not sections:
            return ""
            
        toc_html = '<div class="toc-container">\n'
        toc_html += '<h2 class="toc-title">Table of Contents</h2>\n'
        toc_html += '<div class="toc-entries">\n'
        
        # First add the executive summary if it exists
        exec_summary = next((s for s in sections if s.id == "executive_summary"), None)
        if exec_summary:
            toc_html += f'<div class="toc-entry">\n'
            toc_html += f'  <a href="#section-executive_summary" class="toc-link">Executive Summary</a>\n'
            toc_html += f'</div>\n'
        
        # Then add all sections except the executive summary
        for section in [s for s in sections if s.id != "executive_summary"]:
            section_id = f"section-{section.id}"
            section_title = section.title.strip()
            
            toc_html += f'<div class="toc-entry">\n'
            toc_html += f'  <a href="#{section_id}" class="toc-link">{section_title}</a>\n'
            toc_html += f'</div>\n'
        
        toc_html += '</div>\n</div>\n'
        
        return toc_html

    def _get_static_section_content(self, section_id: str) -> Dict:
        """Get static predefined content for a section cover page based on section ID."""
        section_content = {
            "company_overview": {
                "description": "This section provides a comprehensive overview of the company, including its history, business model, core operations, market position, and key differentiators.",
                "key_topics": [
                    "Company History & Background",
                    "Business Model & Revenue Streams",
                    "Products & Services",
                    "Market Position & Competitive Landscape",
                    "Corporate Structure & Leadership"
                ]
            },
            "financial_analysis": {
                "description": "This section analyzes the company's financial performance, including revenue trends, profitability metrics, cash flow patterns, debt structure, and key financial ratios.",
                "key_topics": [
                    "Revenue & Growth Analysis",
                    "Profitability & Margin Trends",
                    "Cash Flow & Liquidity",
                    "Debt Structure & Capital Allocation",
                    "Financial Ratios & Comparisons"
                ]
            },
            "market_analysis": {
                "description": "This section examines the market dynamics, industry trends, competitive landscape, market share analysis, and growth opportunities for the company.",
                "key_topics": [
                    "Industry Overview & Trends",
                    "Market Size & Growth Potential",
                    "Competitive Landscape Analysis",
                    "Market Share & Positioning",
                    "Growth Opportunities & Challenges"
                ]
            },
            "swot_analysis": {
                "description": "This section provides a structured analysis of the company's internal strengths and weaknesses, as well as external opportunities and threats it faces.",
                "key_topics": [
                    "Key Organizational Strengths",
                    "Operational & Strategic Weaknesses",
                    "Market & Growth Opportunities",
                    "External Threats & Challenges",
                    "Competitive Advantage Assessment"
                ]
            },
            "risk_assessment": {
                "description": "This section identifies and evaluates potential risks facing the company, including operational, financial, regulatory, market, and strategic risks.",
                "key_topics": [
                    "Operational & Business Risks",
                    "Financial & Credit Risks",
                    "Regulatory & Compliance Risks",
                    "Market & Competitive Risks",
                    "Strategic & Long-term Risks"
                ]
            },
            "strategic_recommendations": {
                "description": "This section provides actionable strategic recommendations for the company to enhance performance, address challenges, and capitalize on opportunities.",
                "key_topics": [
                    "Growth & Expansion Strategies",
                    "Operational Efficiency Improvements",
                    "Competitive Positioning Tactics",
                    "Financial Performance Enhancement",
                    "Risk Mitigation Approaches"
                ]
            },
            "technology_landscape": {
                "description": "This section examines the technological aspects of the company, including IT infrastructure, digital capabilities, innovation initiatives, and technology-driven opportunities.",
                "key_topics": [
                    "Technology Stack & Infrastructure",
                    "Digital Transformation Initiatives",
                    "Innovation Pipeline & R&D",
                    "Technology-driven Opportunities",
                    "Competitive Technology Benchmarking"
                ]
            },
            "esg_analysis": {
                "description": "This section evaluates the company's environmental, social, and governance practices, including sustainability initiatives, social responsibility, and corporate governance.",
                "key_topics": [
                    "Environmental Impact & Sustainability",
                    "Social Responsibility & Community Engagement",
                    "Corporate Governance Structure",
                    "ESG Metrics & Performance",
                    "Regulatory Compliance & Reporting"
                ]
            },
            "industry_benchmarking": {
                "description": "This section compares the company's performance against industry benchmarks and competitors across key operational and financial metrics.",
                "key_topics": [
                    "Financial Performance Benchmarking",
                    "Operational Efficiency Comparisons",
                    "Market Share & Growth Analysis",
                    "Product/Service Quality Metrics",
                    "Innovation & Strategic Positioning"
                ]
            },
            "leadership_assessment": {
                "description": "This section evaluates the company's leadership team, management structure, governance practices, and organizational culture.",
                "key_topics": [
                    "Executive Leadership Team Analysis",
                    "Board Composition & Governance",
                    "Management Track Record & Expertise",
                    "Succession Planning & Talent Development",
                    "Organizational Culture & Values"
                ]
            },
            # Default content for any other sections
            "default": {
                "description": "This section provides detailed analysis and insights relevant to understanding the company's position, performance, and strategic outlook.",
                "key_topics": [
                    "Comprehensive Analysis & Insights",
                    "Data-driven Observations",
                    "Strategic Implications",
                    "Key Findings & Takeaways",
                    "Forward-looking Perspectives"
                ]
            }
        }
        
        # Return content for the requested section or default if not found
        return section_content.get(section_id, section_content["default"])
        
    def generate_pdf(self, sections_data: List[PDFSection], output_path: str, metadata: Dict) -> Path:
        """Generate a PDF report from the provided section data and metadata."""
        try:
            # Process sections to extract metadata, format HTML, etc.
            processed_sections = []
            
            # Separate executive summary from other sections
            exec_summary = next((s for s in sections_data if s.id == "executive_summary"), None)
            regular_sections = [s for s in sections_data if s.id != "executive_summary"]
            
            # Process executive summary if it exists
            if exec_summary:
                # Extract metadata from the executive summary
                meta, content = self._extract_section_metadata(exec_summary.content)
                exec_summary.metadata.update(meta)
                
                # Process HTML content
                exec_summary.html_content = self._convert_markdown_to_html(content)
            
            # Process all other sections
            for section in regular_sections:
                # Extract metadata from section content
                meta, content = self._extract_section_metadata(section.content)
                section.metadata.update(meta)
                
                # Get static content for section cover instead of dynamic extraction
                static_content = self._get_static_section_content(section.id)
                
                # Use static key topics instead of dynamically extracted ones
                section.key_topics = static_content["key_topics"]
                
                # Keep the intro static too
                section.intro = f"<p>{static_content['description']}</p>"
                
                # Estimate reading time
                section.reading_time = self._estimate_reading_time(content)
                
                # Convert content to HTML
                section.html_content = self._convert_markdown_to_html(content)
                
                # Add to processed sections
                processed_sections.append(section)
            
            # Set up paths for assets - use the absolute path to the parent directory
            base_url = os.path.dirname(os.path.abspath(__file__))
            assets_dir = os.path.join(base_url, 'templates', 'assets')
            
            # Create absolute paths for the assets
            logo_path = os.path.abspath(os.path.join(assets_dir, 'supervity_logo.png'))
            favicon_path = os.path.abspath(os.path.join(assets_dir, 'supervity_favicon.png'))
            
            # Verify assets exist
            if not os.path.exists(logo_path):
                print(f"Warning: Logo not found at {logo_path}")
            if not os.path.exists(favicon_path):
                print(f"Warning: Favicon not found at {favicon_path}")
                
            print(f"Logo path: {logo_path}")
            print(f"Favicon path: {favicon_path}")
            
            # Prepare template context
            context = {
                'company_name': metadata.get('company', 'Company'),
                'language': metadata.get('language', 'English'),
                'generation_date': datetime.now().strftime('%Y-%m-%d'),
                'sections': processed_sections,
                'toc': self._generate_toc(processed_sections + ([exec_summary] if exec_summary else [])),
                'metadata': metadata,
                'executive_summary': exec_summary,
                'logo_path': logo_path,
                'favicon_path': favicon_path
            }
            
            # Render template
            html_content = self.template.render(**context)
            
            # For debugging, save the HTML content
            debug_html_path = os.path.splitext(output_path)[0] + '.debug.html'
            with open(debug_html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                print(f"Saved debug HTML to: {debug_html_path}")
            
            # Configure font and CSS
            font_config = FontConfiguration()
            css = CSS(string='''
                @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&family=Noto+Sans:wght@400;700&display=swap');
                
                /* Base styles */
                body { 
                    font-family: 'Noto Sans', 'Noto Sans JP', sans-serif;
                    line-height: 1.6;
                }
                
                /* Table of contents styles */
                .toc-container {
                    margin: 1em 0 2em 0;
                }
                
                .toc-title {
                    font-size: 18pt;
                    color: #000b37;
                    margin-bottom: 1.5em;
                    text-align: center;
                    font-weight: bold;
                    letter-spacing: 0.05em;
                    border-bottom: none;
                }
                
                .toc-entries {
                    padding: 0 1em;
                }
                
                .toc-entry {
                    margin: 0.8em 0;
                    position: relative;
                    display: flex;
                    align-items: baseline;
                    justify-content: space-between;
                }
                
                .toc-entry::after {
                    content: "";
                    position: absolute;
                    bottom: 0.5em;
                    left: 0;
                    right: 0;
                    border-bottom: 1px dotted #c7c7c7;
                    z-index: 1;
                }
                
                .toc-link {
                    font-weight: bold;
                    font-size: 12pt;
                    color: #000b37;
                    text-decoration: none;
                    background: white;
                    padding-right: 0.5em;
                    position: relative;
                    z-index: 2;
                    display: inline-block;
                    width: auto;
                    max-width: 80%;
                }
                
                .toc-link::after {
                    content: target-counter(attr(href), page);
                    position: absolute;
                    right: -4em;
                    background: white;
                    padding: 0 0.5em;
                    color: #474747;
                    z-index: 2;
                    font-weight: normal;
                }
                
                /* Enhanced table styles */
                .table-responsive {
                    margin: 1.5em 0;
                    width: 100%;
                    overflow-x: auto;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 0.5em;
                }
                
                .enhanced-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 1em;
                    font-size: 0.95em;
                }
                
                .enhanced-table, .enhanced-table * {
                    box-sizing: border-box;
                }
                
                .enhanced-table thead {
                    display: table-header-group;
                }
                
                .enhanced-table tbody {
                    display: table-row-group;
                }
                
                .enhanced-table tr {
                    display: table-row;
                }
                
                .enhanced-table th, .enhanced-table td {
                    display: table-cell;
                    border: 1px solid #dee2e6;
                    word-break: normal;
                    word-wrap: break-word;
                    vertical-align: middle;
                    max-width: 300px;
                    padding: 8px 12px;
                }
                
                .enhanced-table th {
                    background-color: #f0f2f5;
                    border-bottom: 2px solid #000b37;
                    text-align: left;
                    font-weight: 600;
                    color: #000b37;
                }
                
                .enhanced-table td {
                    background-color: #ffffff;
                }
                
                .enhanced-table tr:nth-child(even) td { 
                    background-color: #f9f9f9;
                }
                
                .enhanced-table tr:hover td { 
                    background-color: rgba(130, 137, 236, 0.1);
                }
                
                .enhanced-table .text-right {
                    text-align: right;
                }
                
                .enhanced-table .text-center {
                    text-align: center;
                }
                
                /* Manual tables (converted from markdown text) */
                .manual-table {
                    border: 2px solid #dee2e6;
                }
                
                .manual-table th,
                .manual-table td {
                    padding: 10px 12px;
                }
                
                /* Ensure tables break correctly between pages */
                table, tr, td, th, tbody, thead, tfoot {
                    page-break-inside: auto !important;
                }
                
                /* Force table to a new page if it would break */
                table { 
                }
                
                /* Enhanced list styles */
                .enhanced-list {
                    padding-left: 1.5em;
                    margin: 0.8em 0;
                    list-style-type: disc;
                }
                
                .enhanced-list-item {
                    margin-bottom: 0.3em;
                    text-align: left;
                }
                
                .nested-list {
                    padding-left: 1.5em;
                    margin: 0.5em 0;
                    list-style-type: circle;
                }
                
                .nested-list-item {
                    margin-bottom: 0.2em;
                }
                
                /* Section cover styling */
                .section-cover {
                    page-break-before: always;
                    page-break-after: always;
                    height: 29.7cm;
                    padding: 4cm 3cm;
                    position: relative;
                    background: linear-gradient(145deg, #f8f9fa 0%, #f1f1f1 100%);
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    text-align: center;
                }
                
                .section-cover::before {
                    content: "";
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 15px;
                    height: 100%;
                    background: linear-gradient(to bottom, #85c20b, #0056b3);
                    border-right: 1px solid rgba(0, 0, 0, 0.05);
                }
                
                .section-cover h2 {
                    font-size: 36pt;
                    margin-bottom: 2.5cm;
                    color: #000b37;
                    border: none;
                    font-weight: bold;
                    line-height: 1.2;
                    position: relative;
                    padding-bottom: 0.5cm;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }
                
                .section-cover h2::after {
                    content: "";
                    position: absolute;
                    bottom: 0;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 8cm;
                    height: 3px;
                    background: linear-gradient(90deg, #0056b3, #85c20b);
                }
                
                .section-cover .subsections {
                    margin: 0 auto;
                    text-align: left;
                    width: 80%;
                    max-width: 600px;
                    background: #ffffff;
                    padding: 1.5cm;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                }
                
                .section-cover .subsections h3 {
                    font-size: 18pt;
                    color: #0056b3;
                    margin-bottom: 1cm;
                    text-align: center;
                    border: none;
                    font-weight: normal;
                }
                
                .section-cover .subsections p {
                    text-align: center;
                    margin-bottom: 1.5cm;
                    font-size: 12pt;
                    color: #34495e;
                    line-height: 1.6;
                    font-style: italic;
                }
                
                .section-cover .key-topics {
                    margin-top: 1cm;
                    list-style-type: none;
                    padding: 0;
                }
                
                .section-cover .key-topics li {
                    margin: 0.5cm 0;
                    padding: 0.25cm 0.5cm;
                    background-color: #f8f9fa;
                    border-left: 3px solid #85c20b;
                    text-align: left;
                    color: #000b37;
                    font-size: 12pt;
                    border-radius: 3px;
                }
                
                .section-cover .reading-time {
                    margin-top: 3cm;
                    font-size: 12pt;
                    color: #7f8c8d;
                    font-style: italic;
                    background: #ffffff;
                    padding: 0.4cm 1cm;
                    border-radius: 50px;
                    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
                }
                
                .section-cover .reading-time-value {
                    font-weight: bold;
                    color: #0056b3;
                }
                
                /* Executive summary styling */
                .executive-summary {
                    margin: 2em 0;
                    padding: 2em;
                    background-color: #f8f9fa;
                    border-left: 6px solid #0056b3;
                    border-radius: 6px;
                    page-break-before: always;
                    page-break-after: always;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
                }
                
                .executive-summary-header {
                    margin-bottom: 1.5em;
                    border-bottom: 2px solid #dee2e6;
                    padding-bottom: 1em;
                }
                
                .executive-summary-label {
                    font-size: 2em;
                    font-weight: 700;
                    color: #0056b3;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }
                
                .executive-summary h3 {
                    color: #0056b3;
                    font-size: 1.4em;
                    margin-top: 1.8em;
                    margin-bottom: 1em;
                    font-weight: 600;
                    border-bottom: 1px solid #e9ecef;
                    padding-bottom: 0.5em;
                }
                
                .executive-summary p {
                    text-align: justify;
                    line-height: 1.6;
                    margin-bottom: 1em;
                }
                
                .executive-summary ul, .executive-summary ol {
                    margin-left: 1.5em;
                    margin-bottom: 1.5em;
                }
                
                .executive-summary li {
                    margin-bottom: 0.8em;
                }
                
                .executive-summary table {
                    width: 100%;
                    margin: 1.5em 0;
                    border-collapse: collapse;
                    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
                }
                
                .executive-summary table th {
                    background-color: #e9ecef;
                    font-weight: 600;
                    text-align: left;
                    padding: 0.8em;
                    border: 1px solid #dee2e6;
                    color: #0056b3;
                }
                
                .executive-summary table td {
                    padding: 0.8em;
                    border: 1px solid #dee2e6;
                    vertical-align: top;
                }
                
                .executive-summary strong {
                    color: #0056b3;
                    font-weight: 600;
                }
                
                .executive-summary-content {
                    margin-top: 1.5em;
                    line-height: 1.6;
                }
                
                .executive-summary-content h2, 
                .executive-summary-content h3, 
                .executive-summary-content h4 {
                    color: #0056b3;
                    margin-top: 1.5em;
                    margin-bottom: 0.8em;
                }
                
                .executive-summary-content ol {
                    counter-reset: item;
                    list-style-type: none;
                    margin-left: 0;
                    padding-left: 0;
                }
                
                .executive-summary-content ol li {
                    counter-increment: item;
                    margin-bottom: 1.2em;
                    padding-left: 2em;
                    position: relative;
                }
                
                .executive-summary-content ol li:before {
                    content: counter(item) ".";
                    position: absolute;
                    left: 0;
                    font-weight: bold;
                    color: #0056b3;
                }
            ''', font_config=font_config)
            
            # Generate PDF
            html = HTML(string=html_content, base_url=base_url)
            html.write_pdf(
                output_path,
                stylesheets=[css],
                presentational_hints=True,
                font_config=font_config
            )
            
            print(f"PDF generated successfully: {output_path}")
            return Path(output_path)
            
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

def process_markdown_files(output_dir: Path, company_name: str, language: str) -> Optional[Path]:
    """Process all markdown files in the markdown directory and generate a PDF."""
    try:
        markdown_dir = output_dir / 'markdown'
        pdf_dir = output_dir / 'pdf'
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Collect sections from markdown files
        sections = []
        
        # First, check if an executive summary exists
        exec_summary_path = markdown_dir / "executive_summary.md"
        has_exec_summary = exec_summary_path.exists()
        
        # Handle the executive summary first, if it exists
        if has_exec_summary:
            with open(exec_summary_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content.strip():
                exec_summary = PDFSection(
                    id="executive_summary",
                    title="Executive Summary",
                    content=content
                )
                sections.append(exec_summary)
                print(f"Including executive summary from {exec_summary_path}")
        
        # Use SECTION_ORDER to determine the correct order of sections
        for section_id, section_title in SECTION_ORDER:
            # Skip executive summary as we've already handled it
            if section_id == "executive_summary":
                continue
                
            file_path = markdown_dir / f"{section_id}.md"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if content.strip():  # Only include non-empty sections
                    section = PDFSection(
                        id=section_id,
                        title=section_title,
                        content=content
                    )
                    sections.append(section)
                    print(f"Including section: {section_id} ({section_title})")
        
        if not sections:
            print("No markdown files found or all files were empty.")
            return None
        
        # Generate PDF
        pdf_generator = EnhancedPDFGenerator()
        output_path = pdf_dir / f"{company_name}_{language}_Report.pdf"
        
        pdf_path = pdf_generator.generate_pdf(
            sections, 
            str(output_path), 
            {
                'title': f"{company_name} {language} Report",
                'company': company_name,
                'language': language
            }
        )
        
        return pdf_path
        
    except Exception as e:
        print(f"Error processing markdown files: {str(e)}")
        import traceback
        traceback.print_exc()
        return None 