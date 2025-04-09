# prompt_testing.py

import textwrap

# --- Standard Instruction Blocks ---

# REVISED Standardized Final Source List instructions block (v4.1 - Integrated formatting emphasis)
FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE = textwrap.dedent("""\
    **Final Source List Requirements:**

    Conclude the *entire* research output, following the 'General Discussion' paragraph, with a clearly marked section titled "**Sources**". This section is critical for verifying the information grounding process AND for document generation.

    **1. Content - MANDATORY URL Type & Source Integrity:**
    *   **Exclusive Source Type:** This list **MUST** contain *only* the specific grounding redirect URLs provided directly by the **Vertex AI Search system** *for this specific query*. These URLs represent the direct grounding evidence used.
    *   **URL Pattern:** These URLs typically follow the pattern: `https://vertexaisearch.cloud.google.com/grounding-api-redirect/...`. **Only URLs matching this exact pattern are permitted.**
    *   **Strict Filtering:** Absolutely **DO NOT** include any other type of URL (direct website links, news, PDFs, etc.).
    *   **CRITICAL - No Hallucination:** **Under NO circumstances should you invent, fabricate, infer, or reuse `vertexaisearch.cloud.google.com/...` URLs** from previous queries or general knowledge if they were not explicitly provided as grounding results *for the current query*. If a fact was identified but lacks a corresponding *provided* Vertex AI grounding URL, it cannot be sourced here and likely should not be included in the report (see Point 4).
    *   **Purpose:** This list verifies the specific grounding data provided *by Vertex AI Search for this request*, not external knowledge or other URLs.

    **2. Formatting and Annotation (CRITICAL FOR PARSING):**
    *   **Source Line Format:** Present **each source** on a **completely new line**. Each line **MUST** start with a Markdown list indicator (`* ` or `- ` followed by a space) and then the hyperlink format, immediately followed by its annotation. **DO NOT** run sources together in a single paragraph or separate them only with commas or spaces.
    *   **REQUIRED Format:** `* [Supervity Source X](Full_Vertex_AI_Grounding_URL) - Annotation text explaining supported information.`
    *   **Example:**
        ```markdown
        ## Sources
        * [Supervity Source 1](https://vertexaisearch.cloud.google.com/grounding-api-redirect/EXAMPLE_URL_1...) - Supports CEO name and headquarters address details in Section 1.
        * [Supervity Source 2](https://vertexaisearch.cloud.google.com/grounding-api-redirect/EXAMPLE_URL_2...) - Provides details on 2023 revenue figures and digital sales share.
        * [Supervity Source 3](https://vertexaisearch.cloud.google.com/grounding-api-redirect/EXAMPLE_URL_3...) - Details the shift in brand strategy and the 'North Star' purpose.
        ```
    *   **INCORRECT Format (DO NOT USE):** `[Source 1](...) - Info. [Source 2](...) - Info.`
    *   **INCORRECT Format (DO NOT USE):** `[Source 1](...), [Source 2](...), ...`
    *   **Sequential Labeling:** The visible hyperlink text **MUST** be labeled sequentially "Supervity Source 1", "Supervity Source 2", etc. Do not skip numbers.
    *   **Annotation Requirement:** The annotation **MUST** be:
        *   Included immediately after the hyperlink on the same line, separated by " - ".
        *   Brief and specific, explaining *exactly* what information in the main body that *specific* grounding URL supports.
        *   Written in the target output language: **{language}**.

    **3. Quantity and Linkage:**
    *   **Target Quantity:** Aim for a minimum of 5 and a maximum of 18 *distinct, verifiable* Vertex AI grounding URLs that directly support content in the report.
    *   **Accuracy Over Quantity:** However, the **absolute requirement is accuracy and adherence to the grounding rules (Points 1, 2 & 4)**. If, after exhaustive research and following the omission rules (Point 4), fewer than 5 *verifiable* grounding URLs supporting included report content can be found in the provided results, list only those that *are* verifiable. **Do NOT invent sources to meet the minimum count.**
    *   **Fact Linkage:** Every Vertex AI grounding URL listed **MUST** directly correspond to grounding data used for specific facts/figures/statements *present* in the final report body. The annotation should make this link clear.

    **4. Content Selection Based on Verifiable Grounding:**
    *   **Prerequisite for Inclusion:** Information (facts, figures, details, quotes) should only be included in the main report body *if* it can be supported by a **verifiable Vertex AI grounding URL provided in the search results for this query**.
    *   **Omission of Ungrounded Facts:** If a specific piece of information is found or known but lacks a direct, verifiable Vertex AI grounding URL *from the current results*, **omit that specific fact, detail, or data point** from the report.
    *   **Omission of Ungrounded Sections:** If the *core subject matter* of an entire requested section (e.g., "Crisis Management") cannot be substantiated by *any* relevant information backed by verifiable Vertex AI grounding URLs from the current results, **omit that entire section** (including its heading) from the final output. Adhere strictly to the `HANDLING_MISSING_INFO_INSTRUCTION`.

    **5. Final Check:**
    *   Before concluding the entire response, perform a final review of the "Sources" list AND the main report body. Ensure **strict adherence** to all rules, especially:
        *   Exclusive use of valid, *provided* Vertex AI grounding URLs in the "Sources" list.
        *   **CRITICAL:** Each source on a new line starting with `* ` or `- `.
        *   Correct hyperlink format `[Text](URL) - Annotation`.
        *   Content in the report body is supported by the listed sources.
        *   No fabricated sources are present.
    """)

# REVISED Standardized Handling Missing Information instruction block (v3 - Explicit Grounding Link)
HANDLING_MISSING_INFO_INSTRUCTION = textwrap.dedent("""\
    *   **Handling Missing or Ungrounded Information:**
        *   **Exhaustive Research First:** Conduct exhaustive research using primarily official company sources (refer to `RESEARCH_DEPTH_INSTRUCTION`).
        *   **Grounding Requirement for Inclusion:** Information is considered "found" and suitable for inclusion *only if* BOTH conditions are met:
            1.  The information itself is located in a reliable source document.
            2.  A **corresponding, verifiable Vertex AI grounding URL** (matching the pattern `https://vertexaisearch.cloud.google.com/grounding-api-redirect/...`) linking to that information **was provided in the search results for this specific query.**
        *   **Strict Omission Policy:** If, after thorough search, specific information requested (a bullet point, data field, sub-section) **cannot meet BOTH conditions above** (i.e., it's not found OR it lacks a verifiable *provided* Vertex AI grounding URL), then ***omit that specific bullet point, data field, or sub-section entirely*** from the final report. This applies even if you know the information from general knowledge or previous interactions but lack the specific grounding proof *for this query*.
        *   **Section Omission:** If the *entire core subject* of a requested section cannot be supported by *any* information meeting both conditions above, **omit the entire section** (including its heading).
        *   **Forbidden Placeholders:** **DO NOT** use phrases like 'Not Applicable', 'N/A', 'Not Found', 'Information Unavailable', or placeholders like 'xx'. The report must contain only verified *and* grounded information.
        *   **No Inference/Fabrication:** Do **NOT** infer, guess, or estimate information that is not explicitly stated or directly calculable from *grounded* sources. Absolutely **DO NOT** fabricate grounding URLs.
        *   **Cross-Language Search (If Necessary):** If information cannot be found *with grounding* in {language}, you may check other languages *within the provided grounding results*. If found *with grounding*, accurately translate *only the necessary specific information* to {language} and list the corresponding grounding source.
    """)

# REVISED Standardized Research Depth & Calculation instruction block (v2)
RESEARCH_DEPTH_INSTRUCTION = textwrap.dedent("""\
    *   **Research Depth & Source Prioritization:**
        *   **Exhaustive Search:** Conduct **thorough and exhaustive research** for *all* requested information points. Dig beyond surface-level summaries in sources.
        *   **Primary Source Focus:** Prioritize information retrieval from **official company sources**. This includes, but is not limited to:
            *   Latest Annual Reports / Integrated Reports (& Previous years for trends)
            *   Official Financial Statements (Income Statement, Balance Sheet, Cash Flow) & **Crucially: Footnotes**
            *   Supplementary Financial Data Packs or Investor Databooks
            *   Official Filings (e.g., EDINET, SEC filings like 10-K/20-F, Local equivalents)
            *   Investor Relations (IR) Presentations & Materials (including Mid-Term Plans, Strategy Day presentations)
            *   Earnings Call Transcripts & Presentations (**Look for Q&A sections**)
            *   Official Corporate Website (especially "About Us", "Investor Relations", "Strategy", "Governance", "Sustainability/ESG" sections)
            *   Official Press Releases detailing strategy, financials, structure, or significant events.
        *   **Management Commentary:** Actively look for and incorporate direct management commentary, explanations, and analysis provided within these official sources.
        *   **Recency:** Focus primarily on the **most recent available data and reporting periods** (e.g., last 1-3 fiscal years) unless a specific historical range is requested. Clearly state the reporting period for all data.
        *   **Secondary Sources:** Use high-quality, reputable secondary sources (e.g., major industry reports, leading financial news outlets like Nikkei, FT, WSJ, Bloomberg) *sparingly*, mainly for context (like market share estimates, independent competitor analysis) or verification if official sources are ambiguous or unavailable for a specific point. Always clearly attribute secondary sources and the date.
    *   **Calculation Guidelines:**
        *   **Permitted Calculations:** Where specific metrics (e.g., financial ratios like margins, ROE, ROA, Debt-to-Equity) are requested but not explicitly stated in sources, you **MAY calculate them** *only if* the necessary base data components (e.g., Net Income, Revenue, Equity, Assets, Debt) are **clearly available and verifiable** within the prioritized official sources.
        *   **State Method:** If a calculation is performed, **clearly state the formula used** within the report body, adjacent to the calculated value (e.g., "Operating Margin (Calculated: Operating Income / Revenue): XX.X%").
        *   **Verify Components:** Ensure the base data used for calculations is accurately sourced and consistent (e.g., same reporting period, same currency, same accounting standard if changes occurred).
    *   **Confirmation of Unavailability:** Only conclude that information is unavailable after demonstrating a diligent search across *multiple relevant primary sources* as listed above. Refer to `HANDLING_MISSING_INFO_INSTRUCTION` for how to proceed if information remains unverified or ungrounded.
    """)

