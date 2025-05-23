import os
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Set
import logging
from rich.logging import RichHandler
import yaml
from google import genai
from config import SECTION_ORDER, LLM_MODEL, LLM_TEMPERATURE # These imports remain unchanged
from test_agent_prompt import generate_content, count_tokens # These imports remain unchanged
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
    for section_id, content in sections.items():
        # Find section title from SECTION_ORDER
        section_title = next((title for id, title in SECTION_ORDER if id == section_id), section_id)
        full_report += f"# {section_title}\n\n{content}\n\n"
    
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

1.  **Financial Performance & Trends:** Revenue, profit (net income, EBITDA), margins, growth rates (YoY, CAGR), liquidity, significant investments, and capital allocation. Focus on the *story* these numbers tell about {company_name}.
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
    *   Format the summary as clean Markdown with clear headings and **unique IDs for all headings** to avoid duplicate anchors (e.g., `{{#executive-summary-main}}`, `{{#company-overview}}`).
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

## Executive Summary {{#executive-summary-main}}

### Company Overview {{#company-overview}}
(A concise yet impactful overview of {company_name}, highlighting its core industry, market position, key business areas, and defining characteristics as derived from the report. Focus on what makes this company stand out and its current strategic posture. Aim for 3-5 sentences.)

### Executive Summary Highlights {{#exec-summary-highlights}}
(5 bullet points, each representing an absolute top-level, strategic takeaway or major headline for {company_name}. These are the "executive elevator pitch" points.)
*   **[Concise Strategic Insight 1]:** (Brief elaboration on why this is a top highlight, linking to its impact.)
*   **[Concise Strategic Insight 2]:** (Brief elaboration.)
*   **[Concise Strategic Insight 3]:** (Brief elaboration.)
*   **[Concise Strategic Insight 4]:** (Brief elaboration.)
*   **[Concise Strategic Insight 5]:** (Brief elaboration.)

