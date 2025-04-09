# test_agent_prompt.py

import asyncio
import base64
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from google import genai
from google.genai import types
import prompt_testing
import tiktoken
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import time
import re
import markdown
from markdown.extensions import fenced_code, tables, toc, attr_list, def_list, footnotes
from markdown.extensions.codehilite import CodeHiliteExtension
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from jinja2 import Environment, FileSystemLoader
import yaml
import logging
from tqdm import tqdm
import signal
import sys
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.logging import RichHandler
from rich.panel import Panel
from bs4 import BeautifulSoup
from pdf_generator import process_markdown_files

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("rich")

# Rich console for better output
console = Console()

# Global flag for graceful shutdown
shutdown_requested = False

def signal_handler(signum, frame):
    """Handle interrupt signals gracefully."""
    global shutdown_requested
    if not shutdown_requested:
        console.print("\n[yellow]Shutdown requested. Completing current tasks...[/yellow]")
        shutdown_requested = True
    else:
        console.print("\n[red]Force quitting...[/red]")
        sys.exit(1)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Load environment variables from .env file
load_dotenv()

# Section order and titles for the final report
SECTION_ORDER = [
    ("basic", "Basic Information"),
    ("vision", "Vision Analysis"),
    ("management_strategy", "Management Strategy"),
    ("management_message", "Management Message"),
    ("crisis", "Crisis Management"),
    ("digital_transformation", "Digital Transformation Analysis"),
    ("financial", "Financial Analysis"),
    ("competitive", "Competitive Landscape"),
    ("regulatory", "Regulatory Environment"),
    ("business_structure", "Business Structure")
]

# Available languages for selection
AVAILABLE_LANGUAGES = {
    "1": "Japanese",
    "2": "English",
    "3": "Chinese",
    "4": "Korean",
    "5": "Vietnamese",
    "6": "Thai",
    "7": "Indonesian",
    "8": "Spanish",
    "9": "German",
    "10": "French"
}

# List of prompt functions to run
PROMPT_FUNCTIONS = [
    ("basic", prompt_testing.get_basic_prompt),
    ("financial", prompt_testing.get_financial_prompt),
    ("competitive", prompt_testing.get_competitive_landscape_prompt),
    ("management_strategy", prompt_testing.get_management_strategy_prompt),
    ("regulatory", prompt_testing.get_regulatory_prompt),
    ("crisis", prompt_testing.get_crisis_prompt),
    ("digital_transformation", prompt_testing.get_digital_transformation_prompt),
    ("business_structure", prompt_testing.get_business_structure_prompt),
    ("vision", prompt_testing.get_vision_prompt),
    ("management_message", prompt_testing.get_management_message_prompt),
]

def count_tokens(text: str) -> int:
    """Count the number of tokens in a text string."""
    encoding = tiktoken.get_encoding("cl100k_base")  # Using OpenAI's encoding
    return len(encoding.encode(text))

def format_time(seconds: float) -> str:
    """Format time in seconds to a human-readable string."""
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    if minutes < 60:
        return f"{minutes} minutes {remaining_seconds:.2f} seconds"
    hours = int(minutes // 60)
    remaining_minutes = minutes % 60
    return f"{hours} hours {remaining_minutes} minutes {remaining_seconds:.2f} seconds"

def generate_content(client: genai.Client, prompt: str, output_path: Path, task_id: Optional[int] = None) -> Dict:
    """Generate content for a single prompt and save to file. Returns token counts and timing."""
    start_time = time.time()
    try:
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]   
        tools = [types.Tool(google_search=types.GoogleSearch())]
        generate_content_config = types.GenerateContentConfig(
            temperature=1.09,
            tools=tools,
            response_mime_type="text/plain",
        )

        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Count input tokens
        input_tokens = count_tokens(prompt)
        
        # Collect output text
        full_output = ""
        
        # Open file for writing
        with open(output_path, 'w', encoding='utf-8') as f:
            response = client.models.generate_content_stream(
                model="gemini-2.5-pro-preview-03-25",
                contents=contents,
                config=generate_content_config,
            )
            
            for chunk in response:
                if shutdown_requested:
                    raise InterruptedError("Generation interrupted by user")
                
                if chunk.text:
                    f.write(chunk.text)
                    f.flush()
                    full_output += chunk.text

        # Count output tokens
        output_tokens = count_tokens(full_output)
        
        execution_time = time.time() - start_time
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "execution_time": execution_time,
            "status": "success"
        }
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error generating content for {output_path.name}: {str(e)}")
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "execution_time": execution_time,
            "status": "error",
            "error": str(e)
        }

