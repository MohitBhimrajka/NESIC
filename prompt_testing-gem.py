# prompt_testing.py

import textwrap

# --- Standard Instruction Blocks ---

# NEW: Strict Company Name Focus Instruction
COMPANY_NAME_FOCUS_INSTRUCTION = textwrap.dedent("""\
    *   **Strict Company Focus Requirement:**
        *   **Target Entity Identification:** If the provided company name ( {company_name} ) could refer to multiple entities, identify the most prominent and contextually relevant one based on typical business research needs.
        *   **Exclusive Research:** Once the target entity is identified, **ALL research, analysis, data extraction, and source usage MUST pertain EXCLUSIVELY to that single company.**
        *   **Filter Out Others:** Actively ignore and discard any information, search results, or grounding sources related to other companies, even if they have similar names or are related (unless specifically requested, e.g., direct parent/subsidiary listing).
        *   **Consistency:** Maintain this exclusive focus throughout the *entire* response generation process, including the General Discussion and the final Sources list. Do not mix data from different entities.
    """)

# FINAL SOURCE LIST INSTRUCTIONS: Revised for simple inline citation linkage.
FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE = textwrap.dedent("""\
    **CRITICAL SOURCE LIST MANDATE:** The following rules for the 'Sources' section are the MOST critical for output validity and grounding verification. Failure to follow these rules precisely, especially regarding URL type, sequential numbering, format, and annotation linkage, constitutes a failed generation. NO EXCEPTIONS.

    **Final Source List Requirements:**

    Conclude the *entire* research output, following the 'General Discussion' paragraph, with a clearly marked section titled "**Sources**". This section is critical for verifying the information grounding process AND for document generation.

    **1. Content - MANDATORY URL Type & Source Integrity:**
    *   **Exclusive Source Type:** This list **MUST** contain *only* the specific grounding redirect URLs provided directly by the **Vertex AI Search system** *for this specific query*. These URLs represent the direct grounding evidence used.
    *   **URL Pattern:** These URLs typically follow the pattern: `https://vertexaisearch.cloud.google.com/grounding-api-redirect/...`. **Only URLs matching this exact pattern are permitted.**
    *   **Strict Filtering:** Absolutely **DO NOT** include any other type of URL (direct website links, news, PDFs, etc.). Do not include sources pertaining to companies other than the single, correctly identified target entity.
    *   **CRITICAL - No Hallucination:** **Under NO circumstances should you invent, fabricate, infer, or reuse `vertexaisearch.cloud.google.com/...` URLs** from previous queries or general knowledge if they were not explicitly provided as grounding results *for this query and the correct target company*. If a fact is identified but lacks a corresponding provided grounding URL for the target company, it must be omitted.
    *   **Purpose:** This list verifies the specific grounding data provided by Vertex AI Search for this request—not external knowledge or other URLs.

    **2. Formatting and Annotation (CRITICAL FOR PARSING):**
    *   **Source Line Format:** Present each source on a completely new line. Each line **MUST** start with a Markdown list indicator (`* ` or `- `) followed by the hyperlink in Markdown format and then its annotation.
    *   **REQUIRED Format:**
        ```markdown
        * [Supervity Source X](Full_Vertex_AI_Grounding_URL) - Annotation explaining exactly what information is supported (e.g., supports CEO details and FY2023 revenue [SSX]).
        ```
    *   **Sequential Labeling:** The visible hyperlink text **MUST** be labeled sequentially "Supervity Source 1", "Supervity Source 2", etc. Do not skip numbers.
    *   **Annotation Requirement:** The annotation MUST be:
        * Included immediately after the hyperlink on the same line, separated by " - ".
        * Brief and specific, explaining exactly which piece(s) of information in the main body (and referenced with inline citation [SSX]) that grounding URL supports.
        * Written in the target output language: **{language}**.

    **3. Quantity and Linkage:**
    *   **Target Quantity:** Aim for a minimum of 5 and a maximum of 18 distinct, verifiable Vertex AI grounding URLs *for the target company* that directly support content in the report.
    *   **Accuracy Over Quantity:** Accuracy and adherence to the grounding rules are absolute. If fewer than 5 verifiable URLs are available from the provided results for the target company, list only those.
    *   **Fact Linkage:** Every grounding URL listed MUST directly correspond to facts/figures/statements present in the report body. The annotation must clearly link to the inline citation(s) [SSX] used in the text.

    **4. Content Selection Based on Verifiable Grounding:**
    *   **Prerequisite for Inclusion:** Only include facts, figures, details, or quotes in the main report if they can be supported by a verifiable Vertex AI grounding URL *from this query and for the correct company*.
    *   **Omission of Ungrounded Facts/Sections:** If specific information cannot be supported by a verifiable grounding URL, omit that detail. If a whole section cannot be grounded, omit the entire section.

    **5. Final Check:**
    *   Before concluding the response, review the entire output. Verify:
        * Exclusive use of valid, provided Vertex AI grounding URLs *for the target company*.
        * Each source is on a new line and follows the correct format.
        * Every fact in the report body is supported by an inline citation [SSX] that corresponds to a source in this list.
        * **URL Pattern Verification:** Double-check that EVERY URL listed STRICTLY matches the `https://vertexaisearch.cloud.google.com/grounding-api-redirect/...` pattern. No other URLs are permitted.
    *   The "**Sources**" section must appear only once, at the end of the entire response.
    """)

# HANDLING MISSING INFORMATION: Revised to enforce strict omission if grounding is unavailable.
HANDLING_MISSING_INFO_INSTRUCTION = textwrap.dedent("""\
    *   **Handling Missing or Ungrounded Information:**
        *   **Exhaustive Research First:** Conduct exhaustive research using primarily official company sources (see `RESEARCH_DEPTH_INSTRUCTION`).
        *   **Grounding Requirement for Inclusion:** Information is included only if:
            1. The information is located in a reliable source document.
            2. A corresponding, verifiable Vertex AI grounding URL (matching the pattern `https://vertexaisearch.cloud.google.com/grounding-api-redirect/...`) is provided in the search results for this query *for the target company*.
        *   **Strict Omission Policy:** If information cannot meet both conditions, omit that specific fact or section entirely. Do not use placeholders such as 'N/A' or 'Not Found'. Also, omit information or sources found pertaining to incorrect companies.
        *   **No Inference/Fabrication:** Do not infer, guess, or estimate ungrounded information. Do not fabricate grounding URLs.
        *   **Cross-Language Search:** If necessary, check other language results; if found, translate only the necessary information and list the corresponding grounding URL.
    """)

# RESEARCH DEPTH & CALCULATION: Revised to include forbidden sources and conflict handling.
RESEARCH_DEPTH_INSTRUCTION = textwrap.dedent("""\
    *   **Research Depth & Source Prioritization:**
        *   **Exhaustive Search:** Conduct thorough research for all requested information points. Dig beyond surface-level summaries.
        *   **Strict Entity Focus:** Discard any information or sources found that pertain to similarly named companies but are not the specific target entity identified ({company_name}).
        *   **Primary Source Focus:** Use official company sources primarily, including:
            * Latest Annual / Integrated Reports (and previous years for trends)
            * Official Financial Statements (Income Statement, Balance Sheet, Cash Flow) & Crucially: Footnotes
            * Supplementary Financial Data, Investor Databooks, Official Filings (e.g., EDINET, SEC filings, local equivalents)
            * Investor Relations Presentations & Materials (including Mid-Term Plans, Strategy Day presentations)
            * Earnings Call Transcripts & Presentations (focus on Q&A sections)
            * Official Corporate Website sections (e.g., "About Us", "Investor Relations", "Strategy", "Governance", "Sustainability/ESG")
            * Official Press Releases detailing strategy, financials, organizational structure, or significant events.
        *   **Forbidden Sources:** Do NOT use:
            * Wikipedia
            * Generic blogs, forums, or social media posts
            * Press release aggregation sites (unless linking directly to an official release)
            * Outdated market reports (unless historical context is explicitly requested)
            * Competitor websites/reports (except in competitive analysis with caution)
            * Generic news articles unless they report specific, verifiable events from highly reputable sources (e.g., Nikkei, Bloomberg, Reuters, FT, WSJ).
        *   **Emphasize Primary Sources:** Primary documents provide accuracy, official positioning, and verifiability *for the target company*.
        *   **Management Commentary:** Actively incorporate direct management commentary and analysis from these sources.
        *   **Recency:** Focus on the most recent 1-2 years for qualitative analysis; use the last 3 full fiscal years for financial trends. Clearly state the reporting period.
        *   **Secondary Sources:** Use reputable secondary sources sparingly for context or verification, always with clear attribution.
        *   **Handling Conflicts:** If conflicting information is found between official sources, prioritize the most recent, definitive source. Note discrepancies with dual citations if significant (e.g., [SSX, SSY]).
        *   **Calculation Guidelines:** If metrics are not explicitly reported but must be calculated:
            * Calculate only if all necessary base data (e.g., Net Income, Revenue, Equity, Assets, Debt) is available and verifiable *from the target company's grounded sources*.
            * Clearly state the formula used, and if averages are used, mention that.
        *   **Confirmation of Unavailability:** Only conclude information is unavailable after a diligent search across multiple primary sources *for the correct company*.
    """)

# ANALYSIS & SYNTHESIS INSTRUCTION: Revised to encourage explicit "why" analysis and linking.
ANALYSIS_SYNTHESIS_INSTRUCTION = textwrap.dedent("""\
    *   **Analysis and Synthesis:**
        *   Beyond listing factual information, provide concise analysis where requested (e.g., explain trends, discuss implications, identify drivers, assess effectiveness).
        *   **Explicitly address "why":** For every data point or trend, explain why it is occurring or what the key drivers are, based *only* on grounded information [SSX].
        *   **Comparative Analysis:** Compare data points (e.g., YoY changes, company performance against competitors) where appropriate, citing sources [SSX].
        *   **Linking Information:** In the General Discussion, explicitly tie together findings from different sections to present a coherent overall analysis (e.g., link financial performance [SSX] with strategic initiatives [SSY]). Ensure all synthesis refers only to the target company.
    """)

# INLINE CITATION INSTRUCTION: Mandate simple inline citations for all factual claims.
INLINE_CITATION_INSTRUCTION = textwrap.dedent("""\
    *   **Inline Citation Requirement (CRITICAL - Simple Format):**
        *   Every factual claim, data point, specific summary, or direct quote MUST include an inline citation immediately following the information it supports (ideally before punctuation).
        *   **REQUIRED FORMAT:** The citation **MUST** be plain text in brackets: `[SSX]`
            *   `SSX`: Where X corresponds *exactly* to the sequential number of the source in the final "Sources" list (e.g., `[SS1]`, `[SS2]`).
        *   **Purpose:** This ensures every fact can be traced back to the specific grounding source listed in the final "Sources" section.
        *   **Placement:** Place the text `[SSX]` immediately after the supported statement.
    """)