### Key Findings {{#key-findings}}
(Exactly 15 distinct, specific, and impactful findings. Each point should have a bold title and detail the finding with data and its implication for {company_name}. Integrate critical tables here if relevant.)
1.  **[Concise Title for Finding 1]:** (First critical finding, backed by specific data/figures, and its direct implication or significance for {company_name}'s performance or strategy.)
2.  **[Concise Title for Finding 2]:** (Second critical finding, with specific data and its implication. Avoid repetition across points.)
... (Continue for a total of exactly 15 distinct and high-impact key findings.)

### Strategic Implications & Outlook {{#strategic-implications}}
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
        # Ensure generate_content function uses LLM_MODEL and LLM_TEMPERATURE from config
        # Assuming generate_content from test_agent_prompt handles model and temperature internally or they are global defaults.
        # If generate_content expects these explicitly, you would add:
        # result = generate_content(client, prompt, output_path, model_name=LLM_MODEL, temperature=LLM_TEMPERATURE)
        # But keeping it as is to avoid modifying external calls if not strictly necessary per your constraint.
        result = generate_content(client, prompt, output_path)
        
        if result["status"] == "success":
            logger.info(f"Executive summary generated successfully: {output_path}")
            
            # 7. Add metadata if not already present, or update if it exists.
            # This logic is adapted to be more robust for existing files while still ensuring
            # that new summaries get the full metadata.
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            yaml_match = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
            
            # Prepare new metadata fields
            new_metadata_dict = {
                'title': f"Executive Summary - {company_name}",
                'date': datetime.now().strftime('%Y-%m-%d'),
                'language': language,
                'type': "executive_summary",
                'company': company_name,
                'sections_processed': len(sections),
                'generated_at': datetime.now().isoformat()
            }

            if yaml_match:
                # If frontmatter exists, try to update it gracefully
                try:
                    existing_metadata = yaml.safe_load(yaml_match.group(1))
                    if not isinstance(existing_metadata, dict):
                        existing_metadata = {} # Reset if malformed YAML
                except yaml.YAMLError:
                    existing_metadata = {}
                
                # Merge new metadata into existing, new values override
                final_metadata = {**existing_metadata, **new_metadata_dict}
                updated_metadata_str = yaml.dump(final_metadata, sort_keys=False, default_flow_style=False)
                new_content = f"---\n{updated_metadata_str.strip()}\n---\n" + content[yaml_match.end():].strip()
            else:
                # Add YAML frontmatter if none exists
                metadata_str = yaml.dump(new_metadata_dict, sort_keys=False, default_flow_style=False)
                new_content = f"---\n{metadata_str.strip()}\n---\n" + content.strip()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            logger.info("Ensured metadata is present and updated in executive summary.")
            
            # 8. Verify the output has expected structure and quality
            with open(output_path, 'r', encoding='utf-8') as f:
                content_for_validation = f.read()
                
                # Check for main headings
                if not re.search(r'^##\s+Executive\s+Summary\s*\{\{#executive-summary-main\}\}', content_for_validation, re.MULTILINE):
                    logger.warning("Executive summary may be missing proper main heading structure ('## Executive Summary').")
                
                if not re.search(r'^###\s+Company\s+Overview\s*\{\{#company-overview\}\}', content_for_validation, re.MULTILINE):
                    logger.warning("Executive summary may be missing '### Company Overview' section.")
                
                # Check for "Executive Summary Highlights" heading and 5 bullet points
                highlights_section_match = re.search(r'###\s+Executive\s+Summary\s+Highlights\s*\{\{#exec-summary-highlights\}\}.*?(?=\n###|\Z)', content_for_validation, re.DOTALL)
                if highlights_section_match:
                    highlight_list_items = re.findall(r'^\*\s+\*\*.*?\*\*:.*', highlights_section_match.group(0), re.MULTILINE)
                    if len(highlight_list_items) != 5:
                        logger.warning(f"Executive summary contains {len(highlight_list_items)} highlights, expected 5.")
                else:
                    logger.warning("Executive summary may be missing '### Executive Summary Highlights' section.")

                # Check for "Key Findings" heading and at least 15 numbered list items
                findings_section_match = re.search(r'###\s+Key\s+Findings\s*\{\{#key-findings\}\}.*?(?=\n###|\Z)', content_for_validation, re.DOTALL)
                if findings_section_match:
                    finding_list_items = re.findall(r'^\d+\.\s+\*\*.*?\*\*:.*', findings_section_match.group(0), re.MULTILINE)
                    if len(finding_list_items) < 15: # At least 15, as LLMs might sometimes produce slightly less. Strict == 15 might be too harsh.
                        logger.warning(f"Executive summary contains {len(finding_list_items)} key findings, expected 15.")
                else:
                    logger.warning("Executive summary may be missing '### Key Findings' section.")
                    
                # Check for "Strategic Implications & Outlook" heading
                if not re.search(r'^###\s+Strategic\s+Implications\s+&\s+Outlook\s*\{\{#strategic-implications\}\}', content_for_validation, re.MULTILINE):
                    logger.warning("Executive summary may be missing '### Strategic Implications & Outlook' section.")

                # Check for tables if they're mentioned in the content (basic check)
                if "table" in content_for_validation.lower() and not re.search(r'\|[\s-]+\|', content_for_validation):
                    logger.warning("Executive summary mentions tables but may be missing proper table markdown formatting.")
                    
                # Check if citations were properly removed (more robust regex)
                citation_count = len(re.findall(r'\[SS\d+\]|\[\d+\]|\(\w+,\s*\d{4}\)|\{\[\s*\w*\s*\]\}', content_for_validation)) 
                if citation_count > 0:
                    logger.warning(f"Executive summary still contains {citation_count} citations that should have been removed.")
                
                # Check for unique heading IDs
                heading_ids = re.findall(r'\{\{#([\w-]+)\}\}', content_for_validation)
                if len(heading_ids) != len(set(heading_ids)):
                    logger.warning("Duplicate heading IDs detected in the executive summary.")

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

    # Create dummy markdown files for testing
    markdown_test_dir = output_dir / "markdown"
    markdown_test_dir.mkdir(parents=True, exist_ok=True)
    
    # Ensure a comprehensive set of dummy sections for better testing
    dummy_sections = {
        "introduction": "# Introduction\n\nThis is an introductory section about {company}. It highlights its overall business model and historical context, detailing its founding mission to innovate energy solutions. This report provides a deep dive into its recent performance and future plans. [INTRO_REF]",
        "company_overview": "# Company Overview\n\n{company} was founded in 2000 and is a leading global player in the sustainable energy sector. It operates across 5 continents, employing over 15,000 people. Its core business revolves around advanced solar panel technology and cutting-edge battery storage solutions for residential and commercial clients. The company is known for its strong R&D pipeline. [CO_REF_1]",
        "financial_performance": "# Financial Performance\n\n{company} reported a revenue of $1.2 billion in 2023, showing a modest 5% increase from 2022 due to market saturation. Net profit was $80 million, a 2% decline, indicating some profitability challenges despite revenue growth. The gross margin stood at 30%. Key competitor 'SunPower' achieved 10% growth in the same period. The debt-to-equity ratio improved slightly to 0.65 from 0.70, showing financial prudence. [FIN_REF_A]",
        "strategic_initiatives": "# Strategic Initiatives\n\n{company} is launching a major AI-driven energy management platform ('EcoSmart AI') in Q3 2024, investing $100M over two years. This initiative is expected to enhance customer experience and operational efficiency. They also aim to expand into new residential markets in South America by 2025, targeting a 10% market share in key countries. [STRAT_REF_B]",
        "market_analysis": "# Market Analysis\n\nThe global solar energy market grew by 18% in 2023, while battery storage solutions grew by 25%. {company} holds a steady 12% market share in Europe for solar panels, but only 5% in battery storage. Customer demand for integrated smart home solutions (combining solar and storage) is growing by 20% annually. This presents a significant opportunity. [MKT_REF_C]",
        "risk_factors": "# Risk Factors\n\nNew stringent environmental regulations in Europe could increase compliance costs by 15% starting 2025, potentially impacting profit margins. There's also increasing competition from Chinese manufacturers, leading to significant price pressures (down 8% in H1 2023). Geopolitical tensions in key rare-earth minerals supply regions also pose a risk. [RISK_REF_D]",
        "future_outlook": "# Future Outlook\n\n{company} plans to diversify its product portfolio to include small-scale wind turbines by 2026, aiming for a new revenue stream. They project a more aggressive 15% growth rate from 2025 onwards, driven primarily by the 'EcoSmart AI' platform and new market entries. Long-term vision includes becoming a full-suite renewable energy provider by 2030. [OUT_REF_E]",
        "operational_efficiency": "# Operational Efficiency\n\nImplemented new automated manufacturing processes reducing production time by 10% and material waste by 5% in Q4 2023. This is expected to save $5 million annually from 2024. Employee training programs increased efficiency by an average of 7% across all departments, contributing to a 3% reduction in overall operating costs. [OP_REF_F]"
    }

    for section_id, content in dummy_sections.items():
        with open(markdown_test_dir / f"{section_id}.md", 'w', encoding='utf-8') as f:
            f.write(content.format(company=company))
    
    print(f"Dummy markdown files created in {markdown_test_dir} for testing.")

    result = create_executive_summary(output_dir, company, lang)
    if result:
        print(f"\nSummary generation process completed.")
        print(f"Generated summary at: {result}")
        print("\n--- Content of Generated Summary ---")
        try:
            with open(result, 'r', encoding='utf-8') as f:
                print(f.read())
        except Exception as e:
            print(f"Could not read generated file: {e}")
    else:
        print("\nFailed to generate summary")
        sys.exit(1)