def generate_all_prompts(company_name: str, language: str):
    """Generate content for all prompts in parallel using ThreadPoolExecutor."""
    start_time = time.time()
    
    # Get API key from .env file
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")

    client = genai.Client(api_key=api_key)

    # Create timestamp for the directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create base output directory with timestamp
    base_dir = Path("output") / f"{company_name}_{language}_{timestamp}"
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    markdown_dir = base_dir / "markdown"
    pdf_dir = base_dir / "pdf"
    misc_dir = base_dir / "misc"
    
    for dir_path in [markdown_dir, pdf_dir, misc_dir]:
        dir_path.mkdir(exist_ok=True)
    
    # Save generation config in misc directory
    config = {
        "company_name": company_name,
        "language": language,
        "timestamp": datetime.now().isoformat(),
        "sections": [section[0] for section in SECTION_ORDER]
    }
    with open(misc_dir / "generation_config.yaml", "w") as f:
        yaml.dump(config, f)
    
    # Process all prompts with progress tracking
    results = {}
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="green", finished_style="green"),
        TaskProgressColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        expand=True
    ) as progress:
        # Add main progress bar
        overall_task = progress.add_task(
            "[bold cyan]Generating sections...", 
            total=len(PROMPT_FUNCTIONS)
        )
        
        # Create progress bars for each section
        section_tasks = {
            prompt_name: progress.add_task(
                f"[green]{prompt_name:.<30}",
                total=1,
                visible=True
            )
            for prompt_name, _ in PROMPT_FUNCTIONS
        }
        
        with ThreadPoolExecutor(max_workers=len(PROMPT_FUNCTIONS)) as executor:
            futures = []
            for prompt_name, prompt_func in PROMPT_FUNCTIONS:
                if shutdown_requested:
                    break
                    
                prompt = prompt_func(company_name, language)
                output_path = markdown_dir / f"{prompt_name}.md"
                
                future = executor.submit(generate_content, client, prompt, output_path)
                futures.append((prompt_name, future))
            
            # Collect results
            for prompt_name, future in futures:
                try:
                    if not shutdown_requested:
                        result = future.result()
                        results[prompt_name] = result
                        
                        # Update progress
                        progress.update(section_tasks[prompt_name], 
                            advance=1,
                            description=f"[bold green]{prompt_name:.<30}✓"
                        )
                        progress.update(overall_task, advance=1)
                    else:
                        results[prompt_name] = {
                            "status": "interrupted",
                            "error": "Generation interrupted by user"
                        }
                        progress.update(section_tasks[prompt_name],
                            description=f"[yellow]{prompt_name:.<30}⚠"
                        )
                except Exception as e:
                    logger.error(f"Error processing {prompt_name}: {str(e)}")
                    results[prompt_name] = {
                        "status": "error",
                        "error": str(e)
                    }
                    progress.update(section_tasks[prompt_name],
                        description=f"[red]{prompt_name:.<30}✗"
                    )
                finally:
                    progress.update(overall_task, advance=1)
    
    total_execution_time = time.time() - start_time
    
    # Compile token statistics
    token_stats = {
        "prompts": results,
        "summary": {
            "total_input_tokens": sum(r.get("input_tokens", 0) for r in results.values()),
            "total_output_tokens": sum(r.get("output_tokens", 0) for r in results.values()),
            "total_tokens": sum(r.get("total_tokens", 0) for r in results.values()),
            "total_execution_time": total_execution_time,
            "timestamp": datetime.now().isoformat(),
            "company_name": company_name,
            "language": language,
            "successful_prompts": sum(1 for r in results.values() if r.get("status") == "success"),
            "failed_prompts": sum(1 for r in results.values() if r.get("status") in ["error", "interrupted"]),
            "interrupted": shutdown_requested
        }
    }
    
    # Save token statistics in misc directory
    stats_path = misc_dir / "token_usage_report.json"
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(token_stats, f, indent=2, ensure_ascii=False)
    
    return token_stats, base_dir