# SPECIFICITY INSTRUCTION: Instruct to include specific dates, definitions, and quantification.
SPECIFICITY_INSTRUCTION = textwrap.dedent("""\
    *   **Specificity and Granularity:**
        *   For all time-sensitive data points (e.g., financials, employee counts, management changes), include specific dates or reporting periods (e.g., "as of 2024-03-31", "for FY2023") [SSX].
        *   Define any industry-specific or company-specific terms or acronyms on their first use [SSX].
        *   Quantify qualitative descriptions with specific numbers or percentages where available (e.g., "growth of 12% [SSX]").
        *   List concrete examples rather than vague categories when describing initiatives, strategies, or risks [SSX]. Ensure examples relate to the target company.
    """)

# AUDIENCE CONTEXT REMINDER
AUDIENCE_CONTEXT_REMINDER = textwrap.dedent("""\
    *   **Audience Relevance:** Keep the target audience (Japanese corporate strategy professionals) in mind. Frame analysis and the 'General Discussion' to highlight strategic implications, competitive positioning, market opportunities/risks, and operational insights relevant for potential partnership, investment, or competitive assessment related to the *specific target company*.
    """)

# STANDARD OUTPUT LANGUAGE INSTRUCTION
def get_language_instruction(language: str) -> str:
    return f"Output Language: The final research output must be presented entirely in **{language}**."

# BASE FORMATTING INSTRUCTIONS: Revised to include logical flow and conciseness.
# CRITICAL FORMATTING PREAMBLE: Added for emphasis
CRITICAL_FORMATTING_PREAMBLE = textwrap.dedent("""\
    **CRITICAL FORMATTING MANDATE:** Adherence to the following Markdown formatting rules (especially for tables, lists, and the final Sources list) is NON-NEGOTIABLE. Errors in formatting will render the output unusable. Pay meticulous attention to every detail specified.
    """)

BASE_FORMATTING_INSTRUCTIONS = CRITICAL_FORMATTING_PREAMBLE + textwrap.dedent("""\
    Output Format & Quality Requirements:

    *   **Direct Start & No Conversational Text:** Begin the response directly with the first requested section heading (e.g., `## 1. Core Corporate Information`). No introductory or concluding remarks are allowed.

    *   **Strict Markdown Formatting Requirements:**
        *   Use valid and consistent Markdown throughout the entire document.
        *   **Section Formatting:** Sections MUST be numbered exactly as specified in the prompt (e.g., `## 1. Core Corporate Information`).
        *   **Subsection Formatting:** Use `###` for subsections and maintain hierarchical structure (e.g., `### CEO Name, Title`).
        *   **List Formatting:** Use asterisks (`*`) or hyphens (`-`) for bullets with consistent indentation (4 spaces for sub-bullets).
        *   **Tables:** Format all tables with proper Markdown table syntax:
            ```markdown
            | Header 1 | Header 2 | Header 3 |
            |----------|----------|----------|
            | Data 1   | Data 2   | Data 3   |
            | Data 4   | Data 5   | Data 6   |
            ```
        *   **CRITICAL Separator Row:** Ensure the Markdown table separator row (`|---|---|...`) is present and correctly formatted immediately below the header row. Incorrect separators break table rendering.
        *   **Code Blocks:** Use triple backticks (```) for code blocks when presenting technical details.
        *   **Quotes:** Use Markdown quote syntax (>) for direct quotations from executives when appropriate.

    *   **Optimal Structure & Readability:**
        *   Present numerical data in tables with proper alignment and headers.
        *   Use bullet points for lists of items or characteristics.
        *   Use paragraphs for narrative descriptions and analysis.
        *   Maintain consistent formatting across similar elements throughout the document.
        *   **Content Organization:** Ensure a logical sequence within each section (e.g., chronological order for trends, priority order for lists).
        *   **Conciseness:** Provide detailed yet concise language—be specific without unnecessary verbosity.

    *   **Data Formatting Consistency:**
        *   Use appropriate thousands separators for numbers per the target language: **{language}**.
        *   **Currency Specification:** Always specify the currency (e.g., ¥, $, €, JPY, USD, EUR) for all monetary values along with the reporting period.
        *   Format dates in a consistent style (e.g., YYYY-MM-DD).
        *   Use consistent percentage formatting (e.g., 12.5%).

    *   **Table Consistency Requirements:**
        *   All tables must have header rows with clear column titles.
        *   Include a separator row (`|---|---|`) between headers and data.
        *   Align column content appropriately (left for text, right for numbers).
        *   Maintain the same number of columns throughout each table.
        *   Include units in column headers where applicable (e.g., "Revenue (JPY millions)").

    *   **Section Completion Verification:**
        *   Every section requested in the prompt MUST be included in the output.
        *   Sections must appear in the exact order specified in the prompt.
        *   Each section must be properly labeled with the exact heading from the prompt.
        *   Incomplete sections should be explicitly marked as having partial data rather than omitted entirely (unless omitted due to lack of grounded information as per HANDLING_MISSING_INFO_INSTRUCTION).

    *   **Tone and Detail Level:**
        *   Maintain a professional, objective, and analytical tone suited for a Japanese corporate strategy audience focused on the target company.
        *   Provide granular detail (e.g., figures, dates, metrics [SSX]) while avoiding promotional language.

    *   **Completeness and Verification:**
        *   Address all requested points in each section *for the target company*.
        *   Verify that every section, the General Discussion, and the Sources list are present and adhere to the instructions.
        *   Perform a final internal review before output.

    *   **Sources List:** The Sources list must be present and adhere to the instructions.
        *   The Sources section should have a header with the text "Sources"
        *   The Sources section should be formatted as a Markdown unordered list.
        *   The Sources section should have a link to the source with the text "Supervity Source X" where X is the source number.

    *   **Inline Citation & Specificity:** Incorporate the inline citation `[SSX]` for every factual claim (see Inline Citation Requirement) and include specific dates/definitions (see Specificity and Granularity).
    """)

# FINAL REVIEW INSTRUCTION
FINAL_REVIEW_INSTRUCTION = textwrap.dedent("""\
    *   **MANDATORY Internal Final Review Checklist:** Before generating the final 'Sources' list, rigorously verify the *entire* generated response against this checklist. Confirm 'Yes' for every point before proceeding:

        *   **1. Target Company Focus:**
            *   [ ] Does ALL content (facts, analysis, discussion, sources) pertain *exclusively* to the single, correctly identified target company ({company_name})? (No data from similarly named entities?)

        *   **2. Citation & Grounding Integrity:**
            *   [ ] Is *every* factual claim, number, or specific statement followed immediately by an inline citation in the exact format `[SSX]`?
            *   [ ] Does each `[SSX]` logically correspond to the information presented and link to an intended source in the final list?
            *   [ ] Does every potential source listed later correspond ONLY to a Vertex AI grounding URL *provided for this query* AND *for the correct target company*? (No invented/reused/wrong-company URLs?)
            *   [ ] Is the information supported by the intended source consistent with the eventual source list annotation? (Mental Check)

        *   **3. Markdown Formatting Validity:**
            *   [ ] Are all Section Headings (`## 1. Title`) and Subsections (`###`) correctly formatted?
            *   [ ] Do all tables have correct headers, separators (`|---|---|`), and consistent columns? Is content aligned appropriately? **CRITICAL Separator Row Present?**
            *   [ ] Are all bulleted/numbered lists correctly formatted with consistent indentation?
            *   [ ] Are there any broken Markdown elements or unintended raw text?

        *   **4. Content & Structure Completeness:**
            *   [ ] Is *every* numbered section requested in the original prompt present in the correct order?
            *   [ ] Does each section contain *all* requested subsections and data points (unless correctly omitted due to lack of grounding or being off-topic for the target company)?
            *   [ ] Is the "General Discussion" paragraph present and synthesizing *only* information from previous sections *about the target company*?
            *   [ ] Does the response start *directly* with the first section heading (No intro)?
            *   [ ] Is the output language consistently `{language}`?

        *   **5. Data Precision:**
            *   [ ] Does *every* monetary value include currency and the reporting period/date [SSX]?
            *   [ ] Are dates formatted consistently?

        *   **Only after confirming 'Yes' for ALL points above, proceed to meticulously generate the 'Sources' list according to its specific, critical instructions.**
    """)

# Template for ensuring complete and properly formatted output
COMPLETION_INSTRUCTION_TEMPLATE = textwrap.dedent("""\
    **Output Completion Requirements:**

    Before concluding your response, verify that:
    1. Every numbered section requested in the prompt is complete with all required subsections for the target company (or correctly noted as ungrounded).
    2. All content follows proper markdown formatting throughout.
    3. Each section contains all necessary details and is not truncated.
    4. The response maintains consistent formatting for lists, tables, and code blocks.
    5. All inline citations `[SSX]` are properly placed and formatted.
""")

# --- Prompt Generating Functions ---

def get_basic_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for a comprehensive basic company profile with all enhancements."""
    language_instruction = get_language_instruction(language)
    company_focus_instruction = COMPANY_NAME_FOCUS_INSTRUCTION.format(company_name=company_name)
    research_depth_instruction = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    handling_missing_info_formatted = HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    final_review_instruction_formatted = FINAL_REVIEW_INSTRUCTION.format(language=language, company_name=company_name)
    completion_instructions = COMPLETION_INSTRUCTION_TEMPLATE

    return f"""
Comprehensive Corporate Profile, Strategic Overview, and Organizational Analysis of {company_name}

Objective: To compile a detailed, accurate, and analytically contextualized corporate profile, strategic overview, organizational structure analysis, and key personnel identification for {company_name}, focusing solely on this entity. Avoid detailed analysis of parent or subsidiary companies except for listing subsidiaries as requested.

Target Audience Context: The final research output is intended for review and strategic planning by a **Japanese company**. Present the information clearly and accurately with granular details and actionable insights. {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

Research Requirements:
{company_focus_instruction}
Conduct in-depth research using {company_name}'s official sources based *only* on provided grounding. Every factual claim, data point, and summary must include an inline citation in the format [SSX] (see Inline Citation Requirement). Provide specific dates or reporting periods (e.g., "as of 2024-03-31", "for FY2023"). Ensure every claim is grounded by a verifiable Vertex AI grounding URL referenced back in the final Sources list.
{handling_missing_info_formatted}
{research_depth_instruction}
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION}

{formatting_instructions}

