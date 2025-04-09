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
from config import SECTION_ORDER, AVAILABLE_LANGUAGES, PROMPT_FUNCTIONS, LLM_MODEL, LLM_TEMPERATURE

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

def generate_content(client: genai.Client, prompt: str, output_path: Path) -> Dict:
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
            temperature=LLM_TEMPERATURE,
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
                model=LLM_MODEL,
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
        "sections": [section[0] for section in SECTION_ORDER],
        "model": LLM_MODEL,
        "temperature": LLM_TEMPERATURE
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
            for prompt_name, prompt_func_name in PROMPT_FUNCTIONS:
                if shutdown_requested:
                    break
                    
                # Get the prompt function from the prompt_testing module
                prompt_func = getattr(prompt_testing, prompt_func_name)
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
            "model": LLM_MODEL,
            "temperature": LLM_TEMPERATURE,
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
        console.print(f"Using model: {LLM_MODEL} with temperature: {LLM_TEMPERATURE}")
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

