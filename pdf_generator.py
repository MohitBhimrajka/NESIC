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
        
        # Initialize markdown with extensions
        self.md = markdown.Markdown(extensions=[
            'meta',
            'tables',
            'fenced_code',
            'codehilite',
            'attr_list',
            'def_list',
            'footnotes',
            'admonition'
        ])

    def _extract_section_metadata(self, content: str) -> Tuple[Dict, str]:
        """Extract YAML frontmatter and content from a markdown section."""
        metadata = {}
        if content.startswith('---'):
            try:
                _, frontmatter, markdown_content = content.split('---', 2)
                metadata = yaml.safe_load(frontmatter)
                return metadata, markdown_content.strip()
            except:
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
        md = markdown.Markdown(extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.tables',
            'markdown.extensions.toc',
            'markdown.extensions.attr_list',
            'markdown.extensions.def_list',
            'markdown.extensions.footnotes',
            'markdown.extensions.codehilite',
            'markdown.extensions.meta'
        ])
        html = md.convert(content)
        
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
        
        # Process source sections
        for div in soup.find_all('div', class_='source'):
            div['class'] = div.get('class', []) + ['source-section']
        
        return str(soup)

    def _generate_toc(self, sections: List[Dict]) -> str:
        """Generate a structured table of contents."""
        toc = ['<nav class="toc">']
        toc.append('<h2>Table of Contents</h2>')
        toc.append('<ul>')
        
        for section in sections:
            title = section.get('title', '')
            anchor = f"section-{hash(title) & 0xFFFFFFFF}"
            toc.append(f'<li><a href="#{anchor}">{title}</a>')
            
            if section.get('subsections'):
                toc.append('<ul>')
                for subsection in section['subsections']:
                    sub_title = subsection.get('title', '')
                    sub_anchor = f"subsection-{hash(sub_title) & 0xFFFFFFFF}"
                    toc.append(f'<li><a href="#{sub_anchor}">{sub_title}</a></li>')
                toc.append('</ul>')
            
            toc.append('</li>')
        
        toc.append('</ul>')
        toc.append('</nav>')
        return '\n'.join(toc)

    def generate_pdf(self, sections: List[Dict], output_path: str, metadata: Dict = None) -> None:
        """Generate a PDF report from the provided sections and metadata."""
        processed_sections = []
        
        for section in sections:
            content = section.get('content', '')
            section_metadata, content = self._extract_section_metadata(content)
            
            processed_section = {
                'title': section.get('title', ''),
                'content': self._convert_markdown_to_html(content),
                'metadata': section_metadata,
                'reading_time': self._estimate_reading_time(content),
                'key_topics': self._extract_key_topics(content),
                'anchor': f"section-{hash(section.get('title', '')) & 0xFFFFFFFF}"
            }
            
            if section.get('subsections'):
                processed_section['subsections'] = []
                for subsection in section['subsections']:
                    sub_content = subsection.get('content', '')
                    sub_metadata, sub_content = self._extract_section_metadata(sub_content)
                    
                    processed_subsection = {
                        'title': subsection.get('title', ''),
                        'content': self._convert_markdown_to_html(sub_content),
                        'metadata': sub_metadata,
                        'reading_time': self._estimate_reading_time(sub_content),
                        'key_topics': self._extract_key_topics(sub_content),
                        'anchor': f"subsection-{hash(subsection.get('title', '')) & 0xFFFFFFFF}"
                    }
                    processed_section['subsections'].append(processed_subsection)
            
            processed_sections.append(processed_section)

        # Prepare template context
        context = {
            'title': metadata.get('title', 'Enhanced Report'),
            'company': metadata.get('company', ''),
            'language': metadata.get('language', ''),
            'date': datetime.now().strftime('%Y-%m-%d'),
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

def process_markdown_files(base_dir: str, template_path: Optional[str] = None) -> None:
    """Process markdown files and generate PDF report."""
    markdown_dir = os.path.join(base_dir, 'markdown')
    pdf_dir = os.path.join(base_dir, 'pdf')
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Get company name and language from directory name
    dir_parts = os.path.basename(base_dir).split('_')
    company_name = ' '.join(dir_parts[:-3])  # Exclude timestamp parts
    language = dir_parts[-3]
    
    # Collect sections from markdown files
    sections = []
    for filename in sorted(os.listdir(markdown_dir)):
        if filename.endswith('.md'):
            with open(os.path.join(markdown_dir, filename), 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract section ID and title from filename
            section_id = filename[:-3]  # Remove .md extension
            title = ' '.join(word.capitalize() for word in section_id.split('_'))
            
            sections.append({
                'id': section_id,
                'title': title,
                'content': content
            })
    
    # Generate PDF
    pdf_generator = EnhancedPDFGenerator(template_path)
    output_path = os.path.join(pdf_dir, f"{company_name}_{language}_Report.pdf")
    pdf_generator.generate_pdf(sections, output_path, {
        'title': f"{company_name} {language} Report",
        'company': company_name,
        'language': language
    }) 