## 1. Core Corporate Information:
    *   **Stock Ticker Symbol / Security Code:** (if publicly traded) [SSX]
    *   **Primary Industry Classification:** (e.g., GICS, SIC – specify the standard) [SSX]
    *   **Full Name and Title of Current CEO:** [SSX]
    *   **Full Registered Headquarters Address:** [SSX]
    *   **Main Corporate Telephone Number:** [SSX]
    *   **Official Corporate Website URL:** [SSX]
    *   **Date of Establishment/Incorporation:** (e.g., "established on YYYY-MM-DD") [SSX]
    *   **Date of Initial Public Offering (IPO)/Listing:** (if applicable, include exact date) [SSX]
    *   **Primary Stock Exchange/Market where listed:** (if applicable) [SSX]
    *   **Most Recently Reported Official Capital Figure:** (specify currency and reporting period) [SSX]
    *   **Most Recently Reported Total Number of Employees:** (include reporting date and source; quantify any significant changes) [SSX]

## 2. Recent Business Overview:
    *   Provide a detailed summary of {company_name}'s core business operations and primary revenue streams based on the most recent official reports [SSX]. Include specific product or service details and any recent operational developments (with exact dates or periods) [SSX].
    *   Include key highlights of recent business performance (e.g., "revenue increased by 12% in FY2023 [SSX]") or operational changes (e.g., restructuring, new market entries with dates), and explain their significance [SSX].

## 3. Business Environment Analysis:
    *   Describe the current market environment by identifying major competitors and market dynamics (include specific names, market share percentages, and exact data dates as available [SSX]).
    *   Identify and explain key industry trends (e.g., technological shifts, regulatory changes) including specific figures or percentages where possible [SSX].
    *   Discuss the strategic implications and opportunities/threats these trends pose for {company_name} from a Japanese corporate perspective [SSX].

## 4. Organizational Structure Overview:
    *   Describe the high-level organizational structure as stated in official sources (e.g., "divisional", "functional", "matrix") and reference the source (e.g., "as shown in the Annual Report, p. XX") [SSX].
    *   Briefly comment on the rationale behind the structure and its implications for decision-making and agility [SSX].

## 5. Key Management Personnel & Responsibilities:
    *   **Board of Directors:** List members, their titles, committee memberships, and key responsibilities (preferably in a table if the list is long) with exact dates of appointment or tenure where available [SSX].
    *   **Corporate Auditors / Audit & Supervisory Board Members:** List members with their primary oversight roles [SSX].
    *   **Executive Officers (Management Team):** List key members (beyond CEO) with titles and detailed descriptions of their strategic responsibilities (include start dates and any recent changes with explanation, if available) [SSX].

## 6. Subsidiaries List:
    *   List major direct subsidiaries (global where applicable) based solely on official documentation *for {company_name}*. For each subsidiary, include primary business activity, country of operation, and, if available, ownership percentage as stated in the source [SSX]. Present this in a table if clarity is needed.

## 7. Leadership Strategic Outlook (Verbatim Quotes):
    *   **CEO & Chairman:** Provide at least four direct, meaningful quotes focusing on long-term vision, key challenges, growth strategies, and market outlook *for {company_name}*. Each quote must be followed immediately by its source citation in parentheses (e.g., `(Source: Annual Report 2023, p.5)`) and an inline citation [SSX].
    *   **Other Key Executives (e.g., CFO, CSO, CTO, Regional Heads):** Provide at least three direct quotes each with similar detailed attribution and inline citation [SSX] where applicable.

## 8. General Discussion:
    *   Provide a concluding single paragraph (approximately 300-500 words).
    *   **Synthesize** the key findings exclusively from Sections 1-7 *about {company_name}*, explicitly linking analysis (e.g., "The declining revenue margin [SSX] suggests...") and ensuring every claim is supported by an inline citation [SSX].
    *   Structure your analysis logically by starting with an overall assessment, then discussing strengths and opportunities, followed by weaknesses and risks, and concluding with an outlook relevant for the Japanese audience.
    *   **Do not introduce new factual claims** that are not derived from the previous sections or relate to other companies.

Source and Accuracy Requirements:
*   **Accuracy:** All information must be factually correct, current, and verifiable against grounded sources *for {company_name}*. Specify currency and reporting periods for all monetary data.
*   **Source Specificity (Traceability):** Every data point, claim, and quote must be traceable to a specific source using an inline citation (e.g., [SSX]). These must match the final Sources list.
*   **Source Quality:** Use only official company sources primarily *for {company_name}*. Secondary sources may be used sparingly for context. All sources must be clearly cited.

{completion_instructions}
{final_review_instruction_formatted}
{final_source_instructions}
""".strip()


def get_financial_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for a detailed financial analysis with all enhancements."""
    language_instruction = get_language_instruction(language)
    company_focus_instruction = COMPANY_NAME_FOCUS_INSTRUCTION.format(company_name=company_name)
    research_depth_instruction = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    handling_missing_info_formatted = HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    final_review_instruction_formatted = FINAL_REVIEW_INSTRUCTION.format(language=language, company_name=company_name)
    completion_instructions = COMPLETION_INSTRUCTION_TEMPLATE
    enhanced_financial_research_instructions = textwrap.dedent(f"""\
    *   **Mandatory Deep Search & Calculation:** Conduct an exhaustive search within **{company_name}'s** official financial disclosures (based *only* on provided grounding) for the last 3 fiscal years, including Annual Reports, Financial Statements (Income Statement, Balance Sheet, Cash Flow Statement), Footnotes, Supplementary Data Packs, official filings, and IR materials. Do not rely solely on summary tables; examine detailed statements and notes for definitions and components [SSX].
    *   **Calculation Obligation:** For financial metrics such as Margins, ROE, ROA, Debt-to-Equity, and ROIC: if not explicitly stated in grounded sources, calculate them using standard formulas only if all necessary base data *for {company_name}* is available and verifiable from grounding. Clearly state the calculation method and any averages used (e.g., "ROE (Calculated: Net Income / Average Shareholders' Equity)") [SSX_supporting_calc].
    *   **Strict Omission Policy:** If a metric cannot be found in grounded sources or reliably calculated, omit that specific line item entirely. Never use placeholders like 'N/A' [SSX].
    """)
    return f"""
Comprehensive Strategic Financial Analysis of {company_name} (Last 3 Fiscal Years)

Objective: Deliver a complete, analytically rich, and meticulously sourced financial profile of **{company_name}** using the last three full fiscal years based *only* on grounded information. Combine traditional financial metrics with analysis of profitability, cost structure, cash flow, investments, and contextual factors.

Target Audience Context: This analysis is for a **Japanese corporate strategy audience**. Use Japanese terminology when appropriate (e.g., "売上総利益" for Gross Profit) and ensure that all monetary values specify currency and reporting period (e.g., "FY2023") with exact dates where available [SSX]. {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

Research Requirements:
{company_focus_instruction}
For each section, provide verifiable data *for {company_name}* with inline citations [SSX] and specific dates or reporting periods based *only* on grounding. Every claim must be traceable to a final source.
{handling_missing_info_formatted}
{research_depth_instruction}
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION}
{enhanced_financial_research_instructions}
{ANALYSIS_SYNTHESIS_INSTRUCTION}

{formatting_instructions}

## 1. Top Shareholders:
    *   List major shareholders of {company_name} (typically the top 5-10, with exact ownership percentages, reporting dates, and source references based on grounding) [SSX].
    *   Briefly comment on the stability or influence of the ownership structure on the financial strategy, *if supported by grounded analysis* [SSX].

## 2. Key Financial Metrics (3-Year Trend in a Table):
    *   Present the following metrics *for {company_name}* for the last 3 fiscal years in a Markdown table, based *only* on grounded data. Specify currency and fiscal year for each value. If calculated, show the formula used and cite the source(s) for base data [SSX_base_data].
        *   Total Revenue / Net Sales
        *   Gross Profit *(Calculated if needed: Revenue - COGS)*
        *   Gross Profit Margin (%) *(Calculated: Gross Profit / Revenue)*
        *   EBITDA and EBITDA Margin (%) *(calculated if possible from grounded data)*
        *   Operating Income / Operating Profit and Operating Margin (%)
        *   Ordinary Income / Pre-Tax Income and Ordinary Income Margin (%)
        *   Net Income and Net Income Margin (%)
        *   ROE (%) *(calculated as Net Income / Average Shareholders' Equity if data grounded)*
        *   ROA (%) *(calculated as Net Income / Average Total Assets if data grounded)*
        *   Total Assets and Total Shareholders' Equity
        *   Equity Ratio (Total Equity / Total Assets)
        *   Key Debt Metrics (e.g., Total Debt and Debt-to-Equity Ratio)
        *   Key Cash Flow Figures (e.g., Net Cash from Operations, Investing, Financing)
    *   Briefly explain any key trends visible in the grounded data (e.g., a 12% increase in revenue [SSX]) and the potential drivers behind them *if mentioned in grounded sources* [SSX].

## 3. Profitability Analysis (3-Year Trend):
    *   Analyze trends in Operating Margin and Net Income Margin *for {company_name}* using grounded data, including year-over-year percentage changes if calculable. Explain the drivers behind these trends (e.g., cost variations, pricing power) *only if specified in grounded sources* with inline citations [SSX].

## 4. Segment-Level Performance (if applicable):
    *   If segment data *for {company_name}* is available *in grounded sources*, present revenue, operating profit, and margin percentages for each segment in a table (include currency and fiscal year) [SSX].
    *   Analyze trends and the relative contribution of each segment, citing specific figures from grounding [SSX].

## 5. Cost Structure Analysis (3-Year Trend):
    *   Detail the composition and trends of major operating costs *for {company_name}* based on grounded data:
        *   Cost of Goods Sold (COGS) and its percentage of revenue [SSX].
        *   SG&A expenses and their percentage of revenue [SSX].
        *   If available in grounding, break down SG&A (e.g., R&D, personnel, marketing) with currency specifications [SSX].
    *   Analyze drivers behind cost trends and comment on cost control effectiveness *if commentary exists in grounded sources* [SSX].

## 6. Cash Flow Statement Analysis (3-Year Trend):
    *   Analyze trends in Operating Cash Flow (OCF) *for {company_name}* based on grounded data and their drivers (e.g., profit changes versus working capital adjustments) *if explained in grounding* [SSX].
    *   Detail major Investing and Financing Cash Flow activities with currency and context, as per grounded sources [SSX].
    *   Calculate and analyze Free Cash Flow (FCF = OCF - CapEx) *if base data is grounded*, and comment on the company's capacity to fund operations and investments *based on grounded analysis* [SSX].

## 7. Investment Activities (Last 3 Years):
    *   Describe major M&A deals, capital expenditure patterns, and any corporate venture or R&D investments *by {company_name}* with specific amounts (specify currency and reporting period) *as found in grounded sources* [SSX].
    *   Analyze the strategic rationale and potential financial impact of these investments *if discussed in grounded sources* [SSX].

## 8. Contextual Financial Factors:
    *   Identify significant one-time events affecting {company_name} (e.g., asset sales, restructurings) with specific dates and financial impacts *if detailed in grounded sources* [SSX].
    *   Discuss any accounting standard changes and external economic or regulatory influences *mentioned in grounded sources as impacting {company_name}* [SSX].
    *   Critically analyze the quality and sustainability of reported earnings *based solely on commentary or data within grounded sources* and link these factors to performance trends [SSX].

## 9. Credit Ratings & Financial Health (if available):
    *   List current and historical credit ratings *for {company_name}* (with reporting dates) *if found in grounded sources* and summarize key highlights from agency commentary *if present in grounding* [SSX].
    *   Analyze the implications of these ratings for financial flexibility and cost of capital *based on grounded analysis* [SSX].

## General Discussion:
    *   Provide a concluding single paragraph (300-500 words) that synthesizes the findings exclusively from Sections 1-9 *about {company_name}*. Explicitly connect the analysis (e.g., "the declining margin found in grounded data [SSX] suggests...") and explain why these trends might exist *based on grounded information*.
    *   Structure the discussion logically by starting with an overall assessment of financial health based on grounded data, then discussing key trends and deviations, and conclude with an outlook tailored to a Japanese audience.
    *   Do not introduce any new factual claims about {company_name} that are not supported by grounded citations from previous sections.

Source and Accuracy Requirements:
*   **Accuracy:** All information must be current and verifiable *against grounded sources for {company_name}*. Specify currency and reporting period for every monetary value.
*   **Source Specificity:** Every data point must include an inline citation [SSX] that corresponds to a specific grounded source in the final Sources list.
*   **Source Quality:** Rely *only* on the provided Vertex AI Search grounding results.

{completion_instructions}
{final_review_instruction_formatted}
{final_source_instructions}
""".strip()


