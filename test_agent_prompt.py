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
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import time
import re
import mistune
import mdformat
from weasyprint import HTML, CSS
from bs4 import BeautifulSoup
import latex2mathml.converter
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

    # Create base output directory
    base_dir = Path("output") / f"{company_name}_{language}"
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Save generation config
    config = {
        "company_name": company_name,
        "language": language,
        "timestamp": datetime.now().isoformat(),
        "sections": [section[0] for section in SECTION_ORDER]
    }
    with open(base_dir / "generation_config.yaml", "w") as f:
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
                output_path = base_dir / f"{prompt_name}.md"
                
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
    
    # Save token statistics
    stats_path = base_dir / "token_usage_report.json"
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(token_stats, f, indent=2, ensure_ascii=False)
    
    return token_stats

class MarkdownValidator:
    """Validates markdown files for common issues and formatting problems."""
    
    def __init__(self):
        self.markdown_parser = mistune.create_markdown()
        # Compile regex patterns once
        self.latex_pattern = re.compile(r'\$\$([^$]+)\$\$|\$([^$\n]+)\$')
        self.currency_pattern = re.compile(r'(?:USD|₹|€|£|\$)\s*\d+(?:[,.]\d+)?(?:\s*(?:billion|million|thousand|crore|lakh))?', re.IGNORECASE)
    
    def validate_latex(self, content: str, section_id: str) -> List[Dict]:
        """Check for LaTeX syntax errors with line numbers."""
        errors = []
        lines = content.split('\n')
        line_offsets = [0]  # Track cumulative length of lines for position mapping
        current_offset = 0
        for line in lines:
            current_offset += len(line) + 1  # +1 for newline
            line_offsets.append(current_offset)
        
        # First, identify currency amounts to ignore
        currency_matches = set()
        for match in self.currency_pattern.finditer(content):
            currency_matches.add((match.start(), match.end()))
        
        # Find all LaTeX expressions (both inline and block)
        for match in self.latex_pattern.finditer(content):
            # Skip if this match overlaps with a currency match
            if any(curr_start <= match.start() <= curr_end or 
                  curr_start <= match.end() <= curr_end 
                  for curr_start, curr_end in currency_matches):
                continue
                
            latex_expr = match.group(1) or match.group(2)
            if not latex_expr:  # Skip empty matches
                continue
                
            start_pos = match.start()
            # Find line number by binary search in line_offsets
            line_num = next(i for i, offset in enumerate(line_offsets) if offset > start_pos)
            context = lines[max(0, line_num-1):min(len(lines), line_num+2)]
            try:
                latex2mathml.converter.convert(latex_expr)
            except Exception as e:
                errors.append({
                    "section": section_id,
                    "error": f"LaTeX error: {str(e)}",
                    "line": line_num,
                    "context": "\n".join(context),
                    "expression": latex_expr[:50] + ("..." if len(latex_expr) > 50 else "")
                })
        
        return errors

    def validate_markdown_structure(self, content: str, section_id: str) -> Tuple[List[Dict], str]:
        """Check for markdown structural issues and auto-fix when possible."""
        errors = []
        fixed_content = content
        lines = content.split('\n')
        
        # Check for unclosed code blocks
        code_block_starts = []
        code_block_ends = []
        in_code_block = False
        current_block_start = None
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    current_block_start = i
                    code_block_starts.append(i)
                else:
                    in_code_block = False
                    code_block_ends.append(i)
        
        if len(code_block_starts) != len(code_block_ends):
            if in_code_block:  # Unclosed block at EOF
                context = lines[current_block_start-1:min(current_block_start+3, len(lines))]
                errors.append({
                    "section": section_id,
                    "error": "Unclosed code block",
                    "line": current_block_start,
                    "context": "\n".join(context)
                })
                fixed_content += "\n```"  # Auto-fix by closing
        
        # Check for broken links with context
        for i, line in enumerate(lines, 1):
            links = re.finditer(r'\[([^\]]+)\]\(([^\)]+)\)', line)
            for link in links:
                text, url = link.groups()
                if not url or url.isspace():
                    context = lines[max(0, i-2):min(len(lines), i+1)]
                    errors.append({
                        "section": section_id,
                        "error": f"Empty link URL for text '{text}'",
                        "line": i,
                        "context": "\n".join(context)
                    })
        
        # Enhanced table validation
        in_table = False
        header_cols = 0
        separator_line = None
        fixed_lines = []
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('|'):
                if not in_table:
                    # Start of new table
                    in_table = True
                    header_cols = len(line.split('|')) - 1
                    if header_cols < 2:
                        context = lines[max(0, i-1):min(len(lines), i+2)]
                        errors.append({
                            "section": section_id,
                            "error": f"Table has too few columns (minimum 2 required)",
                            "line": i,
                            "context": "\n".join(context)
                        })
                    fixed_lines.append(line)
                    continue
                
                # Validate separator row
                if line.strip().replace('|', '').replace('-', '').replace(':', '').strip() == '':
                    separator_line = i
                    if not re.match(r'\|(\s*:?-+:?\s*\|)+$', line):
                        context = lines[max(0, i-2):min(len(lines), i+1)]
                        errors.append({
                            "section": section_id,
                            "error": "Invalid table separator format",
                            "line": i,
                            "context": "\n".join(context)
                        })
                    if len(line.split('|')) - 1 != header_cols:
                        # Fix separator row
                        fixed_line = '|' + '|'.join([' --- ' for _ in range(header_cols)]) + '|'
                        fixed_lines.append(fixed_line)
                        continue
                
                # Handle data rows
                cells = line.split('|')[1:-1]
                if len(cells) != header_cols:
                    context = lines[max(0, i-2):min(len(lines), i+1)]
                    errors.append({
                        "section": section_id,
                        "error": f"Table row has {len(cells)} cells, expected {header_cols}",
                        "line": i,
                        "context": "\n".join(context)
                    })
                    # Pad or trim cells to match header
                    if len(cells) < header_cols:
                        cells.extend([''] * (header_cols - len(cells)))
                    else:
                        cells = cells[:header_cols]
                    fixed_line = '|' + '|'.join(f" {cell.strip()} " for cell in cells) + '|'
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(line)
            else:
                if in_table and not line.strip():
                    in_table = False
                fixed_lines.append(line)
        
        fixed_content = '\n'.join(fixed_lines)
        return errors, fixed_content

    def validate_file(self, file_path: Path, section_id: str) -> Tuple[List[Dict], str]:
        """Validate a markdown file for various issues and return both errors and potentially fixed content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return [{
                "section": section_id,
                "error": f"Failed to read file: {str(e)}",
                "line": 0,
                "context": None
            }], ""
        
        errors = []
        fixed_content = content
        
        # Check basic file issues
        if not content.strip():
            errors.append({
                "section": section_id,
                "error": "File is empty",
                "line": 0,
                "context": None
            })
            return errors, fixed_content
        
        # Validate LaTeX
        latex_errors = self.validate_latex(content, section_id)
        errors.extend(latex_errors)
        
        # Validate markdown structure and get fixed content
        structure_errors, fixed_content = self.validate_markdown_structure(content, section_id)
        errors.extend(structure_errors)
        
        # Try parsing with mistune to catch general markdown issues
        try:
            self.markdown_parser(fixed_content)
        except Exception as e:
            errors.append({
                "section": section_id,
                "error": f"Markdown parsing error: {str(e)}",
                "line": 0,
                "context": content[:200] + "..." if len(content) > 200 else content
            })
        
        # Try formatting with mdformat to catch formatting issues
        try:
            mdformat.text(fixed_content)
        except Exception as e:
            errors.append({
                "section": section_id,
                "error": f"Markdown formatting error: {str(e)}",
                "line": 0,
                "context": content[:200] + "..." if len(content) > 200 else content
            })
        
        return errors, fixed_content

class PDFGenerator:
    """Generates a professionally formatted PDF from markdown files."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.template_dir = Path(__file__).parent / "templates"
        self.template_dir.mkdir(exist_ok=True)
        self._create_templates()
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        # Configure WeasyPrint logging
        from weasyprint.logger import LOGGER as weasyprint_logger
        import logging
        weasyprint_logger.setLevel(logging.WARNING)
        # Compile regex patterns once
        self.latex_pattern = re.compile(r'\$\$([^$]+)\$\$|\$([^$\n]+)\$')
        self.currency_pattern = re.compile(
            r'(?:USD|¥|₹|€|£|\$)\s*\d{1,3}(?:(?:,\d{3})*|(?:\d*))(?:\.\d+)?(?:\s*(?:billion|million|thousand|lakh|crore))?',
            re.IGNORECASE
        )
        # Define allowed HTML tags and attributes for sanitization
        self.allowed_tags = [
            'html', 'head', 'body', 'meta', 'style',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'br', 'hr', 'pre', 'code', 'blockquote',
            'ul', 'ol', 'li', 'table', 'thead', 'tbody',
            'tr', 'th', 'td', 'strong', 'em', 'a', 'img',
            'div', 'span', 'nav', 'section',
            # MathML tags
            'math', 'mi', 'mo', 'mn', 'msup', 'msub',
            'mfrac', 'msqrt', 'mrow'
        ]
        self.allowed_attributes = {
            'meta': ['charset'],
            'a': ['href', 'title', 'id', 'target', 'rel'],  # Added rel for external links
            'img': ['src', 'alt', 'title', 'width', 'height'],
            'code': ['class'],
            'div': ['class', 'id'],
            'span': ['class', 'id'],
            'section': ['class', 'id'],
            'th': ['colspan', 'rowspan', 'scope'],
            'td': ['colspan', 'rowspan'],
            'nav': ['class', 'aria-label']  # Added aria-label for accessibility
        }
    
    def _create_templates(self):
        """Create necessary template files if they don't exist."""
        # Main template with CSS
        main_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        /* Base page settings */
        @page {
            size: A4;
            margin: 0.9cm;
            @top-center {
                content: string(chapter);
                font-size: 9pt;
                color: #666;
                padding-top: 0.5cm;
                font-family: "Noto Sans", Arial, sans-serif;
            }
            @bottom-center {
                content: counter(page);
                font-size: 9pt;
                color: #666;
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
            background-color: #f8f9fa;
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
            string-set: none;
        }
        .toc nav {
            margin-left: 1em;
        }
        .toc nav p {
            margin: 0.4em 0;
            padding-left: 1em;
            text-indent: -1em;
            line-height: 1.4;
        }
        .toc nav a {
            color: #333;
            text-decoration: none;
        }
        .toc nav a::after {
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
        .report-section h3 {
            font-size: 14pt;
            margin-top: 1.5em;
            margin-bottom: 0.8em;
            color: #333;
        }
        
        /* Content elements */
        p {
            margin: 0.8em 0;
            text-align: justify;
            hyphens: auto;
        }
        ul, ol {
            margin: 0.8em 0;
            padding-left: 1.5em;
        }
        li {
            margin: 0.4em 0;
            text-align: justify;
            hyphens: auto;
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
            border: 1px solid #ccc;
            padding: 6px 8px;
            text-align: left;
            vertical-align: top;
        }
        th {
            background-color: #f0f0f0;
            font-weight: bold;
            color: #333;
        }
        tbody tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr {
            page-break-inside: avoid;
        }
        
        /* Code blocks */
        pre, code {
            font-family: "Courier New", monospace;
            background-color: #f5f5f5;
            border-radius: 4px;
        }
        pre {
            padding: 1em;
            margin: 1em 0;
            overflow-x: auto;
            white-space: pre-wrap;
            page-break-inside: avoid;
            font-size: 9pt;
            border: 1px solid #e0e0e0;
        }
        code {
            padding: 2px 4px;
            font-size: 0.9em;
            color: #333;
        }
        
        /* Blockquotes */
        blockquote {
            border-left: 4px solid #ddd;
            padding: 0.5em 0 0.5em 1em;
            margin: 1em 0;
            color: #666;
            font-style: italic;
            background-color: #f9f9f9;
        }
        
        /* Images */
        img {
            max-width: 100%;
            height: auto;
            margin: 1em auto;
            display: block;
        }
        
        /* Error placeholders */
        .error-placeholder {
            color: #721c24;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            padding: 0.5em;
            margin: 0.5em 0;
            border-radius: 4px;
            font-size: 0.9em;
        }
        
        /* Source list styles */
        .sources {
            margin-top: 2em;
            padding-top: 1em;
            border-top: 2px solid #eee;
        }
        .sources h2, .sources h3 {
            color: #666;
            font-size: 14pt;
            margin-bottom: 1em;
            border-bottom: none;
            string-set: none;
        }
        .sources ul {
            list-style-type: none;
            padding-left: 0;
        }
        .sources li {
            margin-bottom: 0.8em;
            font-size: 9pt;
            color: #666;
            text-align: left;
        }
        .sources a {
            color: #0066cc;
            text-decoration: none;
        }
        .sources a:hover {
            text-decoration: underline;
        }
        
        /* Links */
        a {
            color: #0066cc;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
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
</body>
</html>
"""
        template_path = self.template_dir / "report_template.html"
        if not template_path.exists():
            template_path.write_text(main_template)
    
    def _generate_toc(self, sections: List[Dict]) -> str:
        """Generate Table of Contents HTML."""
        toc = ['<nav class="toc">']
        for i, section in enumerate(sections, 1):
            toc.append(f'<p><strong>{i}.</strong> <a href="#{section["id"]}">{section["title"]}</a></p>')
        toc.append('</nav>')
        return '\n'.join(toc)
    
    def _convert_markdown_to_html(self, content: str, section_id: str) -> str:
        """Convert markdown to HTML with special handling for LaTeX and sanitization."""
        import bleach
        
        # First, identify currency amounts to preserve
        currency_matches = {}
        for match in self.currency_pattern.finditer(content):
            placeholder = f"CURRENCY_PLACEHOLDER_{len(currency_matches)}"
            currency_matches[placeholder] = match.group(0)
            content = content[:match.start()] + placeholder + content[match.end():]
        
        # Convert LaTeX to MathML with error handling
        def latex_replacer(match):
            latex = match.group(1) or match.group(2)
            if not latex:  # Skip empty matches
                return match.group(0)
            try:
                return latex2mathml.converter.convert(latex)
            except Exception as e:
                return f'<div class="error-placeholder">LaTeX Error: {latex[:50]}{"..." if len(latex) > 50 else ""}</div>'
        
        # Process LaTeX
        content = self.latex_pattern.sub(latex_replacer, content)
        
        # Restore currency amounts
        for placeholder, original in currency_matches.items():
            content = content.replace(placeholder, original)
        
        try:
            # Convert to HTML using mistune
            html = mistune.html(content)
            
            # Sanitize HTML
            html = bleach.clean(
                html,
                tags=self.allowed_tags,
                attributes=self.allowed_attributes,
                strip=True
            )
            
            # Process source lists
            if "## Sources" in content or "### Sources" in content:
                # Find the sources section
                sources_start = html.find("<h2>Sources</h2>")
                if sources_start == -1:
                    sources_start = html.find("<h3>Sources</h3>")
                
                if sources_start != -1:
                    # Split the HTML at the sources section
                    main_content = html[:sources_start]
                    sources_content = html[sources_start:]
                    
                    # Process source links to ensure proper formatting
                    soup = BeautifulSoup(sources_content, 'html.parser')
                    source_links = soup.find_all('a')
                    for link in source_links:
                        # Check if this is a Supervity Source link
                        if link.string and link.string.startswith('Supervity Source'):
                            # Get the annotation text that follows
                            next_text = link.next_sibling
                            if next_text and ' - ' in str(next_text):
                                # Format is correct, continue
                                continue
                            elif next_text:
                                # Add proper formatting
                                link.insert_after(' - ')
                    
                    # Convert back to string
                    sources_content = str(soup)
                    
                    # Wrap sources in a div with proper class
                    html = f"{main_content}<div class='sources'>{sources_content}</div>"
            
            return html
        except Exception as e:
            error_html = f'<div class="error-placeholder">Error converting section {section_id} to HTML: {str(e)}</div>'
            return error_html
    
    def generate_pdf(self, company_name: str, language: str) -> Tuple[Path, List[str]]:
        """Generate a single PDF from all markdown files in the correct order."""
        sections = []
        warnings = []
        
        # Process each section in order
        for section_id, section_title in SECTION_ORDER:
            file_path = self.output_dir / f"{section_id}.md"
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    
                    # Skip empty sections
                    if not content:
                        warnings.append(f"Skipping empty section: {section_id}")
                        continue
                    
                    # Process the entire content, including sources
                    html_content = self._convert_markdown_to_html(content, section_id)
                    sections.append({
                        "id": section_id,
                        "title": section_title,
                        "content": html_content
                    })
                except Exception as e:
                    warnings.append(f"Error processing section {section_id}: {str(e)}")
                    # Add error placeholder for this section
                    sections.append({
                        "id": section_id,
                        "title": section_title,
                        "content": f'<div class="error-placeholder">Failed to process section: {str(e)}</div>'
                    })
        
        try:
            # Generate HTML using template
            template = self.env.get_template("report_template.html")
            toc = self._generate_toc(sections)
            
            html_content = template.render(
                company_name=company_name,
                generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                language=language,
                toc=toc,
                sections=sections
            )
            
            # Save intermediate HTML for debugging
            html_debug_path = self.output_dir / f"{company_name}_{language}_report_debug.html"
            with open(html_debug_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            # Generate PDF
            pdf_path = self.output_dir / f"{company_name}_{language}_report.pdf"
            try:
                HTML(string=html_content, base_url=str(self.output_dir)).write_pdf(
                    pdf_path,
                    stylesheets=[CSS(string='@page { size: A4; margin: 1.5cm; }')]
                )
                return pdf_path, warnings
            except Exception as e:
                warnings.append(f"PDF generation failed: {str(e)}")
                warnings.append(f"Debug HTML saved to: {html_debug_path}")
                return None, warnings
                
        except Exception as e:
            warnings.append(f"Template rendering failed: {str(e)}")
            return None, warnings

def validate_and_generate_pdf(company_name: str, language: str, output_dir: Path):
    """Validate markdown files and generate PDF if validation passes."""
    validator = MarkdownValidator()
    all_errors = {}
    fixed_files = {}
    
    # Validate each markdown file
    for section_id, section_title in SECTION_ORDER:
        file_path = output_dir / f"{section_id}.md"
        if file_path.exists():
            errors, fixed_content = validator.validate_file(file_path, section_id)
            if errors:
                all_errors[section_id] = errors
            if fixed_content != file_path.read_text(encoding='utf-8'):
                fixed_files[section_id] = fixed_content
    
    # If there are files to fix, save the fixed versions
    if fixed_files:
        print("\n--- Auto-fixing Markdown Formatting Issues ---")
        for section_id, content in fixed_files.items():
            file_path = output_dir / f"{section_id}.md"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed formatting in {file_path}")
        print("------------------------------------------")
    
    # If there are validation errors that couldn't be auto-fixed, save them and report
    remaining_errors = {k: v for k, v in all_errors.items() if k not in fixed_files}
    if remaining_errors:
        error_path = output_dir / "validation_errors.json"
        with open(error_path, 'w', encoding='utf-8') as f:
            json.dump(remaining_errors, f, indent=2, ensure_ascii=False)
        
        print(f"\n--- Markdown Validation Issues ---")
        print(f"Found {sum(len(v) for v in remaining_errors.values())} issues that could not be auto-fixed.")
        
        # Print a summary grouped by error type and section
        error_summary = {}
        for section_id, errors in remaining_errors.items():
            for error in errors:
                error_type = error['error'].split(':')[0]  # Get the main error type
                if error_type not in error_summary:
                    error_summary[error_type] = {'count': 0, 'sections': set()}
                error_summary[error_type]['count'] += 1
                error_summary[error_type]['sections'].add(section_id)
        
        print("\nIssues by type:")
        for error_type, info in error_summary.items():
            sections_str = ", ".join(sorted(info['sections']))
            print(f"• {error_type}: {info['count']} occurrences in sections: {sections_str}")
        
        print("\nDetailed issues by section:")
        for section_id, errors in remaining_errors.items():
            print(f"\n  In {section_id}.md:")
            for error in errors[:3]:  # Show first 3 errors per section
                line_info = f" (line {error['line']})" if error.get('line', 0) > 0 else ""
                print(f"    - {error['error']}{line_info}")
                if error.get('context'):
                    context_lines = error['context'].split('\n')
                    for ctx_line in context_lines[:2]:  # Show up to 2 lines of context
                        print(f"      | {ctx_line}")
            if len(errors) > 3:
                print(f"    - ... and {len(errors) - 3} more issues")
        
        print(f"\nFull validation report saved to: {error_path}")
        print("----------------------------")
        
        # Ask user if they want to proceed with PDF generation despite errors
        while True:
            response = input("\nDo you want to attempt PDF generation despite validation issues? (yes/no): ").lower()
            if response in ['yes', 'y']:
                print("\nProceeding with PDF generation (errors will be visually marked in the output)...")
                break
            elif response in ['no', 'n']:
                print("\nPDF generation skipped. Please fix the validation issues and try again.")
                return None
            else:
                print("Please answer 'yes' or 'no'")
    
    # Generate PDF
    print("\nGenerating PDF...")
    pdf_generator = PDFGenerator(output_dir)
    pdf_path, warnings = pdf_generator.generate_pdf(company_name, language)
    
    if pdf_path:
        print(f"\n✓ PDF generated successfully: {pdf_path}")
        if warnings:
            print("\nWarnings during PDF generation:")
            for warning in warnings:
                print(f"• {warning}")
        return pdf_path
    else:
        print("\n❌ PDF generation failed!")
        print("Please check the warnings above and the debug HTML file for more information.")
        return None

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
        token_stats = generate_all_prompts(company_name, language)

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
                output_dir = Path("output") / f"{company_name}_{language}"
                pdf_path = validate_and_generate_pdf(company_name, language, output_dir)
                
                if pdf_path:
                    console.print(f"\n[green]PDF report generated: {pdf_path}[/green]")
                else:
                    console.print("\n[yellow]PDF generation failed or was skipped.[/yellow]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Process interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"\nError occurred: {str(e)}")
        logger.exception("Unexpected error occurred")
        console.print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()

