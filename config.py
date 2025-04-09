"""
Configuration file for the PDF generation project.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LLM Configuration - Can be overridden with environment variables
LLM_MODEL = os.getenv('LLM_MODEL', 'gemini-2.5-pro-preview-03-25')
LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.8'))

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

# List of prompt functions to run - mapping section IDs to prompt functions
PROMPT_FUNCTIONS = [
    ("basic", "get_basic_prompt"),
    ("financial", "get_financial_prompt"),
    ("competitive", "get_competitive_landscape_prompt"),
    ("management_strategy", "get_management_strategy_prompt"),
    ("regulatory", "get_regulatory_prompt"),
    ("crisis", "get_crisis_prompt"),
    ("digital_transformation", "get_digital_transformation_prompt"),
    ("business_structure", "get_business_structure_prompt"),
    ("vision", "get_vision_prompt"),
    ("management_message", "get_management_message_prompt"),
] 