def get_competitive_landscape_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for a detailed competitive analysis with nuanced grounding rules."""
    language_instruction = get_language_instruction(language)
    company_focus_instruction = COMPANY_NAME_FOCUS_INSTRUCTION.format(company_name=company_name)
    research_depth_instruction = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    handling_missing_info_formatted = HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    final_review_instruction_formatted = FINAL_REVIEW_INSTRUCTION.format(language=language, company_name=company_name)
    completion_instructions = COMPLETION_INSTRUCTION_TEMPLATE
    # Competitive analysis often uses broader sources, but here we STRICTLY rely on grounding.
    competitive_research_instructions = textwrap.dedent(f"""\
    **Research & Grounding Strategy for Competitive Analysis:**

    1.  **STRICT Grounding Focus:** Conduct exhaustive research *using only the provided Vertex AI Search grounding results for this query*. Include facts, figures, and competitor details ONLY if they are directly supported by these grounding URLs, each referenced with an inline citation [SSX].
    2.  **Competitor Information Source:** Information about competitors (names, market share, products, moves) MUST come from grounded sources that explicitly mention them in relation to **{company_name}** or its market. Do NOT perform separate ungrounded searches for competitors.
    3.  **Synthesized Analysis Source:** Any analytical statement comparing {company_name} to competitors must be based on facts explicitly stated and cited [SSX] from the grounded sources. Example: "Grounded source [SS1] states Competitor A launched product Z in March. Grounded source [SS2] notes {company_name}'s competing product Y launched in June. Therefore, Competitor A had a first-mover advantage [SS1, SS2]."
    4.  **Omission Rule:** Omit any competitor detail or comparative claim if it is NOT supported by a provided grounding URL [SSX]. If grounding doesn't mention competitors, state that competitor information was not available in the provided sources.
    5.  **Final Source List Integrity:** The final "Sources" list must include only the Vertex AI grounding URLs provided *for this query*, and inline citations [SSX] must match these sources. It should NOT list external URLs or general knowledge sources about competitors.
    """)
    return f"""
Detailed Competitive Analysis and Strategic Positioning of {company_name}

Objective: To conduct a comprehensive competitive analysis of **{company_name}** by identifying key competitors, analyzing their market share, strengths, weaknesses, and strategic moves *based solely on information available in the provided Vertex AI Search grounding results*. Outline {company_name}'s competitive positioning based on this grounded data. Conclusions should include a synthesized discussion relevant to a Japanese corporate audience, strictly adhering to grounded information.

Target Audience Context: This output is for strategic review by a **Japanese company**. Ensure all analysis and competitor details are supported by explicit inline citations [SSX] derived ONLY from the provided grounding results. {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

{company_focus_instruction}
{handling_missing_info_formatted} # Especially important for competitor info not in grounding
{research_depth_instruction} # Focus search interpretation on {company_name} context
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION}
{competitive_research_instructions} # Critical rules for this prompt type
{ANALYSIS_SYNTHESIS_INSTRUCTION} # Must synthesize based *only* on grounded competitor mentions

{formatting_instructions}

## 1. Major Competitors Identification & Profiling (Based ONLY on Grounding):
    *   Identify primary global and key regional competitors *explicitly mentioned in the grounded sources in relation to {company_name} or its market*. Provide specific names, market share percentages (if stated in grounding [SSX]), and exact data dates with inline citations [SSX].
    *   For each competitor *mentioned in grounding*:
        *   **Full Name & Brief Description:** Outline their operations/scale *as described in the grounded source* [SSX].
        *   **Reported Market Share:** Provide market share data *only if stated in grounding*, along with the market and period cited [SSX].
        *   **Key Geographic Areas of Overlap:** Detail where they compete directly with {company_name} *if specified in grounding* [SSX].
        *   **Specific Competing Products/Services:** List overlapping offerings *mentioned in grounding* [SSX].
        *   **Recent Competitive Moves:** Describe significant strategic moves (e.g., M&A) *only if reported in grounding* with exact dates [SSX].
        *   **Analysis of Relative Positioning:** Compare key dimensions (pricing, quality, innovation) *if comparative statements exist in grounding*, supported by citations [SSX].
    *   Identify any strategic weaknesses *of competitors relative to {company_name}* **only if explicitly stated in grounded sources** [SSX].
    *   If grounding provides no competitor information, state: "No specific competitor details were identified in the provided grounding results for {company_name}."

## 2. {company_name}'s Competitive Advantages & Positioning (Based ONLY on Grounding):
    *   Detail {company_name}'s key sources of sustainable competitive advantage (e.g., USP, technology, brand reputation) *as described in the grounded sources*, with specific examples and inline citations [SSX].
    *   Provide a balanced assessment of competitive strengths and weaknesses relative to identified competitors *based solely on comparisons or statements found in grounded sources* [SSX].

## 3. {company_name}'s Competitive Strategy (Based ONLY on Grounding):
    *   Describe the competitive strategy (e.g., cost leadership, differentiation) *as explicitly stated in grounded sources*, with supporting statements and exact data where available [SSX].
    *   Identify and describe {company_name}'s primary value discipline (e.g., operational excellence, customer intimacy) *if mentioned in grounding*, with supporting evidence [SSX].
    *   List specific initiatives or investments aimed at enhancing its competitive position *if detailed in grounding*, including details like funding amount and timelines [SSX].
    *   Explain how {company_name} measures its competitive success (e.g., target market share, customer satisfaction metrics) *if stated in grounding* [SSX].

## 4. General Discussion:
    *   Provide a concluding single paragraph (300-500 words) that synthesizes the findings exclusively from Sections 1-3, relying *strictly on grounded information*. Clearly link analytical statements using inline citations (e.g., "the market share data mentioned in grounding [SSX] indicates...").
    *   Structure the analysis logically: Assess {company_name}'s position based on grounded advantages/disadvantages, discuss competitive dynamics *only as evidenced by grounding*, and conclude with strategic takeaways (within grounding limits) for the Japanese audience. Acknowledge limitations if grounding on competitors was sparse.
    *   Do not introduce new factual claims or competitor information not supported by grounded citations from previous sections.

Source and Accuracy Requirements:
*   **Accuracy:** All information must be factual and current *as per the grounded sources*. Specify currency, dates, and reporting periods mentioned in grounding.
*   **Traceability:** Every claim must include an inline citation [SSX] corresponding to a grounding URL in the final Sources list.
*   **Source Quality:** Rely *exclusively* on the provided Vertex AI Search grounding results.

{completion_instructions}
{final_review_instruction_formatted}
{final_source_instructions}
""".strip()


def get_management_strategy_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for analyzing management strategy and mid-term business plan with all enhancements."""
    language_instruction = get_language_instruction(language)
    company_focus_instruction = COMPANY_NAME_FOCUS_INSTRUCTION.format(company_name=company_name)
    research_depth_instruction = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    handling_missing_info_formatted = HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    final_review_instruction_formatted = FINAL_REVIEW_INSTRUCTION.format(language=language, company_name=company_name)
    completion_instructions = COMPLETION_INSTRUCTION_TEMPLATE

    return f"""
Comprehensive Analysis of {company_name}'s Management Strategy and Mid-Term Business Plan: Focus, Execution, and Progress (Based ONLY on Grounding)

Objective: To conduct an extensive analysis of **{company_name}**'s management strategy and mid-term business plan (MTP) by evaluating strategic pillars, execution effectiveness, progress against targets, and challenges, using *only* information available in the provided Vertex AI Search grounding results. Focus on explaining *why* strategic choices were made (if stated in grounding) and how progress is tracked using specific grounded data with inline citations [SSX].

Target Audience Context: This analysis is designed for a **Japanese company** needing deep strategic insights *derived solely from verifiable grounded sources*. Present all information with exact dates, reporting periods, and clear source attributions [SSX]. {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

Research Requirements:
{company_focus_instruction}
Conduct in-depth analysis based *only* on grounded official sources (IR documents, Annual/Integrated Reports, earnings call transcripts, strategic website sections found in grounding). Ensure all claims about {company_name}'s strategy include inline citations [SSX] and specific dates or reporting periods *as found in grounding*.
{handling_missing_info_formatted}
{research_depth_instruction}
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION} # Analyze *grounded* statements about strategy

{formatting_instructions}

## 1. Management Strategy and Vision Alignment (Based ONLY on Grounding):
    *   Outline {company_name}'s overall management strategy and analyze its alignment with the company's long-term vision or purpose statement *as stated in grounded sources*. Include precise references (e.g., "as of 2024-01-01") with inline citations [SSX].
    *   Explain the core management philosophy, values, and strategic approach *using examples or statements found in grounding*, including specific dates or document references cited [SSX].
    *   Identify key strategic pillars and priorities for the upcoming 3-5 years *as detailed in grounded sources*, explaining the rationale *if provided* with numerical or qualitative evidence and inline citations [SSX].
    *   Describe any significant strategic shifts from previous plans *if mentioned in grounding*, with supporting data and source references [SSX].

## 2. Current Mid-Term Business Plan (MTP) Overview (Based ONLY on Grounding):
    *   Identify the official name and exact time period of the current MTP (e.g., "FY2024-FY2026 MTP") *if specified in grounded sources* [SSX].
    *   Detail the main objectives and specific quantitative targets (financial and non-financial) *as listed in grounded documents*. Present these targets clearly (tables are acceptable) with explicit KPIs, currency, and target periods cited [SSX].
    *   Discuss key differences from previous strategic plans *if detailed in grounding*, supported by specific examples and inline citations [SSX].

## 3. Strategic Focus Areas and Initiatives (Based ONLY on Grounding):
    *   For each major strategic pillar identified *in grounded sources*:
        *   Detail the background and specific objectives of that area, explaining *why* it is a priority *if stated in grounding* [SSX].
        *   Describe the relevant market conditions and industry trends influencing it *as reported in grounding*, including specific figures or dates [SSX].
        *   List specific initiatives or projects (with funding details, timelines, and measurable outcomes *if available in grounding*) and explain how they support the pillar *according to grounded text* [SSX].
        *   Assess the potential impact and feasibility of these initiatives *based only on analysis or commentary within the grounded sources* [SSX].

## 4. Execution, Progress, and Adaptation (Based ONLY on Grounding):
    *   Identify key internal and external challenges affecting strategy execution *as mentioned in grounded sources*, with precise examples and dates cited [SSX].
    *   Describe the specific countermeasures or adjustments stated by the company *in grounded documents* and assess their likely effectiveness *based on grounded analysis* [SSX].
    *   Provide the latest progress updates *reported in grounding* with detailed performance versus targets (using tables if necessary, with specified reporting periods and currency) [SSX].
    *   Highlight any strategic adjustments made in response to external events (e.g., economic shifts, regulatory changes) *as documented in grounded sources* [SSX].

## 5. General Discussion:
    *   Provide a single concluding paragraph (300-500 words) that synthesizes the findings from Sections 1-4, *relying strictly on grounded information about {company_name}'s strategy*. Clearly connect each analytical insight with inline citations (e.g., "the strategic shift noted in grounded source [SSX] indicates...").
    *   Structure the discussion logically: Summarize the strategy from grounding, discuss execution challenges reported [SSX], and conclude with strategic takeaways relevant for a Japanese audience, acknowledging limitations if grounding was sparse on certain topics.
    *   Do not introduce any new claims or interpretations about the strategy not supported by grounded citations from previous sections.

Source and Accuracy Requirements:
*   **Accuracy:** Information must be factually correct *as presented in grounded sources*. Specify currency and exact dates reported in grounding.
*   **Traceability:** Every claim must have an inline citation [SSX] linked to the final Sources list (which contains only the grounding URLs).
*   **Source Quality:** Rely *exclusively* on the provided Vertex AI Search grounding results.

{completion_instructions}
{final_review_instruction_formatted}
{final_source_instructions}
""".strip()