# NEW: General Analysis & Synthesis Instruction Block
ANALYSIS_SYNTHESIS_INSTRUCTION = textwrap.dedent("""\
    *   **Analysis and Synthesis:** Beyond listing factual information, provide concise analysis where requested (e.g., explain trends, discuss implications, identify drivers, assess effectiveness). Connect related pieces of information *within* the section to provide a more holistic view. Ensure analysis is objective and directly supported by the grounded findings.
    """)

# NEW: Audience Context Reminder Block
AUDIENCE_CONTEXT_REMINDER = textwrap.dedent("""\
    *   **Audience Relevance:** Keep the target audience (Japanese corporate strategy professionals) in mind. Frame analysis and the 'General Discussion' to highlight strategic implications, competitive positioning, market opportunities/risks, and operational insights relevant for potential partnership, investment, or competitive assessment.
    """)

# Standardized Output Language instruction block
def get_language_instruction(language: str) -> str:
    return f"Output Language: The final research output must be presented entirely in **{language}**."

# REVISED Standardized Formatting instruction block (v3 - Table emphasis)
BASE_FORMATTING_INSTRUCTIONS = textwrap.dedent("""\
    Output Format & Quality Requirements:

    *   **Direct Start & No Conversational Text:** Begin the response *directly* with the first requested section heading (e.g., `## 1. Core Corporate Information`). **Absolutely NO introductory phrases** (e.g., "Here is the report...", "Based on the search results...") or **concluding remarks** (e.g., "I hope this helps...", "Let me know..."). The output MUST contain *only* the structured research content, the General Discussion, and the final Sources list.

    *   **Valid and Consistent Markdown:**
        *   Structure the entire output using **syntactically correct and well-formed Markdown**.
        *   Use Markdown elements appropriately: `##` for main sections (use the exact numbering and titles from the prompt), `###` for sub-sections if logical, `* ` or `- ` for bullet points (use consistent indentation for nested lists), `**text**` for bolding key terms or labels as shown in the prompt structure.
        *   Format code blocks (```) correctly if technical details are included.
        *   **CRITICAL - Table Formatting:** Pay *extreme attention* to table formatting. Ensure correct header rows (`| Header 1 | Header 2 |`), separator lines (`|---|---|` or `|:---|---:|` for alignment), and **consistent column counts** in all data rows. Use pipes `|` correctly to delimit cells. Ensure text within cells is concise and readable. Tables should be used where requested or where they significantly improve clarity for comparisons (e.g., multi-year financials, competitor summaries). Use alignment hints in the separator row where appropriate (e.g., `:---` for left, `---:` for right, `:---:` for center).
            *   **Example Table Structure:**
                ```markdown
                | Category      | Metric 1 | Metric 2 (Unit) | Notes         |
                |:--------------|---------:|:---------------:|:--------------|
                | Segment A     |    1,234 |      56.7 %     | Some details  |
                | Segment B     |      890 |      43.3 %     | More details  |
                ```

    *   **Optimal Structure & Readability:**
        *   Present information using the most effective format for clarity, following prompt suggestions:
            *   **Use Tables for:** Multi-year numerical data, personnel lists, subsidiary lists, direct side-by-side comparisons. Ensure tables are well-organized and easy to interpret.
            *   **Use Bullet Points for:** Lists of features, factors, initiatives, non-comparative items. Use clear and concise phrasing for each point. Start each list item on a new line with `* ` or `- `.
            *   **Use Paragraphs for:** Narrative descriptions, analysis, summaries, context. Ensure paragraphs are focused and well-structured.
        *   Maintain clear visual separation between sections, sub-sections, the General Discussion, and the Sources list using appropriate heading levels and spacing. Use exactly `##` for main sections as numbered in prompts.

    *   **Data Formatting Consistency:**
        *   Use appropriate thousands separators for the target language: **{language}**.
        *   **CRITICAL - Currency Specification:** *Always* specify the currency symbol/code (e.g., ¥, $, €, JPY, USD, EUR) for **ALL** monetary values. State the reporting period (e.g., "FY2023").
        *   Format dates consistently (e.g., YYYY-MM-DD or standard local format).

    *   **Tone and Detail Level:**
        *   Maintain a professional, objective, and analytical tone suitable for a **Japanese corporate strategy audience**. Avoid jargon where possible, or explain it briefly.
        *   Provide **granular detail** where requested (specific figures, names, dates, metrics).
        *   Be concise in descriptive text, but provide sufficient detail for analysis and understanding.

    *   **Completeness and Verification:**
        *   Address *all* points requested within each section.
        *   Verify that all sections, the General Discussion, and the Sources list are present and correctly formatted according to ALL instructions.
        *   **Do not submit partial or truncated responses.** Stop cleanly if limits are approached.
        *   Perform a final internal review against these instructions.
    """)

# --- Prompt Generating Functions ---

def get_basic_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for a comprehensive basic company profile with all enhancements."""
    language_instruction = get_language_instruction(language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language)

    return f"""
Comprehensive Corporate Profile, Strategic Overview, and Organizational Analysis of {company_name}

Objective: To compile a detailed, accurate, and analytically contextualized corporate profile, strategic overview, organizational structure analysis, and key personnel identification for {company_name}, focusing solely on this specific entity. Avoid detailed analysis of parent or subsidiary companies, except for listing subsidiaries as requested.

Target Audience Context: The final research output is intended for review, strategic understanding, and planning purposes by a **Japanese company**. Please ensure the information is presented clearly, accurately, granularly, and is relevant to a business audience seeking deep insights into {company_name}. {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

Research Requirements:
Conduct in-depth research primarily utilizing {company_name}'s official sources. Ensure all factual claims, data points, structural descriptions, personnel details, responsibilities, and quotes in the sections below are supported by specific, verifiable grounding URLs referenced back to the final source list.
{HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)}
{RESEARCH_DEPTH_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION}

## 1. Core Corporate Information:
    *   **Stock Ticker Symbol / Security Code:** (if publicly traded)
    *   **Primary Industry Classification:** (e.g., GICS, SIC, or local standard - Specify which standard)
    *   **Full Name and Title of Current CEO:**
    *   **Full Registered Headquarters Address:**
    *   **Main Corporate Telephone Number:**
    *   **Official Corporate Website URL:**
    *   **Date of Establishment/Incorporation:**
    *   **Date of Initial Public Offering (IPO)/Listing:** (if applicable)
    *   **Primary Stock Exchange/Market where listed:** (if applicable)
    *   **Most Recently Reported Official Capital Figure:** **(Specify currency and reporting date/period)**
    *   **Most Recently Reported Total Number of Employees:** **(Specify reporting date/period and source)**. *Briefly comment on the significance of the employee count or recent changes, if notable.*

## 2. Recent Business Overview:
    *   Provide a detailed summary of {company_name}'s core business operations and primary revenue streams based on the *most recent* official reports. Describe the main products/services offered.
    *   Include key highlights of recent business performance (e.g., major achievements, significant growth/decline areas) or significant operational developments (e.g., major restructuring, new market entries). *Explain the significance of these developments.*

## 3. Business Environment Analysis:
    *   Describe the current market environment: Identify major competitors by name, describe general market dynamics (e.g., growth trends, consolidation, key segments), provide estimated market size/share for {company_name} (if available, cite source/date precisely).
    *   Identify and explain key industry trends (e.g., technological shifts, regulatory changes, shifts in consumer behavior, sustainability pressures). Be specific.
    *   ***Discuss the potential strategic implications and specific opportunities/threats these trends pose for {company_name}. Analyze this from a Japanese corporate perspective (e.g., relevance for market entry, partnership, competitive response).***

## 4. Organizational Structure Overview:
    *   Describe the high-level organizational structure (e.g., divisional, functional, matrix, key business units) as explicitly stated in official sources.
    *   *If clearly stated, comment briefly on the rationale behind the structure or its potential implications for agility, decision-making, or integration.*

## 5. Key Management Personnel & Responsibilities:
    *   **Board of Directors:** List members, titles, *specify committee memberships (e.g., Audit, Compensation), and detail key areas of expertise/focus or specific responsibilities if stated*. Indicate if directors are classified as independent or internal. Use a table if the list is long.
    *   **Corporate Auditors / Audit & Supervisory Board Members (or equivalent oversight body):** List members, titles, *and describe their primary oversight role or focus area*.
    *   **Executive Officers (Management Team):** List key members (beyond CEO), titles, *and describe their precise area(s) of operational or strategic responsibility (e.g., CFO, CTO, Head of Region X, Head of Division Y)*. Use a table if the list is long. ***Note any recent significant changes (within the last 1-2 years) in key executive roles and explain the potential impact or reasons for these changes, if reported.***

## 6. Subsidiaries List:
    *   List major direct subsidiaries (global where applicable), based *only* on official documentation (e.g., annual report appendices, group structure charts). *Indicate primary business activity and country of operation for each subsidiary listed.* Use a table for clarity.

## 7. Leadership Strategic Outlook (Verbatim Quotes):
    *   **CEO & Chairman:** Provide at least four (4) direct, meaningful quotes *focusing on long-term vision, key challenges, growth strategies, and market outlook*. Include a brief 1-2 sentence summary noting key themes and the approximate date range of these quotes.
    *   **Other Key Executives (e.g., CFO, CSO, CTO, Regional Heads):** Provide at least three (3) direct quotes *each* from other relevant senior executives or board members, focusing on strategy relevant to their specific functional area or region. Include a brief summary... *(Substitute roles if specific titles unavailable, clearly identifying name/title.)*
    *   **Source Attribution:** Clearly cite the specific source (e.g., Report Name/Date, Interview Source/Date, Transcript Date) immediately adjacent to *each* quote using parentheses `(Source: ...)`.

