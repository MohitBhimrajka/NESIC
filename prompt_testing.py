#prompt-testing.py

import textwrap

# REVISED Standardized Final Source List instructions block (v3 - New Hyperlink Format)
# REVISED Standardized Final Source List instructions block (v4 - Enhanced Grounding Integrity)
FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE = textwrap.dedent("""\
    **Final Source List Requirements:**

    Conclude the *entire* research output, following the 'General Discussion' paragraph, with a clearly marked section titled "**Sources**". This section is critical for verifying the information grounding process.

    **1. Content - MANDATORY URL Type & Source Integrity:**
    *   **Exclusive Source Type:** This list **MUST** contain *only* the specific grounding redirect URLs provided directly by the **Vertex AI Search system** *for this specific query*. These URLs represent the direct grounding evidence used.
    *   **URL Pattern:** These URLs typically follow the pattern: `https://vertexaisearch.cloud.google.com/grounding-api-redirect/...`. **Only URLs matching this exact pattern are permitted.**
    *   **Strict Filtering:** Absolutely **DO NOT** include any other type of URL (direct website links, news, PDFs, etc.).
    *   **CRITICAL - No Hallucination:** **Under NO circumstances should you invent, fabricate, infer, or reuse `vertexaisearch.cloud.google.com/...` URLs** from previous queries or general knowledge if they were not explicitly provided as grounding results *for the current query*. If a fact was identified but lacks a corresponding *provided* Vertex AI grounding URL, it cannot be sourced here and likely should not be included in the report (see Point 4).
    *   **Purpose:** This list verifies the specific grounding data provided *by Vertex AI Search for this request*, not external knowledge or other URLs.

    **2. Formatting and Annotation:**
    *   **Source Line Format:** Present each source on a new line using the following Markdown hyperlink format, immediately followed by its annotation:
        *   Format: `[Supervity Source X](Full_Vertex_AI_Grounding_URL) - Annotation text explaining supported information.`
        *   Example: `[Supervity Source 1](https://vertexaisearch.cloud.google.com/grounding-api-redirect/EXAMPLE_URL_1...) - Supports CEO name and headquarters address details in Section 1.`
    *   **Sequential Labeling:** The visible hyperlink text **MUST** be labeled sequentially "Supervity Source 1", "Supervity Source 2", etc.
    *   **Annotation Requirement:** The annotation **MUST** be:
        *   Included immediately after the hyperlink on the same line, separated by " - ".
        *   Brief and specific, explaining *exactly* what information in the main body that *specific* grounding URL supports.
        *   Written in the target output language: **{language}**.

    **3. Quantity and Linkage:**
    *   **Target Quantity:** Aim for a minimum of 5 and a maximum of 18 *distinct, verifiable* Vertex AI grounding URLs that directly support content in the report.
    *   **Accuracy Over Quantity:** However, the **absolute requirement is accuracy and adherence to the grounding rules (Points 1 & 4)**. If, after exhaustive research and following the omission rules (Point 4), fewer than 5 *verifiable* grounding URLs supporting included report content can be found in the provided results, list only those that *are* verifiable. **Do NOT invent sources to meet the minimum count.**
    *   **Fact Linkage:** Every Vertex AI grounding URL listed **MUST** directly correspond to grounding data used for specific facts/figures/statements *present* in the final report body.

    **4. Content Selection Based on Verifiable Grounding:**
    *   **Prerequisite for Inclusion:** Information (facts, figures, details, quotes) should only be included in the main report body *if* it can be supported by a **verifiable Vertex AI grounding URL provided in the search results for this query**.
    *   **Omission of Ungrounded Facts:** If a specific piece of information is found or known but lacks a direct, verifiable Vertex AI grounding URL *from the current results*, **omit that specific fact, detail, or data point** from the report.
    *   **Omission of Ungrounded Sections:** If the *core subject matter* of an entire requested section (e.g., "Crisis Management") cannot be substantiated by *any* relevant information backed by verifiable Vertex AI grounding URLs from the current results, **omit that entire section** (including its heading) from the final output. Adhere strictly to the `HANDLING_MISSING_INFO_INSTRUCTION`.

    **5. Final Check:**
    *   Before concluding the entire response, perform a final review of the "Sources" list AND the main report body. Ensure **strict adherence** to all rules, especially:
        *   Exclusive use of valid, *provided* Vertex AI grounding URLs in the "Sources" list.
        *   Correct hyperlink format in the "Sources" list.
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

# REVISED Standardized Research Depth & Calculation instruction block
RESEARCH_DEPTH_INSTRUCTION = textwrap.dedent("""\
    *   **Research Depth & Source Prioritization:**
        *   **Exhaustive Search:** Conduct **thorough and exhaustive research** for *all* requested information points.
        *   **Primary Source Focus:** Prioritize information retrieval from **official company sources**. This includes, but is not limited to:
            *   Latest Annual Reports / Integrated Reports
            *   Official Financial Statements (Income Statement, Balance Sheet, Cash Flow) & Footnotes
            *   Supplementary Financial Data Packs
            *   Official Filings (e.g., EDINET, SEC filings like 10-K/20-F)
            *   Investor Relations (IR) Presentations & Materials (including Mid-Term Plans)
            *   Earnings Call Transcripts & Presentations
            *   Official Corporate Website (especially "About Us", "Investor Relations", "Strategy", "Governance" sections)
            *   Official Press Releases detailing strategy, financials, or structure.
        *   **Recency:** Focus primarily on the **most recent available data and reporting periods** unless a specific historical range is requested.
        *   **Secondary Sources:** Use high-quality, reputable secondary sources (e.g., major industry reports, leading financial news outlets) *sparingly*, mainly for context (like market share estimates) or verification if official sources are ambiguous or unavailable for a specific point. Always clearly attribute secondary sources.
    *   **Calculation Guidelines:**
        *   **Permitted Calculations:** Where specific metrics (e.g., financial ratios like margins, ROE, ROA, Debt-to-Equity) are requested but not explicitly stated in sources, you **MAY calculate them** *only if* the necessary base data components (e.g., Net Income, Revenue, Equity, Assets, Debt) are **clearly available and verifiable** within the prioritized official sources.
        *   **State Method:** If a calculation is performed, **clearly state the formula used** within the report body, adjacent to the calculated value (e.g., "Operating Margin (Calculated: Operating Income / Revenue): XX.X%").
        *   **Verify Components:** Ensure the base data used for calculations is accurately sourced and consistent (e.g., same reporting period, same currency).
    *   **Confirmation of Unavailability:** Only conclude that information is unavailable after demonstrating a diligent search across *multiple relevant primary sources* as listed above. Refer to `HANDLING_MISSING_INFO_INSTRUCTION` for how to proceed if information remains unverified.
    """)

# Standardized Output Language instruction block (as defined previously)
def get_language_instruction(language: str) -> str:
    return f"Output Language: The final research output must be presented entirely in **{language}**."

# REVISED Standardized Formatting instruction block (Base Version - v2)
BASE_FORMATTING_INSTRUCTIONS = textwrap.dedent("""\
    Output Format & Quality Requirements:

    *   **Direct Start & No Conversational Text:** Begin the response *directly* with the first requested section (e.g., Section 1 or the first named heading). **Absolutely NO introductory phrases** (e.g., "Here is the report...", "Based on the search results...") or **concluding remarks** (e.g., "I hope this helps...", "Let me know..."). The output MUST contain *only* the structured research content, the General Discussion, and the final Sources list.

    *   **Valid and Consistent Markdown:**
        *   Structure the entire output using **syntactically correct and well-formed Markdown**.
        *   Use Markdown elements appropriately: `##` for main sections, `###` for sub-sections, `*` or `-` for bullet points, `**text**` for bolding.
        *   Ensure consistent list indentation and properly formatted code blocks (```) if used.
        *   Pay close attention to **table formatting**: Ensure correct header rows, separator lines (`|---|---|`), and consistent column counts in data rows. Use pipes `|` correctly to delimit cells.
        *   Verify that all Markdown links (especially in the Sources section) are correctly formatted.

    *   **Optimal Structure & Readability:**
        *   Present information using the most effective format for clarity. Adhere to the following guidelines:
            *   **Use Tables for:** Multi-year numerical data comparisons (e.g., financials), lists of personnel (Board, Execs), lists of subsidiaries, direct side-by-side competitor comparisons.
            *   **Use Bullet Points for:** Lists of features, advantages, initiatives, qualitative factors, non-comparative lists.
            *   **Use Paragraphs for:** Narrative descriptions, analysis, summaries, context.
        *   Maintain clear visual separation between all main sections, the General Discussion, and the final Sources list (e.g., using appropriate heading levels and spacing).

    *   **Data Formatting Consistency:**
        *   Ensure consistent formatting for numbers (use appropriate thousands separators for the target language: **{language}**).
        *   **CRITICAL - Currency Specification:** *Always* specify the currency symbol/code (e.g., ¥, $, €, JPY, USD) for **ALL** monetary values mentioned throughout the *entire* report. Place symbols consistently (e.g., before or after the number based on common practice for the currency/language).
        *   Format dates consistently (e.g., YYYY-MM-DD or local standard).

    *   **Tone and Detail Level:**
        *   Maintain a professional, objective, and analytical tone suitable for a **Japanese corporate strategy audience**.
        *   Provide granular detail where specifically requested (e.g., financial figures, names, dates).
        *   Be concise in descriptive text unless detailed analysis or explanation is explicitly required by the prompt section. Avoid unnecessary jargon or overly promotional language.

    *   **Completeness and Verification:**
        *   Ensure the *entire* requested output is generated according to the specific prompt's structure. Verify that all numbered/headed sections, the General Discussion, and the final Sources list are present and fully addressed.
        *   **Do not submit partial, unfinished, or truncated responses.** If generation limits are reached, stop cleanly *before* starting an incomplete section or the Sources list.
        *   Internally review the final output against these formatting instructions and the specific prompt requirements before concluding generation.
    """)


def get_basic_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for a comprehensive basic company profile with all enhancements."""
    language_instruction = get_language_instruction(language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    return f"""
Comprehensive Corporate Profile, Strategic Overview, and Organizational Analysis of {company_name}

Objective: To compile a detailed and accurate corporate profile, strategic overview, organizational structure analysis, and key personnel identification for {company_name}, focusing solely on this specific entity. Avoid detailed analysis of parent or subsidiary companies, except for listing subsidiaries as requested.

Target Audience Context: The final research output is intended for review, strategic understanding, and planning purposes by a **Japanese company**. Please ensure the information is presented clearly, accurately, granularly, and is relevant to a business audience seeking deep insights into {company_name}.

{language_instruction}

Research Requirements:
Please conduct in-depth research, primarily utilizing {company_name}'s official website (especially Corporate Governance, About Us, Investor Relations sections), Annual Reports, Integrated Reports, official filings, and press releases. Supplement with high-quality secondary sources only for verification or specific data points like market share if not found in primary sources. Ensure all factual claims, data points, structural descriptions, personnel details, responsibilities, and quotes in the sections below are supported by specific, verifiable sources referenced back to the final source list.
{HANDLING_MISSING_INFO_INSTRUCTION}
{RESEARCH_DEPTH_INSTRUCTION} # Basic version, emphasis on official sources

1.  **Core Corporate Information:**
    *   Stock Ticker Symbol / Security Code (if publicly traded)
    *   Primary Industry Classification (e.g., GICS, SIC, or local standard)
    *   Full Name and Title of the current Chief Executive Officer (CEO)
    *   Full Registered Headquarters Address
    *   Main Corporate Telephone Number
    *   Official Corporate Website URL
    *   Date of Establishment/Incorporation
    *   Date of Initial Public Offering (IPO)/Listing (if applicable)
    *   Primary Stock Exchange/Market where listed (if applicable)
    *   Most Recently Reported Official Capital Figure **(Specify currency and reporting date/period)**
    *   Most Recently Reported Total Number of Employees **(Specify reporting date/period)**

2.  **Recent Business Overview:**
    *   Provide a detailed summary of {company_name}'s core business operations and primary revenue streams based on the *most recent* official reports.
    *   Include key highlights of recent business performance or significant operational developments.

3.  **Business Environment Analysis:**
    *   Describe the current market environment: major competitors (list names), general market dynamics (growth trends, consolidation), estimated market size/share (if available, cite source/date).
    *   Identify and explain key industry trends (technological shifts, regulatory changes, consumer behavior).
    *   ***Discuss the potential strategic implications of these trends specifically for {company_name}.***

4.  **Organizational Structure Overview:**
    *   Briefly describe the high-level organizational structure (divisional, matrix, business units) if clearly stated in official sources.

5.  **Key Management Personnel & Responsibilities:**
    *   **Board of Directors:** List members, titles, specific responsibilities/committee memberships.
    *   **Corporate Auditors / Audit & Supervisory Board Members:** List members, titles, role/focus area.
    *   **Executive Officers:** List members, titles, precise area(s) of operational responsibility. ***Note any recent significant changes (within the last year) in key executive roles, if reported.***

6.  **Subsidiaries List:**
    *   List direct subsidiaries (global where applicable), based on official documentation.

7.  **Leadership Strategic Outlook (Verbatim Quotes):**
    *   **CEO & Chairman:** Provide at least four (4) direct quotes on strategy/plans/growth/outlook. Include brief summary noting themes and approx. date range of quotes.
    *   **CMO, CBO, CSO, other Sr. Execs/Board:** Provide at least three (3) direct quotes *each* on strategy relevant to their roles. Include brief summary noting themes and approx. date range of quotes. *(Substitute if specific role quotes unavailable)*.
    *   **Source Attribution:** Clearly cite the specific source next to *each* quote.

8.  **General Discussion:**
    *   Provide a concluding **single paragraph** (approx. **300-500 words**).
    *   Synthesize Sections 1-7. Discuss coherence between profile, market position, structure, leadership roles, and articulated strategy. Offer holistic overview analyzing strengths, challenges, strategic posture relevant to the Japanese audience. Focus on analysis/connections. **Do not introduce new factual claims.**

Source and Accuracy Requirements:
*   **Accuracy:** Info in Sections 1-7 must be factually correct, current, verified. Ensure currency specified for monetary values.
*   **Source Specificity (In-line):** Every claim/data point/detail/quote in Sections 1-7 must be traceable to a specific source in the final list (cite report/page, URL section, date).
*   **Source Quality:** Mandatory primary reliance on official company sources. Use secondary sources sparingly for verification/specific data (e.g., market share), citing clearly.

{final_source_instructions}

{BASE_FORMATTING_INSTRUCTIONS}
"""

def get_financial_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for a detailed financial analysis with all enhancements."""
    language_instruction = get_language_instruction(language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    # Custom formatting for finance prompt
    finance_formatting_instructions = textwrap.dedent("""\
    Output Format:
    *   **Direct Start & No Conversational Text:** Begin the response *directly* with the requested information (starting with Section 1). **Crucially, do not include any introductory phrases** (e.g., "Here is the analysis...") **or concluding remarks** (e.g., "Let me know if you need more...") in the final output. The response must contain *only* the requested research content, the General Discussion, and the Sources list.
    *   **Markdown Format:** Structure the entire output using Markdown formatting (## Headings, ### Sub-headings, *, **bold**).
    *   **Optimal Structure:** Present information using the most effective format. **Tables are encouraged** for presenting multi-year financial data comparisons (e.g., Key Financial Metrics, Segment Performance). Use bullet points and paragraphs for analysis and descriptions.
    *   **Section Separation:** Ensure clear visual separation between all main sections, the General Discussion, and the final Sources list.
    """)

    # Enhanced instructions for financial research depth and calculation
    enhanced_financial_research_instructions = textwrap.dedent("""\
    *   **Mandatory Deep Search & Calculation:** Conduct an **exhaustive search** within {company_name}'s official financial disclosures for the last 3 fiscal years, including **Annual Reports, Financial Statements (Income Statement, Balance Sheet, Cash Flow Statement), Footnotes, Supplementary Data, official Filings (e.g., EDINET/SEC), and Investor Relations presentations.** Do not rely solely on summary tables; examine detailed statements and notes.
    *   **Calculation Obligation:** For metrics like Margins, ROE, ROA, Equity Ratio, Debt-to-Equity, and ROIC: if the metric itself is not explicitly reported, you **MUST attempt to calculate it** using standard financial formulas **IF the necessary base data components** (e.g., Net Income, Revenue, Total Equity, Total Assets, Total Debt, Operating Income, Invested Capital proxies) **are available** within the verified, sourced official documents. Clearly state the formula used for any calculated metric.
    *   **Strict Omission Policy (Reiteration):** Apply the 'Handling Missing Information' rule rigorously. If a specific metric or data point cannot be found directly reported after exhaustive search, AND it cannot be reliably calculated from the available sourced base data, **omit that specific line item or metric entirely**. **Under no circumstances state 'N/A', 'Not Found', or use placeholders.** Focus on presenting only the verifiable and calculable information.
    """)

    return f"""
Comprehensive Strategic Financial Analysis of {company_name} (Last 3 Fiscal Years)

Objective: Deliver a complete and analytically rich financial profile of **{company_name}**, based on the most recent **three full fiscal years**, combining traditional metrics with cost structure, investment activity, cash flow, and contextual factors. Focus exclusively on **{company_name} as a standalone entity**.

Target Audience Context: The report is designed for a **Japanese corporate strategy audience**. Output must reflect precision, relevance, and professionalism. Use Japanese terminology (e.g., "Ordinary Income") if appropriate for the output language and available in sources.

{language_instruction}

Research Requirements:
For each section below, provide data and analysis covering the **last three full fiscal years**. Information must be **verifiable**, **clearly sourced** (traceable to final list), and **analytically explained** regarding trends.
{HANDLING_MISSING_INFO_INSTRUCTION}
{enhanced_financial_research_instructions} # Use enhanced instructions here

1.  **Top Shareholders:** List major shareholders, ownership %, specify data date/period end. Use verifiable filings/databases.

2.  **Key Financial Metrics (3-Year Trend):** *(Exhaustively search & calculate where feasible. Omit if unfindable AND uncalculable. Specify currency and reporting period for all monetary values)*
    *   Total Revenue
    *   Net Sales (if separate)
    *   Gross Profit *(Calculate: Revenue - COGS if needed)*
    *   Gross Profit Margin (%) *(Calculate: Gross Profit / Revenue)*
    *   EBITDA *(Search diligently; calculate if components like Operating Income, D&A are clearly available)*
    *   EBITDA Margin (%) *(Calculate: EBITDA / Revenue)*
    *   Operating Income / Operating Profit
    *   Operating Margin (%) *(Calculate: Operating Income / Revenue)*
    *   Ordinary Income / Pre-Tax Income
    *   Ordinary Income Margin (%) *(Calculate: Ordinary Income / Revenue)*
    *   Net Income (Attributable to Owners)
    *   Net Income Margin (%) *(Calculate: Net Income / Revenue)*
    *   Return on Equity (ROE) (%) *(Calculate: Net Income / Average Shareholders' Equity)*
    *   Return on Assets (ROA) (%) *(Calculate: Net Income / Average Total Assets)*
    *   Total Assets
    *   Total Shareholders' Equity
    *   Equity Ratio / Capital Adequacy Ratio (%) *(Calculate: Total Equity / Total Assets)*
    *   Key Debt Metrics (e.g., Total Debt, Debt-to-Equity Ratio *(Calculate: Total Debt / Total Equity)*)
    *   Key Cash Flow Figures (Operations, Investing, Financing) **(Specify currency)**

3.  **Profitability Analysis (3-Year Trend):** *(Calculate YoY % Change where data is available for consecutive years)*
    *   Operating Margin (%) with **Year-over-Year % Change**
    *   Net Income Margin (%) with **Year-over-Year % Change**

4.  **Segment-Level Performance (if applicable & reported, 3-Year Trend):** Revenue **(Specify currency)**, Operating Profit **(Specify currency)**, Margins (%) by Business/Geographic Segment. Analyze trends/drivers/challenges. *(Omit if segment data not disclosed)*

5.  **Cost Structure Analysis (3-Year Trend):** SG&A breakdown **(Specify currency)** (detail R&D, Personnel, Marketing if available). Cost ratios (SG&A/Rev, COGS/Rev, R&D/Rev). Analyze trends/drivers.

6.  **Cash Flow Statement Analysis (3-Year Trend):** Analyze Operating CF trends/drivers. Detail Investing CF (CapEx, M&A values **(Specify currency)**). Detail Financing CF (dividends, debt, equity values **(Specify currency)**). Comment on Free Cash Flow generation/usage *(FCF = Op CF - CapEx)*.

7.  **Investment Activities (Last 3 Years):** Major M&A (targets, values **(Specify currency)**). CapEx (figures **(Specify currency)**, purposes). CVC investments. ROIC trend *(Search; calculate if Operating Income after tax and Invested Capital can be reliably determined from Balance Sheet/Notes. State method/components used for Invested Capital.)*

8.  **Contextual Financial Factors:** Significant one-time events (e.g., impairments, legal costs **(Specify currency if applicable)**). Relevant accounting standard changes. Economic/regulatory factors cited by management. ***Analyze the quality and sustainability of reported earnings (e.g., reliance on one-offs, core profit consistency).***

9.  **Credit Ratings & Financial Health (if available & reported):** Current/historical ratings (JCR, R&I, Moody's, S&P). Agency commentary highlights. *(Omit if not publicly rated or ratings unavailable)*

General Discussion:
*   Provide a concluding **single paragraph** (approx. **300–500 words**).
*   Synthesize findings on financial health, trends, investments, cash flow, context *based only on the data presented*. Assess financial management effectiveness. Discuss strengths, risks, trajectory. Tailor insights for Japanese audience. **Do not introduce new factual claims.**

Source and Accuracy Requirements:
*   **Accuracy:** Data/ratios/context must be correct, verified. **Crucially, specify the currency for ALL monetary values presented.**
*   **Source Specificity (In-line):** Every data point/ratio/calculation/insight must be traceable to a specific source in the final list (cite report/page, filing date, transcript section). State if a metric was calculated.
*   **Source Quality:** Mandatory primary reliance on official company sources (Reports, Statements, Footnotes, Filings, IR Presentations, Transcripts, Press Releases).

{final_source_instructions}

{finance_formatting_instructions}
"""


def get_competitive_landscape_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for a detailed competitive analysis with nuanced grounding rules."""
    language_instruction = get_language_instruction(language)
    # Use the STRICT global final source instructions for the list itself
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    comp_formatting_instructions = textwrap.dedent("""\
    Output Format:
    *   Direct Start & No Conversational Text: Begin directly with "## Major Competitors...". No intro/outro.
    *   Markdown Format: Use ##, ###, *, **bold**, and well-formatted tables where appropriate (e.g., competitor summary).
    *   Optimal Structure: Use tables for competitor profiles/market share, bullets/paragraphs for analysis.
    *   Section Separation: Clear separation between sections, General Discussion, and Sources.
    """)

    # --- Special Research Instructions for Competitive Analysis ---
    competitive_research_instructions = textwrap.dedent("""\
    **Research & Grounding Strategy for Competitive Analysis:**

    1.  **Prioritize Grounded Facts:** Conduct exhaustive research using the Vertex AI Search tool. Give **highest priority** to including facts, figures (like market share if reported directly), and competitor details that are **directly supported by provided `vertexaisearch.cloud.google.com/...` grounding URLs**. List these URLs accurately in the final "Sources" section as per the main instructions.

    2.  **Handling Synthesis and Secondary Information:** Competitive analysis often requires synthesis or information from sources not directly grounded via a Vertex AI redirect URL in the results.
        *   **Permitted Inclusion:** You MAY include:
            *   **Synthesized analysis:** Conclusions drawn logically from *multiple* grounded facts (state this basis, e.g., "Analysis based on trends reported in Source 1 and Source 3").
            *   **Widely reported data:** Market share estimates or competitor information commonly cited in reputable business news or major industry reports, *even if* a specific Vertex AI grounding URL isn't provided *for that exact point in this query's results*.
        *   **Mandatory In-Text Citation:** If including synthesized analysis or information from secondary sources not directly grounded by a *provided* Vertex AI URL, you **MUST clearly indicate this in the text** next to the information (e.g., "Source: [Name of News Outlet/Report], [Date]" or "Based on synthesis of provided grounding data"). This information *cannot* be listed in the final "Sources" list (which is reserved for the provided Vertex AI URLs).

    3.  **Omission Rule (Modified):** Apply the `HANDLING_MISSING_INFO_INSTRUCTION` strictly for *factual claims* expected to have direct grounding (e.g., specific product names, official announcements). For *analytical points* (positioning, weaknesses, synthesized trends) or *widely reported secondary data* (market share estimates), use the approach in Point 2. If even this synthesized/secondary information is unavailable after diligent search, *then* omit the specific point or sub-section.

    4.  **Focus on Verifiable:** Aim for accuracy. If competitor details are highly speculative or cannot be reasonably verified through reliable primary or secondary means, omit them.

    5.  **Final Source List Integrity:** Remember, the final "Sources" list at the very end MUST still adhere strictly to the `FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE` (only *provided* Vertex AI grounding URLs). The allowance in Point 2 applies only to the *content within the report body* and requires clear in-text attribution for non-Vertex-grounded info.
    """)
    # --- End Special Instructions ---


    # Incorporate the new research instructions into the prompt string
    return f"""
Detailed Competitive Analysis and Strategic Overview of {company_name}

Objective: To conduct a detailed competitive analysis of **{company_name}**, identifying major competitors, evaluating competitive positioning, detailing advantages/weaknesses, and outlining competitive strategy, concluding with a synthesized discussion. Focus primarily on **{company_name}**.

Target Audience Context: Output is for strategic review by a **Japanese company**. Ensure analysis is thorough, insightful, clearly presented, with discussion providing cohesive overview of the competitive landscape.

{language_instruction}

{HANDLING_MISSING_INFO_INSTRUCTION.format(language=language)} # Include general missing info rule for context

{competitive_research_instructions} # Add the specific competitive research strategy

## Major Competitors Identification & Profiling:
*   Identify primary competitors in key markets/segments (Prioritize those mentioned in grounded sources).
*   For *each* major competitor (provide available information, clearly indicating source type if not directly Vertex-grounded as per instructions):
    *   Full Name & brief description of relevant operations.
    *   Estimated/Reported Market Share (Cite source/date clearly, specify if estimate or from secondary source).
    *   Key Geographic Areas of direct competition.
    *   Specific competing Products/Services.
    *   Notable recent Competitive Moves/Strategic Shifts (Cite source).
    *   Analysis of Relative Market Positioning (vs. {company_name} on price, quality, innovation, brand - state basis for analysis).
    *   ***Known or perceived strategic weaknesses (Attribute source/basis clearly, e.g., "Analyst reports suggest...", "Based on lower market share reported by [Source]...").***

## {company_name}'s Competitive Advantages & Positioning:
*   Detail key sources of competitive advantage (prioritize grounded examples, cite source/basis): USP, Tech/Patents, Brand, Loyalty, Scale, Cost, Distribution.
*   Provide balanced assessment of perceived competitive Strengths and Weaknesses relative to key competitors (state basis for assessment).

## {company_name}'s Competitive Strategy:
*   Describe apparent strategic approach (based on grounded statements or reliable analysis, cite source/basis): How it aims to maintain/defend position, expand, respond to threats, exploit weaknesses, adapt.
*   ***Describe the company's primary value discipline (operational excellence, customer intimacy, product leadership) based on observable strategy and actions (state basis).***
*   Identify specific initiatives/programs/investments enhancing competitive position (prioritize grounded info).
*   Describe how competitive success is measured (if stated in grounded sources).

## General Discussion:
*   Provide a concluding **single paragraph** (approx. **300-500 words**).
*   Synthesize findings (Competitors, Advantages/Positioning, Strategy) *based only on the information presented in the report*. Offer holistic overview discussing overall standing, direction, strengths, challenges, outlook. Focus on analysis relevant to Japanese audience. **Do not introduce new factual claims.**

Source and Accuracy Requirements:
*   **Accuracy:** Information must be factually correct or clearly attributed as analysis/estimate.
*   **Source Specificity (In-line):** Follow rules in `competitive_research_instructions` for citing grounded vs. synthesized/secondary info within the text.
*   **Source Quality:** Use Vertex AI grounding results first. Supplement with official disclosures, reputable industry reports, major institutional/consultancy analyses, credible business news where necessary and allowed by the special instructions.

{final_source_instructions} # Strict rules apply ONLY to this final list

{comp_formatting_instructions}
"""

def get_management_strategy_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for analyzing management strategy with all enhancements."""
    language_instruction = get_language_instruction(language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    # Custom formatting for strategy prompt
    strat_formatting_instructions = textwrap.dedent("""\
    Output Format:
    *   **Direct Start & No Conversational Text:** Begin the response *directly* with the requested information (starting with Section 1). **Crucially, do not include any introductory phrases** or **concluding remarks** in the final output. The response must contain *only* the requested research content, the General Discussion, and the Sources list.
    *   **Markdown Format:** Structure the entire output using Markdown formatting (## Headings, ### Sub-headings, *, **bold**).
    *   **Optimal Structure:** Present information using the most effective format. **Tables may be suitable** for listing MTP targets, KPIs, and tracking progress. Use bullet points and paragraphs for strategy descriptions and analysis.
    *   **Section Separation:** Ensure clear visual separation between all main sections, the General Discussion, and the final Sources list.
    """)

    return f"""
Comprehensive Analysis of {company_name}'s Management Strategy and Mid-Term Business Plan: Focus, Execution, and Progress

Objective: To conduct an extensive and detailed analysis of **{company_name}'s** overall management strategy, its current mid-term business plan (MTP), execution status, progress tracking, challenges, and strategic adjustments. Focus on **{company_name}**.

Target Audience Context: Output is for detailed strategic review by a **Japanese company**. Ensure analysis is granular, clearly presented, provides deep, actionable insights into strategic framework, operationalization, performance, adaptability.

{language_instruction}

Research Requirements:
Conduct in-depth research, prioritizing official sources (IR materials on MTP, Reports, Website strategy sections, Earnings calls, Investor days, Announcements). Supplement sparingly. Ensure all claims regarding strategy, MTP elements, execution, etc., are supported by specific, verifiable sources referenced back to the final list.
{HANDLING_MISSING_INFO_INSTRUCTION}
{RESEARCH_DEPTH_INSTRUCTION} # General depth instruction

1.  **Management Strategy and Vision Alignment:**
    *   Outline overall management strategy and alignment with long-term Vision.
    *   Explain core management philosophy/values/approach.
    *   Identify key strategic pillars/priorities for current horizon.
    *   Describe significant shifts from previous strategies.

2.  **Current Mid-Term Business Plan Overview:**
    *   Identify official name and time period (e.g., "FY2024-FY2026 MTP").
    *   Detail main objectives, quantitative targets (financial **(Specify currency)** / non-financial), KPIs.
    *   Discuss key differences from preceding MTP.

3.  **Strategic Focus Areas and Initiatives within the MTP:**
    *   For each major strategic theme/focus area:
        *   Detail Background and Objectives (Why priority?).
        *   Describe relevant Business Context/Market Conditions.
        *   Explain connection to Industry Trends.
        *   List Specific Initiatives/projects/actions (investments **(Specify currency if applicable)**, expansion, R&D, operations, organization). ***If available, state the primary source of funding allocated to major initiatives (e.g., operating cash flow, specific debt issuance, equity).***
        *   Explain how initiatives support strategic pillars (Sec 1).
        *   Provide Implementation Timelines/key milestones if available.

4.  **Execution, Progress, and Adaptation of the MTP:**
    *   Identify Key Issues, Challenges, Risks (internal/external) acknowledged/evident.
    *   Detail Specific Measures/countermeasures stated by company.
    *   Provide Latest Available Progress Updates (official statements on achievements/status).
    *   Include specific data showing Performance Versus Targets for key metrics/KPIs (specify period, **specify currency for financial targets**).
    *   Highlight any Strategic Adjustments/pivots/changes announced and stated reasons. ***Explicitly mention if management commentary links specific external events (e.g., major economic shifts, unexpected competitive actions, regulatory changes) to deviations from the plan or strategic adjustments made.***

5.  **General Discussion:**
    *   Provide a concluding **single paragraph** (approx. **300-500 words**).
    *   Synthesize findings (strategy, MTP specifics, execution, challenges, adaptations). Discuss coherence between vision, strategy, MTP actions. Analyze alignment with market context. Assess plan ambition, execution effectiveness, responsiveness, likelihood of achieving objectives. Highlight successes/difficulties. Focus on strategic takeaways relevant to Japanese audience. **Do not introduce new factual claims.**

Source and Accuracy Requirements:
*   **Accuracy:** All info must be factually correct, accurately reflect official communications. **Ensure currency specified for all monetary targets/values.**
*   **Source Specificity (In-line):** Every claim in Sections 1-4 must be traceable to a specific source in the final list (cite MTP presentation slide #, report page, transcript section, press release date).
*   **Source Quality:** Strongly prioritize official company sources (MTP docs, earnings materials, Reports, Investor Day materials, website strategy sections, relevant press releases).

{final_source_instructions}

{strat_formatting_instructions}
"""

def get_regulatory_prompt(company_name:str, language: str = "Japanese"):
    """Generates a prompt for analyzing the DX regulatory environment with all enhancements."""
    language_instruction = get_language_instruction(language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    return f'''
In-Depth Analysis of the Regulatory Environment and Compliance for {company_name}'s Digital Transformation

Objective: To conduct an in-depth analysis of the regulatory environment impacting **{company_name}'s** Digital Transformation (DX) initiatives and the company's approach to compliance, particularly concerning data and cybersecurity. Focus primarily on **{company_name}'s** own situation.

Target Audience Context: The final research output is intended for strategic review by a **Japanese company**. Please ensure the analysis is thorough, insightful, and presented clearly, focusing on understanding how regulatory landscapes shape digital strategy and risk management.

{language_instruction}

Research Requirements:
Conduct deep research on {company_name}'s operating environment related to its DX journey. Look for specifics on applicable regulations, compliance approaches, and context from reliable sources. Ensure all factual claims, regulatory descriptions, and company approaches below are supported by specific, verifiable sources referenced back to the final list.
{HANDLING_MISSING_INFO_INSTRUCTION}
*   **Research Depth:** Thoroughly search official company disclosures (compliance sections, risk factors in reports) and relevant government/regulatory body publications for details on applicable rules and stated compliance practices.

## Regulatory Environment and Compliance:
*   Describe key regulatory environment aspects and policy trends impacting {company_name}'s DX (data privacy laws like GDPR/CCPA/APPI, cybersecurity mandates, AI governance, sector-specific digital rules).
*   Identify major regulations applicable in key geographies.
*   Explain influence on choices (data handling, cloud, AI dev, cyber measures).
*   Provide info on {company_name}'s stated general compliance approach.
    *   Detail stated policies/strategies (esp. data privacy, cybersecurity).
    *   Mention publicly discussed compliance frameworks/certifications (ISO 27001, SOC 2).
    *   Describe integration into DX project planning/execution (if available).
*   ***Identify any known significant regulatory enforcement actions, fines, or investigations related to data privacy, cybersecurity, or digital practices levied against {company_name} within the last 3-5 years, if publicly reported. (Specify fines in currency if reported).***

## General Discussion:
*   Provide a concluding **single paragraph** (approx. **300-500 words**).
*   Synthesize findings on regulatory pressures on DX and compliance approach. Offer holistic assessment of how regulations shape digital strategy/risk posture. Discuss apparent maturity/proactiveness of compliance efforts based *only* on findings related to regulations, stated approaches, and enforcement actions (if any). Tailor perspective for Japanese audience on navigating complex regulations during DX. **Do not introduce new factual claims.**

Source and Accuracy Requirements:
*   **Accuracy:** All information must be factually correct, verified.
*   **Source Specificity (In-line):** Every claim/detail/description must be traceable to a specific source in the final list.
*   **Source Quality:** Prioritize official company disclosures (Reports, Compliance statements), official government/regulatory publications, reputable legal/consulting reports, credible news analyses on regulatory impacts.

{final_source_instructions}

{BASE_FORMATTING_INSTRUCTIONS}
'''

def get_crisis_prompt(company_name:str, language: str = "Japanese"):
    """Generates a prompt for analyzing digital crisis management with all enhancements."""
    language_instruction = get_language_instruction(language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    return f'''
In-Depth Analysis of {company_name}'s Digital Crisis Management and Business Continuity

Objective: To conduct an in-depth analysis of **{company_name}'s** approach to managing crises related to its digital systems or data, including stated crisis management and business continuity strategies. Focus primarily on **{company_name}'s** experiences and plans.

Target Audience Context: Output is for strategic review by a **Japanese company**. Ensure analysis is thorough, insightful, clearly presented, focusing on understanding digital risk management, incident response, resilience.

{language_instruction}

Research Requirements:
Conduct deep research on {company_name}'s experiences/approach to digital crises. Look for specifics on past incidents (if public), response mechanisms, preparedness strategies from reliable sources. Ensure all claims/descriptions below are supported by specific, verifiable sources referenced back to the final list.
{HANDLING_MISSING_INFO_INSTRUCTION}
*   **Research Depth:** Diligently search credible news archives, cybersecurity incident databases (where applicable), and official company disclosures (press releases, report sections on risk/incidents) for information on past events and stated plans. Acknowledge that details may not be public.

## Crisis Management and Business Continuity:
*   Based on public info (news, statements, databases), describe how **{company_name}** managed/resolved significant digital crises **last 5 years** (if applicable and publicly reported).
    *   Detail specific incidents (cyberattacks, outages, data breaches). Include dates, nature, reported impact **(Specify financial impact currency if reported)** if available.
    *   Describe public response/actions (communication, remediation, reporting). ***Mention any publicly stated 'lessons learned' or changes implemented by the company as a direct result of these incidents.***
*   Detail stated approach to technology-related **crisis management** / digital resilience.
    *   Describe mentioned frameworks/plans (Incident Response Plan, Cyber Crisis Management Plan).
*   Outline stated strategy for **business continuity planning** (BCP) specific to digital systems/infrastructure disruptions.
*   Mention described roles/responsibilities/governance for digital crises (if public).

## General Discussion:
*   Provide a concluding **single paragraph** (approx. **300-500 words**).
*   Synthesize findings on crisis experience (if any), stated crisis management/BCP approach, and lessons learned. Offer holistic assessment of apparent preparedness/resilience based *only* on findings related to incidents, strategies, and stated adaptations. Discuss perceived strengths/weaknesses. Tailor perspective for Japanese audience on digital risk mitigation, response effectiveness, resilience. **Do not introduce new factual claims.**

Source and Accuracy Requirements:
*   **Accuracy:** Information must be correct, verified. Incident details rely on credible reports. Specify currency for any reported financial impacts.
*   **Source Specificity (In-line):** Every claim/incident detail/strategic description must be traceable to a specific source in the final list.
*   **Source Quality:** Prioritize official statements/disclosures on incidents/risk management, reputable news reports, cybersecurity research firm reports, official docs on BCP/crisis management.

{final_source_instructions}

{BASE_FORMATTING_INSTRUCTIONS}
'''

def get_digital_transformation_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for analyzing DX strategy with all enhancements."""
    language_instruction = get_language_instruction(language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    # Custom formatting for DX prompt
    dx_formatting_instructions = textwrap.dedent("""\
    Output Format:
    *   **Direct Start & No Conversational Text:** Begin the response *directly* with the requested information (starting with Section 1). **Crucially, do not include any introductory phrases** or **concluding remarks** in the final output. The response must contain *only* the requested research content, the General Discussion, and the Sources list.
    *   **Markdown Format:** Structure the entire output using Markdown formatting (## Headings, ### Sub-headings, *, **bold**).
    *   **Optimal Structure:** Present information using the most effective format. **Tables may be suitable** for summarizing DX investment breakdowns or case study outcomes. Use bullet points and paragraphs for strategy descriptions and analysis.
    *   **Section Separation:** Ensure clear visual separation between all main sections, the General Discussion, and the final Sources list.
    """)

    return f"""
In-Depth Analysis of {company_name}'s Digital Transformation Strategy and Execution

Objective: To conduct an in-depth analysis of **{company_name}'s** Digital Transformation (DX) strategy, investments, implementation examples, and related regulatory/crisis management environment. Focus primarily on **{company_name}'s** own initiatives.

Target Audience Context: Output is for strategic review by a **Japanese company**. Ensure analysis is thorough, insightful, clearly presented, focusing on understanding digital strategy execution, investment patterns, risk management.

{language_instruction}

Research Requirements:
Conduct deep research on {company_name}'s DX journey. Look for specifics on strategy, financial commitments, outcomes, context from reliable sources. Ensure all claims/data/descriptions below are supported by specific, verifiable sources referenced back to the final list.
{HANDLING_MISSING_INFO_INSTRUCTION}
{RESEARCH_DEPTH_INSTRUCTION} # General depth instruction

1.  **DX Strategy Overview:**
    *   Outline stated overall vision/approach to DX (Core goals?).
    *   Identify key strategic priorities (cloud, data, AI, automation, cyber).
    *   List major specific DX initiatives/projects/programs (underway/planned, brief descriptions).

2.  **DX Investments Analysis (Last 3 Fiscal Years, where available):**
    *   Use bullets/table for DX investment allocation by major activity/initiative area (Cloud, AI, Data, CRM, Automation).
        *   Describe focus within each area.
        *   Provide specific investment amounts/budgets *if public* **(Specify currency and reporting period)**. ***Specify the primary source of funding for major DX investments, if mentioned (e.g., dedicated budget, reallocation, operating cash flow).***
        *   Note available info on timelines/schedules.
        *   Mention approx. allocation % if reported.
        *   Summarize stated Expected ROI, KPIs, anticipated business impacts.
    *   Describe overall trend in DX investment levels over 3 years (cite data).

3.  **DX Case Studies & Implementation Examples:**
    *   Provide detailed descriptions of specific, successful DX implementation examples within {company_name}.
    *   For each case study: Describe initiative/tech, objectives, specific measurable outcomes/value delivered (cost savings % **(Specify currency if applicable)**, efficiency gains %, CSAT improvement, new revenue **(Specify currency)**; cite sources). ***If context available, explain why these examples might be highlighted by the company (e.g., showcase capability, address pain point, demo ROI).***

4.  **Regulatory Environment, Compliance, and Crisis Management (Related to DX):**
    *   *(Focused summary based on other prompts, viewed through DX lens)*
    *   Briefly summarize key regulatory trends impacting DX.
    *   Briefly describe stated approach to compliance (esp. data/cyber) within DX efforts.
    *   Briefly mention approach to managing digital crises from DX initiatives.

5.  **General Discussion:**
    *   Provide concluding **single paragraph** (approx. **300-500 words**).
    *   Synthesize findings (DX strategy, investment, execution, regulatory/risk influence). Offer holistic assessment of maturity, focus, effectiveness. Discuss strengths, challenges, shifts. Tailor perspective for Japanese audience on DX execution/management. **Do not introduce new factual claims.**

Source and Accuracy Requirements:
*   **Accuracy:** Information must be correct, verified. **Specify currency for all monetary values (investments, outcomes).**
*   **Source Specificity (In-line):** Every claim/data point/description/case study detail must be traceable to a specific source in the final list.
*   **Source Quality:** Prioritize official disclosures (Reports, IR, ESG, DX docs, press releases), reputable tech research firm reports (cite specific report), credible tech/business news analyses.

{final_source_instructions}

{dx_formatting_instructions}
"""

def get_business_structure_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for analyzing business structure with all enhancements."""
    language_instruction = get_language_instruction(language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    # Custom formatting for business structure prompt
    struct_formatting_instructions = textwrap.dedent("""\
    Output Format:
    *   **Direct Start & No Conversational Text:** Begin the response *directly* with the requested information (starting with Section 1). **Crucially, do not include any introductory phrases** or **concluding remarks** in the final output. The response must contain *only* the requested research content, the General Discussion, and the Sources list.
    *   **Markdown Format:** Structure the entire output using Markdown formatting (## Headings, ### Sub-headings, *, **bold**).
    *   **Optimal Structure:** Present information using the most effective format. **Tables are encouraged** for presenting multi-year segment sales data or the list of major shareholders. Use bullet points and paragraphs for analysis and descriptions.
    *   **Section Separation:** Ensure clear visual separation between all main sections, the General Discussion, and the final Sources list.
    """)

    return f"""
In-Depth Analysis of {company_name}'s Business Structure, Geographic Footprint, Ownership, and Strategic Vision

Objective: Conduct an **analytical review** of **{company_name}'s** operational structure (business/geographic segments), ownership (shareholders), and future direction (leadership commentary). Focus on trends, interconnections, strategic implications. Use consolidated figures primarily.

Target Audience Context: Output is for strategic assessment by a **Japanese company**. Provide clear insights into revenue drivers, market focus, ownership influences, strategic priorities, relevant for benchmarking/partnership evaluation.

{language_instruction}

Research Requirements:
Conduct **critical analysis** interrogating official IR materials, Reports, filings. Supplement sparingly for verification (e.g., shareholders). Ensure all claims/figures/analyses/quotes below are supported by specific, verifiable sources referenced back to the final list.
{HANDLING_MISSING_INFO_INSTRUCTION}
{RESEARCH_DEPTH_INSTRUCTION} # General depth instruction

1.  **Business Segment Analysis (Last 3 Fiscal Years):**
    *   List reported business segments.
    *   For each: Concise Description of Core Ops/Products/Services; Consolidated Sales **(Specify currency & period)** (3 yrs); Composition Ratio (% Total Sales) (3 yrs).
    *   **Analyze significant trends** (growth, margins, share shifts). *Explain potential drivers* (sourced mgmt commentary/market context).

2.  **Geographic Segment Analysis (Last 3 Fiscal Years):**
    *   List reported geographic segments.
    *   For each significant segment: Consolidated Sales **(Specify currency & period)** (3 yrs); Composition Ratio (% Total Sales) (3 yrs).
    *   **Analyze significant trends**. Highlight regions of growth/decline/importance, explaining *why* (sourced info: market maturity, M&A, investments).

3.  **Major Shareholders & Ownership Structure:**
    *   List **Top 10 major shareholders** (*most recent* data).
    *   For each: Full name, Approx. # Shares Held, Approx. % Shares Outstanding, Type (Institutional, Corp, Fund, Indiv - if possible), Specify exact date/source doc ref.
    *   ***Note if any known 'activist' shareholders are currently involved and briefly summarize their publicly stated objectives/demands, if applicable.***
    *   **Briefly comment** on overall ownership nature (concentrated/dispersed, strategic investors) and potential implications.

4.  **Leadership Strategic Outlook & Vision (Verbatim Quotes):**
    *   Provide direct, **verbatim quotes** from current CEO/Chairman/key C-suite addressing: Long-term vision/priorities; Future growth plans (initiatives, markets, investments); Perspectives on key opportunities/challenges.
    *   Ensure specific **source and context** (report/page, interview/date, slide#, call date) documented *for each quote*.
    *   Where possible, **explicitly link quotes** to analyzed segments, geographic focus, market trends.

5.  **General Discussion:**
    *   Provide concluding **single paragraph** (approx. **300-500 words**).
    *   **Critically synthesize** findings from *all* sections. **Interlink** analysis of segments, geography, ownership, leadership strategy. **Evaluate coherence** between performance, ownership, direction. Discuss strengths, vulnerabilities, strategic questions. Tailor for Japanese audience. **Do not introduce new factual claims.**

Source and Accuracy Requirements:
*   **Accuracy:** Info must be correct, current, verified. **State currency clearly for ALL segment sales figures.**
*   **Source Specificity (In-line):** Every claim/data/quote/analysis in Sections 1-4 must be traceable to a *precise* source in the final list (cite report/page, filing/date, URL section).
*   **Source Quality:** Mandatory primary reliance on official company sources (Reports, Filings, IR presentations, Press Releases, Official communication transcripts). Use high-caliber secondary sources only as supplementary clarification.

{final_source_instructions}

{struct_formatting_instructions}
"""

def get_vision_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt focused on company vision with all enhancements."""
    language_instruction = get_language_instruction(language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    # Custom formatting for vision prompt
    vision_formatting_instructions = textwrap.dedent("""\
    Output Format:
    *   **Direct Start & No Conversational Text:** Begin the response *directly* with the requested information (starting with Section 1). **Crucially, do not include any introductory phrases** or **concluding remarks** in the final output. The response must contain *only* the requested research content, the General Discussion, and the Sources list.
    *   **Markdown Format:** Structure the entire output using Markdown formatting (## Headings, *, **bold**).
    *   **Optimal Structure:** Present information using the most effective format for clarity (likely bullet points and paragraphs). Tables are permitted if useful (e.g., listing KPIs).
    *   **Section Separation:** Ensure clear visual separation between the main section, the General Discussion, and the final Sources list.
    """)

    return f"""
Analysis of {company_name}'s Strategic Vision

Objective: To provide a detailed overview of **{company_name}'s** stated strategic vision, including its core components (pillars/outline) and associated measures/KPIs for tracking progress. Focus solely on **{company_name}**.

Target Audience Context: Output is for strategic review by a **Japanese company**. Ensure information on vision/components is presented clearly, accurately, sourced from official materials.

{language_instruction}

Research Requirements:
Conduct in-depth research, primarily using official website (Strategy, About Us, IR), Reports (Annual, Integrated), MTP docs, official filings/press releases detailing strategy. Ensure claims regarding vision/components/measures below are supported by specific, verifiable sources referenced back to the final list.
{HANDLING_MISSING_INFO_INSTRUCTION}
*   **Research Depth:** Diligently search across various official strategic documents (Vision statements, MTPs, ESG reports, IR presentations) for the required elements.

1.  **Company Vision and Strategy Elements:**
    *   Outline **{company_name}'s** officially stated **Vision Overview** or core mission statement (verbatim if possible).
    *   Describe key **components, pillars, or strategic themes** of the strategic **Vision Outline** or long-term plan.
    *   Identify specific **Vision Measures, Key Performance Indicators (KPIs)**, or concrete initiatives used/announced to track progress towards vision/goals **(Specify currency for any financial KPIs)**.
    *   ***Identify if the vision explicitly addresses key stakeholder groups (e.g., customers, employees, shareholders, society, environment) and how.***

2.  **General Discussion:**
    *   Provide concluding **single paragraph** (approx. **300-500 words**).
    *   Synthesize findings (vision, components/pillars, measures, stakeholder focus). Discuss clarity, ambition, coherence of vision. Analyze how well measures track progress towards pillars. Offer insights relevant to Japanese audience regarding strategic direction implied by vision. **Do not introduce new factual claims.**

Source and Accuracy Requirements:
*   **Accuracy:** Info (statements, pillars, measures) must be correct, current, verified via official sources. **Specify currency for any financial KPIs.**
*   **Source Specificity (In-line):** Every claim in Section 1 must be traceable to a *precise* source in the final list (cite report/page, MTP doc/page, URL section).
*   **Source Quality:** Mandatory primary reliance on official company sources (Website strategy/about pages, Reports, Governance Reports, official strategy docs, MTP presentations, relevant press releases).

{final_source_instructions}

{vision_formatting_instructions}
"""

def get_management_message_prompt(company_name: str, language: str = "Japanese"):
    """Generates a prompt for collecting strategic quotes with all enhancements."""
    language_instruction = get_language_instruction(language)
    final_source_instructions = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    # Custom formatting for quotes prompt
    quote_formatting_instructions = textwrap.dedent("""\
    Output Format:
    *   **Direct Start & No Conversational Text:** Begin the response *directly* with the requested information (starting with "Leadership Strategic Outlook..."). **Crucially, do not include any introductory phrases** or **concluding remarks** in the final output. The response must contain *only* the requested quotes, the General Discussion, and the Sources list.
    *   **Markdown Format:** Structure output using Markdown. Use ## for main headings. Use ### for leader sub-headings. Use bullet points (*) for individual quotes AND their specific sources. Use **bold** for emphasis.
    *   **Optimal Structure:** Present clearly under each leader's subheading. List the brief summary first, then bulleted quotes each immediately followed by its specific source citation. Tables are not expected.
    *   **Section Separation:** Ensure clear visual separation between the main quotes section, General Discussion, and final Sources list.
    """)

    return f"""
Detailed Leadership Strategic Outlook (Verbatim Quotes) for {company_name}

Objective: To compile a detailed collection of direct, verbatim quotes from **{company_name}'s** senior leadership (CEO, Chairman, CMO, CBO, CSO, other key execs/board) articulating strategic direction, future plans, growth initiatives, forward-looking perspective. Focus solely on **{company_name}**.

Target Audience Context: Output is for strategic review by a **Japanese company**. Ensure quotes/context are clear, accurately reflect stated views, relevant for insights into strategic intent.

{language_instruction}

Research Requirements:
Conduct focused research to locate/extract direct, verbatim quotes based on criteria below. Prioritize official sources. Ensure quotes accurately transcribed/attributed with specific sources referenced back to final list.
{HANDLING_MISSING_INFO_INSTRUCTION} # Applies if specific roles or sufficient quotes cannot be found despite diligent search.
*   **Research Depth:** Diligently search diverse official sources (transcripts of earnings calls/investor days, interviews published by the company, letters in Annual/Integrated Reports, official speeches, relevant press releases) for strategic statements from specified leaders. Focus on recent (last 1-2 years) quotes.

## Leadership Strategic Outlook (Verbatim Quotes):

### [CEO Name], CEO (and/or [Chairman Name], Chairman)
*   *(Brief 1-2 sentence summary of key themes from CEO/Chairman quotes. **Note the approximate date range of these quotes.**)*
*   "Quote 1..." (Source: Specific source citation)
*   "Quote 2..." (Source: Specific source citation)
*   "Quote 3..." (Source: Specific source citation)
*   "Quote 4..." (Source: Specific source citation)
    *(Provide at least four quotes total)*

### [Executive Name], [Title - e.g., CMO, CBO, CSO, or other Sr. Exec/Board Member]
*   *(Brief 1-2 sentence summary of key themes from this executive's quotes. **Note the approximate date range of these quotes.**)*
*   "Quote 1..." (Source: Specific source citation)
*   "Quote 2..." (Source: Specific source citation)
*   "Quote 3..." (Source: Specific source citation)
    *(Provide at least three quotes. Repeat structure for other specified roles or relevant senior leaders. Substitute if specific role quotes unavailable, clearly identifying name/title.)*

**Note on Quote Selection:** Quotes must address strategic direction, future plans, growth initiatives, vision, or forward-looking perspectives.

**Source Attribution:** Specific source must be cited *immediately* adjacent to/following *each individual quote*.

## General Discussion:
*   Provide concluding **single paragraph** (approx. **300-500 words**).
*   Synthesize findings presented *solely* through collected quotes. Discuss recurring themes, priorities, tone, consistency/divergence across leaders. Analyze how articulated vision/strategy relates to broader understanding of company/market. Offer insights relevant to Japanese audience. **Do not introduce new factual claims.**

Source and Accuracy Requirements:
*   **Accuracy:** Quotes verbatim, correctly attributed. Speaker roles current.
*   **Source Specificity (In-line):** Every individual quote must have specific source cited immediately adjacent.
*   **Source Quality:** Prioritize official company sources (Reports, Press Releases, Transcripts, Website content, Speeches). Use reliable third-party interviews sparingly.

{final_source_instructions}

{quote_formatting_instructions}
"""