def get_regulatory_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for analyzing the regulatory environment for DX with all enhancements."""
    language_instruction = get_language_instruction(language)
    company_focus_instruction = COMPANY_NAME_FOCUS_INSTRUCTION.format(company_name=company_name)
    research_depth_instruction = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    handling_missing_info_formatted = HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    final_review_instruction_formatted = FINAL_REVIEW_INSTRUCTION.format(language=language, company_name=company_name)
    completion_instructions = COMPLETION_INSTRUCTION_TEMPLATE

    return f'''
In-Depth Analysis of the Regulatory Environment and Compliance for {company_name}'s Digital Transformation (DX) (Based ONLY on Grounding)

Objective: To analyze the regulatory environment impacting **{company_name}**'s DX initiatives, including data privacy, cybersecurity, AI governance, and sector-specific digital rules, *using only information found in the provided Vertex AI Search grounding results*. Evaluate the company's compliance approaches and any enforcement actions *as reported in grounded sources*, with precise dates and references cited [SSX].

Target Audience Context: The output is for a **Japanese company** reviewing regulatory risks for potential partnership, investment, or competitive evaluation based on verifiable information. Provide exact dates, reporting periods, and detailed grounded source references [SSX]. {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

Research Requirements:
{company_focus_instruction}
Conduct analysis *only* on {company_name}'s regulatory environment using the provided grounding results. Each claim must be supported by an inline citation [SSX] with specific dates or reporting periods *as found in grounding*.
{handling_missing_info_formatted}
{research_depth_instruction}
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION} # Analyze grounded statements about regulations/compliance

{formatting_instructions}

## 1. Regulatory Environment and Compliance (Based ONLY on Grounding):
    *   Describe the key regulatory policies impacting {company_name}'s DX *as mentioned in grounded sources*. Identify applicable data privacy laws (e.g., GDPR, APPI) *if named in grounding* with specific references and dates cited [SSX].
    *   Explain cybersecurity mandates and relevant standards (e.g., NIS2 Directive) *if discussed in grounded sources* with precise source details [SSX].
    *   Discuss emerging AI governance regulations (e.g., EU AI Act) and any sector-specific digital rules *if reported in grounding*, citing official documents found in sources [SSX].
    *   Explain how these regulations influence {company_name}'s strategic choices (e.g., data handling, cybersecurity investments) *based on statements in grounded sources* with exact examples and dates cited [SSX].
    *   Detail {company_name}'s stated compliance approach *found in grounding*, including policies, certifications (e.g., ISO 27001), and integration of compliance in DX project planning [SSX].
    *   Identify any significant regulatory enforcement actions or controversies involving {company_name} in the last 3-5 years *if reported in grounded sources*, specifying dates, regulatory bodies, outcomes (with currency where applicable), and company responses [SSX]. If none found, state that.

## 2. General Discussion:
    *   Provide a concluding single paragraph (300-500 words) that synthesizes the regulatory findings exclusively from Section 1, based *only* on grounded information. Clearly articulate the regulatory impacts and compliance posture *as evidenced by grounded sources* with inline citations [SSX].
    *   Structure the analysis by summarizing the regulatory environment described in grounding, assessing compliance strengths and weaknesses *if inferable from grounded data*, and concluding with an evaluation of risk tailored to a Japanese audience, acknowledging limitations if grounding was sparse.
    *   Do not introduce new factual claims about regulations or compliance not supported by grounded citations.

Source and Accuracy Requirements:
*   **Accuracy:** All regulatory details must be current and verifiable *against the grounded sources*. Include specific dates and currency information as applicable *if found in grounding*.
*   **Traceability:** Each statement must have an inline citation [SSX] corresponding to the final Sources list (containing only grounding URLs).
*   **Source Quality:** Use *only* the provided Vertex AI Search grounding results.

{completion_instructions}
{final_review_instruction_formatted}
{final_source_instructions}
'''.strip()


def get_crisis_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for analyzing digital crisis management and business continuity with all enhancements."""
    language_instruction = get_language_instruction(language)
    company_focus_instruction = COMPANY_NAME_FOCUS_INSTRUCTION.format(company_name=company_name)
    research_depth_instruction = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    handling_missing_info_formatted = HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    final_review_instruction_formatted = FINAL_REVIEW_INSTRUCTION.format(language=language, company_name=company_name)
    completion_instructions = COMPLETION_INSTRUCTION_TEMPLATE

    return f'''
In-Depth Analysis of {company_name}'s Digital Crisis Management and Business Continuity (Based ONLY on Grounding)

Objective: To analyze how **{company_name}** prepares for and manages digital crises (e.g., cyberattacks, system outages) and its business continuity plans, using *only information found in the provided Vertex AI Search grounding results*. Include details on past incidents *if reported in grounding* with exact dates, impacts (including financial figures with specified currency), and the company's response strategies, all supported by inline citations [SSX].

Target Audience Context: This output is for a **Japanese company** assessing digital risk resilience based on verifiable information. Provide precise data (with dates and reporting periods) and grounded source references [SSX]. {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

Research Requirements:
{company_focus_instruction}
Conduct thorough analysis *only* on {company_name}'s crisis management and business continuity based on the provided grounding results. Include inline citations [SSX] for every fact, with specific dates or periods *as found in grounding*.
{handling_missing_info_formatted}
{research_depth_instruction}
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION} # Analyze grounded statements about crises/BCP

{formatting_instructions}

## 1. Crisis Management and Business Continuity (Based ONLY on Grounding):
    *   **Handling of Past Digital Crises (Last 5 Years):** Describe significant digital crises involving {company_name} (e.g., ransomware attacks, data breaches, prolonged outages) *only if publicly reported in grounded sources*. Include approximate dates, impact details (systems affected, data compromised, financial loss in specified currency), and sources cited [SSX]. If none found, state that.
    *   Detail the company's public response and subsequent actions (e.g., remedial measures, regulatory reporting, support for affected parties) *as described in grounded sources*, including any lessons learned mentioned [SSX].
    *   Explain the stated approach to digital crisis management (e.g., existence of an Incident Response Plan or dedicated crisis teams) and business continuity planning (e.g., recovery time objectives) *as documented in grounded sources*, citing precise official sources and dates [SSX].
    *   Describe roles or governance structures involved in managing digital crises *if detailed in grounding*, supported by verifiable details [SSX].

## 2. General Discussion:
    *   Provide a concluding single paragraph (300-500 words) synthesizing the findings from Section 1, *based solely on grounded information*. Clearly explain how {company_name}'s crisis management practices and business continuity plans (as described in grounding) contribute to overall resilience, using inline citations (e.g., "the early response mentioned in grounding [SSX] demonstrates...").
    *   Structure the discussion logically, starting with a summary of past incidents found in grounding, followed by evaluation of the response and preparedness (based on grounded evidence), and concluding with strengths, weaknesses, and recommendations relevant to a Japanese audience, acknowledging limitations if grounding was sparse.
    *   Do not introduce any new claims about incidents or plans not supported by grounded citations.

Source and Accuracy Requirements:
*   **Accuracy:** All incident details and response measures must be current *as per the grounded sources*, with currency and exact dates specified *if found*.
*   **Traceability:** Every claim must include an inline citation [SSX] linked to a source in the final Sources list (containing only grounding URLs).
*   **Source Quality:** Rely *exclusively* on the provided Vertex AI Search grounding results.

{completion_instructions}
{final_review_instruction_formatted}
{final_source_instructions}
'''.strip()


def get_digital_transformation_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for analyzing DX strategy and execution with all enhancements."""
    language_instruction = get_language_instruction(language)
    company_focus_instruction = COMPANY_NAME_FOCUS_INSTRUCTION.format(company_name=company_name)
    research_depth_instruction = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    handling_missing_info_formatted = HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    final_review_instruction_formatted = FINAL_REVIEW_INSTRUCTION.format(language=language, company_name=company_name)
    completion_instructions = COMPLETION_INSTRUCTION_TEMPLATE

    return f"""
In-Depth Analysis of {company_name}'s Digital Transformation (DX) Strategy and Execution (Based ONLY on Grounding)

