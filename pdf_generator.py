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
from typing import Optional, Dict, List, Tuple
from config import SECTION_ORDER

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
        soup = BeautifulSoup(self._convert_markdown_to_html(content), 'html.parser')
        headings = soup.find_all(['h1', 'h2', 'h3'])
        topics = [h.get_text().strip() for h in headings[:max_topics]]
        return topics

    def _convert_markdown_to_html(self, content: str) -> str:
        """Convert markdown content to HTML with enhanced features."""
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
        
        # Find the H2/H3 'Sources' section and add a class to its container
        source_heading = soup.find(['h2', 'h3'], string=re.compile(r'^\s*Sources\s*$'))
        if source_heading:
            # Try to find the next sibling element that contains the list
            source_container = source_heading.find_next_sibling()
            if source_container:
                # Add class to the container for styling
                source_container['class'] = source_container.get('class', []) + ['sources-list']
        
        # Process links to ensure they're properly formatted
        for a_tag in soup.find_all('a'):
            href = a_tag.get('href', '')
            if href and len(href) > 80:  # If it's a very long URL
                # Ensure it has the word-wrap class
                a_tag['class'] = a_tag.get('class', []) + ['long-url']
        
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
            # Add section number for clarity
            toc_items.append(f'<li><span class="toc-section-number">{i}.</span> <a href="#{anchor}">{title}</a></li>')
        
        toc_items.append('</ul>')
        toc_items.append('</nav>')
        return '\n'.join(toc_items)

    def _extract_intro(self, content: str) -> str:
        """Extract the text content of the introduction paragraph."""
        # Convert MD to HTML first to handle potential formatting
        html_content = self._convert_markdown_to_html(content)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the first paragraph after any headings
        first_content_element = soup.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if first_content_element:
            first_p = first_content_element.find_next('p')
        else:
            first_p = soup.find('p')  # If no headings, just find the first p
        
        if first_p:
            return str(first_p)
        return "<p>This section provides detailed analysis and insights.</p>"

    def generate_pdf(self, sections: List[Dict], output_path: str, metadata: Dict = None) -> Path:
        """Generate a PDF report from the provided sections and metadata."""
        processed_sections = []
        
        for section in sections:
            content = section.get('content', '')
            section_metadata, content = self._extract_section_metadata(content)
            
            processed_section = {
                'id': section.get('id', ''),
                'title': section.get('title', ''),
                'content': self._convert_markdown_to_html(content),
                'metadata': section_metadata,
                'reading_time': self._estimate_reading_time(content),
                'key_topics': self._extract_key_topics(content),
                'intro': self._extract_intro(content),
                'anchor': f"section-{section.get('id', '')}"
            }
            
            if section.get('subsections'):
                processed_section['subsections'] = []
                for subsection in section['subsections']:
                    sub_content = subsection.get('content', '')
                    sub_metadata, sub_content = self._extract_section_metadata(sub_content)
                    
                    processed_subsection = {
                        'id': subsection.get('id', ''),
                        'title': subsection.get('title', ''),
                        'content': self._convert_markdown_to_html(sub_content),
                        'metadata': sub_metadata,
                        'reading_time': self._estimate_reading_time(sub_content),
                        'key_topics': self._extract_key_topics(sub_content),
                        'anchor': f"subsection-{subsection.get('id', '')}"
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