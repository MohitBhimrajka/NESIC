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
            'toc': {'permalink': True},
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
        soup = BeautifulSoup(self._convert_markdown_to_html(content), 'html.parser')
        
        # Only consider h2 and h3 headings for key topics
        headings = soup.find_all(['h2', 'h3'])
        topics = []
        
        for heading in headings:
            # Skip sources/references sections
            text = heading.get_text().strip()
            if 'sources' in text.lower() or 'references' in text.lower():
                continue
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

    def _generate_toc(self, sections: List[PDFSection]) -> str:
        """Generate a structured table of contents with nested subsections."""
        toc_items = []
        toc_items.append('<nav class="toc-navigation">')
        toc_items.append('<ul class="toc-list">')
        
        for section_idx, section in enumerate(sections, 1):
            # Add main section
            section_id = f"section-{section.id}"
            toc_items.append(f'<li class="toc-item level-1">')
            toc_items.append(f'<span class="toc-number">{section_idx}.</span>')
            toc_items.append(f'<a href="#{section_id}">{section.title}</a>')
            
            # Process all subsections without limiting
            subsections = self._extract_key_topics(section.content)
            if subsections:
                toc_items.append('<ul class="toc-sublist">')
                for topic_idx, topic in enumerate(subsections, 1):
                    topic_id = f"{section.id}-h-{topic_idx-1}"  # Adjust index to match header IDs
                    toc_items.append(f'<li class="toc-item level-2">')
                    toc_items.append(f'<span class="toc-number">{section_idx}.{topic_idx}</span>')
                    toc_items.append(f'<a href="#{topic_id}">{topic}</a>')
                    toc_items.append('</li>')
                toc_items.append('</ul>')
            
            toc_items.append('</li>')
        
        toc_items.append('</ul>')
        toc_items.append('</nav>')
        return '\n'.join(toc_items)

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
        # Convert Markdown to HTML with expanded extensions
        self.md.reset()  # Reset the markdown parser state
        html = self.md.convert(section.content)
        
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
            sources_html = str(sources_div)
        
        # Update heading IDs and add to TOC
        headers = soup.find_all(['h2', 'h3', 'h4'])
        for idx, header in enumerate(headers):
            # Skip sources/references headers
            if any(word in header.get_text().lower() for word in ['sources', 'references']):
                continue
                
            header_id = f"{section.id}-h-{idx}"
            
            # Create anchor tag for the ID
            anchor = soup.new_tag('a')
            anchor['id'] = header_id
            anchor['class'] = ['section-anchor']
            
            # Wrap header content in a span
            header_content = soup.new_tag('span')
            header_content['class'] = ['section-title']
            
            # Move all content to the header_content span
            for content in header.contents:
                header_content.append(content)
            
            # Clear header and add our new structure
            header.clear()
            header.append(anchor)
            header.append(header_content)
            
            # Add section number for h2
            if header.name == 'h2':
                number_span = soup.new_tag('span')
                number_span['class'] = ['section-number']
                number_span.string = f"{idx + 1}. "
                header_content.insert(0, number_span)
        
        return str(soup), metadata, sources_html

    def generate_pdf(self, sections_data: List[PDFSection], output_path: str, metadata: Dict) -> Path:
        """Generate a PDF report from the provided section data and metadata."""
        processed_sections = []
        all_sources_html = []

        for section_data in sections_data:
            section_id = section_data.id
            raw_content = section_data.content

            # Split raw content into metadata, main markdown, and sources markdown
            section_metadata, main_markdown, sources_markdown = self._extract_metadata_and_split_sources(raw_content)

            # Convert main markdown to HTML
            main_html = self._convert_markdown_to_html(main_markdown, section_id)

            # Convert sources markdown to HTML (if any)
            sources_html = self._convert_markdown_to_html(sources_markdown, f"{section_id}-sources")
            if sources_html:
                all_sources_html.append(sources_html)  # Collect sources for final section

            processed_section = PDFSection(
                id=section_id,
                title=section_data.title,
                content=raw_content,  # Keep raw markdown if needed elsewhere
                html_content=main_html,
                source_list_html=sources_html,  # Store sources HTML separately
                intro=self._extract_intro(main_html),
                key_topics=self._extract_key_topics(main_html),
                metadata=section_metadata,
                reading_time=self._estimate_reading_time(main_markdown)
            )
            processed_sections.append(processed_section)

        # If we have sources, add them to the last section for the template to handle
        if all_sources_html and processed_sections:
            combined_sources = "\n".join(all_sources_html)
            processed_sections[-1].source_list_html = combined_sources

        # Get paths for logo and favicon
        template_dir = Path(self.template_dir)
        assets_dir = template_dir / 'assets'
        os.makedirs(assets_dir, exist_ok=True)
        
        # Define paths for PNG files
        logo_path = Path('supervity_logo.png')
        favicon_path = Path('supervity_favicon.png')
        
        # Copy PNG files to assets directory if they exist in workspace root
        if logo_path.exists():
            import shutil
            target_logo = assets_dir / 'supervity_logo.png'
            shutil.copy2(logo_path, target_logo)
            logo_path = target_logo
        else:
            # Fallback to SVG placeholder
            logo_path = assets_dir / 'supervity_logo.svg'
            logo_svg = '''<svg width="200" height="60" xmlns="http://www.w3.org/2000/svg">
                <text x="10" y="40" font-family="Arial" font-size="40" fill="#3498db">Supervity</text>
            </svg>'''
            with open(logo_path, 'w') as f:
                f.write(logo_svg)
        
        if favicon_path.exists():
            import shutil
            target_favicon = assets_dir / 'supervity_favicon.png'
            shutil.copy2(favicon_path, target_favicon)
            favicon_path = target_favicon
        else:
            # Fallback to SVG placeholder
            favicon_path = assets_dir / 'supervity_favicon.svg'
            favicon_svg = '''<svg width="24" height="24" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" fill="#3498db"/>
                <text x="8" y="17" font-family="Arial" font-size="14" fill="white">S</text>
            </svg>'''
            with open(favicon_path, 'w') as f:
                f.write(favicon_svg)

        # Prepare template context
        context = {
            'company_name': metadata.get('company', 'Company'),
            'language': metadata.get('language', 'English'),
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sections': processed_sections,
            'toc': self._generate_toc(processed_sections),
            'metadata': metadata,
            'logo_path': str(logo_path),
            'favicon_path': str(favicon_path)
        }

        # Render template and generate PDF
        final_html_content = self.template.render(**context)

        try:
            html = HTML(string=final_html_content, base_url=self.template_dir)
            # Define font config (consider making this configurable)
            font_config = FontConfiguration()
            css = CSS(string='''
                @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&family=Noto+Sans:wght@400;700&display=swap');
                
                /* Base styles */
                body { 
                    font-family: 'Noto Sans', 'Noto Sans JP', sans-serif;
                    line-height: 1.6;
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
        """Extract YAML frontmatter, main content, and source list from raw markdown."""
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

        # 2. Split content and sources
        # Find the last occurrence of a potential "Sources" heading
        source_heading_patterns = [
            r'\n## \s*Sources\s*\n',
            r'\n### \s*Sources\s*\n',
            r'\n## \s*References\s*\n',
            r'\n### \s*References\s*\n'
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

        if split_point != -1:
            main_content = content_to_process[:split_point].strip()
            # Include the heading marker in the sources content for rendering
            sources_content = source_heading_marker + '\n' + content_to_process[split_point + len(source_heading_marker):].strip()
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