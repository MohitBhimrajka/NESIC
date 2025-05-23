#!/usr/bin/env python3
# test_pdf_generation.py

import os
from pathlib import Path
from pdf_generator import process_markdown_files, EnhancedPDFGenerator, PDFSection
from datetime import datetime

def main():
    """Test PDF generation for the Stripe report"""
    output_dir = Path("output/Stripe_English_20250523_094459")
    company_name = "Stripe"
    language = "English"
    
    print(f"Testing PDF generation for {company_name} ({language})")
    pdf_path = process_markdown_files(output_dir, company_name, language)
    
    if pdf_path:
        print(f"✅ PDF successfully generated: {pdf_path}")
    else:
        print("❌ PDF generation failed")

def test_key_findings_styling():
    """Test script to generate a sample PDF with Key Findings section to check styling."""
    # Create a PDF generator
    pdf_generator = EnhancedPDFGenerator()
    
    # Create a sample section with Key Findings
    key_findings_content = """
# Key Findings

### Key Findings

1. **Massive Payment Volume Growth:** Stripe processed over $1 trillion in payments in 2023, a 25% increase from the approximately $817 billion processed in 2022. Communications in early 2025 indicated $1.4 trillion in TPV for 2024, representing nearly 40% year-over-year growth, underscoring rapid expansion and adoption.

2. **Significant Enterprise Client Traction:** Over 100 companies are now processing more than $1 billion in payments annually with Stripe, including major enterprises like Amazon, Ford, and Maersk, signifying Stripe's successful push into the large enterprise segment.

3. **Achieved Profitability and Positive Cash Flow:** Stripe became cash flow positive in 2023 and expects to maintain profitability, a crucial milestone indicating financial maturity and sustainable operational efficiency alongside continued growth investments.

4. **Valuation Reaffirmed at $65 Billion:** Following a Series I funding round in March 2023 that valued Stripe at $50 billion (raising over $6.5 billion), a secondary share sale in April 2024 reportedly valued the company at $65 billion, indicating sustained investor confidence.

5. **Revenue and Finance Automation Suite Exceeds $500 Million Run Rate:** Stripe's expanded product portfolio beyond payments processing is gaining significant traction, with its suite of financial software tools for billing, invoicing, and revenue management now exceeding $500 million in annual run rate.
"""
    
    section = PDFSection(
        id="key_findings",
        title="Key Findings",
        content=key_findings_content
    )
    
    # Process the section
    section.html_content = pdf_generator._convert_markdown_to_html(section.content)
    
    # Define output directory
    output_dir = Path("output/test_key_findings")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate the PDF
    output_path = output_dir / "test_key_findings.pdf"
    
    # Generate metadata
    metadata = {
        "company_name": "Test Company",
        "generation_date": datetime.now().strftime("%B %d, %Y"),
        "logo_path": "templates/assets/default_logo.png",
        "favicon_path": "templates/assets/favicon.png"
    }
    
    # Generate the PDF
    pdf_generator.generate_pdf([section], str(output_path), metadata)
    
    print(f"Generated test PDF at: {output_path}")
    return output_path

if __name__ == "__main__":
    main()
    test_key_findings_styling() 