## 8. General Discussion:
    *   Provide a concluding **single paragraph** (approx. **300-500 words**).
    *   Synthesize the key findings from Sections 1-7. **Analyze** the coherence between the company's profile, stated strategy, organizational structure, leadership focus, and the business environment. Offer a holistic overview discussing apparent strengths, weaknesses, **key strategic risks, and primary opportunities**. Critically evaluate the company's strategic posture. **Tailor insights specifically for the Japanese audience**, highlighting aspects most relevant for strategic decision-making. Focus on analysis and connections. **Do not introduce new factual claims.**

Source and Accuracy Requirements:
*   **Accuracy:** Ensure all information is factually correct, current, and verifiable against grounded sources. Specify currency and reporting periods for ALL monetary and headcount data.
*   **Source Specificity (Traceability):** Every factual claim, data point, detail, and quote in Sections 1-7 must be traceable to a specific source in the final list via the annotation. Use inline parenthetical citations `(Source:...)` for direct quotes as specified in Section 7.
*   **Source Quality:** Mandatory primary reliance on official company sources. Use secondary sources sparingly only for context (like market share, if not in primary) or verification, citing clearly in-text (as per competitive prompt rules if applicable) or ensuring traceability via final list annotation.

{final_source_instructions}

{formatting_instructions}
"""

# Note: Apply similar integration of ANALYSIS_SYNTHESIS_INSTRUCTION, AUDIENCE_CONTEXT_REMINDER,
# and refined section details to ALL other `get_..._prompt` functions.
# The examples for get_basic_prompt, get_financial_prompt, get_management_strategy_prompt,
# get_competitive_landscape_prompt, get_regulatory_prompt, get_crisis_prompt,
# get_digital_transformation_prompt, get_business_structure_prompt, get_vision_prompt,
# and get_management_message_prompt provided in the previous response already incorporate these.

# Ensure ALL get_..._prompt functions below follow the pattern shown above:
# - Define language_instruction, final_source_instructions, formatting_instructions
# - Include HANDLING_MISSING_INFO_INSTRUCTION, RESEARCH_DEPTH_INSTRUCTION, ANALYSIS_SYNTHESIS_INSTRUCTION, AUDIENCE_CONTEXT_REMINDER
# - Include refined details/analytical prompts within section bullet points
# - Include enhanced General Discussion instructions
# - Include final_source_instructions and formatting_instructions at the end.

# (The remaining prompt functions from the previous response are pasted below,
# assuming they already contain the enhancements)


def get_financial_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for a detailed financial analysis with all enhancements."""
    language_instruction = get_language_instruction(language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language) # Use base for consistency here too

    # Enhanced instructions for financial research depth and calculation
    enhanced_financial_research_instructions = textwrap.dedent("""\
    *   **Mandatory Deep Search & Calculation:** Conduct an **exhaustive search** within {company_name}'s official financial disclosures for the last 3 fiscal years, including **Annual Reports, Financial Statements (Income Statement, Balance Sheet, Cash Flow Statement), Crucially: Footnotes to Financial Statements, Supplementary Data Packs, official Filings (e.g., EDINET/SEC), and Investor Relations presentations/transcripts.** Do not rely solely on summary tables; examine detailed statements and notes for definitions and components.
    *   **Calculation Obligation:** For metrics like Margins, ROE, ROA, Equity Ratio, Debt-to-Equity, and ROIC: if the metric itself is not explicitly reported, you **MUST attempt to calculate it** using standard financial formulas **IF the necessary base data components** (e.g., Net Income, Revenue, Total Equity, Total Assets, Total Debt, Operating Income, Invested Capital proxies like Total Equity + Total Debt - Cash) **are clearly available and defined** within the verified, sourced official documents for *all relevant years*. Clearly state the formula used and the components sourced for any calculated metric. Specify if average balance sheet figures were used (e.g., for ROE/ROA).
    *   **Strict Omission Policy (Reiteration):** Apply the 'Handling Missing Information' rule rigorously. If a specific metric or data point cannot be found directly reported after exhaustive search, AND it cannot be reliably calculated from the available sourced base data (e.g., missing component, inconsistent definition across years), **omit that specific line item or metric entirely**. **Under no circumstances state 'N/A', 'Not Found', or use placeholders.** Focus on presenting only the verifiable and calculable information.
    """)

    return f"""
Comprehensive Strategic Financial Analysis of {company_name} (Last 3 Fiscal Years)

Objective: Deliver a complete, analytically rich, and meticulously sourced financial profile of **{company_name}**, based on the most recent **three full fiscal years**. Combine traditional metrics with analysis of profitability, cost structure, cash flow, investments, and contextual factors. Focus exclusively on **{company_name} consolidated figures** unless segment data is specifically requested and available.

Target Audience Context: The report is designed for a **Japanese corporate strategy audience** requiring detailed financial understanding for assessment. Output must reflect precision, analytical depth, relevance, and professionalism. Use Japanese terminology (e.g., "売上総利益" for Gross Profit, "経常利益" for Ordinary Income) if appropriate for the output language and available in sources. {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

Research Requirements:
For each section below, provide data and analysis covering the **last three full fiscal years**. Information must be **verifiable**, **clearly sourced** (traceable to final list, specifying report/page/note), and **analytically explained** regarding trends, drivers, and implications. **Interpret the trends and provide explanations based on sourced information or management commentary.**
{HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)}
{enhanced_financial_research_instructions.format(company_name=company_name)}
{ANALYSIS_SYNTHESIS_INSTRUCTION}

## 1. Top Shareholders:
    *   List major shareholders (typically Top 5 or Top 10 if available), their approximate ownership percentage (%), and the type of shareholder (e.g., founding family, institutional, strategic). Specify the exact data date/period end and the source document (e.g., Annual Report FY2023, p.XX). Use verifiable filings or official company disclosures primarily.
    *   *Comment briefly on the stability or potential influence of the ownership structure on financial strategy, if evident.*

## 2. Key Financial Metrics (3-Year Trend in a Table):
    *   Present the following metrics for the last 3 fiscal years in a clearly formatted Markdown table. Specify currency and FY for all monetary values. State if metrics were calculated and show the formula. Prioritize official reporting; calculate ONLY if base data is clearly available and verifiable in grounded sources for all years.
    *   Total Revenue / Net Sales (specify which term is used by the company)
    *   Gross Profit *(Calculated: Revenue - COGS if needed & possible)*
    *   Gross Profit Margin (%) *(Calculated: Gross Profit / Revenue)*
    *   EBITDA *(Search diligently; calculate ONLY if Operating Income, D&A are clearly available & consistently defined)*
    *   EBITDA Margin (%) *(Calculate: EBITDA / Revenue)*
    *   Operating Income / Operating Profit (specify term used)
    *   Operating Margin (%) *(Calculate: Operating Income / Revenue)*
    *   Ordinary Income / Pre-Tax Income (specify term used)
    *   Ordinary Income Margin (%) *(Calculate: Ordinary Income / Revenue)*
    *   Net Income (Attributable to Owners of Parent, specify if different measure used)
    *   Net Income Margin (%) *(Calculate: Net Income / Revenue)*
    *   Return on Equity (ROE) (%) *(Calculate: Net Income / Average Shareholders' Equity - Specify if avg. used)*
    *   Return on Assets (ROA) (%) *(Calculate: Net Income / Average Total Assets - Specify if avg. used)*
    *   Total Assets
    *   Total Shareholders' Equity
    *   Equity Ratio / Capital Adequacy Ratio (%) *(Calculate: Total Equity / Total Assets)*
    *   Key Debt Metrics (e.g., Total Debt [specify short/long term if available], Debt-to-Equity Ratio *(Calculate: Total Debt / Total Equity)*)
    *   Key Cash Flow Figures (Net Cash from Operations, Investing, Financing) **(Specify currency)**
    *   *For key trends observed in the table (e.g., significant revenue change, margin pressure, leverage changes), briefly explain potential drivers based on other findings or management commentary.*

## 3. Profitability Analysis (3-Year Trend):
    *   Analyze the trend in Operating Margin (%) including **Year-over-Year % Change**. **Explain the drivers** behind the trend (e.g., cost changes, pricing power, sales mix).
    *   Analyze the trend in Net Income Margin (%) including **Year-over-Year % Change**. **Explain the drivers**, considering factors below the operating line (e.g., interest, taxes, one-offs).

## 4. Segment-Level Performance (if applicable & reported, 3-Year Trend in a Table):
    *   If the company reports segment data (Business or Geographic): Present Revenue **(Specify currency)**, Operating Profit **(Specify currency)**, and Operating Margins (%) by Segment for the last 3 years in a table.
    *   **Analyze trends, relative contribution, profitability drivers, and challenges for each reported segment.** *(Omit section entirely if segment data not disclosed)*.

## 5. Cost Structure Analysis (3-Year Trend):
    *   Detail the composition and trend of major operating costs, if available:
        *   Cost of Goods Sold (COGS) **(Specify currency)** and as % of Revenue.
        *   Selling, General & Administrative (SG&A) expenses **(Specify currency)** and as % of Revenue.
        *   Breakdown of SG&A (e.g., R&D, Personnel, Marketing costs - **Specify currency**) if available.
    *   Analyze trends and drivers for key cost ratios (COGS/Rev, SG&A/Rev, R&D/Rev). **Comment on cost control effectiveness or strategic investment priorities reflected in the cost structure.**

## 6. Cash Flow Statement Analysis (3-Year Trend):
    *   Analyze **Operating Cash Flow (OCF)** trends and key drivers (e.g., changes in profit, working capital movements - detail if possible).
    *   Detail major **Investing Cash Flow (ICF)** activities: Capital Expenditures (CapEx) figures **(Specify currency)** and purpose (e.g., maintenance vs. growth), major M&A outflow values **(Specify currency)**.
    *   Detail major **Financing Cash Flow (FCF)** activities: Dividend payments, debt issuance/repayment, share buybacks/issuance values **(Specify currency)**.
    *   Calculate and comment on **Free Cash Flow (FCF = OCF - CapEx)** generation and its usage/trend. **Assess the company's ability to fund operations, investments, and shareholder returns from internally generated cash.**

## 7. Investment Activities (Last 3 Years):
    *   Describe Major M&A deals (targets, deal values **(Specify currency)**, strategic rationale).
    *   Detail significant Capital Expenditure patterns (total figures **(Specify currency)**, key areas of investment like store openings, digital, logistics).
    *   Mention any Corporate Venture Capital (CVC) investments or significant R&D investments, if detailed.
    *   Analyze Return on Invested Capital (ROIC) trend *(Search for reported ROIC; calculate ONLY if NOPAT (Net Operating Profit After Tax) and Invested Capital can be reliably determined & consistently defined from Balance Sheet/Notes. State calculation method/components used for Invested Capital clearly.)*
    *   **Analyze the strategic rationale and potential financial impact of major investment activities.**

## 8. Contextual Financial Factors:
    *   Identify and explain significant one-time events impacting financials (e.g., gains/losses on asset sales, impairments, major restructuring costs, significant legal settlements **(Specify currency if applicable)**).
    *   Discuss the impact of any relevant accounting standard changes during the period.
    *   Summarize key economic or regulatory factors explicitly cited by management as influencing financial performance.
    *   ***Critically analyze the quality and sustainability of reported earnings (e.g., reliance on one-offs vs. core operating profit consistency, impact of accounting choices if discernible). Connect these factors explicitly to observed performance trends.***

## 9. Credit Ratings & Financial Health (if available & reported):
    *   List current and historical credit ratings from major agencies (e.g., JCR, R&I, Moody's, S&P), including outlooks. Specify the date of the rating/report.
    *   Summarize key highlights or concerns raised in agency commentary.
    *   **Synthesize the implications of the ratings and commentary for the company's financial flexibility and cost of capital.** *(Omit section entirely if not publicly rated or reliable ratings unavailable)*

## General Discussion:
    *   Provide a concluding **single paragraph** (approx. **300–500 words**).
    *   **Synthesize** key findings on financial health, performance trends (revenue, profitability, cash flow), investment strategy, cost management, and contextual influences *based solely on the data presented in sections 1-9*.
    *   **Assess** financial management effectiveness, identifying key financial strengths and risks/vulnerabilities. Evaluate the company's financial trajectory and capacity for future strategic investments or M&A.
    *   **Tailor insights specifically for the Japanese audience**, focusing on financial stability, growth potential, and relevant benchmarks. **Do not introduce new factual claims.**

Source and Accuracy Requirements:
*   **Accuracy:** Data, ratios, context must be correct, verified. **Crucially, specify the currency AND reporting period (e.g., FY2023) for ALL monetary values presented.**
*   **Source Specificity (Traceability):** Every data point, ratio, calculation, and analytical insight must be precisely traceable to a specific source in the final list via the annotation (cite Report Name, Year, Page number, Table/Note number, Filing Date, Transcript Section). Explicitly state if a metric was calculated and show the formula/components.
*   **Source Quality:** Mandatory primary reliance on official company sources (Annual Reports, Financial Statements, Footnotes, Filings, IR Presentations, Transcripts, Press Releases). Use secondary sources only for context (e.g., ratings agency reports) and cite clearly.

{final_source_instructions}

{formatting_instructions}
"""

