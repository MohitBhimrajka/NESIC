#!/usr/bin/env python
"""
Test script for presentation_generator.py

This script demonstrates how to use the presentation generator
to create presentations from markdown files in company directories.
"""

import os
import sys
from presentation_generator import generate_presentation

def main():
    """Test the presentation generator with sample data."""
    # Get list of company directories
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    if not os.path.exists(output_dir):
        print(f"Error: Output directory '{output_dir}' does not exist.")
        return 1
    
    # List company directories
    company_dirs = [
        os.path.join(output_dir, d) for d in os.listdir(output_dir) 
        if os.path.isdir(os.path.join(output_dir, d))
    ]
    
    if not company_dirs:
        print("No company directories found in the output folder.")
        return 1
    
    # Print available companies
    print("Available companies:")
    for i, company_dir in enumerate(company_dirs, 1):
        company_name = os.path.basename(company_dir).split('_')[0]
        print(f"{i}. {company_name}")
    
    # Ask user to select a company
    try:
        selection = int(input("\nSelect a company (number): "))
        if selection < 1 or selection > len(company_dirs):
            print("Invalid selection.")
            return 1
    except ValueError:
        print("Please enter a valid number.")
        return 1
    
    company_dir = company_dirs[selection - 1]
    
    # Ask user to select a color scheme
    print("\nColor schemes:")
    print("1. professional (Blue theme)")
    print("2. modern (Google-style theme)")
    print("3. minimal (Black and white with red accent)")
    
    try:
        color_selection = int(input("\nSelect a color scheme (number): "))
        if color_selection < 1 or color_selection > 3:
            print("Invalid selection, using default 'professional' theme.")
            color_scheme = "professional"
        else:
            color_schemes = ["professional", "modern", "minimal"]
            color_scheme = color_schemes[color_selection - 1]
    except ValueError:
        print("Invalid selection, using default 'professional' theme.")
        color_scheme = "professional"
    
    # Generate the presentation
    print(f"\nGenerating presentation for {os.path.basename(company_dir)} with '{color_scheme}' color scheme...")
    try:
        output_path = generate_presentation(company_dir, color_scheme=color_scheme)
        print(f"\nPresentation successfully created and saved to:\n{output_path}")
        return 0
    except Exception as e:
        print(f"Error generating presentation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 