Objective: To analyze {company_name}'s Digital Transformation strategy, including its vision, key priorities, major investments, and specific case studies of digital initiatives, *using only information found in the provided Vertex AI Search grounding results*. Evaluate also how DX integrates compliance and crisis management *if mentioned in grounding*. Use precise data (e.g., specific investment amounts, dates) supported by inline citations [SSX].

Target Audience Context: The analysis is prepared for a **Japanese company**; therefore, it must be detailed, with exact figures (specifying currency and reporting periods) and grounded source references [SSX]. {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

Research Requirements:
{company_focus_instruction}
Conduct detailed analysis *only* on {company_name}'s DX journey using the provided grounding results (company reports, dedicated DX documentation, press releases found in grounding). Every claim, financial figure, and example must include an inline citation [SSX] and specific dates or periods *as found in grounding*.
{handling_missing_info_formatted}
{research_depth_instruction}
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION} # Analyze grounded DX statements

{formatting_instructions}

## 1. DX Strategy Overview (Based ONLY on Grounding):
    *   Outline {company_name}'s overall digital transformation vision and strategic goals (e.g., to enhance customer experience, improve efficiency) *as stated in grounded sources* with precise references and inline citations [SSX].
    *   Identify the key strategic priorities or pillars of the DX strategy *detailed in grounding* with specific details and dates cited [SSX].
    *   List major DX initiatives or projects currently underway or recently completed *mentioned in grounding*, including specific objectives and target outcomes *if stated* [SSX].

## 2. DX Investments Analysis (Last 3 Fiscal Years) (Based ONLY on Grounding):
    *   Analyze {company_name}'s investments in DX *only if specific figures are provided in grounded sources*. If available, provide breakdowns by initiative or area (e.g., cloud infrastructure, AI development) in a table format. Include specific investment amounts, funding sources, timelines, and reporting periods cited [SSX].
    *   Describe overall investment trends over the last 3 years (e.g., increasing, stable) *based on grounded data* [SSX]. If no investment data found, state that.

## 3. DX Case Studies & Implementation Examples (Based ONLY on Grounding):
    *   Provide detailed descriptions of 2-3 specific DX implementation examples or case studies *if detailed in the grounded sources*. For each example found:
        *   The technology or initiative implemented *as described* [SSX].
        *   The business objective and measurable outcomes (e.g., cost savings percentage, efficiency gains, new revenue in specified currency) *only if quantified in grounding* with exact data and sources cited [SSX].
        *   Explain *why* this example was highlighted by the company *if stated in grounding* (e.g., flagship project) with inline citations [SSX].
    *   If no case studies are found in grounding, state that.

## 4. Regulatory Environment, Compliance, and Crisis Management (Related to DX) (Based ONLY on Grounding):
    *   Briefly summarize the regulatory trends that impact {company_name}'s DX (e.g., data privacy, cybersecurity) *if mentioned in grounded sources*, with specific laws and exact dates cited [SSX].
    *   Describe how {company_name} integrates compliance (e.g., certifications, privacy-by-design) into its DX efforts *based on grounded statements* with precise source details [SSX].
    *   Mention how crisis management and business continuity considerations are addressed in the context of DX, citing official examples *only if found in grounding* [SSX].

## 5. General Discussion:
    *   Provide a concluding single paragraph (300-500 words) that synthesizes the findings from Sections 1-4, *based exclusively on grounded information*. Explicitly link data points and examples using inline citations (e.g., "the investment increase mentioned [SSX] supports the strategic shift...").
    *   Structure your discussion logically—start with the DX strategy found in grounding, proceed through investment and implementation details (as available), then integrate regulatory and risk management aspects *if covered in grounding*.
    *   Tailor your final analysis for a Japanese audience, acknowledging limitations of the analysis if grounding was sparse. Do not introduce new facts about DX outside of the grounded analysis.

Source and Accuracy Requirements:
*   **Accuracy:** All data must be current and verified *against the grounded sources*. Specify currency and reporting period for every monetary value *found in grounding*.
*   **Traceability:** Every fact must include an inline citation [SSX] that corresponds to a source in the final Sources list (containing only grounding URLs).
*   **Source Quality:** Rely *exclusively* on the provided Vertex AI Search grounding results.

{completion_instructions}
{final_review_instruction_formatted}
{final_source_instructions}
""".strip()


def get_business_structure_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for analyzing business structure, geographic footprint, ownership, and leadership linkages with all enhancements."""
    language_instruction = get_language_instruction(language)
    company_focus_instruction = COMPANY_NAME_FOCUS_INSTRUCTION.format(company_name=company_name)
    research_depth_instruction = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    handling_missing_info_formatted = HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    final_review_instruction_formatted = FINAL_REVIEW_INSTRUCTION.format(language=language, company_name=company_name)
    completion_instructions = COMPLETION_INSTRUCTION_TEMPLATE

    # Added enhanced completion guidance for business structure - check if still relevant/needs update
    business_structure_completion_guidance = textwrap.dedent(f"""\
    *   **Data Priority (within Grounding):** If grounded data is limited, prioritize completing:
        1. The business segment breakdown with at least the most recent fiscal year data found [SSX].
        2. The geographic segment breakdown with at least the most recent fiscal year data found [SSX].
        3. The top 3-5 major shareholders *if listed in grounding* [SSX].

    *   **Progressive Completion:** For each section, provide available grounded information:
        * For segments: List main segments found [SSX] and their % of revenue for the most recent year *if data exists in grounding* [SSX].
        * For geography: List main regions found [SSX] and their % of revenue for the most recent year *if data exists in grounding* [SSX].
        * For shareholders: List the largest shareholders *mentioned in grounding* [SSX].

    *   **Partial Data Handling:** If 3-year data is unavailable in grounding, clearly state the available timeframe *based on grounding* (e.g., "Grounded data available for FY2023 only [SSX]") and proceed with analysis of available grounded data. Do not omit sections entirely unless NO relevant information is found in grounding.

    *   **Final Verification within Grounding:** Before completing each section, verify:
        * All priority information points *found in grounding* are addressed.
        * At least one full fiscal year of *grounded data* is provided for segments if available.
        * All available *grounded* ownership information is included.
        * Each data point includes proper citation [SSX].
    """)

    return f"""
In-Depth Analysis of {company_name}'s Business Structure, Geographic Footprint, Ownership, and Strategic Vision Linkages (Based ONLY on Grounding)

Objective: To analytically review {company_name}'s operational structure, geographic markets, ownership composition, and how these link to leadership's strategic vision, using *only information available in the provided Vertex AI Search grounding results*. Include specific figures (with currency and fiscal year), and reference grounded sources (e.g., Annual Report excerpts, IR materials) with inline citations [SSX].

Target Audience Context: This output is intended for a **Japanese company** performing market analysis and partnership evaluation based on verifiable information. Present all claims with exact dates, detailed quantitative figures, and clear grounded source references [SSX]. {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

Research Requirements:
{company_focus_instruction}
Perform a critical analysis using *only* the provided grounding results. Supplementation is forbidden. Ensure each claim includes an inline citation [SSX] and precise data (e.g., "as of YYYY-MM-DD") *as found in grounding*.
{handling_missing_info_formatted}
{research_depth_instruction}
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION} # Synthesize *grounded* structural/strategic links
{business_structure_completion_guidance} # Guidance on handling limited grounding

{formatting_instructions}

## 1. Business Segment Analysis (Last 3 Fiscal Years) (Based ONLY on Grounding):
    *   List the reported business segments (or main business lines) *using descriptions found in grounded sources*. Include a table with consolidated sales figures (specify currency and fiscal year) and composition ratios *if this data is present in grounding*, with each data point referenced [SSX].
    *   For each segment *mentioned in grounding*:
        * Official segment name as reported *in grounding* [SSX]
        * Brief description of products/services in that segment *from grounding* [SSX]
        * Revenue figures (with currency and fiscal year) for the last 3 years *if available in grounding* [SSX]
        * Year-over-year growth/decline rates (%) *if calculable from grounded data* [SSX_base_data]
        * Profit margins *if reported in grounding* with exact reporting period [SSX]
    *   Analyze significant trends (e.g., growth/decline, margin changes) *evident in grounded data* with specific percentages and dates cited [SSX].
    *   Identify the fastest growing and most profitable segments *based on grounded data* [SSX]. If segment data is missing, state so.

## 2. Geographic Segment Analysis (Last 3 Fiscal Years) (Based ONLY on Grounding):
    *   List the geographic regions or segments *mentioned in grounding* with corresponding sales figures and composition ratios in a table *if data exists in grounding*, including the fiscal year and currency cited [SSX].
    *   For each geographic region *reported in grounding*:
        * Region name as officially reported *in grounding* [SSX]
        * Revenue figures (with currency and fiscal year) for last 3 years *if available in grounding* [SSX]
        * Year-over-year growth/decline rates (%) *if calculable from grounded data* [SSX_base_data]
        * Percentage of total revenue for each year reported *if available in grounding* [SSX]
    *   Analyze regional trends *based on grounded data* with specific supporting data and inline citations [SSX].
    *   Identify key growth markets and declining markets *if evidenced by grounded data* [SSX].
    *   Note any stated plans for geographic expansion or contraction *mentioned in grounding* with dates and details cited [SSX]. If geographic data is missing, state so.

## 3. Major Shareholders & Ownership Structure (Based ONLY on Grounding):
    *   Describe the overall ownership type (e.g., publicly traded, privately held) *if specified in grounding*.
    *   List the top 5-10 major shareholders *only if names and percentages are provided in grounding* with:
        * Exact shareholder names *as reported in grounding* [SSX]
        * Precise ownership percentages *as stated in grounding* (as of the most recent reporting date found) [SSX]
        * Shareholder type (institutional, individual, government, etc.) *if mentioned in grounding* [SSX]
        * Any changes in major shareholders over the past year, *if reported in grounding* [SSX]
    *   Include information *found in grounding* on:
        * Total shares outstanding (with exact as-of date) [SSX]
        * Free float percentage [SSX]
        * Presence of controlling shareholders or parent companies [SSX]
        * Cross-shareholdings with business partners [SSX]
    *   Include any details regarding different classes of shares *if mentioned in grounding*, and provide an analytical comment on ownership concentration *based only on grounded data* [SSX]. If shareholder info is missing, state so.

## 4. Corporate Group Structure (Based ONLY on Grounding):
    *   Describe the parent-subsidiary relationships and overall corporate group structure *as detailed in grounded sources* [SSX].
    *   List key subsidiaries *mentioned in grounding* with:
        * Official subsidiary names [SSX]
        * Ownership percentage by the parent company *if stated* [SSX]
        * Primary business functions of each subsidiary *if described* [SSX]
        * Country/region of incorporation *if mentioned* [SSX]
    *   Note any recent restructuring, mergers, or acquisitions *reported in grounding* with specific dates and transaction details cited [SSX]. If structure info is missing, state so.

## 5. Leadership Strategic Outlook & Vision (Verbatim Quotes - Linkages) (Based ONLY on Grounding):
    *   Provide verbatim quotes from key executives (CEO, Chairman, optionally CFO/CSO) *found in grounded sources* that address:
        * Long-term strategic vision for the company structure [SSX]
        * Plans for business segment growth/rationalization [SSX]
        * Geographic expansion or focus strategies [SSX]
        * Comments on ownership structure or major shareholder relations (if any) [SSX]
    *   Each quote must have its source cited immediately after it (e.g., "(Source: Annual Report 2023, p. 5 found in grounding)") and an inline citation [SSX].
    *   Where possible, explicitly connect a quote found in grounding to a specific finding in Sections 1-4 *also based on grounding* (e.g., "Reflecting the focus on Asia reported [SSX] in Section 2, the CEO stated... [SSY]").

## 6. General Discussion:
    *   Provide a single concluding paragraph (300-500 words) synthesizing the findings from Sections 1-5, *strictly based on grounded information*. Clearly link analytical insights and comparisons using inline citations (e.g., "the shift in segment sales reported [SSX] suggests...").
    *   Address specifically *based on grounding*:
        * The alignment between business structure and stated strategic vision [SSX]
        * How ownership structure may influence business decisions [SSX]
        * Geographic expansion strategies and their business segment implications [SSX]
        * Potential future developments based on current structure and leadership comments found in grounding [SSX]
    *   Structure your discussion logically, summarizing grounded business/geographic drivers, assessing ownership influence and leadership vision (as per grounding), and concluding with strategic implications for a Japanese audience, acknowledging limits of grounded data.
    *   Do not introduce new unsupported claims about structure or strategy.

Source and Accuracy Requirements:
*   **Accuracy:** Ensure all data is precise *as per grounding*, with currency and fiscal year reported for numerical values *found*.
*   **Traceability:** Every fact must include an inline citation [SSX] corresponding to the final Sources list (containing only grounding URLs).
*   **Source Quality:** Use *only* the provided Vertex AI Search grounding results.

{completion_instructions}
{final_review_instruction_formatted}
{final_source_instructions}
""".strip()