def get_competitive_landscape_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for a detailed competitive analysis with nuanced grounding rules."""
    language_instruction = get_language_instruction(language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language)

    # --- Special Research Instructions for Competitive Analysis ---
    competitive_research_instructions = textwrap.dedent("""\
    **Research & Grounding Strategy for Competitive Analysis:**

    1.  **Prioritize Grounded Facts:** Conduct exhaustive research using the Vertex AI Search tool. Give **highest priority** to including facts, figures (like market share if reported *by the company itself* or a highly reputable primary source), and competitor details that are **directly supported by provided `vertexaisearch.cloud.google.com/...` grounding URLs**. List these URLs accurately in the final "Sources" section as per the main instructions.
    2.  **Handling Synthesis and Secondary Information:** Competitive analysis often requires synthesis or information from sources not directly grounded via a Vertex AI redirect URL *in this query's results*.
        *   **Permitted Inclusion:** You MAY include:
            *   **Synthesized analysis:** Conclusions drawn logically from *multiple* grounded facts about {company_name} and its market (clearly state this basis, e.g., "Analysis based on {company_name}'s reported strategy [Source 1] and market trends [Source 3]").
            *   **Widely reported, attributed data:** Market share estimates or specific competitor information commonly cited in *reputable, named* business news outlets (e.g., Nikkei, Bloomberg, Reuters) or *major, named* industry research reports (e.g., Gartner, Forrester, Euromonitor - if accessible via grounding). **Attribute clearly.**
        *   **Mandatory In-Text Citation:** If including synthesized analysis or information from secondary sources not directly grounded by a *provided* Vertex AI URL for that specific point, you **MUST clearly indicate the source/basis in the text** next to the information (e.g., "Source: Nikkei Asia, 2024-03-15", "Based on analysis of market trends discussed in Annual Report FY23", "According to a Euromonitor report cited in Source X..."). This information *cannot* be listed in the final "Sources" list (which is reserved *only* for the provided Vertex AI grounding URLs).
    3.  **Omission Rule (Modified):** Apply the `HANDLING_MISSING_INFO_INSTRUCTION` strictly for *factual claims* expected to have direct grounding (e.g., specific competitor product names if comparing features, official financial figures of competitors). For *analytical points* (positioning, strengths/weaknesses, synthesized trends) or *attributed secondary data* (market share estimates), use the approach in Point 2. If even this synthesized/secondary information is unavailable or cannot be reliably attributed after diligent search, *then* omit the specific point or sub-section.
    4.  **Focus on Verifiable:** Aim for accuracy. Avoid speculation. If competitor details or market shares are from dubious/unnamed sources or cannot be reasonably verified, omit them.
    5.  **Final Source List Integrity:** Remember, the final "Sources" list at the very end MUST still adhere strictly to the `FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE` (only *provided* Vertex AI grounding URLs *for this query*). The allowance in Point 2 applies only to the *content within the report body* and requires clear in-text attribution for non-Vertex-grounded info.
    """)
    # --- End Special Instructions ---

    return f"""
Detailed Competitive Analysis and Strategic Positioning of {company_name}

Objective: To conduct a detailed competitive analysis of **{company_name}**, identifying major competitors, evaluating its competitive positioning, detailing advantages/weaknesses, and outlining its competitive strategy. Conclude with a synthesized discussion relevant to the target audience. Focus primarily on **{company_name}** relative to its competitors.

Target Audience Context: Output is for strategic review by a **Japanese company**. Ensure analysis is thorough, insightful, clearly presented, focusing on competitive dynamics, differentiation, and strategic responses. {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

{HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)} # Include general missing info rule for context
{competitive_research_instructions.format(company_name=company_name)} # Add the specific competitive research strategy
{ANALYSIS_SYNTHESIS_INSTRUCTION}

## 1. Major Competitors Identification & Profiling:
*   Identify **primary global and key regional competitors** in {company_name}'s main markets/segments (Prioritize competitors explicitly mentioned in grounded official {company_name} sources or highly reputable secondary sources).
*   For *each* major competitor identified (provide available information, clearly indicating source type/basis as per `competitive_research_instructions`):
    *   **Full Name & Brief Description:** Outline their relevant business operations and scale.
    *   **Estimated/Reported Market Share:** Provide share data if available *from reliable, attributed sources*. Specify the market, period, and source clearly (e.g., "Source: Euromonitor, 2023 Global Share").
    *   **Key Geographic Areas of Overlap:** Where do they directly compete with {company_name}?
    *   **Specific Competing Products/Services:** Mention key overlapping product/service categories.
    *   **Notable Recent Competitive Moves:** Include significant strategic shifts, M&A, or product launches (Cite source/date).
    *   **Analysis of Relative Market Positioning:** Compare vs. {company_name} on key dimensions like price range, product quality focus, innovation emphasis, brand image, target customer segments (State basis for analysis explicitly, e.g., "Based on public product descriptions and pricing tiers...").
    *   ***Known or Perceived Strategic Weaknesses (Relative to {company_name}):*** Identify potential vulnerabilities based on grounded facts or attributed analysis (e.g., "Slower adoption of digital channels reported by [Source]...", "Higher cost structure implied by pricing strategy..."). Attribute source/basis clearly.

## 2. {company_name}'s Competitive Advantages & Positioning:
*   Detail {company_name}'s key sources of **sustainable competitive advantage** (Prioritize examples with grounded evidence): Unique Selling Proposition (USP), Technology/Patents, Brand Reputation/Loyalty, Economies of Scale, Cost Structure Advantages, Distribution Network, Customer Relationships, etc. (Cite source/basis for each).
*   Provide a balanced assessment of {company_name}'s perceived **Competitive Strengths and Weaknesses** *relative to* its key competitors identified above. (State basis for assessment clearly, linking back to facts/analysis).

