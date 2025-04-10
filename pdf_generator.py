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
    html_content: str = "" # Processed HTML content (excluding sources)
    source_list_html: str = "" # HTML for the sources list for this section
    intro: str = ""
    key_topics: List[str] = []
    metadata: Dict = {} # YAML frontmatter metadata
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
        """Extract key topics from the content based on headings.
        
        This extracts the subsection headings (h2, h3) from the content to build
        a table of contents. It skips any headings related to sources/references.
        
        Args:
            content: The markdown content to extract topics from
            max_topics: Optional maximum number of topics to extract
            
        Returns:
            List of topic strings
        """
        # First convert the markdown to HTML to get proper heading structure
        temp_html = self._convert_markdown_to_html(content)
        soup = BeautifulSoup(temp_html, 'html.parser')
        
        # Only consider h2 and h3 headings for key topics
        # First h2 is usually the section title, so skip it
        headings = soup.find_all(['h2', 'h3'])
        topics = []
        
        # Skip the first h2 which is the section title
        starting_index = 0
        if headings and headings[0].name == 'h2':
            starting_index = 1
        
        for heading in headings[starting_index:]:
            # Skip sources/references sections
            text = heading.get_text().strip()
            if ('sources' in text.lower() or 'references' in text.lower() or 
                'source list' in text.lower()):
                continue
            
            # Remove any debug spans we added
            for debug_span in heading.find_all(class_='header-debug'):
                debug_span.extract()
                
            # Get the clean text
            topics.append(text)
            
            # Only limit if max_topics is specified
            if max_topics and len(topics) >= max_topics:
                break
        
        return topics

    def _convert_markdown_to_html(self, content: str, section_id: str = "") -> str:
        """Convert markdown content to HTML with styling enhancements."""
        if not content:
            return ""

        self.md.reset()
        html = self.md.convert(content)
        soup = BeautifulSoup(html, 'html.parser')

        # Add styling classes to tables
        for table in soup.find_all('table'):
            table['class'] = table.get('class', []) + ['enhanced-table']
            
            # Ensure table has thead for multi-page tables
            rows = table.find_all('tr')
            if rows and not table.find('thead') and not rows[0].find_parent('thead'):
                thead = soup.new_tag('thead')
                thead.append(rows[0])
                table.insert(0, thead)
                
                # If we moved a th row to thead, create tbody
                if not table.find('tbody'):
                    tbody = soup.new_tag('tbody')
                    for row in rows[1:]:
                        tbody.append(row)
                    table.append(tbody)
            
            # Basic auto-alignment
            for cell in table.find_all(['th', 'td']):
                text = cell.get_text().strip()
                if text and re.match(r'^[\d,.\-%$¥€£]+$', text.replace('(', '').replace(')', '')): # Check if primarily numeric/currency
                    cell['class'] = cell.get('class', []) + ['text-right']

        # Add page break avoidance classes (but not to tables)
        for tag_name in PDF_CONFIG['STYLING'].get('AVOID_PAGE_BREAK_ELEMENTS', []):
            if tag_name != 'table':  # Skip tables to allow page breaks
                for elem in soup.find_all(tag_name):
                    elem['class'] = elem.get('class', []) + ['avoid-break']

        # Process links to ensure they're properly formatted
        max_url_len = PDF_CONFIG['SOURCES'].get('MAX_URL_DISPLAY_LENGTH', 60)
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            text = a_tag.get_text().strip()
            if text == href and len(href) > max_url_len:
                # Truncate intelligently
                display_text = href[:max_url_len//2 - 2] + '...' + href[-(max_url_len//2 - 2):]
                a_tag.string = display_text
                a_tag['class'] = a_tag.get('class', []) + ['long-url']

        return str(soup)

    def _generate_toc(self, sections):
        """Generate a properly formatted and hyperlinked table of contents."""
        if not sections:
            return ""
            
        toc_html = '<div class="toc-container">\n'
        toc_html += '<h2 class="toc-title">Table of Contents</h2>\n'
        toc_html += '<div class="toc-entries">\n'
        
        for idx, section in enumerate(sections, 1):
            # Create section entry with proper hyperlink
            # Use section-{idx} as the anchor, which matches the IDs in the template
            section_id = f"section-{section.id}"
            section_title = section.title.strip()
            
            toc_html += f'<div class="toc-entry">\n'
            toc_html += f'  <a href="#{section_id}" class="toc-link">{section_title}</a>\n'
            
            # Handle subsections if they exist (using hasattr to check)
            if hasattr(section, 'subsections') and section.subsections:
                toc_html += '  <div class="toc-subsections">\n'
                
                for sub_idx, subsection in enumerate(section.subsections, 1):
                    subsection_id = f"{section_id}-sub-{sub_idx}"
                    subsection_title = subsection.title.strip()
                    
                    toc_html += f'    <div class="toc-subsection">\n'
                    toc_html += f'      <a href="#{subsection_id}" class="toc-sublink">{subsection_title}</a>\n'
                    toc_html += f'    </div>\n'
                
                toc_html += '  </div>\n'
            
            toc_html += '</div>\n'
        
        toc_html += '</div>\n</div>\n'
        
        return toc_html
        
    def _process_sections(self, sections):
        """
        Process sections for the report, adding IDs and handling subsections.
        """
        processed_sections = []
        section_counter = 0
        
        for section in sections:
            section_counter += 1
            # Ensure the section ID is consistent with what the template expects
            if not hasattr(section, "id") or not section.id:
                section.id = f"section-{section_counter}"
            
            # Extract metadata, main content and sources separately
            metadata, main_content, sources_content = self._extract_metadata_and_split_sources(section.content)
            
            # Update section with extracted metadata
            section.metadata.update(metadata)
            
            # Process the main content of the section
            if main_content:
                # Extract key topics for the section cover
                section.key_topics = self._extract_key_topics(main_content, max_topics=5)
                
                # Estimate reading time
                section.reading_time = self._estimate_reading_time(main_content)
                
                # Extract introduction paragraph
                section.intro = self._extract_intro(main_content)
                
                # Convert main content to HTML
                main_html, _, _ = self._extract_html(section)
                
                # Add citation links to HTML
                main_html = self.hyperlink_citations(main_html, section.id)
                
                # Set the HTML content for the section
                section.html_content = main_html
            
            # Process sources content if available
            if sources_content:
                sources_html = self._convert_markdown_to_html(sources_content)
                section.source_list_html = self.format_sources_html(sources_html, section.id)
            
            # Process subsections if they exist
            # (Note: Current implementation doesn't handle subsections in PDFSection objects)
            
            processed_sections.append(section)
        
        return processed_sections

    def _extract_intro(self, content: str) -> str:
        """Extract the introduction paragraph from the content."""
        # Split content into lines
        lines = content.strip().split('\n')
        intro_lines = []
        
        # Skip metadata and empty lines at the start
        i = 0
        while i < len(lines) and (not lines[i].strip() or ':' in lines[i]):
            i += 1
            
        # Skip headers
        while i < len(lines) and lines[i].strip().startswith('#'):
            i += 1
            
        # Collect lines until we hit a header or end of content
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('#') or not line:
                break
            intro_lines.append(line)
            i += 1
            
        if not intro_lines:
            return "<p>This section provides detailed analysis and insights.</p>"
            
        # Convert the intro lines to HTML
        intro_content = ' '.join(intro_lines)
        intro_html = markdown.markdown(intro_content)
        
        return intro_html

    def _extract_html(self, section: PDFSection) -> Tuple[str, Dict, str]:
        """Extract HTML and metadata from markdown content."""
        # First extract metadata and content
        content = section.content
        
        # Convert Markdown to HTML with expanded extensions
        self.md.reset()  # Reset the markdown parser state
        html = self.md.convert(content)
        
        # Extract metadata from markdown meta
        metadata = getattr(self.md, 'Meta', {})
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Process tables with enhanced styling
        tables = soup.find_all('table')
        for table in tables:
            table['class'] = table.get('class', []) + ['enhanced-table']
            
            # Enhanced table styling
            if table.find('thead'):
                table['class'].append('has-header')
             
            # Add zebra striping class if more than 3 rows
            if len(table.find_all('tr')) > 3:
                table['class'].append('zebra-stripe')
             
            # Add responsive wrapper
            wrapper = soup.new_tag('div')
            wrapper['class'] = ['table-responsive']
            table.wrap(wrapper)
 
        # Extract sources section
        sources_html = ""
        sources_header = soup.find(['h2', 'h3'], string=lambda s: s and ('sources' in s.lower() or 'references' in s.lower()))
        if sources_header:
            sources_div = soup.new_tag('div')
            sources_div['class'] = ['sources-section']
            sources_div['id'] = f"{section.id}-sources" # Add unique ID to sources section
             
            # Collect all elements until next header of same level or higher
            current = sources_header
            while current:
                next_sibling = current.next_sibling
                if (next_sibling and next_sibling.name and 
                    next_sibling.name[0] == 'h' and 
                    int(next_sibling.name[1]) <= int(sources_header.name[1])):
                    break
                if current != sources_header:  # Don't extract the header itself yet
                    current.extract()
                    sources_div.append(current)
                current = next_sibling
             
            # Remove the header from the main content
            sources_header.extract()
            # Add the header back to the sources_div with a unique ID
            sources_header['id'] = f"{section.id}-sources-header"
            sources_html = str(sources_div)
         
        # Update heading IDs and add to TOC with consistent pattern
        headers = soup.find_all(['h2', 'h3', 'h4'])
        for idx, header in enumerate(headers):
            # Skip sources/references headers
            if any(word in header.get_text().lower() for word in ['sources', 'references']):
                continue
                 
            # Use section ID and header index for a unique, predictable ID
            # Format: section-id-h-index (e.g., basic-h-0)
            header_id = f"{section.id}-h-{idx}"
            
            # Simply set the ID directly on the header element
            header['id'] = header_id
            
            # Remove any existing debug spans
            for debug_span in header.find_all(class_='header-debug'):
                debug_span.extract()
            
            # Remove any ID text that might be visible
            header_text = header.get_text().strip()
            if 'ID:' in header_text:
                # Extract just the title part (before the ID info)
                clean_title = re.sub(r'ID:.*$', '', header_text).strip()
                # Clear the header content
                header.clear()
                
                # Add section number for h2 if applicable
                if header.name == 'h2':
                    number_span = soup.new_tag('span')
                    number_span['class'] = ['section-number']
                    number_span.string = f"{idx + 1}. "
                    header.append(number_span)
                
                # Add the clean title
                header.append(clean_title)
                continue
            
            # Handle existing numbering
            # Remove any existing numbers at start of header text
            if re.match(r'^\d+(\.\d+)*\.\s+', header_text):
                # Extract just the title part (after the numbering)
                clean_title = re.sub(r'^\d+(\.\d+)*\.\s+', '', header_text)
                # Clear the header content
                header.clear()
                
                # Add section number for h2 with a span
                if header.name == 'h2':
                    number_span = soup.new_tag('span')
                    number_span['class'] = ['section-number']
                    number_span.string = f"{idx + 1}. "
                    header.append(number_span)
                
                # Add the clean title
                header.append(clean_title)
            else:
                # If no existing numbering, add section numbers only for h2
                if header.name == 'h2':
                    # Need to clear and rebuild to insert at beginning
                    header_content = header.get_text()
                    header.clear()
                    number_span = soup.new_tag('span')
                    number_span['class'] = ['section-number']
                    number_span.string = f"{idx + 1}. "
                    header.append(number_span)
                    header.append(header_content)
         
        return str(soup), metadata, sources_html
        
    def hyperlink_citations(self, html: str, section_id: str) -> str:
        """Hyperlink inline citations to their corresponding sources.
        
        This function finds citation markers [SSx] in the text and converts them
        to links that point to the corresponding source in the sources section.
        
        Args:
            html: The HTML content to process
            section_id: The ID of the current section to scope citations
            
        Returns:
            HTML content with citation markers converted to links
        """
        pattern = re.compile(r'\[SS(\d+)\]')
        
        # Use a custom replacement function to add debug info
        def replace_citation(match):
            citation_id = match.group(1)
            target_id = f"{section_id}-source-SS{citation_id}"
            return f'<a href="#{target_id}" class="citation-link" data-source="{section_id}-source-SS{citation_id}">[SS{citation_id}]</a>'
            
        # Apply the replacements
        return pattern.sub(replace_citation, html)
        
    def format_sources_html(self, sources_html, section_id):
        """Format sources as a proper list with IDs for each source."""
        if not sources_html.strip():
            return ""
            
        soup = BeautifulSoup(sources_html, 'html.parser')
        
        # Create a new sources container
        sources_container = BeautifulSoup('<div class="sources-section"><div class="sources-list"></div></div>', 'html.parser')
        sources_list = sources_container.find(class_="sources-list")
        
        # Process the source content to extract all possible source items
        source_entries = []
        
        # Method 1: Try to find existing list items
        li_elements = soup.find_all('li')
        if li_elements:
            for li in li_elements:
                source_entries.append(li.get_text().strip())
        
        # Method 2: Try to parse sources from text with asterisks
        if not source_entries:
            text = soup.get_text()
            if '*' in text:
                source_entries = [s.strip() for s in text.split('*') if s.strip()]
        
        # Method 3: Try to parse sources from numbered lines
        if not source_entries:
            text = soup.get_text()
            lines = text.split('\n')
            in_source = False
            current_source = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    if current_source:
                        source_entries.append(' '.join(current_source))
                        current_source = []
                    continue
                
                # Check if line starts a new numbered source
                if re.match(r'^\d+\.', line) or re.match(r'^\[\w+\]', line):
                    # Save previous source if exists
                    if current_source:
                        source_entries.append(' '.join(current_source))
                        current_source = []
                    
                    current_source.append(line)
                    in_source = True
                elif in_source:
                    # Continue with the current source
                    current_source.append(line)
            
            # Add the last source if there is one
            if current_source:
                source_entries.append(' '.join(current_source))
        
        # Method 4: Try plain text split by line breaks
        if not source_entries:
            text = soup.get_text()
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if lines:
                source_entries = lines
        
        # Method 5: Just use the entire text as one source if nothing else worked
        if not source_entries:
            text = soup.get_text().strip()
            if text:
                source_entries = [text]
        
        # Create consistent formatted list items
        for idx, entry in enumerate(source_entries, 1):
            if not entry or entry.lower() in ['sources', 'references', 'source list']:
                continue
                
            source_id = f"{section_id}-source-{idx}"
            
            # Check if this source contains a citation marker [SSx]
            citation_match = re.search(r'\[SS(\d+)\]', entry)
            if citation_match:
                source_id = f"{section_id}-source-SS{citation_match.group(1)}"
            
            # Create the LI element
            li_tag = soup.new_tag('li')
            li_tag['id'] = source_id
            li_tag['class'] = ['source-item']
            
            # If the entry starts with a number like "1. ", remove it
            entry_text = re.sub(r'^\d+\.\s+', '', entry).strip()
            
            # Process any URLs in the text to make them clickable
            url_pattern = r'https?://[^\s)"]+'
            urls = re.findall(url_pattern, entry_text)
            
            if urls:
                # Replace URLs with hyperlinks
                for url in urls:
                    hyperlink = soup.new_tag('a')
                    hyperlink['href'] = url
                    hyperlink['class'] = ['source-url']
                    hyperlink['target'] = '_blank'  # Open in new tab
                    hyperlink.string = url
                    
                    # Replace URL in the text with the hyperlink
                    entry_text = entry_text.replace(url, str(hyperlink))
                
                # Set the content with hyperlinks
                li_tag.append(BeautifulSoup(entry_text, 'html.parser'))
            else:
                # Just set the text content
                li_tag.string = entry_text
                
            sources_list.append(li_tag)
        
        # Only return non-empty sources
        if sources_list.find_all('li'):
            return str(sources_container)
        else:
            return ""

    def generate_pdf(self, sections_data: List[PDFSection], output_path: str, metadata: Dict) -> Path:
        """Generate a PDF report from the provided section data and metadata."""
        processed_sections = self._process_sections(sections_data)

        # Get paths for logo and favicon
        template_dir = Path(self.template_dir)
        assets_dir = template_dir / 'assets'
        os.makedirs(assets_dir, exist_ok=True)
        
        # Directly use the assets in templates/assets
        logo_path = assets_dir / 'supervity_logo.png'
        favicon_path = assets_dir / 'supervity_favicon.png'
        
        # Use proper URLs for WeasyPrint
        logo_url = f"templates/assets/supervity_logo.png"
        favicon_url = f"templates/assets/supervity_favicon.png"
        
        print(f"Using logo URL: {logo_url}")
        print(f"Using favicon URL: {favicon_url}")

        # Prepare template context
        context = {
            'company_name': metadata.get('company', 'Company'),
            'language': metadata.get('language', 'English'),
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sections': processed_sections,
            'toc': self._generate_toc(processed_sections),
            'metadata': metadata,
            'logo_path': logo_url,
            'favicon_path': favicon_url
        }

        # Render template and generate PDF
        final_html_content = self.template.render(**context)

        try:
            # Get the base directory for proper resource resolution
            base_url = os.path.dirname(os.path.abspath(__file__))
            print(f"Using base URL: {base_url}")
            
            html = HTML(string=final_html_content, base_url=base_url)
            # Define font config (consider making this configurable)
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
                }
                
                .toc-link::after {
                    content: target-counter(attr(href), page);
                    position: absolute;
                    right: -3em;
                    background: white;
                    padding-left: 0.5em;
                    color: #474747;
                    z-index: 2;
                }
                
                .toc-subsections {
                    margin-left: 2em;
                    margin-top: 0.5em;
                }
                
                .toc-subsection {
                    margin: 0.4em 0;
                    position: relative;
                }
                
                .toc-subsection::after {
                    content: "";
                    position: absolute;
                    bottom: 0.3em;
                    left: 0;
                    right: 0;
                    border-bottom: 1px dotted #c7c7c7;
                    z-index: 1;
                }
                
                .toc-sublink {
                    font-size: 10pt;
                    color: #474747;
                    text-decoration: none;
                    background: white;
                    padding-right: 0.5em;
                    position: relative;
                    z-index: 2;
                }
                
                .toc-sublink::after {
                    content: target-counter(attr(href), page);
                    position: absolute;
                    right: -3em;
                    background: white;
                    padding-left: 0.5em;
                    color: #474747;
                    z-index: 2;
                }
                
                /* Enhanced table styles */
                .table-responsive {
                    width: 100%;
                    overflow-x: auto;
                    margin-bottom: 1em;
                }
                
                .enhanced-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 1em;
                }
                
                .enhanced-table.has-header thead {
                    background-color: #f5f5f5;
                }
                
                .enhanced-table.zebra-stripe tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                
                .enhanced-table th,
                .enhanced-table td {
                    padding: 0.75em;
                    border: 1px solid #ddd;
                }
                
                .enhanced-table .text-right {
                    text-align: right;
                }
                
                .enhanced-table .text-center {
                    text-align: center;
                }
                
                /* Table figure and caption styles */
                .table-figure {
                    margin: 2em 0;
                }
                
                .table-figure figcaption {
                    font-style: italic;
                    text-align: center;
                    margin-top: 0.5em;
                    color: #666;
                }
                
                /* Definition list styles */
                .definition-list {
                    margin: 1em 0;
                    padding: 0;
                }
                
                .definition-list .term {
                    font-weight: bold;
                    margin-top: 1em;
                }
                
                .definition-list .definition {
                    margin-left: 2em;
                    margin-bottom: 1em;
                }
                
                /* Footnote styles */
                .enhanced-footnotes {
                    margin-top: 2em;
                    padding-top: 1em;
                    border-top: 1px solid #ddd;
                }
                
                .enhanced-footnotes::before {
                    content: "Footnotes";
                    font-weight: bold;
                    display: block;
                    margin-bottom: 1em;
                }
                
                .footnote-item {
                    font-size: 0.9em;
                    color: #666;
                    margin-bottom: 0.5em;
                }
                
                .footnote-item a {
                    color: #0066cc;
                    text-decoration: none;
                }
                
                .footnote-item a:hover {
                    text-decoration: underline;
                }
                
                /* Sources list styling improvements */
                .sources-list {
                    list-style: none;
                    padding: 0;
                    margin: 0.5em 0;
                }
                
                .sources-list li {
                    position: relative;
                    padding: 0.4em 0;
                    margin-bottom: 0.6em;
                    padding-left: 1em;
                    border-left: 2px solid rgba(133, 194, 11, 0.3);
                }
                
                .sources-list li:target {
                    background-color: rgba(130, 137, 236, 0.1);
                    border-left-color: #8289ec;
                    padding: 0.6em 0.6em 0.6em 1em;
                    border-radius: 0 3px 3px 0;
                    transition: background-color 0.3s ease;
                }
                
                .source-url {
                    color: #8289ec;
                    text-decoration: none;
                    border-bottom: 1px dotted #8289ec;
                    transition: color 0.2s, border-bottom 0.2s;
                    word-break: break-all;
                }
                
                .source-url:hover {
                    color: #000b37;
                    border-bottom: 1px solid #000b37;
                }
                
                .sources-section h3 {
                    margin-top: 1.5em;
                    color: #000b37;
                    font-size: 14pt;
                    padding-bottom: 0.3em;
                    border-bottom: 1px solid rgba(133, 194, 11, 0.3);
                }
                
                /* Permalink styles for TOC */
                .headerlink {
                    font-size: 0.8em;
                    margin-left: 0.5em;
                    color: #999;
                    text-decoration: none;
                }
                
                .headerlink:hover {
                    color: #0066cc;
                }
            ''', font_config=font_config)

            html.write_pdf(
                output_path,
                stylesheets=[css],  # Apply CSS
                presentational_hints=True,  # Allow HTML styling attributes
                font_config=font_config
            )
            print(f"PDF generated successfully: {output_path}")
            return Path(output_path)
        except Exception as e:
            print(f"Error during WeasyPrint PDF generation: {e}")
            # Optionally write the final HTML to a file for debugging
            debug_html_path = Path(output_path).with_suffix('.debug.html')
            with open(debug_html_path, 'w', encoding='utf-8') as f_debug:
                f_debug.write(final_html_content)
            print(f"Debug HTML saved to: {debug_html_path}")
            raise  # Re-raise the exception

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
        return content

    def _extract_metadata_and_split_sources(self, raw_content: str) -> Tuple[Dict, str, str]:
        """Extract YAML frontmatter, main content, and source list from raw markdown.
        
        This function:
        1. Extracts any YAML frontmatter at the beginning of the content
        2. Splits the content into main section and sources section
        3. Returns the metadata and both content parts
        
        Sources are identified by looking for a heading with "Sources" or "References"
        """
        metadata = {}
        main_content = ""
        sources_content = ""

        cleaned_content = self._cleanup_raw_markdown(raw_content)

        # 1. Extract YAML frontmatter (if present)
        content_to_process = cleaned_content
        if cleaned_content.strip().startswith('---'):
            parts = cleaned_content.split('---', 2)
            if len(parts) >= 3:
                try:
                    frontmatter = parts[1]
                    loaded_meta = yaml.safe_load(frontmatter)
                    metadata = loaded_meta if isinstance(loaded_meta, dict) else {}
                    content_to_process = parts[2].strip()
                except yaml.YAMLError:
                    print("Could not parse YAML frontmatter. Treating as content.")
                    content_to_process = cleaned_content # Process everything if YAML fails

        # 2. Split content and sources - more robust pattern matching
        # Find the last occurrence of a potential "Sources" heading
        source_heading_patterns = [
            r'\n## \s*Sources\s*\n',
            r'\n### \s*Sources\s*\n',
            r'\n## \s*References\s*\n',
            r'\n### \s*References\s*\n',
            r'\n## \s*Source List\s*\n',
            r'\n### \s*Source List\s*\n',
            r'\n## \s*Sources:\s*\n',
            r'\n### \s*Sources:\s*\n',
            r'\n## \s*References:\s*\n',
            r'\n### \s*References:\s*\n'
        ]
        split_point = -1
        source_heading_marker = "## Sources" # Default marker

        for pattern in source_heading_patterns:
            matches = list(re.finditer(pattern, content_to_process, re.IGNORECASE | re.MULTILINE))
            if matches:
                # Take the last match
                last_match = matches[-1]
                split_point = last_match.start()
                source_heading_marker = last_match.group(0).strip() # Get the actual heading found
                break # Found the last heading

        # Fallback approach - look for a line just having "Sources" or "References"
        if split_point == -1:
            lines = content_to_process.split("\n")
            for i, line in enumerate(lines):
                if line.strip().lower() in ["sources", "references", "source list", "sources:", "references:"]:
                    # Found a potential standalone sources marker
                    split_point = content_to_process.find(line)
                    source_heading_marker = "## Sources"  # Use a standard h2 heading
                    break

        if split_point != -1:
            main_content = content_to_process[:split_point].strip()
            # Ensure source heading is properly formatted with consistent spacing
            sources_content = source_heading_marker + '\n\n' + content_to_process[split_point + len(source_heading_marker):].strip()
        else:
            # If no Sources heading found, assume all is main content
            main_content = content_to_process.strip()
            sources_content = "" # No sources found in this section

        return metadata, main_content, sources_content

def process_markdown_files(base_dir: Path, company_name: str, language: str, template_path: Optional[str] = None) -> Optional[Path]:
    """Process all markdown files in the markdown directory and generate a PDF."""
    markdown_dir = base_dir / 'markdown'
    pdf_dir = base_dir / 'pdf'
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Collect sections from markdown files
    sections = []
    
    # Use SECTION_ORDER to determine the correct order of sections
    for section_id, section_title in SECTION_ORDER:
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
    
    if not sections:
        print("No markdown files found or all files were empty.")
        return None
    
    # Generate PDF
    pdf_generator = EnhancedPDFGenerator(template_path)
    output_path = pdf_dir / f"{company_name}_{language}_Report.pdf"
    
    return pdf_generator.generate_pdf(
        sections, 
        str(output_path), 
        {
            'title': f"{company_name} {language} Report",
            'company': company_name,
            'language': language
        }
    ) 