def get_vision_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt focused on company vision and strategic purpose with all enhancements."""
    language_instruction = get_language_instruction(language)
    company_focus_instruction = COMPANY_NAME_FOCUS_INSTRUCTION.format(company_name=company_name)
    research_depth_instruction = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    handling_missing_info_formatted = HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    final_review_instruction_formatted = FINAL_REVIEW_INSTRUCTION.format(language=language, company_name=company_name)
    completion_instructions = COMPLETION_INSTRUCTION_TEMPLATE

    return f"""
Analysis of {company_name}'s Strategic Vision and Purpose (Based ONLY on Grounding)

Objective: To provide a detailed analysis of {company_name}'s officially stated vision, mission, or purpose *based only on information found in the provided Vertex AI Search grounding results*. Break down its core components (pillars, strategic themes), explain how progress is measured using specific KPIs (if mentioned), and assess stakeholder focus (if described). Include exact quotes, dates, and reference all information using inline citations [SSX].

Target Audience Context: This analysis is for a **Japanese company** assessing strategic alignment and direction based on verifiable, grounded information. Present precise information with clear source references and detailed explanations (e.g., "as per the Annual Report 2023, p.12, found in grounding [SSX]") {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

Research Requirements:
{company_focus_instruction}
Conduct analysis *only* using the provided grounding results (e.g., excerpts from company website, Annual/Integrated Reports, MTP documents found in grounding). Every claim or data point must have an inline citation [SSX] and include specific dates or periods *as found in grounding*.
{handling_missing_info_formatted}
{research_depth_instruction}
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION} # Analyze grounded statements on vision

{formatting_instructions}

## 1. Company Vision and Strategy Elements (Based ONLY on Grounding):
    *   **Vision/Purpose/Mission Statement:** Present {company_name}'s official statement verbatim *if found in grounding* with an inline citation [SSX] and explain its core message *based on the grounded text*.
    *   **Strategic Vision Components/Pillars:** List and explain the key strategic themes that underpin the vision *as detailed in grounded sources*, with definitions provided on first use (if available) and precise source references [SSX].
    *   **Vision Measures / KPIs:** Identify the specific measures or KPIs used to track progress towards the vision *only if listed in grounded sources*. Present these in a table if needed, including currency (if applicable) and reporting periods, with inline citations [SSX].
    *   **Stakeholder Focus:** Analyze how the vision addresses key stakeholder groups (e.g., customers, employees, investors) *based on statements or evidence found in grounding* [SSX]. If not mentioned, state that.

## 2. General Discussion:
    *   Provide a concluding single paragraph (300-500 words) synthesizing the information in Section 1, *based exclusively on grounded data*. Explain the clarity, ambition, and internal coherence of the vision (as presented in grounding) with explicit connections using inline citations (e.g., "the KPI alignment mentioned [SSX] confirms...").
    *   Structure the analysis logically—summarizing the vision from grounding, detailing components found, and finally evaluating strategic relevance for a Japanese audience, acknowledging limitations if grounding was sparse.
    *   Do not introduce new claims about the vision not supported by grounded citations.

Source and Accuracy Requirements:
*   **Accuracy:** Ensure all statements are current and verified *against the grounded sources*. Specify currency for financial KPIs *if found in grounding*.
*   **Traceability:** Every claim must have an inline citation [SSX] that corresponds to a source in the final Sources list (containing only grounding URLs).
*   **Source Quality:** Use *only* the provided Vertex AI Search grounding results.

{completion_instructions}
{final_review_instruction_formatted}
{final_source_instructions}
""".strip()


def get_management_message_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for collecting strategic quotes from leadership with all enhancements."""
    language_instruction = get_language_instruction(language)
    company_focus_instruction = COMPANY_NAME_FOCUS_INSTRUCTION.format(company_name=company_name)
    research_depth_instruction = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    handling_missing_info_formatted = HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    final_review_instruction_formatted = FINAL_REVIEW_INSTRUCTION.format(language=language, company_name=company_name)
    completion_instructions = COMPLETION_INSTRUCTION_TEMPLATE

    return f"""
Detailed Leadership Strategic Outlook (Verbatim Quotes) for {company_name} (Based ONLY on Grounding)

Objective: To compile a collection of direct, verbatim strategic quotes from {company_name}'s senior leadership (CEO, Chairman, and optionally CFO/CSO) *as found in the provided Vertex AI Search grounding results*. These quotes should illustrate the company's strategic direction, future plans, and responses to challenges *according to the grounded text*. Each quote must be accurately transcribed with an immediate source citation in parentheses and an inline citation [SSX].

Target Audience Context: This information is for a **Japanese company** that requires a clear understanding of leadership's strategic communication *based on verifiable sources*. Ensure that every quote includes exact dates and precise grounded source references [SSX]. {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

Research Requirements:
{company_focus_instruction}
Conduct focused extraction *only* from the provided grounding results (e.g., excerpts from Earnings Call Transcripts, Annual Reports, Investor Day presentations found in grounding) to retrieve strategically relevant verbatim quotes *about {company_name}*. Each quote must have an inline citation [SSX] and be followed by its specific source reference (e.g., "(Source: Excerpt from Annual Report 2023, p.5 found in grounding [SSX])").
{handling_missing_info_formatted}
{research_depth_instruction}
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION} # Synthesize grounded quotes

{formatting_instructions}

## 1. Leadership Strategic Outlook (Verbatim Quotes) (Based ONLY on Grounding):

### [CEO Name], CEO (Specify Name if found in grounding [SSX])
*   Provide a brief 1-2 sentence summary of the key strategic themes reflected in the CEO's quotes *found in grounding* (include the date range, e.g., 2023-2024 if mentioned) with inline citation [SSX].
*   **Quote 1:** "..." (Source: Specify grounded source with exact date/page if available; include inline citation [SSX])
*   **Quote 2:** "..." (Source: Specify grounded source with exact date/page if available; include inline citation [SSX])
*   **(Add more quotes if found in grounding, up to 4 ideal)**

### [Chairman Name], Chairman (if distinct and quotes found in grounding [SSX])
*   Provide a summary of key themes in the Chairman's quotes *found in grounding* (include date range if available) with inline citation [SSX].
*   **Quote 1:** "..." (Source: Specify grounded source; include inline citation [SSX])
*   **Quote 2:** "..." (Source: Specify grounded source; include inline citation [SSX])
*   **(Add more quotes if found in grounding, up to 3 ideal)**

### [Other Key Executive Name], [Title] (Optional if relevant quotes found in grounding [SSX])
*   Provide a brief summary of their strategic focus *based on grounded quotes* (include date range if available) with inline citation [SSX].
*   **Quote 1:** "..." (Source: Specify grounded source; include inline citation [SSX])
*   **Quote 2:** "..." (Source: Specify grounded source; include inline citation [SSX])

*   **(If no quotes for a role are found in grounding, state: "No direct quotes from the [Role Title] were identified in the provided grounding results.")*

## 2. General Discussion:
    *   Provide a concluding single paragraph (300-500 words) synthesizing the key strategic messages *solely from the quotes collected in Section 1*. Explicitly link recurring themes using inline citations referring to the quotes (e.g., "the emphasis on digital innovation [SSX] indicates...").
    *   Structure your analysis logically and tailor the insights for the Japanese audience, based *only* on the grounded quotes.
    *   Do not introduce any new factual claims or interpretations not directly supported by the grounded quotes.

Source and Accuracy Requirements:
*   **Accuracy:** Every quote must be verbatim *as presented in grounding* with correct speaker roles and dates *if available*.
*   **Traceability:** Each quote must include an inline citation [SSX] corresponding to the final Sources list (containing only grounding URLs).
*   **Source Quality:** Use *only* the provided Vertex AI Search grounding results.

{completion_instructions}
{final_review_instruction_formatted}
{final_source_instructions}
""".strip()