class EnhancedPDFGenerator:
    """Enhanced PDF Generator with better markdown support and styling."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.markdown_dir = self.base_dir / "markdown"
        self.pdf_dir = self.base_dir / "pdf"
        self.template_dir = Path(__file__).parent / "templates"
        self.template_dir.mkdir(exist_ok=True)
        self._create_templates()
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        
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
            margin: 2cm;
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
        
        /* Special pages */
        @page cover, @page section-cover {
            margin: 0;
            @top-center { content: none; }
            @bottom-center { content: none; }
        }
        
        @page toc {
            @top-center { content: none; }
        }
        
        /* Base styles */
        body {
            font-family: "Noto Sans", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 10.5pt;
            margin: 0;
            padding: 0;
            counter-reset: section subsection;
        }
        
        /* Cover page styles */
        .cover {
            page: cover;
            min-height: 297mm;
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
            font-size: 36pt;
            margin-bottom: 1em;
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
        
        /* Section cover page */
        .section-cover {
            page: section-cover;
            min-height: 297mm;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: flex-start;
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            padding: 3cm;
            box-sizing: border-box;
            page-break-before: always;
            page-break-after: always;
        }
        .section-cover h2 {
            font-size: 32pt;
            margin-bottom: 1em;
            color: #1a1a1a;
            border-bottom: 4px solid #444;
            padding-bottom: 0.2em;
            width: 100%;
        }
        .section-cover .section-intro {
            font-size: 12pt;
            color: #444;
            margin: 2em 0;
            max-width: 80%;
            line-height: 1.8;
        }
        .section-cover .section-meta {
            margin-top: 3em;
            padding: 1em;
            background: #f8f9fa;
            border-radius: 8px;
            width: 100%;
        }
        .section-cover .meta-item {
            margin: 0.5em 0;
            color: #666;
            font-size: 11pt;
        }
        .section-cover .meta-item strong {
            color: #444;
        }
        
        /* TOC styles */
        .toc {
            page: toc;
            page-break-after: always;
            padding-top: 2cm;
        }
        .toc h1 {
            font-size: 24pt;
            margin-bottom: 2em;
            color: #1a1a1a;
            text-align: center;
        }
        .toc ul {
            list-style: none;
            padding-left: 0;
        }
        .toc ul ul {
            padding-left: 2em;
        }
        .toc li {
            margin: 0.8em 0;
            padding-left: 1em;
        }
        .toc a {
            color: #333;
            text-decoration: none;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .toc a::after {
            content: target-counter(attr(href), page);
            color: #666;
            margin-left: 0.5em;
        }
        .toc .section-number {
            color: #666;
            margin-right: 0.5em;
        }
        
        /* Content section styles */
        .content-section {
            margin-top: 2cm;
        }
        .content-section h3 {
            font-size: 16pt;
            color: #1a1a1a;
            margin-top: 2em;
            margin-bottom: 1em;
            counter-increment: subsection;
        }
        .content-section h3::before {
            content: counter(section) "." counter(subsection) " ";
            color: #666;
        }
        
        /* Table styles */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.5em 0;
            page-break-inside: avoid;
            font-size: 9.5pt;
        }
        thead {
            display: table-header-group;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 10px 12px;
            text-align: left;
            vertical-align: top;
        }
        th {
            background-color: #f5f5f5;
            font-weight: bold;
            color: #333;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        caption {
            font-style: italic;
            color: #666;
            margin-bottom: 0.5em;
            text-align: left;
        }
        
        /* Code blocks */
        pre {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 1em;
            margin: 1.5em 0;
            font-family: "Courier New", monospace;
            font-size: 9pt;
            white-space: pre-wrap;
            page-break-inside: avoid;
            position: relative;
        }
        pre::before {
            content: attr(data-language);
            position: absolute;
            top: -0.7em;
            right: 1em;
            background: #fff;
            padding: 0 0.5em;
            color: #666;
            font-size: 0.8em;
            border: 1px solid #e9ecef;
            border-radius: 2px;
        }
        code {
            font-family: "Courier New", monospace;
            font-size: 0.9em;
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
        }
        
        /* Lists */
        ul, ol {
            margin: 1em 0;
            padding-left: 2em;
        }
        li {
            margin: 0.5em 0;
        }
        li > ul, li > ol {
            margin: 0.3em 0;
        }
        
        /* Blockquotes */
        blockquote {
            border-left: 4px solid #ddd;
            padding: 0.5em 0 0.5em 1.5em;
            margin: 1.5em 0;
            color: #555;
            font-style: italic;
            background-color: #f9f9f9;
        }
        
        /* Sources section */
        .sources {
            margin-top: 3em;
            padding-top: 1.5em;
            border-top: 2px solid #eee;
        }
        .sources h2 {
            font-size: 16pt;
            color: #444;
            margin-bottom: 1.5em;
            border-bottom: none;
        }
        .sources ul {
            list-style: none;
            padding-left: 0;
        }
        .sources li {
            margin: 1em 0;
            padding-left: 1.5em;
            position: relative;
        }
        .sources li::before {
            content: "•";
            position: absolute;
            left: 0;
            color: #666;
        }
        .sources a {
            color: #0066cc;
            text-decoration: none;
        }
        
        /* Key takeaways */
        .key-takeaways {
            background-color: #f8f9fa;
            border-left: 4px solid #28a745;
            padding: 1.5em;
            margin: 2em 0;
            border-radius: 4px;
        }
        .key-takeaways h4 {
            color: #28a745;
            margin-top: 0;
            margin-bottom: 1em;
        }
        .key-takeaways ul {
            margin: 0;
            padding-left: 1.5em;
        }
        
        /* End page */
        .end-page {
            page-break-before: always;
            min-height: 297mm;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            background-color: #f8f9fa;
            padding: 2cm;
            box-sizing: border-box;
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
    <div class="section-cover">
        <h2>{{ section.title }}</h2>
        <div class="section-intro">
            {{ section.intro }}
        </div>
        <div class="section-meta">
            <div class="meta-item">
                <strong>Estimated Reading Time:</strong> {{ section.reading_time }} minutes
            </div>
            <div class="meta-item">
                <strong>Key Topics:</strong> {{ section.key_topics }}
            </div>
            {% if section.key_takeaways %}
            <div class="meta-item">
                <strong>Key Takeaways:</strong>
                <ul>
                {% for takeaway in section.key_takeaways %}
                    <li>{{ takeaway }}</li>
                {% endfor %}
                </ul>
            </div>
            {% endif %}
        </div>
    </div>
    <div class="content-section" id="{{ section.id }}">
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

    def _estimate_reading_time(self, content: str) -> int:
        """Estimate reading time in minutes based on word count."""
        words = len(content.split())
        # Average reading speed: 250 words per minute
        return max(1, round(words / 250))

    def _extract_key_topics(self, content: str) -> str:
        """Extract key topics from the content."""
        # Look for headers and important terms
        headers = re.findall(r'#{2,3}\s+(.+)', content)
        # Join unique headers with commas
        return ', '.join(sorted(set(headers)))[:100] + '...'

    def _extract_key_takeaways(self, content: str) -> list:
        """Extract key takeaways from the content."""
        # Look for key takeaways section or important bullet points
        takeaways = []
        takeaway_section = re.search(r'(?:Key Takeaways?|Summary):\s*\n((?:\*\s+[^\n]+\n?)+)', content)
        if takeaway_section:
            takeaways = re.findall(r'\*\s+([^\n]+)', takeaway_section.group(1))
        if not takeaways:
            # Extract first few bullet points as takeaways
            takeaways = re.findall(r'\*\s+([^\n]+)', content)[:3]
        return takeaways[:5]  # Limit to 5 takeaways

    def _convert_markdown_to_html(self, content: str) -> str:
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
            toc.append(f'<li><span class="section-number">{i}.</span> <a href="#{section["id"]}">{section["title"]}</a></li>')
        toc.append('</ul>')
        return '\n'.join(toc)

    def generate_pdf(self, company_name: str, language: str, sections: list) -> Path:
        """Generate a single PDF from all markdown sections."""
        try:
            # Process each section's markdown content to HTML
            processed_sections = []
            for section in sections:
                content = section['content']
                html_content = self._convert_markdown_to_html(content)
                
                # Add section metadata
                processed_sections.append({
                    'id': section['id'],
                    'title': section['title'],
                    'content': html_content,
                    'intro': self._extract_intro(content),
                    'reading_time': self._estimate_reading_time(content),
                    'key_topics': self._extract_key_topics(content),
                    'key_takeaways': self._extract_key_takeaways(content)
                })
            
            # Generate HTML using template
            template = self.env.get_template("enhanced_report_template.html")
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

def process_markdown_files(base_dir: Path, company_name: str, language: str) -> Path:
    """Process all markdown files in the markdown directory and generate a PDF."""
    sections = []
    markdown_dir = base_dir / "markdown"
    
    # Read and process each markdown file
    for section_id, section_title in SECTION_ORDER:
        file_path = markdown_dir / f"{section_id}.md"
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            if content.strip():  # Only include non-empty sections
                sections.append({
                    'id': section_id,
                    'title': section_title,
                    'content': content
                })
    
    # Generate PDF
    pdf_generator = EnhancedPDFGenerator(base_dir)
    return pdf_generator.generate_pdf(company_name, language, sections)

def get_user_input() -> tuple[str, str]:
    """Get company name and language from user input."""
    company_name = input("\nEnter company name: ")
    
    print("\nAvailable languages:")
    for key, lang in AVAILABLE_LANGUAGES.items():
        print(f"{key}: {lang}")
    
    while True:
        language = input("\nSelect language (1-10, default is 1 for Japanese): ").strip()
        if not language:
            language = "1"
        if language in AVAILABLE_LANGUAGES:
            break
        print("Invalid selection. Please choose a number between 1 and 10.")
    
    return company_name, language

def main():
    try:
        # Get user input
        company_name, language_key = get_user_input()
        language = AVAILABLE_LANGUAGES[language_key]
        
        console.print(f"\nGenerating prompts for {company_name} in {language}...")
        console.print("Output will be saved in the 'output' directory.\n")

        # Run the generation process
        token_stats, base_dir = generate_all_prompts(company_name, language)

        if shutdown_requested:
            console.print("\n[yellow]Generation process interrupted.[/yellow]")
            return

        # Display results
        if token_stats:
            console.print("\n[bold]Generation Summary:[/bold]")
            console.print(Panel.fit(
                "\n".join([
                    f"Total Execution Time: {format_time(token_stats['summary']['total_execution_time'])}",
                    f"Total Tokens: {token_stats['summary']['total_tokens']:,}",
                    f"Successful Prompts: [green]{token_stats['summary']['successful_prompts']}[/]",
                    f"Failed Prompts: [red]{token_stats['summary']['failed_prompts']}[/]"
                ]),
                title="Results",
                border_style="cyan"
            ))

            # Generate PDF if there were successful prompts
            if token_stats['summary']['successful_prompts'] > 0:
                console.print("\n[bold cyan]Generating PDF report...[/bold cyan]")
                pdf_path = process_markdown_files(base_dir, company_name, language)
                
                if pdf_path:
                    console.print(f"\n[green]PDF report generated: {pdf_path}[/green]")
                else:
                    console.print("\n[yellow]PDF generation failed.[/yellow]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Process interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"\nError occurred: {str(e)}")
        logger.exception("Unexpected error occurred")
        console.print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()

