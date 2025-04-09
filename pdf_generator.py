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
from bs4 import BeautifulSoup
import re
from typing import Optional, Dict, List, Tuple, Any
from config import SECTION_ORDER, PDF_CONFIG
from pydantic import BaseModel

class PDFSection(BaseModel):
    """Model for a section in the PDF."""
    id: str
    title: str
    content: str
    html_content: str = ""
    intro: str = ""
    key_topics: List[str] = []

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
        
        # Initialize markdown with a robust set of extensions
        self.md = markdown.Markdown(extensions=[
            'extra',  # Includes tables, fenced_code, footnotes, etc.
            'meta',
            'codehilite',
            'admonition',
            'attr_list',
            'toc'
        ], extension_configs={
            'codehilite': {'css_class': 'highlight', 'guess_lang': False}
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
        return max(1, round(words / 200))  # Assuming 200 words per minute

    def _extract_key_topics(self, content: str, max_topics: int = 5) -> List[str]:
        """Extract key topics from the content based on heading frequency."""
        soup = BeautifulSoup(self._convert_markdown_to_html(content, section_id="topics"), 'html.parser')
        headings = soup.find_all(['h1', 'h2', 'h3'])
        topics = [h.get_text().strip() for h in headings[:max_topics]]
        return topics

    def _convert_markdown_to_html(self, content: str, section_id: str = "") -> str:
        """Convert markdown content to HTML with enhanced features.
        
        Args:
            content: The markdown content to convert
            section_id: Optional section ID to prefix anchor IDs to ensure uniqueness
        """
        # Use the initialized self.md instance
        self.md.reset()  # Reset state for each conversion
        html = self.md.convert(content)
        
        # Process tables for better styling
        soup = BeautifulSoup(html, 'html.parser')
        for table in soup.find_all('table'):
            table['class'] = table.get('class', []) + ['enhanced-table']
            if not table.find('thead'):
                first_row = table.find('tr')
                if first_row:
                    thead = soup.new_tag('thead')
                    thead.append(first_row.extract())
                    table.insert(0, thead)
        
        # Enhanced Sources section handling
        # Look for both "Sources" and "References" headings
        source_heading = soup.find(['h2', 'h3'], string=re.compile(r'^\s*(Sources|References)\s*$'))
        if source_heading:
            # Make sure the heading itself has the id 'sources' for direct linking
            source_heading['id'] = 'sources'
            
            # Try to find the next sibling elements that contain the source links
            source_container = source_heading.find_next_sibling()
            
            if source_container:
                # Mark the container as sources-list for styling
                source_container['class'] = source_container.get('class', []) + ['sources-list']
                
                # Handle case where sources are in a list (ideal)
                source_ul = source_container.find('ul')
                if source_ul:
                    source_ul['class'] = source_ul.get('class', []) + ['sources-list']
                    
                    # Process each list item for better formatting
                    for li in source_ul.find_all('li'):
                        # Ensure list items have proper spacing and formatting
                        li['class'] = li.get('class', []) + ['source-item']
                
                # Handle case where sources are just paragraphs with links (fallback)
                elif source_container.name == 'p':
                    # Try to improve the paragraph structure
                    text = source_container.get_text()
                    links = source_container.find_all('a')
                    
                    # If we have multiple links in one paragraph, try to fix formatting
                    if len(links) > 1:
                        # Create a new list to replace the paragraph
                        new_ul = soup.new_tag('ul')
                        new_ul['class'] = ['sources-list']
                        
                        # Process each link and create a list item
                        for link in links:
                            # Get the text after the link if any (annotation)
                            link_html = str(link)
                            link_idx = text.find(link.get_text())
                            
                            if link_idx >= 0:
                                end_idx = link_idx + len(link.get_text())
                                # Look for the next link or end of paragraph
                                next_link = text.find('[', end_idx)
                                if next_link < 0:
                                    next_link = len(text)
                                
                                # Extract annotation text
                                annotation = text[end_idx:next_link].strip()
                                
                                # Create a new list item
                                new_li = soup.new_tag('li')
                                new_li['class'] = ['source-item']
                                
                                # Add the link
                                new_li.append(link)
                                
                                # Add the annotation text
                                if annotation and annotation not in ['.', ',', ';', ':', '-']:
                                    annotation_node = soup.new_string(' ' + annotation)
                                    new_li.append(annotation_node)
                                    
                                new_ul.append(new_li)
                        
                        # Replace the paragraph with our new list
                        source_container.replace_with(new_ul)
                
                # Look for any following paragraphs that might also contain sources
                next_sibling = source_container.find_next_sibling()
                while next_sibling and next_sibling.name in ['p', 'ul']:
                    next_sibling['class'] = next_sibling.get('class', []) + ['sources-list']
                    next_sibling = next_sibling.find_next_sibling()
        
        # Process links to ensure they're properly formatted
        for a_tag in soup.find_all('a'):
            href = a_tag.get('href', '')
            # Check if it's a URL (not just an anchor)
            if href and ('http' in href or 'www.' in href):
                # If it's a very long URL, add long-url class
                if len(href) > 70:  # Threshold for "long" URLs
                    a_tag['class'] = a_tag.get('class', []) + ['long-url']
                    
                # Handle potential blank link text (showing raw URL)
                if not a_tag.text.strip() or a_tag.text.strip() == href:
                    # Truncate display text for very long URLs
                    if len(href) > 60:
                        display_text = href[:40] + '...' + href[-15:]
                        a_tag.string = display_text
        
        # Add .avoid-break class to elements that shouldn't break across pages
        for tag_name in ['table', 'figure', 'pre', 'blockquote']:
            for elem in soup.find_all(tag_name):
                elem['class'] = elem.get('class', []) + ['avoid-break']
        
        # Fix duplicate anchor IDs by prefixing with section_id if provided
        if section_id:
            for tag in soup.find_all(id=True):
                original_id = tag['id']
                # Skip if it's the sources section ID we just set
                if original_id == 'sources':
                    continue
                    
                # Only modify if it's not already prefixed
                if not original_id.startswith(f"{section_id}-"):
                    tag['id'] = f"{section_id}-{original_id}"
                    
                    # Update any internal links pointing to this anchor
                    for a_tag in soup.find_all('a', href=f"#{original_id}"):
                        a_tag['href'] = f"#{section_id}-{original_id}"
        
        return str(soup)

    def _generate_toc(self, sections: List[Dict]) -> str:
        """Generate a structured table of contents using section IDs."""
        toc_items = []
        toc_items.append('<nav class="toc-navigation">')
        toc_items.append('<ul>')
        
        for i, section in enumerate(sections, 1):
            title = section.get('title', f'Section {i}')
            section_id = section.get('id', '')
            anchor = f"section-{section_id}"
            # Add section number and use leader dots via CSS
            toc_items.append(f'<li><span class="toc-section-number">{i}.</span> <a href="#{anchor}">{title}</a></li>')
        
        toc_items.append('</ul>')
        toc_items.append('</nav>')
        return '\n'.join(toc_items)

    def _extract_intro(self, content: str) -> str:
        """Extract the HTML content of the introduction paragraph."""
        # Convert MD to HTML first to handle potential formatting
        html_content = self._convert_markdown_to_html(content, section_id="intro")
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the first paragraph after any headings
        first_content_element = soup.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if first_content_element:
            first_p = first_content_element.find_next('p')
        else:
            first_p = soup.find('p')  # If no headings, just find the first p
        
        if first_p:
            # Clean up the intro by removing any excessively long content
            # This keeps the intro concise for section covers
            intro_text = str(first_p)
            if len(intro_text) > 500:  # If intro is too long, truncate it
                soup_p = BeautifulSoup(intro_text, 'html.parser')
                text = soup_p.get_text()
                truncated = text[:450] + '...'
                return f"<p>{truncated}</p>"
            return intro_text
        
        return "<p>This section provides detailed analysis and insights.</p>"

    def _extract_html(self, section_content: str, section_id: str) -> Tuple[str, Dict, str]:
        """Extract HTML and metadata from markdown content."""
        # Convert Markdown to HTML
        html = markdown.markdown(
            section_content,
            extensions=[
                'markdown.extensions.tables',
                'markdown.extensions.fenced_code',
                'markdown.extensions.attr_list',
                'markdown.extensions.meta',
                'markdown.extensions.toc'
            ]
        )
        
        # Extract metadata
        metadata = {}
        soup = BeautifulSoup(html, 'html.parser')
        
        # Process tables to add classes and ensure proper styling
        tables = soup.find_all('table')
        for table in tables:
            table['class'] = table.get('class', []) + ['enhanced-table']
            
            # Add text alignment classes to cells if needed
            for cell in table.find_all(['th', 'td']):
                text = cell.get_text().strip()
                # Check if the cell contains mostly numbers
                if text and all(c.isdigit() or c in '.,-%$' for c in text.strip()):
                    cell['class'] = cell.get('class', []) + ['text-right']
                # Check for centered content markers
                elif text.startswith('^') and text.endswith('^'):
                    cell.string = text[1:-1]
                    cell['class'] = cell.get('class', []) + ['text-center']
            
            # Wrap table in figure for better styling and captions
            caption = table.find_previous_sibling('p')
            if caption and caption.get_text().strip().lower().startswith('table:'):
                caption_text = caption.get_text().strip()[6:].strip()
                caption.decompose()
                
                figure = soup.new_tag('figure')
                figure['class'] = 'table'
                table.wrap(figure)
                
                figcaption = soup.new_tag('figcaption')
                figcaption.string = caption_text
                table.insert_after(figcaption)
        
        # Process source sections to ensure proper formatting
        sources_headers = soup.find_all(['h2', 'h3'], string=lambda s: s and ('sources' in s.lower() or 'references' in s.lower()))
        for header in sources_headers:
            sources_section = header
            sources_div = soup.new_tag('div')
            sources_div['class'] = 'sources'
            
            # Move the header and all following elements until next header into sources div
            current = header
            elements = []
            while current and (current.name not in ['h2', 'h3'] or current is header):
                next_element = current.next_sibling
                elements.append(current)
                current = next_element
            
            # Ensure sources are in a proper list structure
            has_list = any(el.name == 'ul' for el in elements)
            
            if not has_list:
                # Find paragraphs that look like sources/links and convert to list
                source_paragraphs = [el for el in elements if el.name == 'p' and el.find('a')]
                if source_paragraphs:
                    ul = soup.new_tag('ul')
                    for p in source_paragraphs:
                        li = soup.new_tag('li')
                        li.append(p.contents)
                        ul.append(li)
                        if p in elements:
                            elements.remove(p)
                    elements.append(ul)
            
            # Move all elements to the sources div
            for el in elements:
                if el.parent:
                    el.extract()
                sources_div.append(el)
            
            # Add the sources div to the document
            if header.parent:
                header.parent.append(sources_div)
        
        # Use BeautifulSoup to extract metadata
        # Look for metadata in the form of "Key: Value" at the beginning of the document
        lines = section_content.strip().split('\n')
        in_metadata = True
        metadata_lines = []
        
        for line in lines:
            if in_metadata and ':' in line and not line.startswith('#'):
                metadata_lines.append(line)
            elif line.strip() == '':
                pass  # Skip empty lines in metadata block
            else:
                in_metadata = False
                
        for line in metadata_lines:
            key, value = line.split(':', 1)
            metadata[key.strip().lower()] = value.strip()
        
        # Extract intro paragraph
        intro_html = self._extract_intro(soup, section_id)
        
        # Add section and anchor IDs to headers for navigation
        headers = soup.find_all(['h2', 'h3', 'h4'])
        for i, header in enumerate(headers):
            header_id = f"{section_id}-h-{i}"
            header['id'] = header_id
            
            # Create anchor that can be linked to
            anchor = soup.new_tag('a')
            anchor['class'] = 'section-anchor'
            anchor['id'] = f"section-{header_id}"
            anchor['name'] = f"section-{header_id}"
            header.insert(0, anchor)
        
        # Process links to add appropriate classes and handle long URLs
        for link in soup.find_all('a'):
            href = link.get('href', '')
            link_text = link.get_text()
            
            # Skip anchors without href
            if not href:
                continue
            
            # Handle long URLs in text
            if link_text == href and len(link_text) > 40:
                link['class'] = link.get('class', []) + ['long-url']
            
            # Ensure external links open in new tab
            if href.startswith(('http', 'https', 'www')):
                link['target'] = '_blank'
                link['rel'] = 'noopener noreferrer'
        
        return str(soup), metadata, intro_html

    def generate_pdf(self, sections: List[Dict], output_path: str, metadata: Dict = None) -> Path:
        """Generate a PDF report from the provided sections and metadata."""
        processed_sections = []
        
        for section in sections:
            content = section.get('content', '')
            section_id = section.get('id', '')
            section_metadata, content = self._extract_section_metadata(content)
            
            # Pass section_id to ensure unique anchor IDs
            html_content = self._convert_markdown_to_html(content, section_id)
            
            processed_section = {
                'id': section_id,
                'title': section.get('title', ''),
                'content': html_content,
                'metadata': section_metadata,
                'reading_time': self._estimate_reading_time(content),
                'key_topics': self._extract_key_topics(content),
                'intro': self._extract_intro(content),
                'anchor': f"section-{section_id}"
            }
            
            if section.get('subsections'):
                processed_section['subsections'] = []
                for subsection in section['subsections']:
                    sub_content = subsection.get('content', '')
                    sub_id = subsection.get('id', '')
                    sub_metadata, sub_content = self._extract_section_metadata(sub_content)
                    
                    # Pass section_id + sub_id to ensure unique anchor IDs
                    sub_html = self._convert_markdown_to_html(sub_content, f"{section_id}-{sub_id}")
                    
                    processed_subsection = {
                        'id': sub_id,
                        'title': subsection.get('title', ''),
                        'content': sub_html,
                        'metadata': sub_metadata,
                        'reading_time': self._estimate_reading_time(sub_content),
                        'key_topics': self._extract_key_topics(sub_content),
                        'anchor': f"subsection-{section_id}-{sub_id}"
                    }
                    processed_section['subsections'].append(processed_subsection)
            
            processed_sections.append(processed_section)

        # Prepare template context
        context = {
            'title': metadata.get('title', 'Enhanced Report'),
            'company_name': metadata.get('company', ''),
            'language': metadata.get('language', ''),
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sections': processed_sections,
            'toc': self._generate_toc(processed_sections),
            'metadata': metadata or {}
        }

        # Render template and generate PDF
        html_content = self.template.render(**context)
        HTML(string=html_content).write_pdf(
            output_path,
            presentational_hints=True
        )
        
        return Path(output_path)

def process_markdown_files(base_dir: Path, company_name: str, language: str, template_path: Optional[str] = None) -> Path:
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
                sections.append({
                    'id': section_id,
                    'title': section_title,
                    'content': content
                })
    
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