import streamlit as st
import os
import time
import base64
import re
import threading
from pathlib import Path
from datetime import datetime
import yaml
from typing import List, Tuple, Optional, Dict, Set

# Import functions from test_agent_prompt.py directly
from test_agent_prompt import (
    generate_content,
    generate_all_prompts,
    count_tokens,
    format_time
)
from pdf_generator import process_markdown_files
from summary_generator import create_executive_summary
from config import SECTION_ORDER, AVAILABLE_LANGUAGES, PROMPT_FUNCTIONS, LLM_MODEL, LLM_TEMPERATURE
from google import genai

# Import analytics and user authentication modules
from analytics_logger_apps_script import log_report_generation, show_analytics_status
from user_auth import (
    check_user_authentication,
    show_user_info_form,
    get_user_info,
    show_user_info_header
)

# Configure page settings
st.set_page_config(
    page_title="Account Research AI Agent",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load logo
@st.cache_data
def get_logo_base64():
    try:
        logo_path = Path("templates/assets/supervity_logo.png")
        if not logo_path.exists():
            st.warning(f"Logo file not found at {logo_path}")
            return ""
            
        with open(logo_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.warning(f"Error loading logo: {str(e)}")
        return ""

# Function to display PDF in Streamlit
def display_pdf(pdf_path):
    with open(pdf_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Check if a markdown file contains proper content with a "Sources" heading
def validate_markdown(file_path: Path) -> bool:
    """
    Check if a markdown file contains a "Sources" heading at any level.
    This is a simple heuristic to determine if the file contains proper content.

    Args:
        file_path: Path to the markdown file

    Returns:
        bool: True if the file is valid, False otherwise
    """
    if not file_path.exists() or file_path.stat().st_size == 0:
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if the markdown has a "Sources" heading at any level
        sources_pattern = re.compile(r'^#+\s+Sources', re.MULTILINE)
        if sources_pattern.search(content):
            return True

        # Alternative patterns that might indicate valid content
        alt_patterns = [
            re.compile(r'^#+\s+参考資料', re.MULTILINE),  # Japanese "References"
            re.compile(r'^#+\s+出典', re.MULTILINE),      # Japanese "Sources"
            re.compile(r'^#+\s+References', re.MULTILINE),
            re.compile(r'^#+\s+Bibliography', re.MULTILINE),
            re.compile(r'\[SSX\]', re.MULTILINE)         # Citation markers
        ]

        for pattern in alt_patterns:
            if pattern.search(content):
                return True

        return False
    except Exception:
        return False

# Custom wrapper around generate_all_prompts to integrate with Streamlit
def generate_report_with_progress(company_name: str, language: str, selected_prompts: List[Tuple[str, str]], 
                            context_company_name: str, include_executive_summary: bool = True,
                            ticker: Optional[str] = None, industry: Optional[str] = None):
    """Wrapper around generate_all_prompts with Streamlit progress indicators"""
    # Create a Streamlit progress display
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.markdown("""
    <div style="text-align: center; color: white; font-size: 1.1rem; margin: 1rem 0;">
        <div style="margin-bottom: 0.5rem;">🚀 Initializing report generation...</div>
        <div style="font-size: 0.9rem; opacity: 0.8;">Setting up AI analysis systems...</div>
    </div>
    """, unsafe_allow_html=True)

    # Define a simple progress class that integrates with Streamlit
    class StreamlitProgress:
        def __init__(self):
            self.tasks = {}
            self.current_progress = 0

        def add_task(self, description, total=1, visible=True):
            task_id = len(self.tasks)
            self.tasks[task_id] = {"description": description, "total": total, "completed": 0}
            return task_id

        def update(self, task_id, advance=0, description=None):
            # Check if generation was stopped by user
            if not st.session_state.generation_in_progress or st.session_state.cancel_generation:
                raise Exception("Report generation stopped by user")
                
            if task_id not in self.tasks:
                return

            if advance > 0:
                self.tasks[task_id]["completed"] += advance
                # Calculate overall progress as average of all tasks
                total_progress = sum(task["completed"] / task["total"] for task in self.tasks.values()) / len(self.tasks)
                progress_bar.progress(min(total_progress, 1.0))

            if description:
                self.tasks[task_id]["description"] = description
                clean_description = description.replace("[bold green]", "").replace("[cyan]", "").replace("[/]", "")
                status_text.markdown(f"""
                <div style="text-align: center; color: white; font-size: 1.1rem; margin: 1rem 0;">
                    <div style="margin-bottom: 0.5rem;">Processing {clean_description}</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">Business intelligence report in progress...</div>
                </div>
                """, unsafe_allow_html=True)
                
    # Calculate total steps including executive summary if enabled
    total_steps = len(selected_prompts) + 2  # +1 for validation, +1 for PDF generation
    if include_executive_summary:
        total_steps += 1

    # Create an executive summary progress task to track separately
    exec_summary_progress = StreamlitProgress()
    exec_summary_task = exec_summary_progress.add_task("Executive Summary Generation", total=3)  # 3 steps: start, process, complete

    # Call the original function with our progress display
    try:
        # Check for cancellation before starting
        if st.session_state.cancel_generation:
            raise Exception("Report generation cancelled by user")
            
        token_stats, base_dir = generate_all_prompts(
            company_name,
            language,
            selected_prompts,
            context_company_name,
            ticker=ticker,
            industry=industry,
            progress=StreamlitProgress()
        )

        # Check if the initial generation failed completely
        if not token_stats or not base_dir:
            raise Exception("Initial report generation failed. Cannot proceed to validation.")

        # Validate all markdown files and rerun invalid ones
        markdown_dir = base_dir / "markdown"
        if not markdown_dir.exists():
            raise Exception(f"Markdown directory not found after initial generation: {markdown_dir}")

        invalid_files: Dict[str, Path] = {}

        status_text.markdown("""
        <div style="text-align: center; color: white; font-size: 1.1rem; margin: 1rem 0;">
            <div style="margin-bottom: 0.5rem;">🔍 Validating generated content...</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">Ensuring report quality and completeness...</div>
        </div>
        """, unsafe_allow_html=True)

        # First check - validate each markdown file
        for prompt_name, _ in selected_prompts:
            md_file = markdown_dir / f"{prompt_name}.md"
            if not validate_markdown(md_file):
                invalid_files[prompt_name] = md_file
                status_text.markdown(f"""
                <div style="text-align: center; color: white; font-size: 1.1rem; margin: 1rem 0;">
                    <div style="margin-bottom: 0.5rem;">⚠️ Found invalid content in {prompt_name}.md</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">Will retry generation for better quality...</div>
                </div>
                """, unsafe_allow_html=True)

        # Re-run prompts for invalid files if any
        if invalid_files:
            status_text.markdown(f"""
            <div style="text-align: center; color: white; font-size: 1.1rem; margin: 1rem 0;">
                <div style="margin-bottom: 0.5rem;">🔄 Re-running {len(invalid_files)} sections...</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">Improving content quality for optimal results...</div>
            </div>
            """, unsafe_allow_html=True)

            # Create API client with the new format
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in .env file")
            client = genai.Client(api_key=api_key)

            # Get remaining invalid prompt pairs
            invalid_prompts = [(name, next(p[1] for p in selected_prompts if p[0] == name))
                              for name in invalid_files.keys()]

            # Create a progress indicator for retries
            retry_progress = StreamlitProgress()
            for retry_idx, (prompt_name, prompt_func_name) in enumerate(invalid_prompts):
                retry_task = retry_progress.add_task(f"Retrying {prompt_name}...", total=1)

                # Get the prompt function from prompt_testing module
                import prompt_testing
                prompt_func = getattr(prompt_testing, prompt_func_name)

                # Generate the prompt with proper parameters
                if prompt_name == "strategy_research":
                    prompt = prompt_func(
                        company_name,
                        language,
                        ticker=ticker,
                        industry=industry,
                        context_company_name=context_company_name
                    )
                else:
                    prompt = prompt_func(
                        company_name,
                        language,
                        ticker=ticker,
                        industry=industry,
                        context_company_name=context_company_name
                    )

                # Generate content
                status_text.markdown(f"""
                <div style="text-align: center; color: white; font-size: 1.1rem; margin: 1rem 0;">
                    <div style="margin-bottom: 0.5rem;">🔄 Retrying {prompt_name}...</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">Generating enhanced content...</div>
                </div>
                """, unsafe_allow_html=True)
                result = generate_content(client, prompt, invalid_files[prompt_name])

                # Update token stats
                if result["status"] == "success":
                    token_stats["prompts"][prompt_name] = result
                    token_stats["summary"]["total_input_tokens"] += result["input_tokens"]
                    token_stats["summary"]["total_output_tokens"] += result["output_tokens"]
                    token_stats["summary"]["total_tokens"] += result["total_tokens"]
                    token_stats["summary"]["successful_prompts"] += 1

                    # --- CORRECTED LOGIC ---
                    # If a prompt succeeded on retry, decrement the failed count,
                    # but ensure the count doesn't go below zero.
                    if token_stats["summary"]["failed_prompts"] > 0:
                        token_stats["summary"]["failed_prompts"] -= 1
                    # --- END CORRECTION ---

                retry_progress.update(retry_task, advance=1, description=f"Retried {prompt_name}")

            # Second check - validate retried files
            still_invalid = []
            for prompt_name in invalid_files:
                md_file = markdown_dir / f"{prompt_name}.md"
                if not validate_markdown(md_file):
                    still_invalid.append(prompt_name)

            if still_invalid:
                status_text.markdown(f"""
                <div style="text-align: center; color: #ff9a5a; font-size: 1.1rem; margin: 1rem 0;">
                    <div style="margin-bottom: 0.5rem;">⚠️ Some content needs improvement</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">Proceeding with available sections...</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                status_text.markdown("""
                <div style="text-align: center; color: white; font-size: 1.1rem; margin: 1rem 0;">
                    <div style="margin-bottom: 0.5rem;">✅ All content validated successfully!</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">Quality check complete...</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            status_text.markdown("""
            <div style="text-align: center; color: white; font-size: 1.1rem; margin: 1rem 0;">
                <div style="margin-bottom: 0.5rem;">✅ All sections generated successfully!</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">Content validation passed...</div>
            </div>
            """, unsafe_allow_html=True)

        # Generate executive summary if report generation was successful
        if token_stats['summary']['successful_prompts'] > 0 and include_executive_summary:
            status_text.markdown("""
            <div style="text-align: center; color: white; font-size: 1.1rem; margin: 1rem 0;">
                <div style="margin-bottom: 0.5rem;">📋 Preparing executive summary...</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">Creating comprehensive overview...</div>
            </div>
            """, unsafe_allow_html=True)
            exec_summary_progress.update(exec_summary_task, advance=1, description="Preparing executive summary...")
            
            # Initialize executive summary path
            exec_summary_path = None
            retries = 2  # Allow up to 2 retries for executive summary generation
            
            for attempt in range(retries + 1):
                try:
                    status_text.markdown(f"""
                    <div style="text-align: center; color: white; font-size: 1.1rem; margin: 1rem 0;">
                        <div style="margin-bottom: 0.5rem;">📝 Creating executive summary (attempt {attempt+1}/{retries+1})...</div>
                        <div style="font-size: 0.9rem; opacity: 0.8;">Synthesizing key insights...</div>
                    </div>
                    """, unsafe_allow_html=True)
                    exec_summary_progress.update(exec_summary_task, advance=0, 
                                                description=f"Generating executive summary (attempt {attempt+1}/{retries+1})...")
                    
                    exec_summary_path = create_executive_summary(base_dir, company_name, language)
                    
                    if exec_summary_path and exec_summary_path.exists():
                        status_text.markdown("""
                        <div style="text-align: center; color: white; font-size: 1.1rem; margin: 1rem 0;">
                            <div style="margin-bottom: 0.5rem;">✅ Executive summary completed!</div>
                            <div style="font-size: 0.9rem; opacity: 0.8;">Key insights captured...</div>
                        </div>
                        """, unsafe_allow_html=True)
                        exec_summary_progress.update(exec_summary_task, advance=1, 
                                                    description="Executive summary generated successfully!")
                        
                        # Add the summary to the token stats
                        try:
                            with open(exec_summary_path, 'r', encoding='utf-8') as f:
                                summary_content = f.read()
                                summary_tokens = count_tokens(summary_content)
                                
                            # Update token stats to include the executive summary
                            token_stats["prompts"]["executive_summary"] = {
                                "status": "success",
                                "output_tokens": summary_tokens,
                                "input_tokens": 0,  # We don't track this separately
                                "total_tokens": summary_tokens,
                                "execution_time": 0  # We don't track this separately
                            }
                            token_stats["summary"]["total_output_tokens"] += summary_tokens
                            token_stats["summary"]["total_tokens"] += summary_tokens
                            token_stats["summary"]["successful_prompts"] += 1
                            
                            # Success - break out of retry loop
                            exec_summary_progress.update(exec_summary_task, advance=1, 
                                                        description="Executive summary metrics collected")
                            break
                        except Exception as e:
                            status_text.text(f"Warning: Could not count tokens for executive summary: {str(e)}")
                            # Even if token counting fails, we still have a summary
                            break
                    else:
                        status_text.text(f"Executive summary generation attempt {attempt+1} failed. " + 
                                        ("Retrying..." if attempt < retries else "Giving up."))
                        if attempt >= retries:
                            status_text.text("Warning: Failed to generate executive summary after all attempts. Proceeding without it.")
                
                except Exception as e:
                    if attempt < retries:
                        status_text.text(f"Error generating executive summary: {str(e)}. Retrying...")
                        time.sleep(2)  # Brief pause before retry
                    else:
                        status_text.text(f"Error generating executive summary after all attempts: {str(e)}. Proceeding without it.")
        elif include_executive_summary:
            status_text.text("No successful sections generated, skipping executive summary.")
        else:
            status_text.text("Executive summary generation disabled. Skipping this step.")

        # Return the results
        pdf_path = None
        if token_stats['summary']['successful_prompts'] > 0:
            # Define PDF path relative to base_dir
            pdf_file_name = f"{company_name}_{language}_Report.pdf"
            pdf_path = base_dir / "pdf" / pdf_file_name

            # Ensure PDF directory exists
            (base_dir / "pdf").mkdir(parents=True, exist_ok=True)

            # Check if PDF needs generation (only if markdown exists and PDF doesn't)
            markdown_files_exist = any((markdown_dir / f"{name}.md").exists() for name, _ in selected_prompts)
            if markdown_files_exist and not pdf_path.exists():
                status_text.markdown("""
                <div style="text-align: center; color: white; font-size: 1.1rem; margin: 1rem 0;">
                    <div style="margin-bottom: 0.5rem;">📄 Generating final PDF report...</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">Formatting and compiling content...</div>
                </div>
                """, unsafe_allow_html=True)
                generated_pdf_path = process_markdown_files(base_dir, company_name, language)
                if generated_pdf_path:
                    pdf_path = generated_pdf_path # Update path if generated
                else:
                    pdf_path = None # PDF generation failed
                    status_text.markdown("""
                    <div style="text-align: center; color: #ff9a5a; font-size: 1.1rem; margin: 1rem 0;">
                        <div style="margin-bottom: 0.5rem;">⚠️ PDF generation failed</div>
                        <div style="font-size: 0.9rem; opacity: 0.8;">Content is available in markdown format...</div>
                    </div>
                    """, unsafe_allow_html=True)
            elif not markdown_files_exist:
                status_text.markdown("""
                <div style="text-align: center; color: #ff9a5a; font-size: 1.1rem; margin: 1rem 0;">
                    <div style="margin-bottom: 0.5rem;">⚠️ No content files found</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">Unable to generate PDF...</div>
                </div>
                """, unsafe_allow_html=True)
                pdf_path = None

        status_text.markdown("""
        <div style="text-align: center; color: var(--primary-lime); font-size: 1.3rem; margin: 1rem 0;">
            <div style="margin-bottom: 0.5rem;">🎉 Report generation complete!</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">Your business intelligence report is ready...</div>
        </div>
        """, unsafe_allow_html=True)
        progress_bar.empty()

        return token_stats, pdf_path, base_dir

    except Exception as e:
        status_text.text(f"Error: {str(e)}")
        st.error(f"Error during report generation: {str(e)}")
        # Ensure None is returned for all parts if an error occurs
        return None, None, None


# Add custom CSS with Supervity brand colors
def apply_custom_css():
    st.markdown("""
    <style>
    /* Supervity Brand Colors */
    :root {
        /* Primary Colors */
        --primary-black: #000000;
        --primary-white: #ffffff;
        --primary-navy: #000b37;
        --primary-lime: #85c20b;

        /* Secondary Colors */
        --secondary-dark-gray: #474747;
        --secondary-light-gray: #c7c7c7;
        --secondary-soft-blue: #8289ec;
        --secondary-light-lime: #c3fb54;

        /* Complementary Colors */
        --comp-coral: #ff9a5a;
        --comp-purple: #b181ff;
        --comp-cyan: #31b8e1;
        --comp-pink: #ff94a8;
    }

    .stApp {
        background-color: #f7f7f7;
    }

    /* Ensure all text is visible */
    .stApp, .stApp p, .stApp div, .stApp span, .stApp label {
        color: var(--primary-navy) !important;
    }

    /* Fix specific text elements */
    .stMarkdown, .stMarkdown p, .stMarkdown div {
        color: var(--primary-navy) !important;
    }

    /* Comprehensive text visibility fixes */
    .stText, .stText p, .stText div, .stText span {
        color: var(--primary-navy) !important;
    }

    /* Radio button labels */
    .stRadio label, .stRadio > div > label {
        color: var(--primary-navy) !important;
    }

    /* Info message text */
    .stInfo, .stInfo p, .stInfo div {
        color: var(--primary-navy) !important;
    }

    /* Any element with markdown class */
    [data-testid="stMarkdownContainer"], 
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] div {
        color: var(--primary-navy) !important;
    }

    /* Override any potential light/invisible text */
    * {
        color: inherit !important;
    }

    body, html {
        color: var(--primary-navy) !important;
    }

    /* Header styling */
    .main-header-container {
        background-color: var(--primary-navy);
        padding: 1.5rem 1rem 1rem 1rem;
        border-radius: 0px;
        margin-bottom: 1rem;
        box-shadow: none;
        border: none;
    }

    .main-header {
        color: var(--primary-white);
        text-align: center;
        padding: 0;
        margin: 0.25rem 0;
        font-size: 2rem;
        font-weight: 700;
    }

    .sub-header {
        color: var(--primary-lime);
        text-align: center;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 0.5rem;
    }

    /* Logo styling */
    .logo-container {
        text-align: center;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .logo-image {
        max-width: 60px;
        max-height: 60px;
        height: auto;
        width: auto;
        margin: 0 auto;
    }

    /* Form styling */
    .form-container {
        background-color: transparent;
        padding: 1rem 0;
        border-radius: 0px;
        box-shadow: none;
        border: none;
    }

    .form-header {
        color: var(--primary-navy);
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    /* Button styling */
    .stButton>button {
        width: 100%;
        padding: 0.75rem;
        background-color: var(--primary-lime);
        color: var(--primary-navy);
        font-weight: bold;
        border: none;
        border-radius: 6px;
        transition: all 0.3s;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 1rem;
    }

    .stButton>button:hover {
        background-color: var(--secondary-light-lime);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }

    /* Section styling */
    .section-title {
        color: var(--primary-navy);
        font-weight: bold;
        margin-top: 2rem;
        font-size: 1.5rem;
        border-bottom: 2px solid var(--primary-lime);
        padding-bottom: 0.5rem;
    }

    /* Stats cards styling */
    .report-stats {
        padding: 1rem;
        background-color: transparent;
        border-radius: 0px;
        margin-top: 1rem;
        border-left: 4px solid var(--primary-lime);
        box-shadow: none;
        border: none;
    }

    /* Input fields styling */
    div[data-baseweb="input"] {
        border-radius: 6px;
    }

    div[data-baseweb="input"]:focus-within {
        border-color: var(--primary-lime);
        box-shadow: 0 0 0 1px var(--primary-lime);
    }

    /* Hide sidebar */
    section[data-testid="stSidebar"] {
        display: none;
    }

    /* Success message */
    div[data-baseweb="notification"] {
        background-color: var(--primary-lime);
        border-color: var(--primary-lime);
        color: var(--primary-navy);
    }

    /* Footer */
    .footer {
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid var(--secondary-light-gray);
        text-align: center;
        color: var(--secondary-dark-gray);
        font-size: 0.9rem;
    }

    /* Custom metric styles */
    .metric-card {
        background-color: transparent;
        border-radius: 0px;
        padding: 1rem;
        box-shadow: none;
        border: none;
        text-align: center;
        height: 100%;
    }

    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--primary-navy);
        margin: 0.5rem 0;
    }

    .metric-label {
        font-size: 1rem;
        color: var(--secondary-dark-gray);
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        color: var(--primary-lime);
    }

    /* PDF container */
    .pdf-container {
        margin-top: 2rem;
        padding: 1rem;
        background-color: transparent;
        border-radius: 0px;
        box-shadow: none;
        border: none;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f0f2f6;
        border-radius: 6px;
        padding: 0.5rem;
        font-weight: 600;
        color: var(--primary-navy);
    }

    .streamlit-expanderHeader:hover {
        background-color: #e6e9ef;
    }

    .streamlit-expanderContent {
        border: 1px solid #e6e9ef;
        border-top: none;
        border-radius: 0 0 6px 6px;
        padding: 1rem;
    }

    /* Report Type Selection Styles */
    .report-type-container {
        margin: 1.5rem 0;
    }

    .report-type-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--primary-navy);
        margin-bottom: 0.5rem;
    }

    .report-type-subtitle {
        color: var(--secondary-dark-gray);
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    .preset-cards-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .preset-card {
        background: white;
        border: 2px solid #e1e5e9;
        border-radius: 12px;
        padding: 1.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        text-align: left;
    }

    .preset-card:hover {
        border-color: var(--primary-lime);
        box-shadow: 0 4px 15px rgba(133, 194, 11, 0.15);
        transform: translateY(-2px);
    }

    .preset-card.selected {
        border-color: var(--primary-lime);
        background: linear-gradient(135deg, #f8fff4 0%, #ffffff 100%);
        box-shadow: 0 4px 20px rgba(133, 194, 11, 0.2);
    }

    .preset-card.selected::after {
        content: "✓";
        position: absolute;
        top: 10px;
        right: 15px;
        background: var(--primary-lime);
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: bold;
    }

    .preset-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        display: block;
    }

    .preset-title {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: var(--primary-navy) !important;
        margin-bottom: 0.5rem !important;
    }

    .preset-description {
        color: var(--secondary-dark-gray) !important;
        font-size: 0.9rem !important;
        margin-bottom: 0.75rem !important;
        line-height: 1.4 !important;
    }

    .preset-best-for {
        font-size: 0.85rem !important;
        color: var(--comp-cyan) !important;
        font-style: italic !important;
        margin-bottom: 0.5rem !important;
    }

    .preset-time {
        font-size: 0.8rem !important;
        color: var(--secondary-dark-gray) !important;
        background: #f8f9fa !important;
        padding: 0.25rem 0.5rem !important;
        border-radius: 15px !important;
        display: inline-block !important;
    }

    .custom-selection {
        background: white;
        border: 2px solid #e1e5e9;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
    }

    .custom-selection.expanded {
        border-color: var(--primary-lime);
    }

    .custom-header {
        display: flex;
        align-items: center;
        cursor: pointer;
        margin-bottom: 1rem;
    }

    .custom-icon {
        font-size: 1.5rem;
        margin-right: 0.75rem;
    }

    .custom-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--primary-navy);
        flex-grow: 1;
    }

    .section-groups {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }

    .section-group {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
    }

    .section-group-title {
        font-weight: 600;
        color: var(--primary-navy);
        margin-bottom: 0.75rem;
        font-size: 0.95rem;
    }

    .section-preview {
        background: var(--secondary-light-lime);
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
        border-left: 4px solid var(--primary-lime);
    }

    .section-preview-title {
        font-weight: 600;
        color: var(--primary-navy);
        margin-bottom: 0.5rem;
    }

    .section-preview-content {
        font-size: 0.9rem;
        color: var(--secondary-dark-gray);
    }

    /* Professional Wizard Styles */
    .wizard-container {
        max-width: 1200px !important;
        margin: 0 auto !important;
        padding: 0 1rem !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }

    .step-container {
        background: transparent;
        border-radius: 0px;
        padding: 1rem 0;
        margin-bottom: 1rem;
        box-shadow: none;
        border: none;
    }

    .step-container.disabled {
        opacity: 0.6;
        pointer-events: none;
    }

    .step-title {
        color: var(--primary-navy);
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }

    .step-description {
        color: var(--secondary-dark-gray);
        font-size: 0.95rem;
        margin-bottom: 1rem;
        line-height: 1.4;
    }

    /* Professional Button Styles */
    .stButton > button {
        border-radius: 6px !important;
        font-weight: 500 !important;
        padding: 0.75rem 1.25rem !important;
        transition: all 0.2s ease !important;
        border: 1px solid #e1e5e9 !important;
        font-size: 0.95rem !important;
        background: white !important;
        color: var(--primary-navy) !important;
    }

    .stButton > button:hover {
        background: var(--primary-lime) !important;
        color: var(--primary-navy) !important;
        border-color: var(--primary-lime) !important;
    }

    /* Prominent Generate Button */
    .generate-button button {
        background: linear-gradient(135deg, var(--primary-lime) 0%, var(--secondary-light-lime) 100%) !important;
        color: var(--primary-navy) !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 2rem 4rem !important;
        font-size: 1.4rem !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        box-shadow: 0 8px 40px rgba(133, 194, 11, 0.6) !important;
        transition: all 0.4s ease !important;
        min-height: 80px !important;
        position: relative !important;
        overflow: hidden !important;
        transform: scale(1.05) !important;
        width: 100% !important;
        margin: 2rem 0 !important;
    }

    .generate-button button:hover {
        background: linear-gradient(135deg, var(--secondary-light-lime) 0%, var(--primary-lime) 100%) !important;
        color: var(--primary-navy) !important;
        transform: scale(1.1) translateY(-4px) !important;
        box-shadow: 0 12px 50px rgba(133, 194, 11, 0.8) !important;
    }

    .generate-button button:active {
        transform: scale(1.02) translateY(-1px) !important;
    }

    /* Progress Styles */
    .progress-container {
        background: rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        padding: 2rem;
        margin: 2rem 0;
        text-align: center;
        backdrop-filter: blur(10px);
    }

    .progress-title {
        color: white;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }

    .progress-subtitle {
        color: rgba(255, 255, 255, 0.8);
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .progress-animation {
        width: 60px;
        height: 60px;
        border: 4px solid rgba(255, 255, 255, 0.3);
        border-top: 4px solid var(--primary-lime);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Professional Selection Preview */
    .selection-preview {
        background: transparent;
        border: none;
        border-radius: 0px;
        padding: 1.25rem 0;
        margin-top: 1rem;
    }

    .preview-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.75rem;
    }

    .preview-icon {
        font-size: 1.25rem;
        color: var(--primary-lime);
    }

    .preview-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--primary-navy);
    }

    .preview-description {
        color: var(--secondary-dark-gray);
        font-size: 0.95rem;
        margin-bottom: 0.75rem;
        line-height: 1.4;
    }

    .preview-details {
        display: grid;
        gap: 0.4rem;
    }

    .preview-item {
        color: var(--secondary-dark-gray);
        font-size: 0.9rem;
        padding: 0.2rem 0;
    }

    /* Professional Custom Preview */
    .custom-preview {
        background: transparent;
        border: none;
        border-radius: 0px;
        padding: 1.25rem 0;
        margin-top: 1rem;
    }

    .custom-preview-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--primary-navy);
        margin-bottom: 0.75rem;
    }

    .custom-preview-details {
        display: grid;
        gap: 0.4rem;
    }

    .custom-item {
        color: var(--secondary-dark-gray);
        font-size: 0.9rem;
        padding: 0.2rem 0;
    }

    /* Prominent Generate Section */
    .generate-section {
        background: linear-gradient(135deg, var(--primary-navy) 0%, var(--secondary-dark-gray) 100%);
        border-radius: 12px;
        padding: 3rem 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0, 11, 55, 0.3);
        border: none;
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .generate-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        transition: left 0.8s;
    }

    .generate-section:hover::before {
        left: 100%;
    }

    .generate-title {
        color: white !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
    }

    .generate-subtitle {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 1rem !important;
        margin-bottom: 2rem !important;
        line-height: 1.4 !important;
    }

    /* Professional Input Styles */
    .stTextInput > div > div > input {
        border-radius: 4px !important;
        border: 1px solid #e1e5e9 !important;
        padding: 0.6rem 0.75rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--primary-lime) !important;
        box-shadow: 0 0 0 2px rgba(133, 194, 11, 0.1) !important;
    }

    .stSelectbox > div > div > div {
        border-radius: 4px !important;
        border: 1px solid #e1e5e9 !important;
        transition: all 0.2s ease !important;
    }

    .stSelectbox > div > div > div:focus-within {
        border-color: var(--primary-lime) !important;
        box-shadow: 0 0 0 2px rgba(133, 194, 11, 0.1) !important;
    }

    /* Professional Checkbox Styles */
    .stCheckbox > label {
        padding: 0.4rem 0 !important;
        font-size: 0.95rem !important;
        font-weight: 400 !important;
        color: var(--secondary-dark-gray) !important;
    }

    .stCheckbox > label > div:first-child {
        margin-right: 0.6rem !important;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .step-container {
            padding: 1.5rem !important;
            margin-bottom: 1.5rem !important;
        }
        
        .step-title {
            font-size: 1.5rem !important;
        }
        
        .wizard-container {
            padding: 0 0.5rem !important;
        }
        
        .summary-section {
            margin: 1rem auto !important;
            padding: 1.5rem !important;
        }
        
        .summary-items {
            grid-template-columns: 1fr !important;
        }
        
        .summary-current-selection {
            font-size: 1rem !important;
            padding: 0.8rem 1rem !important;
        }
    }

    /* Animation for smooth transitions */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .step-container {
        animation: fadeInUp 0.5s ease-out;
    }
    
    /* Animation for generation progress */
    .generation-progress {
        background: linear-gradient(135deg, var(--primary-navy) 0%, var(--secondary-dark-gray) 100%);
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        text-align: center;
        color: white;
    }
    
    /* Stop button styling */
    .stop-button button {
        background-color: var(--comp-coral) !important;
        color: white !important;
        border: 2px solid var(--comp-coral) !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stop-button button:hover {
        background-color: #ff7043 !important;
        border-color: #ff7043 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(255, 154, 90, 0.3) !important;
    }

    /* Success states */
    .stSuccess {
        border-radius: 12px !important;
        border-left: 4px solid var(--primary-lime) !important;
    }

    /* Info states */
    .stInfo {
        border-radius: 12px !important;
        border-left: 4px solid var(--comp-cyan) !important;
    }

    /* Professional Summary Section */
    .summary-section {
        background: transparent !important;
        border: none !important;
        border-radius: 0px !important;
        padding: 1rem 0 !important;
        margin: 2rem auto !important;
        max-width: 1000px !important;
        width: 100% !important;
        box-shadow: none !important;
        display: block !important;
    }

    .summary-header {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        color: var(--primary-navy) !important;
        margin-bottom: 1rem !important;
        text-align: center;
        border-bottom: 2px solid var(--primary-lime);
        padding-bottom: 0.5rem;
    }

    .summary-current-selection {
        background: var(--primary-navy) !important;
        color: white !important;
        padding: 1rem 1.5rem !important;
        border-radius: 8px !important;
        text-align: center !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
        font-size: 1.1rem !important;
        min-height: 50px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        word-wrap: break-word !important;
        white-space: normal !important;
    }

    .summary-items {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)) !important;
        gap: 1rem !important;
        align-items: stretch !important;
        margin-top: 1rem !important;
    }

    .summary-item {
        background: transparent !important;
        padding: 1rem !important;
        border-radius: 0px !important;
        border-left: 4px solid var(--primary-lime) !important;
        font-size: 0.95rem !important;
        color: var(--primary-navy) !important;
        font-weight: 500 !important;
        min-height: 60px !important;
        display: flex !important;
        align-items: center !important;
        box-shadow: none !important;
    }

    .summary-item strong {
        color: var(--primary-navy) !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Report preset configurations
REPORT_PRESETS = {
    "complete": {
        "name": "Complete Analysis",
        "description": "Comprehensive business analysis covering all operational areas",
        "best_for": "Due diligence, M&A research, full company assessment",
        "sections": [name for name, _ in PROMPT_FUNCTIONS],
        "est_time": "15-20 minutes"
    },
    "strategic": {
        "name": "Strategic Assessment",
        "description": "Leadership, competitive positioning, and strategic direction analysis",
        "best_for": "Partnership evaluation, strategic planning, competitive intelligence",
        "sections": ["basic", "vision", "management_strategy", "competitive", "strategy_research"],
        "est_time": "8-12 minutes"
    },
    "financial": {
        "name": "Financial & Risk Review",
        "description": "Financial performance, regulatory compliance, and risk assessment",
        "best_for": "Investment decisions, credit analysis, risk evaluation",
        "sections": ["basic", "financial", "regulatory", "crisis"],
        "est_time": "6-10 minutes"
    },
    "innovation": {
        "name": "Innovation & Technology",
        "description": "Digital transformation capabilities and business model innovation",
        "best_for": "Technology partnerships, innovation assessment, digital readiness",
        "sections": ["basic", "digital_transformation", "business_structure", "vision", "management_strategy"],
        "est_time": "6-10 minutes"
    }
}

# Section groups for custom selection
SECTION_GROUPS = {
    "foundational": {
        "name": "Foundational Analysis",
        "sections": ["basic"],
        "always_selected": True
    },
    "strategic": {
        "name": "Strategic Analysis",
        "sections": ["vision", "management_strategy", "strategy_research"]
    },
    "financial": {
        "name": "Financial Analysis", 
        "sections": ["financial", "regulatory"]
    },
    "operational": {
        "name": "Operational Analysis",
        "sections": ["business_structure", "digital_transformation", "competitive"]
    },
    "risk": {
        "name": "Risk Analysis",
        "sections": ["crisis"]
    }
}

# Custom metric component
def metric_card(icon, label, value):
    return f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """

# Helper function to create preset card HTML
def create_preset_card(preset_id, preset_data, is_selected=False):
    selected_class = "selected" if is_selected else ""
    return f"""
    <div class="preset-card {selected_class}" onclick="selectPreset('{preset_id}')">
        <div class="preset-icon">{preset_data['icon']}</div>
        <div class="preset-title">{preset_data['name']}</div>
        <div class="preset-description">{preset_data['description']}</div>
        <div class="preset-best-for">Best for: {preset_data['best_for']}</div>
        <div class="preset-time">⏱️ {preset_data['est_time']}</div>
    </div>
    """

# Helper function to get section title from section ID
def get_section_title(section_id):
    """Get human-readable title for a section ID"""
    section_titles = {
        "basic": "Basic Information",
        "financial": "Financial Analysis", 
        "competitive": "Competitive Landscape",
        "management_strategy": "Management Strategy",
        "regulatory": "Regulatory Environment",
        "crisis": "Crisis Management",
        "digital_transformation": "Digital Transformation",
        "business_structure": "Business Structure",
        "vision": "Vision & Leadership",
        "management_message": "Management Message",
        "strategy_research": "Strategy Research"
    }
    return section_titles.get(section_id, section_id.replace("_", " ").title())

# Check user authentication first - if not authenticated, show only the auth form
if not check_user_authentication():
    show_user_info_form()
    st.stop()

# User is authenticated - show the main app
apply_custom_css()

# Header with Supervity branding
st.markdown('<div class="main-header-container">', unsafe_allow_html=True)
logo_html = f'<div class="logo-container"><img src="data:image/png;base64,{get_logo_base64()}" class="logo-image"></div>'
st.markdown(logo_html, unsafe_allow_html=True)
st.markdown('<h1 class="main-header">Account Research AI Agent</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your intelligent research assistant for comprehensive company analysis</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state for reactive behavior (moved to top)
if 'report_type' not in st.session_state:
    st.session_state.report_type = 'complete'
if 'custom_sections' not in st.session_state:
    st.session_state.custom_sections = []
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'generation_in_progress' not in st.session_state:
    st.session_state.generation_in_progress = False
if 'cancel_generation' not in st.session_state:
    st.session_state.cancel_generation = False

# Show analytics status (now hidden for clean UI)
show_analytics_status()

# Handle actual report generation when in progress
if st.session_state.generation_in_progress and 'generation_params' in st.session_state:
    params = st.session_state.generation_params
    
    # Get selected sections based on report type
    if params['report_type'] != 'custom':
        selected_sections = REPORT_PRESETS[params['report_type']]["sections"]
    else:
        selected_sections = params['custom_sections']

    # Filter selected prompts based on selected sections
    selected_prompts = [(section_id, prompt_func) for section_id, prompt_func in PROMPT_FUNCTIONS if section_id in selected_sections]
    
    # Ensure we have at least basic information
    if not selected_prompts:
        selected_prompts = [("basic", "get_basic_prompt")]

    # Get user info for analytics
    user_info = get_user_info()
    
    # Record start time for analytics
    generation_start_time = time.time()
    
    # Generate report
    try:
        result = generate_report_with_progress(
            params['target_company'],
            params['language'],
            selected_prompts,
            params['context_company'],
            include_executive_summary=True,  # Always generate executive summary
            ticker=params['ticker'],
            industry=params['industry']
        )
        
        token_stats, pdf_path, base_dir = result
    except Exception as e:
        # Handle any errors during generation
        st.session_state.generation_in_progress = False
        st.session_state.pop('generation_params', None)  # Clean up
        st.error(f"An error occurred during generation: {str(e)}")
        st.rerun()

    # Calculate generation time
    generation_time = time.time() - generation_start_time
    
    # Check if generation was successful
    # Add a small delay and retry mechanism to handle potential file system delays
    pdf_exists = False
    if pdf_path and isinstance(pdf_path, Path):
        # Try multiple times to check for file existence (handles file system delays)
        for attempt in range(3):
            if pdf_path.exists():
                pdf_exists = True
                break
            time.sleep(0.5)  # Wait 500ms before retrying
        
        # Debug logging to help identify the issue
        print(f"DEBUG: PDF path: {pdf_path}")
        print(f"DEBUG: PDF exists after retry: {pdf_exists}")
        print(f"DEBUG: Token stats exists: {token_stats is not None}")
    
    report_success = token_stats is not None and pdf_exists
    
    # Log the report generation to analytics
    try:
        sections_generated = [section_id for section_id, _ in selected_prompts] if selected_prompts else []
        token_count = token_stats['summary']['total_tokens'] if token_stats and 'summary' in token_stats else 0
        
        log_report_generation(
            user_name=user_info['name'],
            business_email=user_info['email'],
            target_company=params['target_company'],
            language=params['language'],
            sections_generated=sections_generated,
            report_success=report_success,
            session_id=user_info['session_id'],
            generation_time=generation_time,
            token_count=token_count,
            context_company=params['context_company']
        )
    except Exception as e:
        # Don't let analytics logging failure break the app
        st.warning(f"Analytics logging failed: {str(e)}")
        pass
    
    # Store results and reset generation state
    st.session_state.generation_results = {
        'token_stats': token_stats,
        'pdf_path': pdf_path,
        'base_dir': base_dir,
        'params': params,
        'generation_time': generation_time,
        'pdf_exists': pdf_exists,
        'report_success': report_success
    }
    st.session_state.generation_in_progress = False
    st.session_state.pop('generation_params', None)  # Clean up
    st.rerun()

# Show generation status banner and progress if in progress  
if st.session_state.generation_in_progress:
    st.markdown("""
    <div style="background: linear-gradient(135deg, var(--comp-coral) 0%, #ff7043 100%); color: white; padding: 1rem; text-align: center; margin-bottom: 1rem; border-radius: 8px; border: none;">
        <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.25rem;">Report Generation in Progress</div>
        <div style="font-size: 0.9rem; opacity: 0.9;">Interface is temporarily locked. Use the stop button below to cancel generation.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show progress UI with stop button
    st.markdown('''
    <div class="progress-container">
        <div class="progress-animation"></div>
        <div class="progress-title">Generating Your Report</div>
        <div class="progress-subtitle">Please wait while we analyze and compile your business intelligence report</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Stop button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="stop-button">', unsafe_allow_html=True)
        if st.button("Stop Generation", type="secondary", use_container_width=True, key="stop_generation_header"):
            st.session_state.cancel_generation = True
            st.session_state.generation_in_progress = False
            st.warning("Report generation stopped by user.")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)



# Function to create an interactive preset card
def create_interactive_preset_card(preset_id, preset_data, is_selected=False):
    selected_class = "selected" if is_selected else ""
    return f"""
    <div class="interactive-preset-card {selected_class}" onclick="selectPreset('{preset_id}')">
        <div class="preset-icon-large">{preset_data['icon']}</div>
        <div class="preset-title-large">{preset_data['name']}</div>
        <div class="preset-description-large">{preset_data['description']}</div>
        <div class="preset-details">
            <div class="preset-best-for"><strong>💡 Best for:</strong> {preset_data['best_for']}</div>
            <div class="preset-time-large">⏱️ <strong>{preset_data['est_time']}</strong></div>
            <div class="preset-sections-count">📋 <strong>{len(preset_data['sections'])} sections</strong></div>
        </div>
    </div>
    """

# Main interface - Only show if generation is NOT in progress
if not st.session_state.generation_in_progress:
    st.markdown('<div class="wizard-container">', unsafe_allow_html=True)

    # Step 1: Company Information
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="step-title">Company Information</h2>', unsafe_allow_html=True)
    st.markdown('<p class="step-description">Enter the target company details and your organization information</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.5, 1, 1])

    with col1:
        target_company = st.text_input(
            "Target Company Name",
            placeholder="e.g., Apple, Tesla, Microsoft",
            key="target_company_input",
            disabled=st.session_state.generation_in_progress
        )
        
        context_company = st.text_input(
            "Your Company Name",
            placeholder="Your organization's name",
            key="context_company_input",
            disabled=st.session_state.generation_in_progress
        )

    with col2:
        ticker = st.text_input(
            "Stock Ticker (Optional)",
            placeholder="AAPL, TSLA, MSFT",
            key="ticker_input",
            disabled=st.session_state.generation_in_progress
        )
        
        industry = st.text_input(
            "Industry (Optional)",
            placeholder="Technology, Automotive",
            key="industry_input",
            disabled=st.session_state.generation_in_progress
        )

    with col3:
        # Language selection
        language_options = [(key, value) for key, value in AVAILABLE_LANGUAGES.items()]
        selected_language_option = st.selectbox(
            "Report Language",
            options=language_options,
            format_func=lambda x: f"{x[1]}",
            index=1,  # English default
            key="language_select",
            disabled=st.session_state.generation_in_progress
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # Step 2: Report Type Selection
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="step-title">Analysis Configuration</h2>', unsafe_allow_html=True)
    st.markdown('<p class="step-description">Choose the analysis scope that matches your specific business needs. Each option covers different areas of company intelligence.</p>', unsafe_allow_html=True)

    # Analysis Mode Selection with detailed cards
    st.markdown("### Choose Your Analysis Mode")

    # Create radio button selection with detailed descriptions
    analysis_options = [
        ("complete", "Complete Analysis", "Comprehensive 360° business analysis covering all operational areas", "Perfect for: Due diligence, M&A research, full company assessment", "15-20 minutes", "All 10 sections"),
        ("strategic", "Strategic Assessment", "Leadership, competitive positioning, and strategic direction analysis", "Perfect for: Partnership evaluation, strategic planning, competitive intelligence", "8-12 minutes", "5 key sections"),
        ("financial", "Financial & Risk Review", "Financial performance, regulatory compliance, and risk assessment", "Perfect for: Investment decisions, credit analysis, risk evaluation", "6-10 minutes", "4 focused sections"),
        ("innovation", "Innovation & Technology", "Digital transformation capabilities and business model innovation", "Perfect for: Technology partnerships, innovation assessment, digital readiness", "6-10 minutes", "5 innovation sections"),
        ("custom", "Custom Selection", "Hand-pick specific sections based on your unique requirements", "Perfect for: Targeted research, specific use cases, custom reporting needs", "Variable timing", "Choose your sections")
    ]

    # Create radio selection
    selected_analysis = st.radio(
        "Select Analysis Type:",
        options=[option[0] for option in analysis_options],
        format_func=lambda x: next(option[1] for option in analysis_options if option[0] == x),
        index=[option[0] for option in analysis_options].index(st.session_state.report_type),
        key="analysis_radio",
        disabled=st.session_state.generation_in_progress
    )

    # Update session state when selection changes
    if selected_analysis != st.session_state.report_type:
        st.session_state.report_type = selected_analysis

    # Show detailed information for selected option
    selected_option = next(option for option in analysis_options if option[0] == selected_analysis)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #f8fff4 0%, #ffffff 100%); border-left: 4px solid var(--primary-lime); padding: 1rem; margin: 0.5rem 0; border-radius: 8px;">
        <h4 style="color: var(--primary-navy); margin-bottom: 0.5rem; font-size: 1.1rem;">{selected_option[1]}</h4>
        <p style="color: var(--secondary-dark-gray); margin-bottom: 0.75rem; font-size: 0.95rem;">{selected_option[2]}</p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.75rem; margin-top: 0.75rem;">
            <div style="color: var(--comp-cyan); font-size: 0.85rem;"><strong>{selected_option[3]}</strong></div>
            <div style="color: var(--secondary-dark-gray); font-size: 0.85rem;"><strong>Duration:</strong> {selected_option[4]}</div>
            <div style="color: var(--secondary-dark-gray); font-size: 0.85rem;"><strong>Coverage:</strong> {selected_option[5]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


    # Custom selection interface (only show if custom is selected)
    if st.session_state.report_type == 'custom':
        st.markdown("---")
        st.markdown("### Custom Section Selection")
        st.markdown("**Choose specific sections to create a tailored analysis report:**")
        
        # Initialize custom sections
        if 'custom_sections' not in st.session_state:
            st.session_state.custom_sections = ['basic']  # Always include basic
        
        # Section descriptions for better understanding
        section_descriptions = {
            'financial': 'Financial Performance - Revenue, profitability, financial health analysis',
            'competitive': 'Competitive Landscape - Market position, competitors, competitive advantages',
            'regulatory': 'Regulatory Environment - Compliance, regulations, legal considerations',
            'vision': 'Vision & Leadership - Company vision, leadership team, corporate culture',
            'management_strategy': 'Management Strategy - Strategic direction, business strategy, growth plans',
            'strategy_research': 'Strategy Research - Deep strategic analysis, market strategy, future outlook',
            'business_structure': 'Business Structure - Organization, operations, business model',
            'digital_transformation': 'Digital Transformation - Technology adoption, digital capabilities, innovation',
            'management_message': 'Management Message - Leadership communications, company messaging',
            'crisis': 'Crisis Management - Risk assessment, crisis preparedness, business continuity'
        }
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("#### Core Business Analysis")
            
            # Always include basic (disabled checkbox)
            st.checkbox("Basic Information", value=True, disabled=True, help="Always included - Company overview, key facts, basic information")
            
            fin_check = st.checkbox("Financial Performance", value="financial" in st.session_state.custom_sections, key="custom_fin", help="Revenue analysis, profitability metrics, financial health", disabled=st.session_state.generation_in_progress)
            comp_check = st.checkbox("Competitive Landscape", value="competitive" in st.session_state.custom_sections, key="custom_comp", help="Market position, competitor analysis, competitive advantages", disabled=st.session_state.generation_in_progress)
            reg_check = st.checkbox("Regulatory Environment", value="regulatory" in st.session_state.custom_sections, key="custom_reg", help="Compliance status, regulatory challenges, legal considerations", disabled=st.session_state.generation_in_progress)
            
            st.markdown("#### Strategic Analysis")
            vis_check = st.checkbox("Vision & Leadership", value="vision" in st.session_state.custom_sections, key="custom_vis", help="Company vision, leadership team analysis, corporate culture", disabled=st.session_state.generation_in_progress)
            mgmt_check = st.checkbox("Management Strategy", value="management_strategy" in st.session_state.custom_sections, key="custom_mgmt", help="Strategic direction, business strategy, growth plans", disabled=st.session_state.generation_in_progress)
            strat_check = st.checkbox("Strategy Research", value="strategy_research" in st.session_state.custom_sections, key="custom_strat", help="Deep strategic analysis, market strategy, future outlook", disabled=st.session_state.generation_in_progress)
        
        with col_b:
            st.markdown("#### Operational Analysis")
            bus_check = st.checkbox("Business Structure", value="business_structure" in st.session_state.custom_sections, key="custom_bus", help="Organizational structure, operations, business model analysis", disabled=st.session_state.generation_in_progress)
            digi_check = st.checkbox("Digital Transformation", value="digital_transformation" in st.session_state.custom_sections, key="custom_digi", help="Technology adoption, digital capabilities, innovation assessment", disabled=st.session_state.generation_in_progress)
            msg_check = st.checkbox("Management Message", value="management_message" in st.session_state.custom_sections, key="custom_msg", help="Leadership communications, company messaging, public statements", disabled=st.session_state.generation_in_progress)
            
            st.markdown("#### Risk Management")
            crisis_check = st.checkbox("Crisis Management", value="crisis" in st.session_state.custom_sections, key="custom_crisis", help="Risk assessment, crisis preparedness, business continuity planning", disabled=st.session_state.generation_in_progress)
        
        # Update custom sections based on checkboxes
        custom_sections = ['basic']  # Always include basic
        if fin_check: custom_sections.append('financial')
        if comp_check: custom_sections.append('competitive')
        if reg_check: custom_sections.append('regulatory')
        if vis_check: custom_sections.append('vision')
        if mgmt_check: custom_sections.append('management_strategy')
        if strat_check: custom_sections.append('strategy_research')
        if bus_check: custom_sections.append('business_structure')
        if digi_check: custom_sections.append('digital_transformation')
        if msg_check: custom_sections.append('management_message')
        if crisis_check: custom_sections.append('crisis')
        
        st.session_state.custom_sections = custom_sections
        selected_sections = custom_sections
        
        # Show custom selection preview with better styling
        section_count = len(selected_sections)
        estimated_time = f"{3 + section_count * 1}-{5 + section_count * 2} minutes"
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #fff8e1 0%, #ffffff 100%); border-left: 4px solid var(--comp-coral); padding: 1.5rem; margin: 1rem 0; border-radius: 8px;">
            <h4 style="color: var(--primary-navy); margin-bottom: 0.5rem;">Your Custom Configuration</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
                <div style="color: var(--secondary-dark-gray); font-size: 0.9rem;"><strong>Sections:</strong> {section_count} selected</div>
                <div style="color: var(--secondary-dark-gray); font-size: 0.9rem;"><strong>Duration:</strong> {estimated_time}</div>
                <div style="color: var(--secondary-dark-gray); font-size: 0.9rem;"><strong>Executive Summary:</strong> Always included</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Set selected_sections based on current report type
    if st.session_state.report_type != 'custom':
        preset = REPORT_PRESETS[st.session_state.report_type]
        selected_sections = preset["sections"]
    else:
        selected_sections = st.session_state.custom_sections

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # Close wizard-container

else:
    # Show locked interface when generation is in progress
    st.markdown("""
    <div style="background: linear-gradient(135deg, var(--secondary-dark-gray) 0%, var(--primary-navy) 100%); 
                border-radius: 12px; padding: 2rem; margin: 1rem 0; text-align: center; color: white;">
        <h2 style="color: white; margin-bottom: 1rem;">🔒 Interface Locked During Generation</h2>
        <p style="color: rgba(255, 255, 255, 0.9); font-size: 1.1rem; margin-bottom: 0;">
            All controls are temporarily disabled while your report is being generated.<br>
            Use the stop button below to cancel generation if needed.
        </p>
    </div>
    """, unsafe_allow_html=True)



# Report Generation Section - Only show if generation is NOT in progress
if not st.session_state.generation_in_progress:
    st.markdown("---")
    st.markdown("## Execute Analysis")

    # Status check and generation interface
    ready_to_generate = bool(target_company and context_company)

    if ready_to_generate:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-left: 4px solid var(--comp-cyan); padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                <span style="font-size: 1.1rem; font-weight: 600; color: var(--primary-navy);">System Ready - All Prerequisites Met</span>
            </div>
            <p style="color: var(--secondary-dark-gray); margin: 0; font-size: 0.95rem;">
                Your configuration is complete. Execute the analysis below to generate your comprehensive business intelligence report.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        missing_items = []
        if not target_company:
            missing_items.append("Target Company Name")
        if not context_company:
            missing_items.append("Your Company Name")
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-left: 4px solid var(--comp-coral); padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                <span style="font-size: 1.1rem; font-weight: 600; color: var(--primary-navy);">Configuration Incomplete</span>
            </div>
            <p style="color: var(--secondary-dark-gray); margin-bottom: 0.75rem; font-size: 0.95rem;">
                Please complete the following required information to proceed with report generation:
            </p>
            <ul style="color: var(--secondary-dark-gray); margin: 0; font-size: 0.9rem; padding-left: 1.5rem;">
                {' '.join([f'<li>{item}</li>' for item in missing_items])}
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Generate button section
    # Show generation options
    can_generate = bool(target_company and context_company)
    
    if can_generate:
        # Get current selection info
        if st.session_state.report_type != 'custom':
            preset = REPORT_PRESETS[st.session_state.report_type]
            button_text = f"Generate {preset['name']}"
            section_count = len(preset['sections'])
            est_time = preset['est_time']
        else:
            button_text = f"Generate Custom Report"
            section_count = len(st.session_state.custom_sections)
            est_time = f"{3 + section_count * 1}-{5 + section_count * 2} minutes"
        
        st.markdown(f'''
        <div class="generate-title">Analysis Execution Ready</div>
        <div class="generate-subtitle">
            {section_count} sections • Estimated time: {est_time}
            <br>Analysis for <strong>{target_company}</strong> by <strong>{context_company}</strong>
        </div>
        ''', unsafe_allow_html=True)
        
        # Prominent generate button
        st.markdown('<div class="generate-button">', unsafe_allow_html=True)
        generate_button = st.button(
            button_text,
            key="generate_report_btn",
            use_container_width=True,
            type="primary",
            disabled=st.session_state.generation_in_progress
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.button(
            "Complete Company Information to Continue",
            disabled=True,
            use_container_width=True
        )
        generate_button = False

else:
    # Show progress UI when generation is in progress  
    st.markdown("---")
    st.markdown("## Report Generation in Progress")
    
    st.markdown('''
    <div class="progress-container">
        <div class="progress-animation"></div>
        <div class="progress-title">Generating Your Report</div>
        <div class="progress-subtitle">Please wait while we analyze and compile your business intelligence report</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Stop button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="stop-button">', unsafe_allow_html=True)
        if st.button("Stop Generation", type="secondary", use_container_width=True, key="stop_generation_main"):
            st.session_state.cancel_generation = True
            st.session_state.generation_in_progress = False
            st.warning("Report generation stopped by user.")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    generate_button = False

# Handle form submission
if not st.session_state.generation_in_progress and 'generate_button' in locals() and generate_button:
    if not target_company:
        st.error("Please enter a target company name.")
    elif not context_company:
        st.error("Please enter your company name as the context company.")
    else:
        # Store generation parameters in session state and trigger generation
        st.session_state.generation_params = {
            'target_company': target_company,
            'context_company': context_company,
            'language_key': selected_language_option[0],
            'language': selected_language_option[1],
            'ticker': ticker if ticker else None,
            'industry': industry if industry else None,
            'report_type': st.session_state.report_type,
            'custom_sections': st.session_state.custom_sections.copy() if st.session_state.report_type == 'custom' else None
        }
        
        # Set generation in progress and reset cancellation flag
        st.session_state.generation_in_progress = True
        st.session_state.cancel_generation = False
        st.rerun()  # Force immediate UI update to block interface

# Display results if generation was completed
if 'generation_results' in st.session_state:
    results = st.session_state.generation_results
    token_stats = results['token_stats']
    pdf_path = results['pdf_path']
    params = results['params']
    pdf_exists = results['pdf_exists']
    
    if token_stats and pdf_exists:
        # Debug logging
        print(f"DEBUG: Taking SUCCESS branch - token_stats: {bool(token_stats)}, pdf_exists: {pdf_exists}")
        # Display success message and stats
        st.success(f"Report for {params['target_company']} generated successfully!")

        # Display report statistics
        st.markdown('<h3 class="section-title">Report Statistics</h3>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                metric_card(
                    "",
                    "Total Tokens",
                    f"{token_stats['summary']['total_tokens']:,}"
                ),
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                metric_card(
                    "",
                    "Generation Time",
                    format_time(token_stats['summary']['total_execution_time'])
                ),
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                metric_card(
                    "",
                    "Successful Sections",
                    token_stats['summary']['successful_prompts']
                ),
                unsafe_allow_html=True
            )
            
        with col4:
            # Check if executive summary was generated
            has_exec_summary = "executive_summary" in token_stats.get("prompts", {})
            exec_summary_value = "Generated" if has_exec_summary else "Not Generated"
            
            st.markdown(
                metric_card(
                    "",
                    "Executive Summary",
                    exec_summary_value
                ),
                unsafe_allow_html=True
            )

        # Display PDF preview
        st.markdown('<h3 class="section-title">Report Preview</h3>', unsafe_allow_html=True)
        st.markdown('<div class="pdf-container">', unsafe_allow_html=True)
        display_pdf(pdf_path)
        st.markdown('</div>', unsafe_allow_html=True)

        # Download button for PDF
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with open(pdf_path, "rb") as file:
                st.download_button(
                    label="Download PDF Report",
                    data=file,
                    file_name=f"{params['target_company']}_{params['language']}_Report.pdf",
                    mime="application/pdf",
                    key="download-pdf",
                    disabled=st.session_state.generation_in_progress
                )

        # Save location
        st.info(f"Report saved to: {pdf_path}")
        
        # Clear results after displaying (optional - user might want to keep them)
        if st.button("Generate New Report", key="new_report", disabled=st.session_state.generation_in_progress):
            st.session_state.pop('generation_results', None)
            st.rerun()
        
    elif token_stats and not pdf_exists and pdf_path is not None:
        # Debug logging
        print(f"DEBUG: Taking WARNING branch - token_stats: {bool(token_stats)}, pdf_exists: {pdf_exists}, pdf_path: {pdf_path}")
        # Case where generation finished but PDF could not be generated or found
        st.warning("Report generation completed, but PDF could not be generated or found. Please check the logs.")
        
        # Still show report statistics
        st.markdown('<h3 class="section-title">Report Statistics</h3>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(
                metric_card(
                    "",
                    "Total Tokens",
                    f"{token_stats['summary']['total_tokens']:,}"
                ),
                unsafe_allow_html=True
            )
            
        with col2:
            st.markdown(
                metric_card(
                    "",
                    "Generation Time",
                    format_time(token_stats['summary']['total_execution_time'])
                ),
                unsafe_allow_html=True
            )
            
        with col3:
            st.markdown(
                metric_card(
                    "",
                    "Successful Sections",
                    token_stats['summary']['successful_prompts']
                ),
                unsafe_allow_html=True
            )
    
        # Clear results button
        if st.button("Try Again", key="try_again", disabled=st.session_state.generation_in_progress):
            st.session_state.pop('generation_results', None)
            st.rerun()
        
    else:
        # Debug logging  
        print(f"DEBUG: Taking ERROR branch - token_stats: {bool(token_stats)}, pdf_exists: {pdf_exists}, pdf_path: {pdf_path}")
        # Case where generate_report_with_progress returned None for stats/path
        st.error("Failed to generate report. Please check the logs for details.")

        # Clear results button
        if st.button("Try Again", key="retry", disabled=st.session_state.generation_in_progress):
            st.session_state.pop('generation_results', None)
            st.rerun()

# Show user info at bottom (only when not generating)
if not st.session_state.generation_in_progress:
    show_user_info_header()

# Add footer
st.markdown('<div class="footer">', unsafe_allow_html=True)
st.markdown('2025 Account Research AI Agent by Supervity', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)