## 3. {company_name}'s Competitive Strategy:
*   Describe {company_name}'s apparent **competitive strategic approach** (Based on grounded statements, observed actions, or reliable analysis - cite source/basis clearly): How does it aim to compete? (e.g., Cost leadership, differentiation, focus/niche strategy). How does it maintain/defend its position, expand market share, respond to competitive threats, exploit competitor weaknesses, or adapt to market changes?
*   ***Identify and describe the company's primary **value discipline** (e.g., operational excellence, customer intimacy, product leadership) based on its observable strategy and actions (State basis/evidence).***
*   Identify specific **initiatives, programs, or investments** aimed at enhancing its competitive position (Prioritize grounded information, e.g., specific R&D projects, marketing campaigns, supply chain improvements).
*   Describe how competitive success is **measured or defined** by the company, if explicitly stated in grounded sources (e.g., market share goals, customer satisfaction targets).

## 4. General Discussion:
*   Provide a concluding **single paragraph** (approx. **300-500 words**).
*   **Synthesize** findings on Major Competitors, {company_name}'s Advantages/Positioning, and its Competitive Strategy *based only on the information presented above*.
*   Offer a holistic overview discussing {company_name}'s **overall competitive standing**, strategic direction, key competitive strengths, vulnerabilities/risks, and future outlook in the competitive landscape.
*   Focus on analysis and strategic takeaways relevant to the **Japanese audience** (e.g., potential impact on Japanese market, partnership opportunities, competitive threats to Japanese firms). **Do not introduce new factual claims.**

Source and Accuracy Requirements:
*   **Accuracy:** Information must be factually correct or clearly attributed as analysis/estimate/secondary source.
*   **Source Specificity (In-line/Traceability):** Strictly follow rules in `competitive_research_instructions` for citing grounded vs. synthesized/secondary info within the text. Attribute ALL non-Vertex-grounded info clearly. Ensure traceability via final source list annotations.
*   **Source Quality:** Prioritize Vertex AI grounding results. Supplement ONLY as allowed by `competitive_research_instructions` using official disclosures, reputable/named industry reports, major institutional analyses, or credible/named business news.

{final_source_instructions} # Strict rules apply ONLY to this final list

{formatting_instructions}
"""


def get_management_strategy_prompt(company_name: str, language: str = "Japanese"):
    language_instruction = get_language_instruction(language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language) # Use base

    return f"""
Comprehensive Analysis of {company_name}'s Management Strategy and Mid-Term Business Plan: Focus, Execution, and Progress

Objective: To conduct an extensive and detailed analysis of **{company_name}'s** overall management strategy, its current mid-term business plan (MTP) or equivalent strategic framework, execution status, progress tracking against targets, identified challenges, and strategic adjustments. **Focus on understanding the 'why' behind strategic choices and assessing execution effectiveness.** Focus on **{company_name}**.

Target Audience Context: Output is for detailed strategic review by a **Japanese company**. Ensure analysis is granular, clearly presented, and provides deep, actionable insights into {company_name}'s strategic framework, operationalization, performance against goals, and adaptability. {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

Research Requirements:
Conduct in-depth research, prioritizing official sources (IR materials on MTP/Strategy, Annual/Integrated Reports, Website strategy sections, Earnings call transcripts/presentations, Investor Day materials, Official Announcements). Supplement sparingly only for context. Ensure all claims regarding strategy, MTP elements, execution, KPIs, etc., are supported by specific, verifiable sources referenced back to the final list.
{HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)}
{RESEARCH_DEPTH_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION}

## 1. Management Strategy and Vision Alignment:
    *   Outline {company_name}'s stated overall management strategy. **Analyze its alignment** with the company's long-term Vision or Purpose statement.
    *   Explain the core management philosophy, values, or strategic approach explicitly stated by the company. *How does this philosophy appear to influence strategic choices and operational priorities?*
    *   Identify the key strategic pillars, priorities, or focus areas for the current planning horizon (e.g., MTP period or next 3-5 years). *Explain the stated rationale for these priorities.*
    *   Describe any significant strategic shifts compared to previous strategies or plans. *Analyze the potential drivers for these shifts (e.g., market changes, new leadership, performance issues).*

## 2. Current Mid-Term Business Plan (MTP) Overview (or equivalent strategic plan):
    *   Identify the official name (if any) and the time period covered by the current MTP or strategic plan (e.g., "FY2024-FY2026 MTP", "Vision 2030 Strategy").
    *   Detail the main objectives and **specific, quantitative targets** outlined in the plan (both financial - **Specify currency** - and non-financial/operational). List the Key Performance Indicators (KPIs) used to measure progress against these targets. Present targets and KPIs clearly, potentially using a table.
    *   Discuss key differences compared to the preceding MTP or strategic direction. *What do these differences signal about the company's evolving priorities?*

## 3. Strategic Focus Areas and Initiatives within the MTP/Strategy:
    *   For **each major strategic pillar/theme/focus area** identified in Section 1:
        *   Detail the Background and Stated Objectives (Why is this area a priority? What does the company aim to achieve?).
        *   Describe the relevant Business Context / Market Conditions influencing this focus area.
        *   Explain the connection to specific Industry Trends.
        *   List Specific Initiatives, projects, or actions planned/underway (e.g., major investments **(Specify currency and planned amount if available)**, market expansion plans, R&D programs, operational changes, organizational restructuring). ***If available, state the primary source of funding allocated to major initiatives (e.g., operating cash flow, specific debt issuance, equity).***
        *   Explain explicitly how these initiatives support the corresponding strategic pillar(s) from Section 1.
        *   Provide Implementation Timelines or key milestones associated with these initiatives, if publicly stated.
        *   *Assess the potential impact and feasibility of the key initiatives listed.*

## 4. Execution, Progress, and Adaptation of the MTP/Strategy:
    *   Identify Key Issues, Challenges, and Risks (both internal and external) that the company has acknowledged or that are evident from performance, impacting the strategy's execution. *Assess the potential significance of these risks.*
    *   Detail Specific Measures or countermeasures stated by the company to address these challenges/risks. *Evaluate the appropriateness or likely effectiveness of these countermeasures.*
    *   Provide the Latest Available Progress Updates based on official company statements regarding achievements or status against the MTP/strategy goals.
    *   Include specific data showing **Performance Versus Targets** for key financial and non-financial metrics/KPIs identified in Section 2 (Specify reporting period, **specify currency for financial targets**). Use a table if helpful. *Analyze deviations from targets and provide explanations offered by management.*
    *   Highlight any Strategic Adjustments, pivots, or changes to the plan announced by the company and the stated reasons. ***Explicitly mention if management commentary links specific external events (e.g., major economic shifts, pandemic impact, unexpected competitive actions, regulatory changes) to deviations from the plan or strategic adjustments made. Analyze the company's adaptability.*

## 5. General Discussion:
    *   Provide a concluding **single paragraph** (approx. **300-500 words**).
    *   **Synthesize** the findings regarding the company's strategy, MTP specifics, execution progress, challenges faced, and adaptations made.
    *   **Evaluate** the coherence between the company's vision, stated strategy, MTP actions, and reported progress. Analyze the strategy's alignment with the external market context and industry trends.
    *   **Assess** the plan's ambition versus realism, the effectiveness of execution based on progress against KPIs, and the company's responsiveness to challenges. Highlight key successes and persistent difficulties.
    *   Focus on strategic takeaways relevant to the **Japanese audience**, such as strategic clarity, execution capability, potential risks, and long-term direction. **Do not introduce new factual claims.**

