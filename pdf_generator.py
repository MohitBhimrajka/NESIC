import os
from pathlib import Path
import markdown
from markdown.extensions import fenced_code, tables, toc, attr_list, def_list, footnotes
from markdown.extensions.codehilite import CodeHiliteExtension
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import yaml
from bs4 import BeautifulSoup
import re
from typing import Optional

class EnhancedPDFGenerator:
    """Enhanced PDF Generator with better markdown support and styling."""
    
    def __init__(self, base_dir: Path, template_path: Optional[str] = None):
        self.base_dir = Path(base_dir)
        self.markdown_dir = self.base_dir / "markdown"
        self.pdf_dir = self.base_dir / "pdf"
        self.template_dir = Path(__file__).parent / "templates"
        self.template_dir.mkdir(exist_ok=True)
        
        # Set up template environment
        if template_path:
            template_dir = Path(template_path).parent
            template_name = Path(template_path).name
            self.env = Environment(loader=FileSystemLoader([str(template_dir), str(self.template_dir)]))
            self.template_name = template_name
        else:
            self._create_templates()
            self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
            self.template_name = "enhanced_report_template.html"
        
        # Initialize markdown with all extensions
        self.md = markdown.Markdown(extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.tables',
            'markdown.extensions.toc',
            'markdown.extensions.attr_list',
            'markdown.extensions.def_list',
            'markdown.extensions.footnotes',
            'markdown.extensions.meta',
            'markdown.extensions.admonition',
            CodeHiliteExtension(css_class='highlight', guess_lang=False)
        ])

    def _create_templates(self):
        """Create necessary template files."""
        main_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        /* Base page settings */
        @page {
            size: A4;
            margin: 1cm;
            @top-center {
                content: string(chapter);
                font-size: 9pt;
                color: #444;
                padding-top: 0.5cm;
                font-family: "Noto Sans", Arial, sans-serif;
            }
            @bottom-center {
                content: counter(page);
                font-size: 9pt;
                color: #444;
                padding-bottom: 0.5cm;
                font-family: "Noto Sans", Arial, sans-serif;
            }
        }
        
        /* Cover page */
        @page cover {
            margin: 0;
            @top-center { content: none; }
            @bottom-center { content: none; }
        }
        
        /* TOC page */
        @page toc {
            @top-center { content: none; }
        }
        
        /* Base styles */
        body {
            font-family: "Noto Sans", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 10pt;
            margin: 0;
            padding: 0;
        }
        
        /* Cover page styles */
        .cover {
            page: cover;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 2cm;
            box-sizing: border-box;
        }
        .cover h1 {
            font-size: 32pt;
            margin-bottom: 0.5em;
            color: #1a1a1a;
        }
        .cover h2 {
            font-size: 24pt;
            margin-bottom: 2em;
            color: #444;
        }
        .cover p {
            font-size: 12pt;
            color: #666;
            margin: 0.5em 0;
        }
        
        /* TOC styles */
        .toc {
            page: toc;
            page-break-after: always;
            padding-top: 1cm;
        }
        .toc h1 {
            font-size: 24pt;
            margin-bottom: 1.5em;
            color: #1a1a1a;
        }
        .toc ul {
            list-style: none;
            padding-left: 0;
        }
        .toc ul ul {
            padding-left: 2em;
        }
        .toc li {
            margin: 0.4em 0;
            padding-left: 1em;
        }
        .toc a {
            color: #333;
            text-decoration: none;
        }
        .toc a::after {
            content: leader('.') target-counter(attr(href), page);
            color: #666;
            margin-left: 0.5em;
        }
        
        /* Section styles */
        .report-section {
            page-break-before: always;
            margin-top: 1cm;
        }
        .report-section:first-of-type {
            page-break-before: avoid;
        }
        .report-section h2 {
            font-size: 18pt;
            margin-top: 0;
            margin-bottom: 1.2em;
            padding-bottom: 0.2em;
            border-bottom: 2px solid #444;
            string-set: chapter content();
            color: #1a1a1a;
        }
        
        /* Table styles */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.2em 0;
            page-break-inside: avoid;
            font-size: 9pt;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }
        th {
            background-color: #f5f5f5;
            font-weight: bold;
            color: #333;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        
        /* Code blocks */
        pre {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 1em;
            margin: 1em 0;
            font-family: "Courier New", monospace;
            font-size: 9pt;
            overflow-x: auto;
            page-break-inside: avoid;
        }
        code {
            font-family: "Courier New", monospace;
            font-size: 0.9em;
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
        }
        
        /* Links */
        a {
            color: #0066cc;
            text-decoration: none;
        }
        
        /* Blockquotes */
        blockquote {
            border-left: 4px solid #ddd;
            padding: 0.5em 0 0.5em 1em;
            margin: 1em 0;
            color: #666;
            font-style: italic;
        }
        
        /* Images */
        img {
            max-width: 100%;
            height: auto;
            margin: 1em auto;
            display: block;
        }
        
        /* End page */
        .end-page {
            page-break-before: always;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            background-color: #f8f9fa;
        }
        .end-page h2 {
            font-size: 24pt;
            color: #444;
            margin-bottom: 1em;
        }
        .end-page p {
            font-size: 12pt;
            color: #666;
        }
        
        /* Highlight syntax */
        .highlight { background-color: #f8f9fa; }
        .highlight .c { color: #998; font-style: italic; }
        .highlight .k { color: #000; font-weight: bold; }
        .highlight .o { color: #000; font-weight: bold; }
        .highlight .cm { color: #998; font-style: italic; }
        .highlight .cp { color: #999; font-weight: bold; }
        .highlight .c1 { color: #998; font-style: italic; }
        .highlight .cs { color: #999; font-weight: bold; font-style: italic; }
        .highlight .gd { color: #000; background-color: #fdd; }
        .highlight .gd .x { color: #000; background-color: #faa; }
        .highlight .ge { font-style: italic; }
        .highlight .gr { color: #a00; }
        .highlight .gh { color: #999; }
        .highlight .gi { color: #000; background-color: #dfd; }
        .highlight .gi .x { color: #000; background-color: #afa; }
        .highlight .go { color: #888; }
        .highlight .gp { color: #555; }
        .highlight .gs { font-weight: bold; }
        .highlight .gu { color: #aaa; }
        .highlight .gt { color: #a00; }
        .highlight .kt { color: #458; font-weight: bold; }
        .highlight .m { color: #099; }
        .highlight .s { color: #d14; }
        .highlight .n { color: #333; }
        .highlight .na { color: #008080; }
        .highlight .nb { color: #0086B3; }
        .highlight .nc { color: #458; font-weight: bold; }
        .highlight .no { color: #008080; }
        .highlight .ni { color: #800080; }
        .highlight .ne { color: #900; font-weight: bold; }
        .highlight .nf { color: #900; font-weight: bold; }
        .highlight .nn { color: #555; }
        .highlight .nt { color: #000080; }
        .highlight .nv { color: #008080; }
        .highlight .w { color: #bbb; }
        .highlight .mf { color: #099; }
        .highlight .mh { color: #099; }
        .highlight .mi { color: #099; }
        .highlight .mo { color: #099; }
        .highlight .sb { color: #d14; }
        .highlight .sc { color: #d14; }
        .highlight .sd { color: #d14; }
        .highlight .s2 { color: #d14; }
        .highlight .se { color: #d14; }
        .highlight .sh { color: #d14; }
        .highlight .si { color: #d14; }
        .highlight .sx { color: #d14; }
        .highlight .sr { color: #009926; }
        .highlight .s1 { color: #d14; }
        .highlight .ss { color: #990073; }
        .highlight .bp { color: #999; }
        .highlight .vc { color: #008080; }
        .highlight .vg { color: #008080; }
        .highlight .vi { color: #008080; }
        .highlight .il { color: #099; }
    </style>
</head>
<body>
    <div class="cover">
        <h1>{{ company_name }}</h1>
        <h2>Company Analysis Report</h2>
        <p>Generated on: {{ generation_date }}</p>
        <p>Language: {{ language }}</p>
    </div>
    
    <div class="toc">
        <h1>Table of Contents</h1>
        {{ toc }}
    </div>
    
    {% for section in sections %}
    <div class="report-section" id="{{ section.id }}">
        <h2>{{ section.title }}</h2>
        {{ section.content }}
    </div>
    {% endfor %}
    
    <div class="end-page">
        <h2>End of Report</h2>
        <p>Generated by Supervity Analysis System</p>
        <p>{{ generation_date }}</p>
    </div>
</body>
</html>
"""
        template_path = self.template_dir / "enhanced_report_template.html"
        if not template_path.exists():
            template_path.write_text(main_template)

    def _convert_markdown_to_html(self, content: str, section_number: int) -> str:
        """Convert markdown to HTML with enhanced features."""
        # Reset markdown instance
        self.md.reset()
        
        # Convert markdown to HTML
        html = self.md.convert(content)
        
        # Clean up the HTML using BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Process tables
        for table in soup.find_all('table'):
            table['class'] = table.get('class', []) + ['data-table']
            # Add thead if not present
            if not table.find('thead') and table.find('tr'):
                first_row = table.find('tr')
                thead = soup.new_tag('thead')
                thead.append(first_row.extract())
                table.insert(0, thead)
            # Add caption if table has a preceding paragraph that ends with ':'
            prev_elem = table.find_previous_sibling('p')
            if prev_elem and prev_elem.string and prev_elem.string.strip().endswith(':'):
                caption = soup.new_tag('caption')
                caption.string = prev_elem.string.strip().rstrip(':')
                table.insert(0, caption)
                prev_elem.decompose()
        
        # Process headings for section numbering
        for h_tag in soup.find_all(['h2', 'h3', 'h4']):
            level = int(h_tag.name[1])
            if level == 2:
                h_tag.string = f"{section_number}. {h_tag.string}"
            elif level == 3:
                subsection_number = len(h_tag.find_previous_siblings('h3')) + 1
                h_tag.string = f"{section_number}.{subsection_number} {h_tag.string}"
            elif level == 4:
                subsection_number = len(h_tag.find_previous_siblings('h3', class_=lambda x: x != 'no-number')) + 1
                subsubsection_number = len(h_tag.find_previous_siblings('h4')) + 1
                h_tag.string = f"{section_number}.{subsection_number}.{subsubsection_number} {h_tag.string}"
        
        # Process code blocks
        for pre in soup.find_all('pre'):
            # Try to detect language from class
            classes = pre.get('class', [])
            language = next((c.replace('language-', '') for c in classes if c.startswith('language-')), 'text')
            pre['data-language'] = language
        
        # Fix duplicate anchors
        used_ids = set()
        for tag in soup.find_all(id=True):
            original_id = tag['id']
            if original_id in used_ids:
                counter = 1
                while f"{original_id}-{counter}" in used_ids:
                    counter += 1
                tag['id'] = f"{original_id}-{counter}"
            used_ids.add(tag['id'])
        
        # Process source sections
        sources = soup.find_all(['h2', 'h3'], string='Sources')
        for source_heading in sources:
            source_section = source_heading.find_next_sibling()
            if source_section:
                source_section['class'] = source_section.get('class', []) + ['sources']
        
        return str(soup)

    def _generate_toc(self, sections: list) -> str:
        """Generate Table of Contents HTML."""
        toc = ['<ul class="toc-list">']
        for i, section in enumerate(sections, 1):
            # Add main section
            toc.append(f'<li><span class="section-number">{i}.</span> <a href="#{section["id"]}">{section["title"]}</a>')
            
            # Add subsections if any
            subsections = re.findall(r'##\s+(.+)', section['content'])
            if subsections:
                toc.append('<ul>')
                for j, subsection in enumerate(subsections, 1):
                    toc.append(f'<li><span class="section-number">{i}.{j}</span> <a href="#{self._make_id(subsection)}">{subsection}</a></li>')
                toc.append('</ul>')
            
            toc.append('</li>')
        
        toc.append('</ul>')
        return '\n'.join(toc)

    def _make_id(self, text: str) -> str:
        """Convert text to HTML id attribute."""
        return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

    def generate_pdf(self, company_name: str, language: str, sections: list) -> Path:
        """Generate a single PDF from all markdown sections."""
        try:
            # Process each section's markdown content to HTML
            processed_sections = []
            for i, section in enumerate(sections, 1):
                content = section['content']
                html_content = self._convert_markdown_to_html(content, i)
                metadata = section['metadata']
                
                # Add section metadata
                processed_sections.append({
                    'id': section['id'],
                    'title': section['title'],
                    'content': html_content,
                    'intro': metadata.get('summary', self._extract_intro(content)),
                    'reading_time': self._estimate_reading_time(content),
                    'key_topics': metadata.get('key_points', self._extract_key_topics(content)),
                    'key_takeaways': metadata.get('key_points', self._extract_key_takeaways(content)),
                    'prerequisites': metadata.get('prerequisites', []),
                    'related_sections': metadata.get('related_sections', [])
                })
            
            # Generate HTML using template
            template = self.env.get_template(self.template_name)
            toc = self._generate_toc(processed_sections)
            
            html_content = template.render(
                company_name=company_name,
                generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                language=language,
                toc=toc,
                sections=processed_sections
            )
            
            # Configure fonts and styles
            font_config = FontConfiguration()
            
            # Generate PDF in the pdf directory
            pdf_path = self.pdf_dir / f"{company_name}_{language}_enhanced_report.pdf"
            HTML(string=html_content).write_pdf(
                pdf_path,
                font_config=font_config,
                presentational_hints=True
            )
            
            return pdf_path
            
        except Exception as e:
            raise Exception(f"PDF generation failed: {str(e)}")

    def _extract_intro(self, content: str) -> str:
        """Extract introduction text from the content."""
        # Try to find the first paragraph after any headers
        intro_match = re.search(r'^(?:#+[^\n]+\n+)?((?:[^\n]+\n){1,3})', content)
        if intro_match:
            return intro_match.group(1).strip()
        return "This section provides detailed analysis and insights."

def process_markdown_files(base_dir: Path, company_name: str, language: str, template_path: Optional[str] = None) -> Path:
    """Process all markdown files in the markdown directory and generate a PDF."""
    sections = []
    markdown_dir = base_dir / "markdown"
    
    # Read and process each markdown file
    for section_id, section_title in SECTION_ORDER:
        file_path = markdown_dir / f"{section_id}.md"
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            if content.strip():  # Only include non-empty sections
                # Extract section metadata
                metadata = _extract_section_metadata(content)
                sections.append({
                    'id': section_id,
                    'title': section_title,
                    'content': content,
                    'metadata': metadata
                })
    
    # Generate PDF
    pdf_generator = EnhancedPDFGenerator(base_dir, template_path)
    return pdf_generator.generate_pdf(company_name, language, sections)

def _extract_section_metadata(content: str) -> dict:
    """Extract metadata from section content."""
    metadata = {
        'summary': '',
        'key_points': [],
        'prerequisites': [],
        'related_sections': []
    }
    
    # Look for metadata section at the start of the file
    meta_match = re.search(r'<!--\s*metadata\s*\n(.*?)\n-->', content, re.DOTALL)
    if meta_match:
        try:
            yaml_data = yaml.safe_load(meta_match.group(1))
            if isinstance(yaml_data, dict):
                metadata.update(yaml_data)
        except yaml.YAMLError:
            pass
    
    # Extract summary if not in metadata
    if not metadata['summary']:
        summary_match = re.search(r'^(?:#+[^\n]+\n+)?([^\n]+)', content)
        if summary_match:
            metadata['summary'] = summary_match.group(1).strip()
    
    # Extract key points if not in metadata
    if not metadata['key_points']:
        key_points = re.findall(r'(?:Key Points|Key Takeaways):\s*\n((?:\*\s+[^\n]+\n?)+)', content)
        if key_points:
            metadata['key_points'] = [point.strip('* \n') for point in re.findall(r'\*\s+([^\n]+)', key_points[0])]
    
    return metadata 