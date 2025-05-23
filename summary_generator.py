import os
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Set
import logging
from rich.logging import RichHandler
import yaml
from google import genai
from config import SECTION_ORDER, LLM_MODEL, LLM_TEMPERATURE
from test_agent_prompt import generate_content, count_tokens
import re
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("rich")

def load_markdown_files(base_dir: Path) -> Dict[str, str]:
    """
    Load all markdown files from a report directory.
    
    Args:
        base_dir: The base directory containing the report files
        
    Returns:
        Dictionary mapping section IDs to markdown content
    """
    markdown_dir = base_dir / "markdown"
    if not markdown_dir.exists():
        raise FileNotFoundError(f"Markdown directory not found: {markdown_dir}")
    
    sections = {}
    
    # Load each markdown file based on SECTION_ORDER
    for section_id, section_title in SECTION_ORDER:
        # Skip executive_summary if it exists (we're creating a new one)
        if section_id == "executive_summary":
            continue
            
        file_path = markdown_dir / f"{section_id}.md"
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():  # Only include non-empty sections
                        sections[section_id] = content
                        logger.info(f"Loaded section: {section_id} ({section_title})")
            except Exception as e:
                logger.error(f"Error reading {file_path}: {str(e)}")
    
    return sections

def create_executive_summary_prompt(sections: Dict[str, str], company_name: str, language: str) -> str:
    """
    Create a prompt for generating the executive summary.
    
    Args:
        sections: Dictionary mapping section IDs to markdown content
        company_name: Name of the company in the report
        language: Target language for the summary
        
    Returns:
        The prompt string
    """
    # Get section titles for context
    section_titles = [
        next((title for id, title in SECTION_ORDER if id == section_id), section_id)
        for section_id in sections.keys()
    ]
    
    section_list = ", ".join(section_titles)
    
    # Concatenate all section content with section titles as headers
    full_report = ""
    for section_id, content_text in sections.items(): # Renamed 'content' to 'content_text' to avoid conflict
        # Find section title from SECTION_ORDER
        section_title = next((title for id, title in SECTION_ORDER if id == section_id), section_id)
        full_report += f"# {section_title}\n\n{content_text}\n\n" # Used 'content_text'
    
    # Create the prompt
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    prompt = f"""
# EXECUTIVE SUMMARY GENERATION TASK - STRATEGIC SYNTHESIS FOR DYNAMIC INSIGHTS

## Role and Objective
You are a highly experienced and discerning Senior Business Analyst and Strategic Advisor. Your primary objective is to analyze a comprehensive business report about **{company_name}** and synthesize its most crucial, impactful, and **differentiating insights** into a concise, actionable, and profoundly informative Executive Summary. This summary must quickly enable busy executives to grasp {company_name}'s unique situation, key drivers, challenges, and future trajectory, without needing to read the entire, extensive report.

## Report Context
The full report contains the following key sections: {section_list}. You must intelligently navigate and prioritize information across *all* these sections to uncover the core narrative, most significant developments, and unique characteristics of {company_name}.

## Dynamic Prioritization Guidelines for Insight Extraction
Unlike generic summaries, your task is to identify what is **truly critical and impactful for *this specific company, {company_name}, at this moment***. The relative importance of different categories of information (financials, strategy, risks, etc.) will vary significantly based on the actual content of the report and {company_name}'s unique context. Do not apply a fixed hierarchy.

**Prioritize based on:**
*   **Significance & Impact:** What has the greatest positive or negative effect on {company_name}'s performance, market position, or future prospects?
*   **Novelty & Change:** What are the newest developments, significant changes, or emerging trends specifically affecting {company_name}?
*   **Quantifiability:** Information supported by precise figures, dates, percentages, and clear metrics.
*   **Strategic Relevance:** Insights that directly inform strategic decisions, highlight opportunities, or expose major challenges.
*   **Uniqueness to {company_name}:** What makes {company_name}'s situation distinct from industry norms or general business trends?

**Key Areas for Assessment (Evaluate their *relative* importance based on report content):**

1.  **Financial Performance & Trends:** Revenue, profit (net income, EBITDA), margins, growth rates (YoY, CAGR), market share, liquidity, significant investments, and capital allocation. Focus on the *story* these numbers tell about {company_name}.
2.  **Core Strategic Initiatives & Vision:** Overarching vision, mission, long-term strategic goals, significant new initiatives, major transformations (e.g., pivot in business model, market entry/exit).
3.  **Competitive Landscape & Market Dynamics:** {company_name}'s distinct competitive advantages, unique value propositions, market positioning, key competitors, industry trends, and disruptive forces.
4.  **Innovation & Digital Transformation:** Major R&D breakthroughs, new product/service launches, adoption of advanced technologies (AI, automation, IoT), and their impact on operations or customer experience.
5.  **Operational Excellence & Business Model:** Major operational improvements, supply chain resilience, efficiency gains, or significant shifts in how {company_name} delivers value.
6.  **Risk Factors & Challenges:** Principal risks (financial, operational, regulatory, competitive, geopolitical), significant compliance issues, or major obstacles and {company_name}'s mitigation strategies.
7.  **Leadership, Governance & Culture:** Key leadership changes, significant appointments, board dynamics, or notable aspects of corporate culture that impact performance.
8.  **Sustainability & ESG (Environmental, Social, Governance):** Key sustainability initiatives, ESG performance, ethical considerations, or community engagement efforts relevant to {company_name}'s reputation or operations.
9.  **Forward-Looking Outlook & Projections:** Future plans, strategic objectives, targets, or investment areas with specific timelines (e.g., 5-year growth targets, new market entry plans, major R&D milestones).

## Requirements for Executive Summary Content
1.  **Executive Summary Highlights (Top 5 Critical Insights):**
    *   Synthesize the **5 absolute most critical, high-level, and strategically impactful insights** from the entire report for {company_name}.
    *   Each highlight should be a concise, powerful bullet point, acting as a strategic headline.
    *   These are the "must-knows" that even the busiest executive would instantly grasp as central to {company_name}'s current narrative.
    *   They should be distinct and not just rephrased findings from the longer list.

2.  **Comprehensive Key Findings (Exactly 15 Points):**
    *   Present **exactly 15 distinct, data-driven, and high-impact insights** from the report.
    *   Each point must:
        *   Be specific and quantifiable (include exact figures, dates, percentages, or clear metrics) where data exists.
        *   Focus on the *implication*, *significance*, or *strategic consequence* for {company_name}, rather than just describing a fact.
        *   Be written in concise, actionable language.
        *   **CRITICAL:** REMOVE ALL CITATIONS (e.g., `[SSX]`, `[1]`, `(Author, Year)`) from the summary, including within tables. The summary must be self-contained.

3.  **Critical Tables (Optional, but prioritized if highly relevant):**
    *   Include **up to 2** *most critical* tables that concisely summarize vital quantitative data (e.g., key financial performance, market share breakdown, critical operational metrics, or strategic targets) for {company_name}.
    *   Ensure tables are properly formatted in Markdown and are directly integrated into the flow of information where most relevant to the findings.
    *   Ensure table content is self-explanatory within the summary context and **free of citations**.

4.  **Language and Length:**
    *   Write the entire summary in **{language}** language.
    *   Limit the summary to approximately **1000-1500 words** to ensure conciseness while maintaining comprehensive depth.

5.  **Formatting and Structure:**
    *   Format the summary as clean Markdown with clear headings and **unique IDs for all headings** to avoid duplicate anchors (e.g., `{{{{#executive-summary-main}}}}`, `{{{{#company-overview}}}}`).
    *   Ensure a logical flow from a high-level overview to strategic highlights, then detailed findings, and finally, comprehensive implications.

## Output Structure
Your Executive Summary should strictly adhere to this Markdown structure:

---
title: "Executive Summary - {company_name}"
date: "{current_date}"
language: "{language}"
type: "executive_summary"
company: "{company_name}"
---

### Company Overview {{{{company-overview}}}}
(A concise yet impactful overview of {company_name}, highlighting its core industry, market position, key business areas, and defining characteristics as derived from the report. Focus on what makes this company stand out and its current strategic posture. Aim for 3-5 sentences.)

### Executive Summary Highlights {{{{exec-summary-highlights}}}}
(5 bullet points, each representing an absolute top-level, strategic takeaway or major headline for {company_name}. These are the "executive elevator pitch" points.)
*   **[Concise Strategic Insight 1]:** (Brief elaboration on why this is a top highlight, linking to its impact.)
*   **[Concise Strategic Insight 2]:** (Brief elaboration.)
*   **[Concise Strategic Insight 3]:** (Brief elaboration.)
*   **[Concise Strategic Insight 4]:** (Brief elaboration.)
*   **[Concise Strategic Insight 5]:** (Brief elaboration.)

### Key Findings {{{{key-findings}}}}
(Exactly 15 distinct, specific, and impactful findings. Each point should have a bold title and detail the finding with data and its implication for {company_name}. Integrate critical tables here if relevant.)
1.  **[Concise Title for Finding 1]:** (First critical finding, backed by specific data/figures, and its direct implication or significance for {company_name}'s performance or strategy.)
2.  **[Concise Title for Finding 2]:** (Second critical finding, with specific data and its implication. Avoid repetition across points.)
... (Continue for a total of exactly 15 distinct and high-impact key findings.)

### Strategic Implications & Outlook {{{{strategic-implications}}}}
(A comprehensive analytical synthesis of the overarching strategic implications derived from *all* the preceding findings and highlights. Discuss the key opportunities, critical challenges, and forward-looking strategic directives for {company_name}. This section should provide a high-level strategic roadmap based on the report's insights, explaining how the findings inform future decisions and the company's trajectory. This should be a robust paragraph or two, demonstrating advanced analytical depth.)

## Common Pitfalls to Avoid (Self-Correction Guidelines)
1.  **DO NOT** retain *any* citations (e.g., `[SSX]`, `[1]`, `(Source, Year)`) anywhere in the summary, including tables. They must be completely removed.
2.  **DO NOT** simply copy and paste large blocks of text from the original report. Your task is sophisticated synthesis, rephrasing, and analysis.
3.  **DO NOT** produce a generic summary. Every point must be profoundly specific, data-driven, and uniquely tailored to the specific dynamics, strengths, and weaknesses of {company_name}.
4.  **DO NOT** introduce new facts or data not explicitly found in the provided report content.
5.  **DO NOT** apply a fixed hierarchy of importance to different report sections; dynamically assess what is most critical for {company_name} based on the report's actual content.
6.  **DO NOT** use qualifying phrases like "according to the report," "the document states," or "it is mentioned that." Present information directly as fact.
7.  **DO NOT** use placeholder text or hypothetical examples.
8.  **DO NOT** generate statistical approximations when precise figures are available in the report.
9.  **DO NOT** use filler phrases like "It is important to note that" or "It is worth mentioning." Be direct and concise.
10. **DO NOT** repeat the same information or implication across multiple key points (both in Highlights and Key Findings). Each point must offer a distinct, valuable insight.
11. **DO NOT** use duplicate heading IDs. Each ID must be unique within the summary.
12. **DO NOT** neglect to explain the *significance* or *implication* of data points. Data without context or impact is not valuable.
13. **DO NOT** make assumptions about {company_name} that are not supported by the report's content.

## Full Report to Analyze
{full_report}
"""
    
    return prompt