def get_account_strategy_prompt(company_name: str, language: str = "Japanese"):
    """
    Generates a prompt for a detailed 3-Year Account Strategy Action Plan
    for a specific company, from the perspective of NESIC, using grounding.
    """
    language_instruction = get_language_instruction(language)
    company_focus_instruction = COMPANY_NAME_FOCUS_INSTRUCTION.format(company_name=company_name)
    research_depth_instruction = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    handling_missing_info_formatted = HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    final_review_instruction_formatted = FINAL_REVIEW_INSTRUCTION.format(language=language, company_name=company_name)
    completion_instructions = COMPLETION_INSTRUCTION_TEMPLATE

    # Specific Persona/Context for this prompt
    persona_objective = textwrap.dedent(f"""\
        **Persona & Objective:** Assume the role of an expert Account Strategy Action Planner from NEC Network and System Integration Corporation (NESIC) with 15+ years of experience. Your task is to generate a comprehensive, data-driven, and highly specific **3-Year Account Strategy Action Plan (targeting FY2025-2027)** for **{company_name}**.

        **Critical Constraint:** You MUST rely *exclusively* on the information retrieved and grounded via the **Vertex AI Search system for {company_name}** for this specific request. Do *not* use external knowledge about NESIC's internal specifics, pricing, or undisclosed capabilities unless presenting generic NESIC solution categories known to address *grounded* customer needs.

        **Action Planning Approach:**
        1.  Thoroughly analyze the grounded information about {company_name}.
        2.  Identify specific, verifiable challenges, goals, projects, and organizational details relevant to NESIC's potential offerings using inline citations `[SSX]`.
        3.  Synthesize these findings into concrete, actionable steps for NESIC.
        4.  Propose relevant, *standard* NESIC solution categories or known service lines that directly address the *grounded* customer needs. The need must be cited `[SSX]`; the proposed NESIC solution acts as the recommendation.
        5.  AVOID generic suggestions ("consider improving X"). Be decisive and specific ("NESIC to propose [Solution Category] targeting [Specific Dept/Goal] in QX YYYY based on grounded need [SSX]").
        6.  If crucial planning data (e.g., exact budget holder name, specific budget figure) is NOT available in grounded sources, state this gap clearly (e.g., "Budget owner for Project Y requires confirmation [SSX_confirming_project_but_not_owner]"). Do not invent details.
    """)

    # Refined Analysis instruction emphasizing NESIC perspective
    nesic_analysis_synthesis = textwrap.dedent(f"""\
    *   **NESIC-Centric Analysis and Synthesis:**
        *   Analyze all grounded data points *through the lens of identifying opportunities for NESIC*.
        *   Explicitly link {company_name}'s stated challenges, initiatives, or technology gaps (citing `[SSX]`) to potential NESIC value propositions (e.g., "The stated need for improved data center efficiency [SSX] presents an opportunity for NESIC's Managed Services.").
        *   In the Action Plan (Section 7) and General Discussion, synthesize findings to present a coherent strategy *for NESIC*, prioritizing actions based on grounded evidence of customer need and potential impact.
        *   Quantify opportunities *only* if grounded data provides a basis for estimation (e.g., stated project scope, investment figures [SSX]). Otherwise, focus on the qualitative strategic fit. Estimate source must be cited [SSX].
    """)

    return f"""
{persona_objective}

Target Audience Context: Internal NESIC strategic planning team. Clarity, specificity, and grounding are paramount for internal decision-making. {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

Research & Planning Requirements:
{company_focus_instruction}
Conduct thorough research focused *solely* on **{company_name}** using the provided grounding results. Every factual statement about {company_name} (their structure, finances, plans, challenges) MUST be supported by an inline citation `[SSX]`.
{handling_missing_info_formatted}
{research_depth_instruction}
{SPECIFICITY_INSTRUCTION} # Apply rigorously to customer data and action items
{INLINE_CITATION_INSTRUCTION} # Use the mandatory simple format
{nesic_analysis_synthesis} # Apply ANALYSIS_SYNTHESIS_INSTRUCTION with NESIC focus

{formatting_instructions} # Includes critical formatting rules

--- START OF PLAN ---

## 1. Target Customer Profile ({company_name}) (Based ONLY on Grounding):
    *   **Core Business Scope:** Describe primary operations, markets served, and key products/services based *only* on grounded data [SSX].
    *   **Headquarters & Scale:** State full HQ address [SSX] and the most recent reported employee count [SSX] *if found in grounding*.
    *   **Current Leadership:** Identify the current CEO by full name and title [SSX] *if found in grounding*.

## 2. Financial Overview & Key Performance Indicators (KPIs) (Last 3 Fiscal Years) (Based ONLY on Grounding):
    *   **Revenue Trend:** Report exact revenue figures (specify currency, FY) for the last 3 available years [SSX] *if found in grounding*. Calculate YoY growth rates if data permits [SSX_supporting_calc]. Identify key growth/decline drivers *if stated* in grounded sources [SSX]. If no data, state that.
    *   **Profitability:** Report exact net income figures (specify currency, FY) for the last 3 available years [SSX] *if found in grounding*. Calculate net profit margin if possible [SSX_supporting_calc]. Note any specific segment profitability details found [SSX]. If no data, state that.
    *   **Stated Financial Goals/KPIs:** List any explicitly stated financial targets or KPIs {company_name} aims for, relevant to NESIC's domain (e.g., IT cost reduction targets, ROI expectations for tech projects) [SSX] *if found in grounding*.

## 3. Stated Strategic Initiatives & Technology Roadmap (Next 1-3 Years) (Based ONLY on Grounding):
    *   **Key Strategic Pillars:** List {company_name}'s major stated strategic goals or initiatives relevant to IT, digital transformation, operations, etc. [SSX] *if found in grounding*.
    *   **Specific Projects/Investments:** Detail known projects (e.g., cloud migration, cybersecurity enhancement, specific application rollouts) including timelines, stated goals, and investment amounts *if available in grounded data* [SSX].
    *   **Technology Focus:** Outline stated technology adoption plans (specific platforms, vendors mentioned, standards) [SSX] *if found in grounding*. Identify potential integration points or gaps relevant to NESIC [SSX_showing_gap]. If no relevant initiatives found, state that.

## 4. Organizational Structure & Key Decision-Makers (for IT/Relevant Areas) (Based ONLY on Grounding):
    *   **Structure Overview:** Describe the relevant parts of the organizational structure (e.g., IT department, digital units) based on grounded data [SSX].
    *   **Key Stakeholders:** List names and titles of executives/managers identified in grounded sources as responsible for IT, technology, digital strategy, procurement, or specific relevant projects [SSX].
    *   **Decision Process:** Note any information found in grounding regarding the IT decision-making process or key influencers [SSX]. If no specific info is found, state that.

## 5. Identified Business Challenges & Pain Points (Based ONLY on Grounding):
    *   Enumerate specific challenges, operational issues, or pain points explicitly mentioned in grounded sources (e.g., system integration difficulties, cybersecurity concerns, need for cost efficiency) [SSX].
    *   Quantify impact where possible based on data found in grounding [SSX].
    *   **NESIC Opportunity Link:** For each identified challenge [SSX], briefly state *why* it represents a potential opportunity for a standard NESIC solution category (e.g., "Stated cybersecurity skills gap [SSX] suggests potential need for NESIC's Managed Security Services."). If no challenges found, state that.

## 6. Current Vendor Landscape & NESIC Competitive Positioning (Based ONLY on Grounding):
    *   **Known Incumbents/Partners:** List technology vendors, integrators, or consultants currently working with {company_name} *as identified in grounded sources* [SSX]. Specify the area of engagement if known [SSX]. If none mentioned, state that.
    *   **NESIC's Potential Advantage:** For key opportunity areas identified (linked to grounded challenges/initiatives [SSX]), briefly articulate NESIC's standard competitive strengths (e.g., reliability, specific expertise area, integration capabilities) relevant to the *grounded customer need*. Focus on the fit-for-purpose based on the customer's stated situation in grounding.

## 7. Proposed 3-Year NESIC Engagement Strategy & Action Plan (FY2025-2027):
    *   Present a **quarter-by-quarter action plan**. Be highly specific based on grounded information. Use decisive language.
    *   **Structure:** Use sub-headings for each Quarter (e.g., `### FY2025 Q1 Actions`).
    *   **Content per Quarter:**
        *   **Focus Theme:** (e.g., Relationship Building based on contact [SSX], Needs Discovery for Project X [SSX], Solution Proposal for Y Challenge [SSX])
        *   **Specific Actions:** List 3-5 concrete actions NESIC should take (e.g., "Schedule introductory meeting with [Stakeholder Name identified in grounding [SSX]], Head of IT Infrastructure", "Present NESIC capabilities brief focused on addressing [Specific Challenge found in grounding [SSX]]", "Submit proposal for [NESIC Solution Category] targeting [Specific Initiative detailed in grounding [SSX]]").
        *   **Target Stakeholders:** Name specific individuals or departments identified in grounding [SSX]. If unknown based on grounding, state "Identify and engage relevant stakeholder for [Area mentioned in grounding [SSX]]".
        *   **Proposed NESIC Solutions:** Name the *standard* NESIC solution categories/service lines relevant to the grounded needs [SSX] being addressed that quarter.
        *   **Expected Outcome/Goal:** (e.g., "Secure follow-up meeting", "Gain understanding of budget cycle for Project X [SSX]", "Proposal submitted", "Pilot project agreement for [Solution Category]").
        *   **Estimated Opportunity Value:** If grounded data on project scope or investment [SSX] allows for a *rough estimate*, provide it (e.g., "Potential Order Value Estimate: ~¥XXM based on stated project investment [SSX]"). If not calculable from grounding, state "Value TBD". **Acknowledge these are estimates derived from cited data [SSX].**

## 8. Proposed Success Metrics & KPIs for NESIC Account Team:
    *   Define specific, measurable, achievable, relevant, and time-bound (SMART) metrics *for the NESIC team* based on this plan, derived *only* from information gathered in grounding.
    *   **Examples:**
        *   **Relationship:** Number of meetings held with key decision-makers (identified in Sec 4 [SSX]) per quarter.
        *   **Opportunity Pipeline:** Number of qualified opportunities generated related to grounded challenges/initiatives [SSX] per FY. Value of pipeline created (based on estimates in Sec 7 [SSX]).
        *   **Solution Penetration:** Number of NESIC solution categories successfully proposed/piloted/implemented against identified needs [SSX].
        *   **Revenue/Orders:** Quarterly/Annual order targets based on estimated values derived from grounded customer information (reference Section 7 estimates [SSX]). State these are targets derived from analysis of grounded data [SSX].

## 9. General Discussion / Strategic Synthesis:
    *   Provide a concluding single paragraph (approx. 300-500 words).
    *   Synthesize the key findings *exclusively* from Sections 1-8, focusing on the overall strategic approach for NESIC towards {company_name} based *only* on grounded information.
    *   Summarize the primary opportunities based on grounded needs [SSX], the proposed NESIC engagement highlights, key risks (e.g., identified competitors [SSX], missing information gaps noted), and the rationale for the prioritization in the action plan, all linked back to grounding [SSX].
    *   Maintain the NESIC perspective, providing a cohesive strategic narrative derived from grounded data.
    *   Ensure every synthesizing statement traces back to cited information [SSX] in the previous sections. Do not introduce new factual claims about the customer or NESIC's plan not based on prior grounded analysis.

--- END OF PLAN ---

{completion_instructions}
{final_review_instruction_formatted}
{final_source_instructions}
""".strip()


# --- End of Prompt Generating Functions ---