Source and Accuracy Requirements:
*   **Accuracy:** All information must be factually correct and accurately reflect official company communications. **Ensure currency is specified for ALL monetary targets/values.** State reporting periods clearly.
*   **Source Specificity (Traceability):** Every claim, target, KPI, initiative, and progress update in Sections 1-4 must be traceable to a specific source in the final list via the annotation (cite MTP presentation slide #, report name/page, transcript section/date, press release date).
*   **Source Quality:** Strongly prioritize official company sources (MTP documents, Annual/Integrated Reports, earnings materials, Investor Day materials, website strategy sections, relevant official press releases/announcements).

{final_source_instructions}

{formatting_instructions}
"""


def get_regulatory_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for analyzing the DX regulatory environment with all enhancements."""
    language_instruction = get_language_instruction(language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language)

    return f'''
In-Depth Analysis of the Regulatory Environment and Compliance for {company_name}'s Digital Transformation (DX)

Objective: To conduct an in-depth analysis of the regulatory environment impacting **{company_name}'s** Digital Transformation (DX) initiatives. Assess the company's stated approach to compliance, particularly concerning data privacy, cybersecurity, and emerging digital regulations (e.g., AI). Focus primarily on **{company_name}'s** own situation and publicly stated positions/actions.

Target Audience Context: The final research output is intended for strategic review by a **Japanese company**, potentially considering partnership, investment, or competition. Focus on understanding how regulatory landscapes shape {company_name}'s digital strategy, risk management practices, and potential liabilities. {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

Research Requirements:
Conduct deep research on {company_name}'s operating environment related to its DX journey, focusing on regulatory aspects. Look for specifics on applicable regulations in key operating regions, stated compliance approaches, certifications, and any reported regulatory issues, using reliable grounded sources. Ensure all factual claims, regulatory descriptions, and company approaches below are supported by specific, verifiable sources referenced back to the final list.
{HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)}
{RESEARCH_DEPTH_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION}

## 1. Regulatory Environment and Compliance:
*   Describe the **key regulatory environment aspects and policy trends** impacting {company_name}'s DX. Focus on:
    *   **Data Privacy Laws:** Identify major applicable laws (e.g., GDPR in Europe, CCPA/CPRA in California, APPI in Japan, PIPL in China, LGPD in Brazil) in key geographies where {company_name} operates. Explain their core requirements regarding data collection, consent, processing, user rights, and cross-border transfers.
    *   **Cybersecurity Mandates:** Describe relevant cybersecurity regulations or standards impacting the company (e.g., NIS2 Directive in EU, sector-specific requirements if applicable).
    *   **AI Governance:** Discuss any emerging AI regulations or ethical guidelines in key markets that might affect {company_name}'s use of AI in DX (e.g., EU AI Act).
    *   **Sector-Specific Digital Rules:** Mention any regulations specific to {company_name}'s industry (e.g., retail, manufacturing) concerning digital practices, e-commerce, or platform operations.
*   **Explain the influence** of these regulations on {company_name}'s strategic choices related to DX: (e.g., data handling procedures, cloud provider selection, AI development guardrails, cybersecurity investment priorities, market entry/exit decisions). Provide specific examples if found.
*   Provide detailed information on **{company_name}'s stated general compliance approach** regarding these regulations:
    *   Detail stated **policies, strategies, or frameworks** for compliance, especially concerning data privacy and cybersecurity. Look for mentions in official reports (Annual, Sustainability, Governance) or dedicated website sections.
    *   Mention any publicly discussed **compliance certifications** (e.g., ISO 27001 for information security, SOC 2 for service organizations) held by the company or its key divisions, if reported.
    *   Describe how compliance considerations are reportedly **integrated into DX project planning and execution** (e.g., privacy-by-design principles, security reviews), if specific information is available.
*   ***Identify any known significant **regulatory enforcement actions, fines, investigations, or major public controversies** related to data privacy, cybersecurity, or digital practices levied against or involving {company_name} within the last 3-5 years, based on credible public reports. Specify dates, regulatory body involved, nature of the issue, outcome (e.g., fines - specify currency if reported, required remediation), and company response, if available.***

## 2. General Discussion:
*   Provide a concluding **single paragraph** (approx. **300-500 words**).
*   **Synthesize** the findings on the key regulatory pressures impacting {company_name}'s DX and its stated compliance approach and track record.
*   Offer a holistic **assessment** of how regulations appear to shape {company_name}'s digital strategy, risk posture, and operational constraints.
*   **Evaluate** the apparent maturity, proactiveness, and potential gaps in its compliance efforts based *only* on the findings related to stated approaches, certifications, and reported enforcement actions/controversies (if any).
*   **Tailor the perspective for the Japanese audience**, highlighting potential regulatory risks or compliance strengths relevant for business interactions with {company_name}. **Do not introduce new factual claims.**

Source and Accuracy Requirements:
*   **Accuracy:** All information (regulatory details, company policies, incident specifics) must be factually correct and verified against grounded sources.
*   **Source Specificity (Traceability):** Every claim, detail, policy description, and incident report must be traceable to a specific source in the final list via the annotation (cite report name/page, official publication, news source/date).
*   **Source Quality:** Prioritize official company disclosures (Annual/Sustainability/Governance Reports, Privacy Policies, Compliance statements), official government/regulatory body publications, reputable legal/consulting analyses on regulatory impacts, and credible news reports regarding enforcement actions.

{final_source_instructions}

{formatting_instructions}
'''

def get_crisis_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for analyzing digital crisis management with all enhancements."""
    language_instruction = get_language_instruction(language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language)

    return f'''
In-Depth Analysis of {company_name}'s Digital Crisis Management and Business Continuity

Objective: To conduct an in-depth analysis of **{company_name}'s** approach to preparing for and managing crises related to its digital systems, data, or online reputation. Include details on past incidents (if publicly known), stated crisis management and business continuity strategies, and apparent organizational resilience. Focus primarily on **{company_name}'s** experiences and stated plans.

Target Audience Context: Output is for strategic review by a **Japanese company**, assessing {company_name}'s digital risk posture and resilience. Ensure analysis is thorough, insightful, clearly presented, focusing on preparedness, response effectiveness, and lessons learned relevant for risk assessment. {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

Research Requirements:
Conduct deep research on {company_name}'s experiences and approach to digital crises. Look for specifics on past incidents (if public), stated response mechanisms, preparedness strategies, and BCP plans from reliable grounded sources. Ensure all claims and descriptions below are supported by specific, verifiable sources referenced back to the final list.
{HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)}
*   **Research Depth:** Diligently search credible news archives (major outlets), cybersecurity incident databases (where applicable), security research blogs, and official company disclosures (press releases, annual/sustainability reports sections on risk management/incidents) for information on past events and stated plans. Acknowledge that details of internal plans and non-public incidents may be unavailable. Focus on verifiable information.
{ANALYSIS_SYNTHESIS_INSTRUCTION}

## 1. Crisis Management and Business Continuity:
*   **Handling of Past Digital Crises (Last 5 Years):** Based *only* on publicly available information (news reports, security databases, company statements):
    *   Describe any significant publicly reported digital crises {company_name} has faced in the last 5 years (e.g., major cyberattacks like ransomware, significant data breaches impacting customers/employees, prolonged critical system outages, major online reputational crises linked to digital platforms).
    *   For each documented incident: Detail the approximate date(s), the nature of the incident, the reported impact (e.g., systems affected, data types exposed, estimated number of individuals impacted, reported financial impact - **Specify currency if available**), and the source of the information.
    *   Describe the company's **public response** and actions taken during and after the incident (e.g., public communication/acknowledgement, remediation steps taken, reporting to authorities, support offered to affected parties). ***Critically, mention any publicly stated 'lessons learned' or specific changes to security, policy, or technology implemented by the company as a direct result of these incidents, if reported.*** *(If no significant public incidents found in the last 5 years despite search, state this clearly).*
*   Detail {company_name}'s **stated approach to technology-related crisis management** and digital resilience, based on official disclosures:
    *   Describe any mentioned **frameworks, plans, or specific teams** dedicated to handling digital/cyber crises (e.g., Incident Response Plan (IRP), Cyber Crisis Management Plan, dedicated SOC - Security Operations Center). What are their stated functions?
    *   Explain stated strategies for digital resilience, such as system redundancy, data backup/recovery procedures, or proactive threat hunting, if mentioned.
*   Outline {company_name}'s **stated strategy for business continuity planning (BCP)** specifically concerning potential disruptions to digital systems, IT infrastructure, or critical data access.
    *   Are specific BCP goals, testing procedures, or recovery time objectives (RTOs)/recovery point objectives (RPOs) mentioned in relation to digital assets?
*   Mention described **roles, responsibilities, or governance structures** for overseeing and managing digital crises and business continuity, if publicly disclosed (e.g., specific executive oversight, dedicated risk committees).

## 2. General Discussion:
*   Provide a concluding **single paragraph** (approx. **300-500 words**).
*   **Synthesize** the findings on {company_name}'s past crisis experiences (if any were publicly documented), its stated crisis management/BCP approach, governance structures, and any reported lessons learned or adaptations.
*   Offer a holistic **assessment** of {company_name}'s apparent preparedness, responsiveness, and resilience regarding digital crises, based *only* on the findings presented above.
*   **Discuss** perceived strengths (e.g., dedicated teams, proactive measures) and potential weaknesses or areas lacking public transparency (e.g., recurring incident types, lack of detail on BCP specifics, limited disclosure on lessons learned).
*   **Tailor the perspective for the Japanese audience**, focusing on digital risk mitigation effectiveness, incident response capability, and overall operational resilience relevant for business partnerships or competitive evaluation. **Do not introduce new factual claims.**

Source and Accuracy Requirements:
*   **Accuracy:** Information must be factually correct and verified against grounded sources. Incident details must rely on credible reports; clearly distinguish alleged vs. confirmed information if necessary. Specify currency for any reported financial impacts.
*   **Source Specificity (Traceability):** Every claim, incident detail, strategic description, and policy mention must be traceable to a specific source in the final list via the annotation (cite news source/date, report name/page, official statement date).
*   **Source Quality:** Prioritize official company statements/disclosures on incidents/risk management. Use reputable news reports, cybersecurity research firm reports, and official documents on BCP/crisis management carefully, verifying where possible. Acknowledge limitations in public information.

{final_source_instructions}

{formatting_instructions}
'''

def get_digital_transformation_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for analyzing DX strategy with all enhancements."""
    language_instruction = get_language_instruction(language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language) # Use base

    return f"""
In-Depth Analysis of {company_name}'s Digital Transformation (DX) Strategy and Execution

Objective: To conduct an in-depth analysis of **{company_name}'s** stated Digital Transformation (DX) strategy, including its vision, key priorities, major investments, specific implementation examples (case studies), and the integration of related regulatory/compliance and crisis management considerations. Focus primarily on **{company_name}'s** own initiatives and publicly available information.

Target Audience Context: Output is for strategic review by a **Japanese company**. Ensure analysis is thorough, insightful, clearly presented, focusing on understanding {company_name}'s digital strategy articulation, execution maturity, investment patterns, achieved outcomes, and approach to managing associated risks. {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

Research Requirements:
Conduct deep research into {company_name}'s DX journey using official sources (reports, website, press releases) and reputable secondary analysis. Look for specifics on strategy articulation, financial commitments, concrete implementation examples with outcomes, and how DX interacts with compliance and risk management. Ensure all claims/data/descriptions below are supported by specific, verifiable sources referenced back to the final list.
{HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)}
{RESEARCH_DEPTH_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION}

## 1. DX Strategy Overview:
    *   Outline {company_name}'s stated overall **vision or ambition** for DX. What are the core strategic goals it aims to achieve through digital transformation? (e.g., enhance customer experience, improve operational efficiency, develop new business models, become data-driven).
    *   Identify the key **strategic priorities or pillars** of its DX strategy (e.g., focus areas like cloud adoption, data analytics & AI, automation, cybersecurity enhancement, omnichannel integration, supply chain digitalization).
    *   List major specific **DX initiatives, projects, or programs** mentioned as currently underway or recently completed. Provide brief descriptions and objectives for key initiatives.

## 2. DX Investments Analysis (Last 3 Fiscal Years, where available):
    *   Analyze available information on {company_name}'s investments related to DX. Use bullet points or a table if appropriate. Detail:
        *   **Allocation by Activity/Area:** Is there any breakdown of DX investment focus by major activity or initiative area (e.g., Cloud infrastructure, AI/ML development, Data platform implementation, CRM systems, Automation tools, Cybersecurity)? Describe the focus within key areas.
        *   **Specific Investment Amounts/Budgets:** Provide specific investment figures, budgets, or financial commitments related to DX *if publicly stated* **(Specify currency and reporting period/timeframe)**.
        *   ***Funding Sources:*** Specify the primary source of funding for major DX investments, *if explicitly mentioned* (e.g., dedicated DX budget, reallocation from other areas, operating cash flow, specific capital raising).
        *   **Timelines:** Note available information on timelines or schedules for major DX programs.
        *   **Stated ROI/KPIs/Impacts:** Summarize any stated Expected ROI, KPIs used to measure DX success, or anticipated business impacts mentioned in relation to these investments (e.g., cost savings targets, efficiency gain goals, customer satisfaction improvements).
    *   Describe the **overall trend** in DX investment levels over the last 3 years, if discernible from available data or company commentary (e.g., increasing, stable, focused on specific areas). Cite supporting data/statements.

## 3. DX Case Studies & Implementation Examples:
    *   Provide detailed descriptions of specific, concrete **DX implementation examples or case studies** highlighted by {company_name} or reported in reliable sources. Focus on examples demonstrating successful application of digital technologies.
    *   For each case study (aim for 2-3 distinct examples if possible):
        *   Describe the specific **Initiative/Technology** implemented.
        *   Outline the **Business Objectives** it aimed to address.
        *   Detail the **Specific Measurable Outcomes or Value Delivered** (e.g., quantified cost savings %/**Specify currency**, efficiency gains %, customer satisfaction (CSAT) score improvement, new revenue generated **Specify currency**, faster time-to-market). **Cite sources clearly for all outcomes.**
        *   ***If context is available, explain *why* these specific examples might be highlighted by the company (e.g., showcases a core capability, addresses a major industry pain point, demonstrates significant ROI, flagship project for a new technology).***

## 4. Regulatory Environment, Compliance, and Crisis Management (Related to DX):
    *   *(Provide a focused summary drawing on findings potentially generated for other report sections, viewed specifically through the DX lens. Avoid simple repetition; synthesize the connection.)*
    *   Briefly summarize the **key regulatory trends** (e.g., data privacy, cybersecurity, AI governance) that most significantly impact or shape {company_name}'s DX initiatives and choices.
    *   Briefly describe how {company_name}'s stated approach to **compliance** (especially regarding data protection and cybersecurity) is integrated into or influences its DX efforts and platform development.
    *   Briefly mention how {company_name}'s stated approach to **managing digital crises** and business continuity relates to the risks introduced or amplified by its DX initiatives.

## 5. General Discussion:
    *   Provide a concluding **single paragraph** (approx. **300-500 words**).
    *   **Synthesize** the findings on {company_name}'s DX strategy (vision, priorities), investment patterns, execution examples (case studies), and the influence of regulatory/risk management considerations.
    *   Offer a holistic **assessment** of the company's DX maturity, strategic focus, and apparent effectiveness based on reported outcomes and initiatives.
    *   **Discuss** perceived strengths (e.g., clear vision, successful implementations, integrated approach) and potential challenges or weaknesses (e.g., investment scale vs. ambition, managing complexity, ensuring ROI, adapting to regulation) in its DX journey. Note any significant recent shifts in strategy or focus.
    *   **Tailor the perspective for the Japanese audience**, highlighting aspects of {company_name}'s DX approach (e.g., technology choices, integration strategies, risk management) that are most relevant for benchmarking or potential collaboration/competition. **Do not introduce new factual claims.**

Source and Accuracy Requirements:
*   **Accuracy:** Information must be correct, current, and verified against grounded sources. **Specify currency and period for ALL monetary values (investments, outcomes).**
*   **Source Specificity (Traceability):** Every claim, data point, strategic description, and case study detail must be traceable to a specific source in the final list via the annotation (cite report name/page, press release date, specific secondary source/date).
*   **Source Quality:** Prioritize official company disclosures (Annual/Sustainability/Digital Reports, IR presentations, dedicated DX documentation, press releases). Use reputable technology research firm reports (cite specific report/date) and credible tech/business news analyses where appropriate for context or specific examples, citing clearly.

{final_source_instructions}

{formatting_instructions}
"""


def get_business_structure_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for analyzing business structure with all enhancements."""
    language_instruction = get_language_instruction(language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language) # Use base

    return f"""
In-Depth Analysis of {company_name}'s Business Structure, Geographic Footprint, Ownership, and Strategic Vision Linkages

Objective: Conduct an **analytical review** of **{company_name}'s** operational structure (key business and geographic segments), ownership composition, and how these elements connect to leadership's stated strategic vision and commentary. Focus on identifying trends, revenue/profit drivers, ownership influences, and strategic coherence. Use consolidated figures primarily, unless segment data is reported.

Target Audience Context: Output is for strategic assessment by a **Japanese company**. Provide clear insights into where {company_name} generates revenue, its major markets, the nature and potential influence of its ownership, and how its structure supports (or hinders) its strategic priorities. Relevant for benchmarking, market analysis, and partnership evaluation. {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

Research Requirements:
Conduct **critical analysis** interrogating official sources (Annual/Integrated Reports, IR materials, Filings, Corporate Governance sections of website). Supplement sparingly ONLY for verification (e.g., shareholder identification if not in primary sources, using reputable financial databases). Ensure all claims, figures, analyses, and quotes below are supported by specific, verifiable sources referenced back to the final list.
{HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)}
{RESEARCH_DEPTH_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION}

## 1. Business Segment Analysis (Last 3 Fiscal Years, if reported):
    *   List the **reported business segments** (e.g., by product category, service type, customer group). If the company doesn't report formal segments, describe the main business lines/divisions based on its operational descriptions.
    *   For each major segment/business line reported: Provide a concise Description of Core Operations/Products/Services.
    *   If available, present in a **table**: Consolidated Sales **(Specify currency & FY)** and Composition Ratio (% of Total Sales) for the last 3 years. If segment profit is reported, include that too **(Specify currency & FY)** and Segment Profit Margin (%).
    *   **Analyze significant trends** within and between segments (e.g., growth/decline rates, shifts in sales contribution, margin changes). *Explain potential drivers for these trends based on sourced management commentary or clearly linked market context.* *(Omit section or parts if segment data is not publicly disclosed).*

## 2. Geographic Segment Analysis (Last 3 Fiscal Years, if reported):
    *   List the **reported geographic segments** (e.g., by country, region like Europe, Asia, Americas).
    *   For each significant geographic segment reported, present in a **table**: Consolidated Sales **(Specify currency & FY)** and Composition Ratio (% of Total Sales) for the last 3 years. Include segment profit/margin if available.
    *   **Analyze significant geographic trends**. Highlight regions of growth, decline, or strategic importance. *Explain the 'why' behind these trends using sourced information (e.g., market maturity, specific country performance, M&A activity, targeted investments, economic factors cited by management).* *(Omit section or parts if geographic data is not publicly disclosed).*

## 3. Major Shareholders & Ownership Structure:
    *   Describe the overall ownership type (e.g., publicly traded, privately held - family-owned, PE-backed, state-owned).
    *   If publicly traded OR if details on private ownership are available from reliable sources: List the **Top 5-10 major shareholders** based on the *most recent* available data.
    *   For each listed shareholder: Provide Full Name, Approximate % Shares Outstanding (or nature of control if % not available), Type of Shareholder (e.g., Founding Family, Institutional Investor, PE Firm, Sovereign Wealth Fund, Holding Company - specify if possible). **Specify the exact 'as of' date for the data and the source document reference.**
    *   ***Note if any known 'activist' shareholders are currently involved and briefly summarize their publicly stated objectives/demands regarding {company_name}, if applicable and publicly reported.***
    *   **Provide a brief analytical comment** on the nature of the ownership structure (e.g., concentrated vs. dispersed, influence of founding families/strategic investors, potential implications for long-term strategy vs. short-term pressures).

## 4. Leadership Strategic Outlook & Vision (Verbatim Quotes - Linkages):
    *   Provide direct, **verbatim quotes** from current CEO, Chairman, and/or other key C-suite executives (e.g., CFO, CSO) that explicitly address:
        *   The company's long-term strategic vision or core priorities.
        *   Future growth plans (specific initiatives, target markets, key investments).
        *   Perspectives on key market opportunities or challenges faced by the company.
    *   Ensure the specific **source and context** (e.g., report name/page, interview source/date, transcript date, presentation slide #) is documented *immediately following each quote* using parentheses `(Source: ...)`. Aim for recent quotes (last 1-2 years).
    *   ***Crucially, where possible, explicitly link these strategic quotes to the business or geographic segments analyzed in Sections 1 & 2, or the ownership structure discussed in Section 3. (e.g., "Reflecting the focus on Asia noted in Section 2, the CEO stated '[Quote about Asian expansion]' (Source)...").***

## 5. General Discussion:
    *   Provide a concluding **single paragraph** (approx. **300-500 words**).
    *   **Critically synthesize** the findings from *all* sections above (Business Segments, Geography, Ownership, Leadership Vision).
    *   **Analyze and interlink** how the company's structure (business/geographic focus) and ownership model appear to support or potentially conflict with its stated strategic vision and leadership commentary.
    *   **Evaluate the overall coherence** between the company's operational footprint, performance trends, ownership influences, and strategic direction.
    *   Discuss resultant strategic strengths, potential vulnerabilities, or key strategic questions arising from this analysis. Tailor insights for the **Japanese audience's** strategic perspective. **Do not introduce new factual claims.**

Source and Accuracy Requirements:
*   **Accuracy:** Information must be correct, current, and verified. **State currency clearly and specify the Fiscal Year (FY) for ALL segment sales/profit figures.**
*   **Source Specificity (Traceability):** Every claim, data point, quote, and element of analysis in Sections 1-4 must be traceable to a *precise* source in the final list via the annotation (cite report name/page, filing/date, database source/date, transcript section/date). Use inline parenthetical citations `(Source:...)` for direct quotes as specified in Section 4.
*   **Source Quality:** Mandatory primary reliance on official company sources (Annual/Integrated Reports, Filings, IR presentations, official Corporate Governance statements, transcripts). Use high-caliber secondary sources (reputable financial databases, major news outlets) ONLY as supplementary clarification for ownership details if not in primary sources, and cite meticulously.

{final_source_instructions}

{formatting_instructions}
"""

def get_vision_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt focused on company vision with all enhancements."""
    language_instruction = get_language_instruction(language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language) # Use base

    return f"""
Analysis of {company_name}'s Strategic Vision and Purpose

Objective: To provide a detailed analysis of **{company_name}'s** officially stated strategic vision, purpose, or mission statement. Detail its core components (pillars/themes), how progress is measured (key metrics/KPIs), and how it addresses key stakeholder groups. Focus solely on **{company_name}**'s formally communicated vision.

Target Audience Context: Output is for strategic review by a **Japanese company**. Ensure information on the vision, its components, and measurement is presented clearly, accurately, and sourced from official materials, allowing assessment of strategic direction and alignment. {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

Research Requirements:
Conduct in-depth research, primarily using official sources such as the company website (Strategy, About Us, IR, Sustainability sections), Annual Reports, Integrated Reports, Mid-Term Plan documents, official filings, and press releases detailing strategy or vision. Ensure claims regarding the vision, its components, and associated measures/KPIs below are supported by specific, verifiable sources referenced back to the final list.
{HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)}
{RESEARCH_DEPTH_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION}

## 1. Company Vision and Strategy Elements:
    *   **Vision/Purpose/Mission Statement:** Outline **{company_name}'s** officially stated **Vision, Purpose, or Mission Statement**. Quote it verbatim if possible and cite the source document/location. *Explain the core message or goal it conveys.*
    *   **Strategic Vision Components/Pillars:** Describe the key **components, pillars, or strategic themes** that constitute the company's strategic **Vision Outline** or long-term plan, as officially articulated. List and briefly explain each component/pillar.
    *   **Vision Measures / KPIs:** Identify specific **Measures, Key Performance Indicators (KPIs)**, or concrete strategic initiatives that the company has announced or uses to track progress towards its overall vision or the goals of its strategic pillars. Group these by pillar/component if possible. **(Specify currency for any financial KPIs and the target timeframe/year if mentioned).** Use a table if it enhances clarity.
    *   ***Stakeholder Focus:*** **Analyze and identify** if and how the company's stated vision explicitly addresses or prioritizes key stakeholder groups (e.g., Customers, Employees, Shareholders/Investors, Society, Environment, Suppliers/Partners). Provide evidence or examples from the vision/strategy documents.

## 2. General Discussion:
    *   Provide concluding **single paragraph** (approx. **300-500 words**).
    *   **Synthesize** the findings regarding the company's stated vision, its core components/pillars, how it measures progress (KPIs), and its explicit stakeholder focus.
    *   **Analyze** the clarity, ambition, and internal coherence of the vision and its components. How well do the identified measures and KPIs seem aligned with tracking progress towards the stated vision and pillars?
    *   Offer insights relevant to the **Japanese audience** regarding the strategic direction, priorities, and values implied by {company_name}'s vision. How does it compare to typical corporate visions in relevant sectors? **Do not introduce new factual claims.**

Source and Accuracy Requirements:
*   **Accuracy:** Information (statements, pillars, measures) must be factually correct, current, and accurately reflect official company communications. Verify against official sources. **Specify currency for any financial KPIs.**
*   **Source Specificity (Traceability):** Every claim, quote, pillar description, and KPI listed in Section 1 must be traceable to a *precise* source in the final list via the annotation (cite report name/page, MTP document/page, specific website URL section, press release date).
*   **Source Quality:** Mandatory primary reliance on official company sources (Website strategy/about/IR/sustainability pages, Annual/Integrated/Governance Reports, official strategy documents, MTP presentations, relevant press releases).

{final_source_instructions}

{formatting_instructions}
"""

def get_management_message_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for collecting strategic quotes with all enhancements."""
    language_instruction = get_language_instruction(language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatting_instructions = BASE_FORMATTING_INSTRUCTIONS.format(language=language) # Use base

    return f"""
Detailed Leadership Strategic Outlook (Verbatim Quotes) for {company_name}

Objective: To compile a detailed collection of direct, verbatim quotes from **{company_name}'s** senior leadership (specifically CEO, Chairman, and potentially CFO or CSO if highly relevant strategic quotes are found) that articulate strategic direction, future plans, responses to challenges, growth initiatives, and forward-looking perspectives. Focus solely on **{company_name}**.

Target Audience Context: Output is for strategic review by a **Japanese company**. Ensure quotes and context are clear, accurately reflect stated views from leadership, and provide relevant insights into strategic intent, priorities, and tone from the top. {AUDIENCE_CONTEXT_REMINDER}

{language_instruction}

Research Requirements:
Conduct focused research to locate and extract direct, impactful, and strategically relevant verbatim quotes based on the criteria below. Prioritize official sources and recent statements (last 1-2 years). Ensure quotes are accurately transcribed and attributed with specific sources referenced back to the final list.
{HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)} # Applies if specific roles or sufficient strategic quotes cannot be found despite diligent search.
{RESEARCH_DEPTH_INSTRUCTION} # Especially focus on Earnings Call Transcripts, IR Presentations, Annual Report Letters.
{ANALYSIS_SYNTHESIS_INSTRUCTION} # Apply mainly to the summaries and General Discussion.

## 1. Leadership Strategic Outlook (Verbatim Quotes):

### [CEO Name], CEO (Specify Name)
*   *(Brief 1-2 sentence summary distilling the key strategic themes, priorities, and overall tone reflected in the CEO's recent quotes below. **Note the approximate date range of these quotes (e.g., 2023-2024).**)*
*   **Quote 1:** "..." (Source: Specific source citation - e.g., FY2023 Earnings Call Transcript, Q1 2024, p. 5 / Annual Report 2023, CEO Letter / Interview, Publication Name, YYYY-MM-DD)
*   **Quote 2:** "..." (Source: Specific source citation)
*   **Quote 3:** "..." (Source: Specific source citation)
*   **Quote 4:** "..." (Source: Specific source citation)
    *(Provide at least four strategically significant quotes. Ensure they cover aspects like overall vision, key initiatives, market view, or major challenges/responses.)*

### [Chairman Name], Chairman (Specify Name, if applicable and distinct from CEO)
*   *(Brief 1-2 sentence summary distilling key strategic themes from the Chairman's recent quotes, often focusing on governance, long-term direction, or shareholder value. **Note date range.**)*
*   **Quote 1:** "..." (Source: Specific source citation)
*   **Quote 2:** "..." (Source: Specific source citation)
*   **Quote 3:** "..." (Source: Specific source citation)
    *(Provide at least three strategically relevant quotes if available.)*

### [Other Key Executive Name], [Title - e.g., CFO, CSO, CTO - Specify Name & Title] (Optional, include ONLY if highly relevant strategic quotes are found)
*   *(Brief 1-2 sentence summary of key themes relevant to their function's strategic contribution. **Note date range.**)*
*   **Quote 1:** "..." (Source: Specific source citation)
*   **Quote 2:** "..." (Source: Specific source citation)
    *(Provide 2-3 highly relevant quotes if found, focusing on financial strategy, tech strategy, market strategy etc. directly from them. Otherwise, omit this sub-section.)*

**Note on Quote Selection:** Quotes MUST be **verbatim** and focus on **strategic** topics: direction, future plans, priorities, growth initiatives, market outlook, vision, response to major challenges/opportunities. Avoid purely operational or backward-looking descriptive quotes unless they have clear strategic context.

**Source Attribution:** A specific, verifiable source must be cited *immediately* adjacent to/following *each individual quote* using parentheses `(Source: ...)`. Be precise (Report name/date/page, Transcript date/section, Interview source/date).

## 2. General Discussion:
*   Provide concluding **single paragraph** (approx. **300-500 words**).
*   **Synthesize** the key strategic messages and priorities presented *solely* through the collected quotes from leadership.
*   **Analyze** recurring themes, the overall strategic tone (e.g., confident, cautious, transformative), any apparent consistency or potential divergence in messaging between leaders (if multiple leaders quoted), and how the articulated vision/strategy relates to broader understanding of the company and its market context (drawing *only* from info within this quote section).
*   Offer insights relevant to the **Japanese audience** regarding leadership's focus, strategic intent, and communication style. **Do not introduce new factual claims.**

Source and Accuracy Requirements:
*   **Accuracy:** Quotes must be verbatim and correctly attributed to the speaker and source. Ensure speaker roles/titles are current as of the quote date, or note if they have changed.
*   **Source Specificity (Traceability):** Every individual quote MUST have its specific source cited immediately adjacent using parentheses `(Source: ...)`. Ensure traceability via the final source list annotations.
*   **Source Quality:** Prioritize official company sources: Letters to Shareholders in Annual/Integrated Reports, transcripts/recordings of Earnings Calls or Investor Days, official speeches published by the company, strategic sections of the corporate website, relevant official press releases announcing strategy. Use reliable third-party interviews (e.g., from major financial news outlets) sparingly and cite clearly.

{final_source_instructions}

{formatting_instructions}
"""

# --- End of Prompt Generating Functions ---