def generate_executive_summary(base_dir: Path, company_name: str, language: str) -> Optional[Path]:
    """
    Generate an executive summary from all markdown files in a report.
    
    Args:
        base_dir: The base directory containing the report files
        company_name: Name of the company in the report
        language: Target language for the summary
        
    Returns:
        Path to the generated executive summary file, or None if generation failed
    """
    try:
        # 1. Load all markdown files
        logger.info(f"Loading markdown files from {base_dir}")
        sections = load_markdown_files(base_dir)
        
        if not sections:
            logger.error("No valid markdown sections found to generate summary")
            return None
        
        # 2. Create the prompt
        logger.info("Creating executive summary prompt")
        prompt = create_executive_summary_prompt(sections, company_name, language)
        
        # 3. Get API key from environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # 4. Initialize the client
        client = genai.Client(api_key=api_key)
        
        # 5. Define the output file path
        output_path = base_dir / "markdown" / "executive_summary.md"
        
        # 6. Generate the content
        logger.info("Generating executive summary")
        # Note: The original call to generate_content did not include model_name or temperature.
        # It's assumed test_agent_prompt.generate_content handles this or uses defaults.
        # Or these are set globally if needed by that function.
        # For consistency with the provided script, I am not adding them here.
        result = generate_content(client, prompt, output_path) 
        
        if result["status"] == "success":
            logger.info(f"Executive summary generated successfully: {output_path}")
            
            # 7. Add metadata if not already present
            # This logic will now primarily act as a fallback if the LLM somehow fails to produce
            # the frontmatter defined in the prompt.
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read() # Renamed from 'content_text' to 'content' to match original scope
                
            # Check if the summary has YAML frontmatter
            if not content.startswith('---'):
                # Add YAML frontmatter
                logger.warning("LLM did not include frontmatter as prompted. Adding default frontmatter.")
                metadata = f"""---
title: "Executive Summary - {company_name}"
date: "{datetime.now().strftime('%Y-%m-%d')}"
language: "{language}"
type: "executive_summary"
company: "{company_name}"
sections: {len(sections)}
generated_at: "{datetime.now().isoformat()}"
---

"""
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(metadata + content)
                logger.info("Added default metadata to executive summary")
            
            # 8. Verify the output has expected structure
            # This validation logic is from the original script and remains unchanged.
            # It might not fully align with the new, more detailed prompt structure, but per your request,
            # it's kept as is.
            with open(output_path, 'r', encoding='utf-8') as f:
                content_for_validation = f.read() # Used a new variable to avoid confusion with 'content' above
                
                # Check for key headings
                if not re.search(r'^##\s+Executive\s+Summary', content_for_validation, re.MULTILINE):
                    logger.warning("Executive summary may be missing proper heading structure")
                
                # Check for tables if they're mentioned in the content
                if "table" in content_for_validation.lower() and not re.search(r'\|[\s-]+\|', content_for_validation):
                    logger.warning("Executive summary mentions tables but may be missing proper table formatting")
                    
                # Check if citations were properly removed
                # Updated regex slightly for common citation patterns to be more robust.
                citation_count = len(re.findall(r'\[SS\d+\]|\[\d+\]|\(\s*\w+[^)]*,\s*\d{4}\s*\)|{{\s*\[\s*\w*\s*\]\s*}}', content_for_validation))
                if citation_count > 0:
                    logger.warning(f"Executive summary still contains {citation_count} citations that should have been removed.")
            
            return output_path
        else:
            logger.error(f"Failed to generate executive summary: {result.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        logger.exception(f"Error generating executive summary: {str(e)}")
        return None

# Function to be called from the main application
def create_executive_summary(base_dir: Path, company_name: str, language: str) -> Optional[Path]:
    """
    Public function to generate an executive summary for a report.
    
    Args:
        base_dir: The base directory containing the report files
        company_name: Name of the company in the report
        language: Target language for the summary
        
    Returns:
        Path to the generated executive summary file, or None if generation failed
    """
    return generate_executive_summary(base_dir, company_name, language)

if __name__ == "__main__":
    # Test functionality if run directly
    import sys
    if len(sys.argv) < 4:
        print("Usage: python summary_generator.py <output_dir> <company_name> <language>")
        sys.exit(1)
    
    output_dir = Path(sys.argv[1])
    company = sys.argv[2]
    lang = sys.argv[3]
    
    # You would need to ensure `config.py` and `test_agent_prompt.py` are available
    # and set up correctly for this __main__ block to work, including GEMINI_API_KEY.
    # For example, create dummy files if they don't exist for basic testing:

    # Example dummy config.py (create this file if it doesn't exist for testing)
    # """
    # SECTION_ORDER = [
    #     ("introduction", "Introduction"),
    #     ("company_overview", "Company Overview"),
    #     ("financial_performance", "Financial Performance")
    # ]
    # LLM_MODEL = "gemini-pro"  # Or your preferred model
    # LLM_TEMPERATURE = 0.3
    # """

    # Example dummy test_agent_prompt.py (create this file for testing)
    # """
    # import logging
    # from datetime import datetime
    # logger = logging.getLogger("rich")
    #
    # def count_tokens(text):
    #     return len(text.split()) # A very basic approximation
    #
    # def generate_content(client, prompt, output_path):
    #     logger.info(f"MOCK: Simulating LLM call for {output_path.name}")
    #     # This mock function should generate content that matches the new prompt's structure
    #     # for testing the overall flow.
    #     # For a real test, you'd remove this mock and use the actual API call.
    #     mock_company_name = "TestCorp" # Extract from prompt or pass if possible
    #     mock_language = "English" # Extract from prompt or pass
    #     mock_current_date = datetime.now().strftime('%Y-%m-%d')
    #
    #     mock_summary_content = f'''---
# title: "Executive Summary - {mock_company_name}"
# date: "{mock_current_date}"
# language: "{mock_language}"
# type: "executive_summary"
# company: "{mock_company_name}"
# ---
    #
    # ## Executive Summary {{{{executive-summary-main}}}}
    #
    # ### Company Overview {{{{company-overview}}}}
    # {mock_company_name} is a fictional company used for testing purposes. It operates in the innovative sector of placeholder industries, showing moderate growth.
    #
    # ### Executive Summary Highlights {{{{exec-summary-highlights}}}}
    # *   **[Strategic Shift to Digital]:** {mock_company_name} announced a major pivot towards digital-first operations, investing $50M in new platforms.
    # *   **[Market Entry Success]:** Successfully launched in 2 new regional markets, exceeding initial user adoption targets by 15%.
    # *   **[Key Product Innovation]:** Unveiled 'Product X,' a next-generation solution, already securing 3 major enterprise contracts.
    # *   **[Operational Efficiency Gains]:** Implemented automation leading to a 10% reduction in operational costs in Q4.
    # *   **[Sustainability Commitment]:** Pledged to achieve carbon neutrality by 2030, with a 5% emission reduction in the past year.
    #
    # ### Key Findings {{{{key-findings}}}}
    # 1.  **[Financial Snapshot]:** Revenue for FY2023 was $100M, a 5% increase YoY. Net profit margin remained stable at 12%.
    # 2.  **[Digital Transformation Progress]:** 60% of customer interactions are now through digital channels, up from 30% last year.
    # 3.  **[New Market Performance]:** The Asian market contributed $5M in revenue in its first six months of operation.
    # 4.  **[R&D Investment]:** R&D spending increased by 20% to $10M, focusing on AI and machine learning applications.
    # 5.  **[Customer Growth]:** Added 10,000 new customers in 2023, a 8% growth in the customer base.
    # 6.  **[Employee Engagement]:** Employee satisfaction scores improved by 7% following new HR initiatives.
    # 7.  **[Supply Chain Optimization]:** Reduced average lead times by 3 days through new supplier partnerships.
    # 8.  **[Brand Awareness]:** Brand recognition increased by 10% in target demographics according to recent surveys.
    # 9.  **[Competitive Positioning]:** Maintained a 15% market share in its core domestic market despite new entrants.
    # 10. **[Regulatory Compliance]:** Successfully adapted to new data privacy regulations with no operational disruptions.
    # 11. **[Partnership Ecosystem]:** Formed 5 new strategic alliances to enhance product distribution channels.
    # 12. **[Infrastructure Upgrade]:** Completed a $20M upgrade to IT infrastructure, improving system reliability by 99.9%.
    # 13. **[Talent Acquisition]:** Hired 50 new engineers, focusing on specialized AI and cybersecurity skills.
    # 14. **[Product Diversification]:** Launched 2 new ancillary services, contributing 3% to total revenue in Q4.
    # 15. **[Future Outlook]:** Projects 8-10% revenue growth for 2024, driven by new product launches and market expansion.
    #
    # ### Strategic Implications & Outlook {{{{strategic-implications}}}}
    # {mock_company_name}'s strategic shift towards digitalization and expansion into new markets, coupled with product innovation, positions it for sustained growth. While financial growth is moderate, investments in R&D and talent are laying the groundwork for future acceleration. The company must continue to navigate competitive pressures and ensure operational efficiencies to capitalize on emerging opportunities.
    # '''
    #     try:
    #         with open(output_path, 'w', encoding='utf-8') as f:
    #             f.write(mock_summary_content)
    #         return {"status": "success", "tokens_used": count_tokens(mock_summary_content)}
    #     except Exception as e:
    #         logger.error(f"Mock generation failed: {e}")
    #         return {"status": "error", "error": str(e)}
    # """

    # Ensure output_dir/markdown exists for the dummy files
    # (markdown_dir_path = output_dir / "markdown").mkdir(parents=True, exist_ok=True)
    # # Create some dummy markdown files in output_dir/markdown for testing
    # dummy_md_content = {
    #     "introduction.md": f"# Introduction\nThis is an intro to {company}.",
    #     "financial_performance.md": f"# Financials\n{company} made some money. Revenue was $1M. [SS1]",
    # }
    # for fname, fcontent in dummy_md_content.items():
    #     with open(output_dir / "markdown" / fname, "w") as f:
    #         f.write(fcontent)

    result = create_executive_summary(output_dir, company, lang)
    if result:
        print(f"Summary generated at: {result}")
    else:
        print("Failed to generate summary")
        sys.exit(1)