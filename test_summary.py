#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from summary_generator import create_executive_summary
from pdf_generator import process_markdown_files, EnhancedPDFGenerator
from rich.console import Console
from rich.panel import Panel
import logging
from rich.logging import RichHandler

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

def main():
    # Check if arguments are provided
    if len(sys.argv) < 3:
        console.print("[yellow]Usage: python test_summary.py <company_name> <language>[/yellow]")
        console.print("[yellow]Example: python test_summary.py 'Japan Airlines' 'English'[/yellow]")
        sys.exit(1)
    
    company_name = sys.argv[1]
    language = sys.argv[2]
    
    # Find the most recent directory for the company
    base_path = Path("output")
    
    # Look for directories that start with the company name
    matching_dirs = sorted([
        d for d in base_path.iterdir() 
        if d.is_dir() and d.name.startswith(f"{company_name}_{language}")
    ], key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not matching_dirs:
        console.print(f"[red]No directories found for {company_name} in {language}[/red]")
        sys.exit(1)
    
    # Use the most recent directory
    output_dir = matching_dirs[0]
    console.print(f"Found latest directory: {output_dir}")
    
    # Generate executive summary
    console.print("Generating executive summary...")
    summary_path = create_executive_summary(output_dir, company_name, language)
    
    if summary_path:
        console.print(Panel(f"Executive summary generated successfully!\nOutput: {summary_path}", title="Success", style="green"))
        
        # Preview the executive summary
        with open(summary_path, 'r', encoding='utf-8') as f:
            content = f.read()
            preview_content = content[:2000] + "..." if len(content) > 2000 else content
            console.print(Panel(preview_content, title="Summary Preview"))
        
        # Generate PDF with the executive summary
        console.print("Generating PDF with executive summary...")
        
        # Create a PDF generator instance directly
        generator = EnhancedPDFGenerator(output_dir, company_name, language)
        if generator.process_sections():
            pdf_path = generator.generate_pdf()
            
            if pdf_path and pdf_path.exists():
                console.print(Panel(f"PDF generated successfully!\nOutput: {pdf_path}", title="Success", style="green"))
                # Open the PDF (macOS specific)
                os.system(f"open {pdf_path}")
            else:
                console.print("[red]Failed to generate PDF[/red]")
        else:
            console.print("[red]Failed to process sections for PDF generation[/red]")
    else:
        console.print("[red]Failed to generate executive summary[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main() 