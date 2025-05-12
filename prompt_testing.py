# prompt_testing.py

import textwrap
from typing import Optional

# --- Standard Instruction Blocks ---
# (Updated with placeholders for formatting)

# --- Enhanced NESIC Capabilities Block ---
NESIC_CAPABILITIES_CONTEXT = textwrap.dedent("""\
    **NESIC Capabilities & Strategic Context (Reference for Analysis):**

    *   **Core Business Domains (What We Do):**
        *   **Digital Transformation (DX) Enablement:** Partnering with clients from strategic DX consulting and roadmap design through to complex implementation and ongoing optimization, focusing on solving core business challenges and driving innovation.
        *   **Advanced System Integration (SI):** Expertise in architecting, building, testing, and integrating sophisticated, mission-critical IT systems, ensuring seamless operation within complex multi-vendor environments. Focus on reliability and future-readiness.
        *   **Next-Generation Network Solutions:** Designing, deploying, securing, and managing robust network infrastructures (LAN, WAN, Wireless, 5G/Local 5G, SD-WAN). Delivering high-performance, secure connectivity for both enterprise and carrier-grade requirements.
        *   **Comprehensive Cybersecurity Services:** Providing end-to-end security solutions: strategic consulting, risk/vulnerability assessments, advanced Security Operations Center (SOC) services, Managed Security Service Provider (MSSP) offerings, threat detection/response, and compliance support.
        *   **Strategic Cloud Services:** Enabling multi-cloud adoption (AWS, Azure, GCP, OCI+) through expert migration planning and execution, secure cloud infrastructure management, performance/cost optimization, and hybrid/private cloud integration.
        *   **Intelligent Managed Services & BPO:** Delivering high-quality IT infrastructure operation, 24/7 proactive monitoring & management, service desk support, and IT-related Business Process Outsourcing to enhance client operational efficiency, reduce TCO, and ensure service continuity.
        *   **Modern Collaboration & Communication Platforms:** Implementing and managing unified communications (UC), advanced video conferencing systems, AI-enhanced contact center solutions, and digital workplace tools to boost productivity and user experience.
        *   **Applied IoT & Data Analytics:** Designing and implementing IoT solutions for data collection/integration, providing data visualization and analytics services, often leveraging advanced AI/ML capabilities from the NEC Group to unlock business insights.
        *   **Converged Physical Security & Facility Management:** Integrating IT infrastructure with physical security systems (biometrics, surveillance, access control) and smart building/facility management solutions for enhanced safety and efficiency.

    *   **NESIC's Core Value Proposition & Strategic Approach (How We Succeed):**
        *   **Co-Creation Partnership:** We prioritize understanding client challenges deeply and collaborating closely to design and deliver the *optimal* solution, acting as a long-term strategic partner.
        *   **Leveraging NEC Group Strengths:** We uniquely integrate cutting-edge technologies (AI, biometrics, 5G/6G R&D, advanced analytics) and the broad solution portfolio of the NEC Corporation to deliver innovative and differentiated outcomes.
        *   **Ensuring Mission-Critical Reliability:** Decades of proven experience delivering and managing large-scale, complex systems for demanding clients, ensuring operational stability and resilience.
        *   **End-to-End Service Lifecycle:** Providing comprehensive support across the entire lifecycle, from initial consultation and design to implementation, management, and continuous improvement.
        *   **Vendor-Agnostic Integration Expertise:** Skillfully integrating best-of-breed solutions from a wide range of technology partners while ensuring interoperability and avoiding vendor lock-in where appropriate.

    *   **Key Differentiators (Why Choose NESIC):**
        *   **NEC Group Technology Access:** Unique ability to incorporate world-class NEC R&D and specialized technologies.
        *   **Proven SI Track Record:** Unmatched experience in delivering complex, large-scale projects within the Japanese market.
        *   **Deep Networking & Security DNA:** Core technical leadership and heritage in designing and securing critical networks.
        *   **Nationwide Delivery & Support:** Robust, skilled service infrastructure across Japan for reliable installation, maintenance, and operational support.
        *   **Client-Centric Flexibility:** Combining structured methodologies with the agility to tailor solutions and engagement models to specific client needs.

    *   **Primary Target Segments:** Large Enterprises, Government Agencies & Public Sector Organizations, Telecommunications Carriers, Critical Social Infrastructure Providers.

    **(Note for AI Strategist:** Use this context to identify how NESIC's specific capabilities, approach, and differentiators can best address the target company's identified needs, challenges, and strategic initiatives from both web grounding and provided documents. Frame opportunities by highlighting NESIC's unique value.)
""")

# NEW Instruction Block for Document Handling
DOCUMENT_ANALYSIS_INSTRUCTION = textwrap.dedent("""\
    *   **CRITICAL: Analysis of Provided Documents (PDFs, PPTXs, etc.):**
        *   **Priority Source:** You **WILL BE PROVIDED** with relevant documents (e.g., internal presentations, past proposals, meeting notes, org charts). Treat these documents as a **PRIMARY and often MORE CURRENT/DETAILED source of context** than general web search results, especially regarding:
            *   Specific ongoing projects, initiatives, and timelines.
            *   Internal challenges, pain points, and stated needs.
            *   Detailed organizational structure, key personnel, and decision-making processes.
            *   Relationship history or past engagements between {company_name} and {context_company_name} (if mentioned).
            *   Specific figures, targets, or plans not yet publicly released.
        *   **Mandatory Integration:** Your analysis and the resulting Account Strategy **MUST** deeply integrate insights extracted directly from these provided documents. Do not rely solely on web grounding when relevant document information is available.
        *   **Information Extraction:** Diligently extract information from all parts of the documents:
            *   **Text:** Key strategies, statements, goals, challenges, personnel names/roles.
            *   **Tables:** Financial data, project timelines, KPI targets, organizational lists. Extract relevant data accurately.
            *   **Charts/Graphs:** Summarize the key trends, data points, or conclusions presented visually. Note the existence and location (e.g., "Chart on slide 15 shows X trend [DOC1, Slide 15]"). Do not attempt to recreate charts.
            *   **Images/Diagrams:** Interpret information conveyed (e.g., Org charts, process flows, infrastructure diagrams). Describe the key takeaways and note the location (e.g., "Org chart on p.3 indicates... [DOC2, p.3]").
        *   **Document Citation (MANDATORY & DISTINCT):**
            *   Cite information extracted *directly* from provided documents using the format `[DOCX, reference]`, where 'X' is the document number (if multiple are provided, assume DOC1 if only one) and 'reference' is the specific page number, slide number, section header, or figure/table identifier (e.g., `[DOC1, p.5]`, `[DOC2, Slide 10]`, `[DOC1, Section 3.1]`).
            *   This `[DOCX]` citation is **distinct** from the `[SSX]` citation used for web grounding URLs. Use the appropriate citation type based on the information's origin.
        *   **Conflict Resolution:** If conflicting information exists between provided documents and web grounding results:
            *   Prioritize the **latest official provided document** for internal strategy, plans, and organizational details specific to {company_name}. Cite as `[DOCX]`.
            *   Prioritize the **latest verifiable public web grounding source** (`[SSX]`) for publicly stated facts (e.g., official revenue figures, CEO name).
            *   If a significant conflict exists that impacts the strategy, briefly note it in the analysis (e.g., "Document [DOC1, p. 8] outlines Plan A, while recent press release [SS3] mentions Plan B adjustment.").
        *   **Multi-lingual Documents:** Be prepared to process documents in Japanese or English. Extract relevant information regardless of source language and present the final analysis in the target output language: **{language}**.
        *   **Silent Omission:** If specific information requested cannot be verified *either* through web grounding (`[SSX]`) *or* within the provided documents (`[DOCX]`) after exhaustive review, omit it silently per the standard handling instructions.
    """)

ADDITIONAL_REFINED_INSTRUCTIONS = textwrap.dedent("""\
    **Additional Refined Instructions for Zero Hallucination, Perfect Markdown, and Strict Single-Entity Coverage:**

    *   **Mandatory Self-Check Before Final Output:**
        - Before producing the final answer, confirm:
            1. All requested sections are fully included with correct headings.
            2. All factual statements have inline citations [SSX] pointing to valid Vertex AI URLs in the final Sources list.
            3. Only the permitted Vertex AI grounding URLs are used—no external or fabricated links.
            4. Markdown headings and tables follow the specified format (##, ###, consistent columns, **strict pipe alignment**). Ensure data within tables is accurate against the source.
            5. A single "Sources" section is present, properly labeled, and each source is on its own line.
            6. Inline citations appear before punctuation where feasible.
            7. No data or sources are invented. If information is omitted due to lack of verifiable grounding after exhaustive search, this is done silently without comment.
            8.  **Strict Single-Entity Focus:** Strictly reference only the **exact** company named: **'{company_name}'** (with identifiers like Ticker: '{ticker}', Industry: '{industry}' if provided). **Crucially verify** you are NOT including data from similarly named but unrelated entities (e.g., if the target is 'Marvell Technology, Inc.', absolutely DO NOT include 'Marvel Entertainment' or data related to comics/movies). Confirm if data relates to the parent/consolidated entity or a specific subsidiary, and report accordingly based ONLY on the source [SSX].
            9. Verify recency of all primary sources used (AR, MTP, website data, etc.).
            10. Confirm key financial figures and table data points against cited sources. **Verify specifically that all financial data has valid [SSX] citations linked to provided grounding URLs.**
            11. Ensure lists (KPIs, Officers, Subsidiaries) are complete based on source availability.
            12. Confirm analytical depth provided where requested (explaining 'why' and drivers).

    *   **Exactness of Table Columns:**
        - Each row in any table **MUST** have the exact same number of columns as the header row, delimited by pipes (`|`).
        - Use exactly one pipe (`|`) at the beginning and end of each row.
        - Ensure header separator lines (`|---|---|`) match the number of columns precisely.
        - If data for a specific cell is missing *in the source* after exhaustive search, use a simple hyphen (-) as a placeholder *only if necessary* to maintain table structure and alignment. Do not add explanatory text.
        - Always include an inline citation [SSX] if referencing factual numbers within a table cell or in a note below the table referencing the table's data. Verify the cited data matches the source.

    *   **Quotes with Inline Citations:**
        - Any verbatim quote must include:
            1. The speaker's name and date or document reference in parentheses.
            2. An inline citation [SSX] immediately following.
        - This ensures clarity on who said it, when they said it, and the exact source.

    *   **Exactness of Hyperlinks in Sources:**
        - The final "Sources" section must use the format "* [Supervity Source X](Full_Vertex_AI_Grounding_URL) - Brief annotation [SSX]."
        - Number sources sequentially without skipping.
        - Provide no additional domain expansions or transformations beyond what is given.
        - Do not summarize entire documents—only note which facts the source supports.

    *   **Do Not Summarize Sources:**
        - In each source annotation, reference only the specific claim(s) the link supports, not a broad summary.

    *   **High-Priority Checklist (Must Not Be Violated):**
        1. No fabrication: Silently omit rather than invent ungrounded data after exhaustive search.
        2. Adhere strictly to the specified Markdown formats (headings, lists, **perfect tables**).
        3. Use inline citations [SSX] matching final sources exactly.
        4. Provide only one "Sources" section at the end.
        5. Do not use any URLs outside "vertexaisearch.cloud.google.com/..." pattern if not explicitly provided.
        6.  **Enforce Single-Entity Coverage (CRITICAL):** If '{company_name}' is the focus, DO NOT include other similarly named but unrelated entities. Verify target entity identity throughout.
        7. Complete an internal self-check (see above) to ensure compliance with all instructions before concluding.
""")

FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE = textwrap.dedent("""\
    **Final Source List Requirements:**

    Conclude the *entire* research output, following the 'General Discussion' paragraph, with a clearly marked section titled "**Sources**". This section is critical for verifying the information grounding process AND for document generation.

    **1. Content - MANDATORY URL Type & Source Integrity:**
    *   **Exclusive Source Type:** This list **MUST** contain *only* the specific grounding redirect URLs provided directly by the **Vertex AI Search system** *for this specific query*. These URLs represent the direct grounding evidence used.
    *   **URL Pattern:** These URLs typically follow the pattern: `https://vertexaisearch.cloud.google.com/grounding-api-redirect/...`. **Only URLs matching this exact pattern are permitted.**
    *   **Strict Filtering:** Absolutely **DO NOT** include any other type of URL (direct website links, news, PDFs found elsewhere, etc.).
    *   # NEW: Explicitly exclude DOCX citations from this list
        **Document citations (`[DOCX, reference]`) MUST NOT be included in this final "Sources" list.** Those citations are handled inline only, referencing the provided documents directly. This list is exclusively for the `[SSX]` web grounding URLs.
    *   **CRITICAL - No Hallucination:** **Under NO circumstances should you invent, fabricate, infer, or reuse `vertexaisearch.cloud.google.com/...` URLs** from previous queries or general knowledge if they were not explicitly provided as grounding results *for this query*. If a fact is identified but lacks a corresponding provided grounding URL after exhaustive search, it must be silently omitted from the report body AND no source should be listed for it.
    *   **Purpose:** This list verifies the specific web grounding data provided by Vertex AI Search for this request—not external knowledge, other URLs, or provided documents.

    **2. Formatting and Annotation (CRITICAL FOR PARSING):**
    *   **Source Line Format:** Present each source on a completely new line. Each line **MUST** start with a Markdown list indicator (`* ` or `- `) followed by the hyperlink in Markdown format and then its annotation.
    *   **REQUIRED Format:**
        * [Supervity Source X](Full_Vertex_AI_Grounding_URL) - Annotation explaining exactly what information is supported (e.g., supports CEO details and FY2023 revenue [SSX]).
    *   **Sequential Labeling:** The visible hyperlink text **MUST** be labeled sequentially "Supervity Source 1", "Supervity Source 2", etc. Do not skip numbers.
    *   **Annotation Requirement:** The annotation MUST be:
        * Included immediately after the hyperlink on the same line, separated by " - ".
        * Brief and specific, explaining exactly which piece(s) of information in the main body (and referenced with inline citation [SSX]) that grounding URL supports.
        * Written in the target output language: **{language}**.

    **3. Quantity and Linkage:**
    *   **List All Verifiable Used Sources:** List ***every distinct***, verifiable Vertex AI grounding URL provided for this specific query that directly supports content presented in the report body via an inline citation [SSX]. Do *not* include provided grounding URLs if they were not ultimately used to support any statement in the report.
    *   **Accuracy Over Quantity:** Accuracy and adherence to the grounding rules are absolute. If fewer verifiable URLs are available *and used* from the provided results after exhaustive search, list only those used.
    *   **Fact Linkage:** Every grounding URL listed MUST directly correspond to facts/figures/statements present in the report body referenced with the corresponding inline citation [SSX].

    **4. Content Selection Based on Verifiable Grounding:**
    *   **Prerequisite for Inclusion:** Only include facts, figures, details, or quotes in the main report if they can be supported by a verifiable Vertex AI grounding URL from this query `[SSX]` or are present in a provided document `[DOCX, reference]` after exhaustive search.
    *   **Omission of Ungrounded Facts/Sections:** If specific information cannot be supported by a verifiable grounding URL or found in provided documents after exhaustive search, silently omit that detail. If a whole section cannot be grounded/documented after exhaustive search, retain the section heading but omit the content.

    **5. Final Check:**
    *   Before concluding the response, review the entire output. Verify:
        * Exclusive use of valid, provided Vertex AI grounding URLs that support cited facts `[SSX]`.
        * Correct use of `[DOCX, reference]` for documented facts.
        * Each source in this list is on a new line and follows the correct format.
        * Every fact in the report body is supported by an appropriate inline citation (`[SSX]` or `[DOCX]`) that corresponds to a source in this list or a provided document.
        * Every source listed corresponds to at least one inline citation [SSX] in the report body.
    *   The "**Sources**" section must appear only once, at the end of the entire response.
    """)

HANDLING_MISSING_INFO_INSTRUCTION = textwrap.dedent("""\
    *   **Handling Missing or Ungrounded Information:**
        *   **Exhaustive Research First:** Conduct exhaustive research using primarily official company sources (see `RESEARCH_DEPTH_INSTRUCTION`). Search diligently across *multiple relevant primary sources* (e.g., latest AR, previous AR, Financial Statements + Footnotes, Supplementary Data Packs, Tanshin/Filings, MTP docs, IR presentations, Results Overviews, specific website sections, **checking alternate language versions of the website**) for *each data point* before concluding information is unavailable. Check document publication dates for recency.
        *   **Grounding Requirement for Inclusion:** Information is included only if:
            1. The information is located in a reliable source document (either provided or found via web search).
            2. For web-found information, a corresponding, verifiable Vertex AI grounding URL (matching the pattern `https://vertexaisearch.cloud.google.com/grounding-api-redirect/...`) is provided in the search results for this query.
            3. For provided document information, it is clearly present within the document.
        *   **Strict Silent Omission Policy:** If information cannot meet these conditions *after exhaustive research*, omit that specific fact, sentence, or data point entirely. Do **not** include statements like 'Data not found' or 'Information unavailable'. If an entire subsection lacks verifiable grounded/documented data, retain the heading but omit the content. If a table cell requires a placeholder for structure, use only `-` without explanation (verify data is missing *in the source*).
        *   **No Inference/Fabrication:** Do not infer, guess, or estimate ungrounded information. Do not fabricate grounding URLs.
        *   **Cross-Language Search:** If necessary, check other language results; if found, translate only the necessary information and cite the corresponding grounding URL `[SSX]` or document reference `[DOCX, reference]`.
    """)

RESEARCH_DEPTH_INSTRUCTION = textwrap.dedent("""\
    *   **Research Depth & Source Prioritization:**
        *   **Exhaustive Search & Recency:** Conduct thorough research for all requested information points. Dig beyond surface-level summaries. **MANDATORY: Prioritize and use the absolute *latest* available official sources.** Check document/website publication dates. Critically, cross-verify information across *multiple relevant primary sources* before accepting it.
        *   **Multi-Document Search Strategy:** For each key data point (e.g., specific financials, KPIs, management names, strategic initiatives), search across *different types* of official documents (e.g., Annual Report, Financial Statements + Footnotes, Supplementary Data/Databooks, Official Filings like Tanshin/EDINET/SEC, Investor Relations Presentations, Mid-Term Plans, Strategy Day materials, Earnings Call Transcripts & Presentations, official Corporate Website sections, specific Policy documents, official Press Releases).
        *   **Primary Source Focus (MANDATORY):** Use official company sources primarily, including:
            *   Latest Annual / Integrated Reports (and previous years *only* for trends/baselines)
            *   Official Financial Statements (Income Statement, Balance Sheet, Cash Flow) & **Crucially: Footnotes**
            *   Supplementary Financial Data, Investor Databooks, Official Filings (e.g., **Japanese Annual Security Reports / 有価証券報告書 (Yuho)**, Tanshin, EDINET, **SEC Form 20-F/10-K**, local equivalents) - **prioritize these definitive annual filings.**
            *   Investor Relations Presentations & Materials (including Mid-Term Plans, Strategy Day presentations)
            *   Earnings Call Transcripts & Presentations (focus on Q&A sections)
            *   Official Corporate Website sections (e.g., "About Us", "Investor Relations", "Strategy", "Governance", "Sustainability/ESG", "Management/Directors") - check for "last updated" dates.
            *   Official Press Releases detailing strategy, financials, organizational structure, or significant events.
        *   # NEW: Specific Annual Report Prioritization
            **CRITICAL: Prioritize full, official annual financial reports (e.g., Annual Security Report/有価証券報告書, Form 20-F/10-K, audited consolidated Financial Statements) over summary reports, preliminary results, or quarterly/half-year interim reports.** Only use interim reports if they are the *sole* source for essential recent data *and* acknowledge this limitation internally. Always seek the comprehensive year-end filing for the period requested.
        *   # NEW: Complex Website Navigation Awareness
            **Be aware that consumer-facing websites (e.g., `brand.com`) are often distinct from the Corporate / Investor Relations site (e.g., `brand-global.com/corp/`, `brand.com/ir/`). Navigate diligently:**
            *   Look for "Investor Relations (IR)", "Shareholders & Investors", "Company Information", or "Corporate" links, often in the site footer or main navigation.
            *   Within IR sections, common paths are: IR Home -> IR Library / Financial Information / Filings -> Annual Reports / SEC Filings / Financial Results / Security Reports (有価証券報告書).
            *   Search specifically for the document types mentioned above covering the required fiscal year (e.g., "FY2023 ended March 31, 2024").
        *   # NEW: Language/Regional Site Variation Handling
            **Check both Japanese and English versions of the corporate/IR website if necessary.** Content availability (especially specific report types like Security Reports vs. Financial Results summaries) and site structure can differ. If a key document is missing on one language site, check the other before concluding it's unavailable. Prioritize the most comprehensive/official version found.
        *   **Forbidden Sources:** Do NOT use:
            *   Wikipedia
            *   Generic blogs, forums, or social media posts
            *   Press release aggregation sites (unless linking directly to an official release)
            *   Outdated market reports (unless historical context is explicitly requested)
            *   Competitor websites/reports (except in competitive analysis with extreme caution and strict grounding rules)
            *   Generic news articles unless they report specific, verifiable events from highly reputable sources (e.g., Nikkei, Bloomberg, Reuters, FT, WSJ) AND can be **cross-verified against primary sources** and have grounding URLs.
        *   **Data Verification:** Cross-verify critical figures (e.g., revenue, profit, key KPIs, management names/titles) between sources where possible (e.g., AR summary vs. detailed financials vs. website).
        *   **Group Structure Handling:** Clearly identify if data refers to the consolidated parent group (**{company_name}**) or a specific target subsidiary mentioned *in the source*. If the prompt focuses on the parent, report consolidated data unless segment data is explicitly requested and available. If focusing on a subsidiary mentioned in the source, clearly label it. Actively search for subsidiary-specific sections, appendices, or footnotes within parent company reports. Acknowledge (internally for decision-making) potential data limitations for non-publicly listed subsidiaries. **Do not report on subsidiaries unless directly relevant to the parent's structure or segment reporting as per the source [SSX].**
        *   **Noting Charts/Figures:** If relevant visual information (org charts, strategy frameworks, process diagrams) is found in sources, note its existence and location (e.g., "An organizational chart is provided on page X of the 2023 Annual Report [SSX]"). Do not attempt to recreate complex visuals textually.
        *   **Management Commentary:** Actively incorporate direct management commentary and analysis from these sources to explain trends and rationale.
        *   **Recency:** Focus on the most recent 1-2 years for qualitative analysis; use the last 3 full fiscal years for financial trends. Clearly state the reporting period for all data.
        *   **Secondary Sources:** Use reputable secondary sources sparingly *only* for context (e.g., credit ratings, widely accepted industry trends) or verification, always with clear attribution **and cross-reference with primary sources and grounding URLs.**
        *   **Handling Conflicts:** If conflicting information is found between official sources, prioritize the most recent, definitive source. Note discrepancies with dual citations if significant (e.g., [SSX, SSY]).
        *   **Calculation Guidelines:** If metrics are not explicitly reported but must be calculated:
            *   Calculate only if all necessary base data (e.g., Net Income, Revenue, Equity, Assets, Debt) is available and verifiable from grounded sources.
            *   Clearly state the formula used, and if averages are used, mention that (e.g., "ROE (Calculated: Net Income / Average Shareholders' Equity)") [SSX]. **Cite the sources for all base data points used in the calculation.**
        *   **Confirmation of Unavailability (Internal):** Only conclude information is unavailable *internally* after a diligent, confirmed search across *multiple* relevant primary source *types* (including different website sections and language versions) fails to yield verifiable, grounded data. **Do not state this conclusion in the output.**
    """)

ANALYSIS_SYNTHESIS_INSTRUCTION = textwrap.dedent("""\
    *   **Analysis and Synthesis:**
        *   Beyond listing factual information, provide concise analysis where requested (e.g., explain trends, discuss implications, identify drivers, assess effectiveness).
        *   **Explicitly address "why":** For every data point or trend, explain *why* it is occurring or what the key drivers are, based on sourced information or management commentary [SSX]. Quantify trends (e.g., "Revenue increased by 12% YoY [SSX] due to...").
        *   **Comparative Analysis:** Compare data points (e.g., YoY changes, company performance against MTP targets or baseline values, segment performance differences) where appropriate and insightful, using sourced data [SSX]. Compare against industry benchmarks *only* if reliable, grounded benchmark data is available [SSY].
        *   **Linking Information:** In the General Discussion, explicitly tie together findings from different sections to present a coherent overall analysis (e.g., link financial performance [SSX] with strategic initiatives [SSY] and competitive pressures [SSZ]).
        *   **Causal Linkage:** Look for and report management commentary that explains causal relationships (e.g., "Management stated the increase in SG&A was driven by investment in X [SSX]").
        *   **DX Implications:** In summary/discussion sections, actively consider and mention potential Digital Transformation (DX) implications, opportunities, or challenges arising from the findings in other sections, citing the relevant data (e.g., "The stated need for supply chain efficiency [SSX] presents a clear opportunity for DX solutions like...")
    """)

INLINE_CITATION_INSTRUCTION = textwrap.dedent("""\
    *   **Inline Citation Requirement:**
        *   # MODIFIED: Mention dual citation types
            Every factual claim, data point (including figures in tables), direct quote, and specific summary **MUST** include an inline citation indicating its source. Use the format `[SSX]` for information derived from **verifiable web grounding URLs** provided by Vertex AI Search, where X corresponds exactly to the sequential number of the source in the final Sources list. Use the format `[DOCX, reference]` for information derived directly from **provided documents**, where X is the document number and 'reference' is the page/slide/section.
        *   Place the inline citation immediately after the supported statement and **before punctuation** when possible (e.g., "Revenue was ¥100B [SS1].", "The plan outlines three pillars [DOC1, p.5].").
        *   If a single sentence contains multiple distinct facts from different sources, cite each appropriately (e.g., "Revenue was ¥100B [SS1] and the internal target is ¥110B [DOC2, Slide 10].").
        *   If a single source (web or document) supports multiple facts within a paragraph or table, reuse the same citation.
        *   This ensures that each fact is directly verifiable against either the corresponding "Supervity Source X" in the final Sources list or the referenced provided document.
    """)

SPECIFICITY_INSTRUCTION = textwrap.dedent("""\
    *   **Specificity and Granularity:**
        *   For all time-sensitive data points (e.g., financials, employee counts, management changes, MTP periods, KPIs, targets), include specific dates or reporting periods (e.g., "as of 2024-03-31", "for FY2023 ended March 31, 2024", "MTP covers FY2024-FY2026").
        *   Define any industry-specific or company-specific terms or acronyms on their first use.
        *   Quantify qualitative descriptions with specific numbers or percentages where available (e.g., "significant growth of 12% YoY [SSX]").
        *   List concrete examples rather than vague categories when describing initiatives, strategies, or risks.
    """)

AUDIENCE_CONTEXT_REMINDER = textwrap.dedent("""\
    *   **Audience Relevance:** Keep the target audience (Japanese corporate strategy professionals) in mind. Frame analysis and the 'General Discussion' to highlight strategic implications, competitive positioning, market opportunities/risks, and operational insights relevant for potential partnership, investment, or competitive assessment. Use terminology common in Japanese business contexts where appropriate and natural for the {language}.
    """)

def get_language_instruction(language: str) -> str:
    return f"Output Language: The final research output must be presented entirely in **{language}**."

BASE_FORMATTING_INSTRUCTIONS = textwrap.dedent("""\
    Output Format & Quality Requirements:

    *   **Direct Start & No Conversational Text:** Begin the response directly with the first requested section heading (e.g., `## 1. Core Corporate Information`). No introductory or concluding remarks are allowed.

    *   **Strict Markdown Formatting Requirements:**
        *   Use valid and consistent Markdown throughout the entire document.
        *   **Section Formatting:** Sections MUST be numbered exactly as specified in the prompt (e.g., `## 1. Core Corporate Information`). Use `##` for main sections.
        *   **Subsection Formatting:** Use `###` for subsections and maintain hierarchical structure.
        *   **List Formatting:** Use asterisks (`*`) or hyphens (`-`) for bullets with consistent indentation (use 4 spaces for sub-bullets relative to the parent bullet).
        *   **Tables (CRITICAL FOR RENDERING):** Format all tables with *perfect* Markdown table syntax. Pay meticulous attention to:
            *   **Exact Column Count:** Every single row (header, separator, data) **MUST** have the *exact same number of columns* delimited by pipes (`|`).
            *   **Mandatory Start/End Pipes:** Every single row **MUST** begin with a pipe (`|`) and end with a pipe (`|`).
            *   **Header Separator Match:** The separator line (`|---|---|...`) **MUST** match the number of header columns exactly.
            *   **Alignment (Visual Aid):** While not strictly required by all parsers, using spaces within cells to visually align pipes in the raw Markdown source significantly helps prevent errors.
            *   **Table Data Integrity:** Every data point within a table cell MUST be verified against the cited source [SSX] for accuracy and correct reporting period.
            *   **Missing Data Placeholder:** If data for a specific cell is missing *in the source* after exhaustive search, use only a hyphen (`-`) as a placeholder if required for table structure. Do not add explanatory text.
            *   **Example of Perfect Table (Re-emphasized):**
                | Header 1        | Header 2      | Header 3          | Source(s) | <--- Ends with pipe
                |-----------------|---------------|-------------------|-----------| <--- Matches 4 columns, ends with pipe
                | Data Item 1     | 123.45        | Long text content | [SS1]     | <--- Matches 4 columns, ends with pipe
                | Another Item    | -             | More text here    | [SS2]     | <--- Matches 4 columns, ends with pipe
                | Final Item Data | 5,000 (JPY M) | Short text        | [SS1, SS3]| <--- Matches 4 columns, ends with pipe
            *   **Consequence of Error:** Even a single missing pipe or mismatched column count will likely cause the table to render incorrectly or not at all. Double-check every table before output.
        *   **Code Blocks:** Use triple backticks (```) for code blocks.
        *   **Quotes:** Use Markdown quote syntax (`>`) for direct quotations.

    *   **Optimal Structure & Readability:**
        *   Present numerical data in tables with proper alignment and headers. Right-align numbers where possible using spaces.
        *   Use bullet points for lists of items or characteristics.
        *   Use paragraphs for narrative descriptions and analysis.
        *   Maintain consistent formatting across similar elements.
        *   **Content Organization:** Ensure a logical sequence within each section (e.g., chronological for trends, priority for lists).
        *   **Conciseness:** Provide detailed yet concise language—be specific without unnecessary verbosity.
        *   **Quantitative Summaries:** Where summary paragraphs are requested (e.g., end of Basic Info, General Discussions), integrate key figures and quantitative trends from the analysis, not just qualitative descriptions.

    *   **Data Formatting Consistency:**
        *   Use appropriate thousands separators for numbers per the target language: **{language}**.
        *   **Currency Specification:** Always specify the currency (e.g., ¥, $, €, JPY, USD, EUR) for all monetary values along with the reporting period (e.g., "¥1,234 million for FY2023").
        *   Format dates consistently (e.g., YYYY-MM-DD or as commonly used in the target language for official reports).
        *   Use consistent percentage formatting (e.g., 12.5%).

    *   **Section Completion Verification:**
        *   Every section requested in the prompt MUST be included in the output.
        *   Sections must appear in the exact order specified.
        *   Each section must be properly labeled with the exact heading.
        *   If verifiable data for an entire subsection is missing after exhaustive research, omit the *content* of that subsection, but **retain the subsection heading** (e.g., `### Subsection Title`) to maintain the document's structure as requested by the prompt. Do not state that data is missing.

    *   **Tone and Detail Level:**
        *   Maintain a professional, objective, and analytical tone suited for a Japanese corporate strategy audience.
        *   Provide granular detail (e.g., figures, dates, metrics) while avoiding promotional language.

    *   **Completeness and Verification:**
        *   Address all requested points in each section by providing the information or silently omitting it if ungrounded after exhaustive search.
        *   Verify that every section, the General Discussion, and the Sources list are present and adhere to the instructions.
        *   Perform a final internal review before output.

    *   **Sources List:** The Sources list must be present at the very end and adhere strictly to the instructions (see `FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE`). Format: `* [Supervity Source X](URL) - Annotation [SSX].`

    *   **Inline Citation & Specificity:** Incorporate the inline citation [SSX] for every factual claim (see Inline Citation Requirement) and include specific dates/definitions (see Specificity and Granularity).
    """)

FINAL_REVIEW_INSTRUCTION = textwrap.dedent("""\
    *   **Internal Final Review:** Before generating the 'Sources' list, review your generated response for:

        *   **Completeness Check:**
            * Every numbered section requested in the prompt is present with the correct heading.
            * Each section contains all requested subsections and information points, or the content has been silently omitted if ungrounded after exhaustive search (headings retained).
            * The "General Discussion" paragraph is included.
            * No sections have been accidentally omitted or truncated.

        *   **Formatting Verification:**
            * All line breaks are properly formatted (no literal '\\n').
            * All section headings use correct Markdown format (`## Number. Title`).
            * All subsections use proper hierarchical format (`###` or indented bullets).
            * **Tables are PERFECTLY formatted** (aligned pipes, matching columns, start/end pipes, `-` used sparingly only for missing cell data *confirmed absent in source*, data accuracy check vs source).
            * Lists use consistent formatting and indentation.

        *   **Citation Integrity:**
            * Every factual claim has an inline citation `[SSX]`.
            * **Specifically verify financial data points and table entries for correct [SSX] citations.**
            * Citations are placed immediately after the supported claim, before punctuation.
            * All citations correspond to entries that WILL BE in the final Sources list.
            * Every source listed corresponds to at least one inline citation [SSX].

        *   **Data Precision & Recency:**
            * All monetary values specify currency and reporting period.
            * All dates are in consistent format and reflect the latest available data.
            * Numerical data is presented with appropriate precision and units.
            * Primary sources used are confirmed to be the most recent available.

        *   **Content Quality:**
            * Direct start with no conversational text.
            * Professional tone with no placeholders (except the minimal `-` in tables where structurally needed and confirmed absent in source).
            * Adherence to silent omission handling instructions.
            * Logical flow within and between sections.
            * Analytical depth provided where required (explaining 'why').
            * Lists (KPIs, Officers, Subsidiaries) verified for completeness based on source availability.

        *   **Single-Entity & Group Structure Clarity (CRITICAL):**
            *   Ensure that only the specified company name **'{company_name}'** is researched and included. Verify no data from similarly named but unrelated entities has crept in.
            *   Clarity maintained between parent group data and specific subsidiary data where applicable, clearly sourced [SSX].

        Proceed to generate the final 'Sources' list only after confirming these conditions are met.
    """)

COMPLETION_INSTRUCTION_TEMPLATE = textwrap.dedent("""\
    **Output Completion Requirements:**

    Before concluding your response, verify that:
    1. Every numbered section requested in the prompt is complete with all required subsections (or content is silently omitted if ungrounded after exhaustive search, retaining headings).
    2. All content follows **perfect markdown formatting** throughout, especially for tables (check data accuracy and source alignment).
    3. Each section contains all necessary details based on available grounded information and is not truncated. Check for data recency.
    4. The response maintains consistent formatting for lists, tables, and code blocks.
    5. All inline citations `[SSX]` are properly placed, with no extraneous or fabricated URLs. Every fact presented MUST be cited, **especially all financial data**.
    6. Strictly focus on the exact named company **'{company_name}'** (no confusion with similarly named entities). Verify parent vs. subsidiary context where needed.
""")

# --- Prompt Generating Functions ---

# Basic Prompt
def get_basic_prompt(company_name: str, language: str = "Japanese", ticker: Optional[str] = None, industry: Optional[str] = None, context_company_name: str = "NESIC"):
    """Generates a prompt for a comprehensive basic company profile with enhanced entity focus."""
    context_str = f"**{company_name}**"
    if ticker: context_str += f" (Ticker: {ticker})"
    if industry: context_str += f" (Industry: {industry})"

    # Prepare formatted instruction blocks
    formatted_additional_instructions = ADDITIONAL_REFINED_INSTRUCTIONS.format(company_name=company_name, ticker=ticker or "N/A", industry=industry or "N/A")
    formatted_research_depth = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    formatted_final_review = FINAL_REVIEW_INSTRUCTION.format(company_name=company_name)
    formatted_completion_template = COMPLETION_INSTRUCTION_TEMPLATE.format(company_name=company_name)
    formatted_final_source_list = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatted_base_formatting = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    formatted_audience_reminder = AUDIENCE_CONTEXT_REMINDER.format(language=language)

    prompt = f"""
**CRITICAL FOCUS:** This entire request is *exclusively* about the specific entity: {context_str}. Absolutely DO NOT include information about any other similarly named companies (e.g., entertainment, unrelated industries). Verify the identity of the company for all sourced information.

Comprehensive Corporate Profile, Strategic Overview, and Organizational Analysis of {company_name}

Objective: To compile a detailed, accurate, and analytically contextualized corporate profile, strategic overview, organizational structure analysis, and key personnel identification for {company_name}, focusing solely on this entity: {context_str}. Avoid detailed analysis of parent or subsidiary companies except for listing subsidiaries as requested and clearly sourced [SSX].

Target Audience Context: {formatted_audience_reminder}

{get_language_instruction(language)}

Research Requirements:
Conduct in-depth research using {company_name}'s official sources. Perform exhaustive checks across multiple primary sources before omitting any requested information silently. Every factual claim, data point, and summary must include an inline citation in the format [SSX]. Provide specific dates or reporting periods (e.g., "as of 2024-03-31", "for FY2023"). Ensure every claim is grounded by a verifiable Vertex AI grounding URL referenced back in the final Sources list for **{company_name}**. Use the absolute latest available official information.
{HANDLING_MISSING_INFO_INSTRUCTION}
{formatted_research_depth}
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION}

{formatted_additional_instructions}

## 1. Core Corporate Information:
    *   **Stock Ticker Symbol / Security Code:** (if publicly traded, verify it matches '{ticker or "N/A"}') [SSX]
    *   **Primary Industry Classification:** (e.g., GICS, SIC – specify the standard, verify it aligns with '{industry or "N/A"}') [SSX]
    *   **Full Name and Title of Current CEO:** [SSX] (Verify against latest official sources)
    *   **Full Registered Headquarters Address:** [SSX]
    *   **Main Corporate Telephone Number:** [SSX]
    *   **Official Corporate Website URL:** [SSX]
    *   **Date of Establishment/Incorporation:** (e.g., "established on YYYY-MM-DD") [SSX]
    *   **Date of Initial Public Offering (IPO)/Listing:** (if applicable, include exact date) [SSX]
    *   **Primary Stock Exchange/Market where listed:** (if applicable) [SSX]
    *   **Most Recently Reported Official Capital Figure:** (specify currency and reporting period, verify against latest financial statement/filing) [SSX]
    *   **Most Recently Reported Total Number of Employees:** (include reporting date and source; quantify any significant changes YoY if available [SSY]) [SSX]
    *   *Summary Paragraph:* Briefly summarize the company's situation based on the figures above, incorporating quantitative trends where available (e.g., "Capital increased by X% in the latest period...") [SSX].

## 2. Recent Business Overview:
    *   Provide a detailed summary of **{company_name}**'s core business operations and primary revenue streams based on the most recent official reports [SSX]. Include specific product or service details and any recent operational developments (with exact dates or periods).
    *   Include key highlights of recent business performance (e.g., "revenue increased by 12% in FY2023 [SSX]") or operational changes (e.g., restructuring, new market entries with dates), and explain their significance [SSX].

## 3. Business Environment Analysis:
    *   Describe the current market environment by identifying major competitors and market dynamics (include specific names, market share percentages if available and verifiable, and exact data dates as available [SSX]).
    *   Identify and explain key industry trends (e.g., technological shifts, regulatory changes) including specific figures or percentages where possible [SSX]. Note where these trends are discussed in company reports [SSY].
    *   ***Discuss the strategic implications and opportunities/threats these trends pose for {company_name} from a Japanese corporate perspective [SSX].***

## 4. Organizational Structure Overview:
    *   Describe the high-level organizational structure as stated in official sources (e.g., "divisional based on Mobility, Safety, and Entertainment sectors [SSX]", "functional", "matrix") and reference the source (e.g., "as shown in the Annual Report 2023, p. XX") [SSX].
    *   If an official organization chart is found in sources, note its existence and location (e.g., "An org chart is available on the company website under 'About Us' [SSX]" or "Figure X in the Annual Report [SSY] shows the structure.").
    *   Briefly comment on the rationale behind the structure (if stated) and its potential implications for decision-making and agility [SSX].

## 5. Key Management Personnel & Responsibilities:
    *   **Prioritize the latest official company website** for the most current lists of Directors and Executive Officers. Cross-reference with recent Annual Reports or official filings for verification and responsibilities. Ensure names/titles relate specifically to **{company_name}**, not exclusively a parent company unless specified.
    *   Present the Board of Directors and Audit & Supervisory Board members (or equivalent) in **perfectly formatted Markdown tables**. Include Name, Title, Key Notes (e.g., External, Committee Chair, Independence status), and Source(s). State the 'as of' date clearly for the data. Use '-' for missing data points only if needed for table structure. Ensure the *complete list* as per the source is included.
        *   **Board of Directors (as of [Date] [SSX]):**
            | Name | Title | Notes | Source(s) |
            |------|-------|-------|-----------|
            |      |       |       |           |
        *   **Audit & Supervisory Board Members / Equivalent (as of [Date] [SSX]):**
            | Name | Title | Notes | Source(s) |
            |------|-------|-------|-----------|
            |      |       |       |           |
    *   **Executive Officers (Management Team):** List key members (beyond CEO) with titles and detailed descriptions of their strategic responsibilities (e.g., COO Mobility, CFO, CTO, Head of Administration). Include start dates or tenure if available [SSX]. Ensure the *complete list* as per the source is included. Use a list or table for clarity.

## 6. Subsidiaries List:
    *   List *major* direct subsidiaries (global where applicable) based solely on official documentation (e.g., list in Annual Report Appendix). Acknowledge this may not be exhaustive. For each subsidiary, include primary business activity, country of operation, and, if available, ownership percentage as stated in the source [SSX]. Present this in a **perfectly formatted Markdown table** for clarity. Use '-' for missing data points only if needed for table structure. Note any recent major M&A impacting the subsidiary structure if verifiable [SSY].
        | Subsidiary Name | Primary Business | Country | Ownership % (if stated) | Source(s) |
        |-----------------|------------------|---------|-------------------------|-----------|
        |                 |                  |         | -                       |           |

## 7. Leadership Strategic Outlook (Verbatim Quotes):
    *   **CEO & Chairman:** Provide at least four direct, meaningful quotes focusing on long-term vision, key challenges, growth strategies, and market outlook. Each quote must be followed immediately by its source citation in parentheses (e.g., "(Source: Annual Report 2023, p.5)"), and an inline citation [SSX] must confirm the quote's origin.
    *   **Other Key Executives (e.g., CFO, CSO, CTO, COO, relevant BU Heads):** Provide verifiable quotes (aim for 1-3 per relevant executive if strategically insightful) detailing their perspective on their area of responsibility (e.g., financial strategy, tech roadmap, operational plans) with similar detailed attribution and inline citation [SSX].

## 8. General Discussion:
    *   Provide a concluding single paragraph (approximately 300-500 words).
    *   **Synthesize** the key findings exclusively from Sections 1-7 about **{company_name}**, explicitly linking analysis (e.g., "The organizational structure described in section 4 [SSX] supports the strategic focus mentioned by the CEO [SSY]...") and ensuring every claim is supported by an inline citation. Incorporate key quantitative points.
    *   Structure your analysis logically by starting with an overall assessment, then discussing strengths and opportunities, followed by weaknesses and risks, and concluding with an outlook relevant for the Japanese audience. Look for and mention potential DX implications arising from the company's structure or leadership messages [SSX].
    *   **Do not introduce new factual claims** that are not derived from the previous sections about **{company_name}**.

Source and Accuracy Requirements:
*   **Accuracy:** All information must be factually correct, current, and verifiable against grounded sources for **{company_name}**. Specify currency and reporting periods for all monetary data. Omit unverified data silently after exhaustive search. Verify management lists against latest website data.
*   **Source Specificity (Traceability):** Every data point, claim, and quote must be traceable to a specific source using an inline citation (e.g., [SSX]). These must match the final Sources list.
*   **Source Quality:** Use only official company sources primarily. Secondary sources may be used sparingly for context but must be verified and grounded. All sources must be clearly cited.

{formatted_completion_template}
{formatted_final_review}
{formatted_final_source_list}
{formatted_base_formatting}
"""
    return prompt

# Financial Prompt
def get_financial_prompt(company_name: str, language: str = "Japanese", ticker: Optional[str] = None, industry: Optional[str] = None, context_company_name: str = "NESIC"):
    """Generates a prompt for a detailed financial analysis with enhanced entity focus."""
    context_str = f"**{company_name}**"
    if ticker: context_str += f" (Ticker: {ticker})"
    if industry: context_str += f" (Industry: {industry})"

    # Prepare formatted instruction blocks
    formatted_additional_instructions = ADDITIONAL_REFINED_INSTRUCTIONS.format(company_name=company_name, ticker=ticker or "N/A", industry=industry or "N/A")
    formatted_research_depth = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    formatted_final_review = FINAL_REVIEW_INSTRUCTION.format(company_name=company_name)
    formatted_completion_template = COMPLETION_INSTRUCTION_TEMPLATE.format(company_name=company_name)
    formatted_final_source_list = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatted_base_formatting = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    formatted_audience_reminder = AUDIENCE_CONTEXT_REMINDER.format(language=language)

    enhanced_financial_research_instructions = textwrap.dedent(f"""\
    *   **Mandatory Deep Search & Calculation:** Conduct an exhaustive search within **{company_name}**'s official financial disclosures for the last 3 full fiscal years, including Annual Reports, Financial Statements (Income Statement, Balance Sheet, Cash Flow Statement), **Footnotes**, Supplementary Data Packs (Databases, Tanshin), official filings, and IR materials. Do not rely solely on summary tables; examine detailed statements and notes for definitions and components [SSX]. Cross-verify figures across multiple sources. Verify table data accuracy meticulously. **Crucially, every single financial figure, ratio, or data point presented, whether in text or tables, MUST be directly supported by a verifiable Vertex AI grounding URL provided *for this query* [SSX] related to {context_str}.**
    *   **Calculation Obligation & Citation:** For financial metrics such as Margins, ROE, ROA, Debt-to-Equity, and ROIC: if not explicitly stated, calculate them using standard formulas only if all necessary base data is available and verifiable from grounded sources for {company_name}. Clearly state the formula used [SSX]. **When reporting a calculated metric, cite the sources for all underlying base data points used in the calculation** (e.g., "ROE (Calculated: NI [SS1] / Avg Equity [SS2]) [SS1, SS2]").
    *   **Strict Silent Omission Policy:** If a metric cannot be found or reliably calculated from verifiable sources after exhaustive search, omit that specific line item entirely. Do not use placeholders like 'N/A' or state that data is missing.
    *   **Industry Specific Metrics:** Be aware of industry nuances (e.g., for Insurance, distinguish between flow metrics like 'premium income' and stock metrics like 'annualized premiums in-force' if both are reported and used strategically, e.g., in MTP targets). If including non-standard metrics, briefly explain their definition/relevance based on the source [SSX].
    *   **Data Sparsity Acknowledgement (Internal):** For non-listed subsidiaries or complex groups, acknowledge internally that certain detailed metrics might be unavailable at the subsidiary level and analysis will rely on available consolidated or segment data for {company_name}.
    """)

    analytical_depth_instructions = textwrap.dedent("""\
    *   **Analytical Depth Requirements:**
        *   **Time-Series Trends:** For key metrics of {company_name}, identify and analyze growth/decline trends over the 3-year period. Quantify these trends (e.g., CAGR, YoY change) [SSX]. Explain the *drivers* behind these trends using management commentary or related data (e.g., cost structure changes impacting margins) [SSY].
        *   **Competitive Comparison Outliers (if feasible):** If reliable, grounded data for key competitors (identified in separate competitive analysis) is available, identify metrics where {company_name} appears unusually high or low (e.g., high fixed cost ratio, lower ROA than industry average). Analyze potential reasons based on sources [SSX, SSY]. *Perform this only if competitor data is grounded and available.*
        *   **Management Efficiency Evaluation:** Objectively evaluate management efficiency of {company_name} using relevant ratios (ROE, ROA, Margins, etc.) compared to past performance and targets [SSX].
        *   **Causal & Correlation Analysis:** Analyze potential correlations (e.g., sales vs. advertising costs, operating profit vs. personnel costs) based on reported data and management discussion for {company_name} [SSX]. Identify key drivers impacting profitability (e.g., "Which KPI is working for profit?" based on segment data or management statements) [SSY].
        *   **Identify Key Management Drivers:** Based on the analysis of {company_name}, highlight the primary levers management appears to be using or focusing on to influence financial performance [SSX].
    """)

    advanced_analysis_feasibility_note = textwrap.dedent(f"""\
    *   **Advanced Analysis (Feasibility Dependent):** If sufficient historical and competitive data is available and grounded, attempt the following:
        *   **Competitor Comparison Matrix:** Create a matrix comparing key financial metrics (from Section 2) between {company_name} and 1-2 key competitors for the latest year [SSX, SSY]. *Only if grounded competitor data is available.*
        *   **Financial Soundness Risk Scoring:** (Conceptual) Briefly assess {company_name}'s financial soundness based on key ratios (leverage, liquidity, profitability trends). *Do not create a numerical score unless a published methodology is cited [SSX].*
        *   **Scenario Analysis / Forecasting:** (Conceptual) Summarize any company-provided forecasts or scenarios for {company_name} (e.g., MTP targets, sensitivity analysis like FX impact mentioned in reports [SSX]). *Do not perform independent forecasting.* Briefly describe forecasting models mentioned in sources if any [SSY].
    """)

    prompt = f"""
**CRITICAL FOCUS:** This entire request is *exclusively* about the specific entity: {context_str}. Absolutely DO NOT include information about any other similarly named companies. Verify the identity for all financial data sourced.

Comprehensive Strategic Financial Analysis of {company_name} (Last 3 Fiscal Years)

Objective: Deliver a complete, analytically rich, and meticulously sourced financial profile of **{company_name}** using the last three full fiscal years. Combine traditional financial metrics with analysis of profitability, cost structure, cash flow, investments, and contextual factors. Provide deep analysis explaining trends and drivers, requiring meticulous sourcing and in-depth analysis explaining the 'why' behind the numbers. Focus strictly on {context_str}.

Target Audience Context: This analysis is for a **Japanese corporate strategy audience**. Use Japanese terminology when appropriate (e.g., "売上総利益" for Gross Profit) and ensure that all monetary values specify currency (e.g., JPY millions) and reporting period (e.g., "FY2023 ended March 31, 2024") with exact dates where available [SSX]. {formatted_audience_reminder}

{get_language_instruction(language)}

Research Requirements:
For each section, provide verifiable data with inline citations [SSX] and specific dates or reporting periods after conducting exhaustive research across multiple primary sources (including **footnotes**) for **{company_name}**. **Every single financial figure MUST have a verifiable grounding URL citation [SSX] from this query.** Every claim must be traceable to a final source. Silently omit any data not found. Use **perfect Markdown tables** for financial data presentation, verifying data accuracy against sources. Use '-' for missing data points only if needed for table structure.
{HANDLING_MISSING_INFO_INSTRUCTION}
{formatted_research_depth}
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION}
{enhanced_financial_research_instructions}
{ANALYSIS_SYNTHESIS_INSTRUCTION}
{analytical_depth_instructions}
{advanced_analysis_feasibility_note}

{formatted_additional_instructions}

## 1. Top Shareholders:
    *   List major shareholders of {company_name} (typically the top 5-10, with exact ownership percentages, reporting dates, and source references) in a **perfectly formatted Markdown table** [SSX]. Use '-' for missing data points only if needed for table structure.
        | Shareholder Name | Ownership % | As of Date | Source(s) |
        |------------------|-------------|------------|-----------|
        |                  |             |            |           |
    *   Briefly comment on the stability or influence of the ownership structure on the financial strategy of {company_name} [SSX].

## 2. Key Financial Metrics (3-Year Trend in a Table):
    *   Present the following metrics for {company_name} for the last 3 full fiscal years in a **perfectly formatted Markdown table**. Specify currency (e.g., JPY millions) and fiscal year (e.g., FY2021, FY2022, FY2023) for each value. Verify data accuracy. If calculated, note this below the table or in a 'Notes' column and cite base data sources. Cite sources for all data [SSX]. Use '-' for missing data points only if needed for table structure. *Consider adding industry-specific metrics if relevant and reported (see instructions).*
        | Metric                                          | FYXXXX | FYYYYY | FYZZZZ | Notes / Calculation Basis (Cite Base Data) | Source(s) |
        |-------------------------------------------------|--------|--------|--------|---------------------------------------------|-----------|
        | Total Revenue / Net Sales / Premium Income etc. |        |        |        | (Specify metric used)                       | [SSX]     |
        | Gross Profit                                    |        |        |        | (Calc: Rev [SSX] - COGS [SSY])              | [SSX, SSY]|
        | Gross Profit Margin (%)                         |        |        |        | (Calc: GP [SSZ] / Rev [SSX])                | [SSX, SSZ]|
        | EBITDA                                          |        |        |        | (If available/calculable)                   | [SSX]     |
        | EBITDA Margin (%)                               |        |        |        | (Calc: EBITDA [SSX] / Rev [SSY])            | [SSX, SSY]|
        | Operating Income / Operating Profit             |        |        |        |                                             | [SSX]     |
        | Operating Margin (%)                            |        |        |        | (Calc: OpInc [SSX] / Rev [SSY])             | [SSX, SSY]|
        | Ordinary Income / Pre-Tax Income                |        |        |        |                                             | [SSX]     |
        | Ordinary Income Margin (%)                      |        |        |        | (Calc: OrdInc [SSX] / Rev [SSY])            | [SSX, SSY]|
        | Net Income attributable to Parent               |        |        |        |                                             | [SSX]     |
        | Net Income Margin (%)                           |        |        |        | (Calc: NetInc [SSX] / Rev [SSY])            | [SSX, SSY]|
        | ROE (%)                                         |        |        |        | (Calc: NI [SSX] / Avg Equity [SSY])         | [SSX, SSY]|
        | ROA (%)                                         |        |        |        | (Calc: NI [SSX] / Avg Assets [SSY])         | [SSX, SSY]|
        | Total Assets                                    |        |        |        |                                             | [SSX]     |
        | Total Shareholders' Equity                      |        |        |        |                                             | [SSX]     |
        | Equity Ratio (%)                                |        |        |        | (Calc: Equity [SSX] / Assets [SSY])         | [SSX, SSY]|
        | Total Interest-Bearing Debt                     |        |        |        |                                             | [SSX]     |
        | Debt-to-Equity Ratio (x)                        |        |        |        | (Calc: Debt [SSX] / Equity [SSY])           | [SSX, SSY]|
        | Net Cash from Operations                        |        |        |        |                                             | [SSX]     |
        | Net Cash from Investing                         |        |        |        |                                             | [SSX]     |
        | Net Cash from Financing                         |        |        |        |                                             | [SSX]     |
        | (Add other key metrics like Premiums In-Force if needed) |       |        |        |                                             | [SSX]     |
    *   **Analyze** key trends observed in the table for {company_name} (YoY changes, CAGR). Explain the *drivers* behind these trends based on source commentary [SSX]. Identify any standout performance aspects (positive or negative) [SSY].

## 3. Profitability Analysis (3-Year Trend):
    *   Analyze trends in Operating Margin and Net Income Margin for {company_name} in more detail (building on the table above). Explain the *drivers* behind these trends (e.g., cost variations, pricing power, product mix shifts, one-off items mentioned in reports) with specific evidence and inline citations [SSX]. Quantify changes YoY. Discuss the sustainability of current profitability levels [SSY].

## 4. Segment-Level Performance (if applicable, Last 3 Fiscal Years):
    *   If segment data is available for {company_name} (e.g., Mobility, Safety, Entertainment), present revenue, operating profit, and margin percentages for each segment in a **perfectly formatted Markdown table** (include currency and fiscal year, verify data) [SSX]. Use '-' for missing data points only if needed for table structure.
        | Segment Name | Metric           | FYXXXX | FYYYYY | FYZZZZ | Source(s) |
        |--------------|------------------|--------|--------|--------|-----------|
        | Segment A    | Revenue          |        |        |        | [SSX]     |
        | Segment A    | Operating Income |        |        |        | [SSX]     |
        | Segment A    | Operating Margin%|        |        |        | [SSX]     |
        | Segment B    | Revenue          |        |        |        | [SSY]     |
        | ...          | ...              |        |        |        |           |
    *   Analyze trends, growth drivers, and the relative contribution/profitability of each segment of {company_name}, citing specific figures [SSX]. Identify key profit-driving segments based on available data [SSY].

## 5. Cost Structure Analysis (3-Year Trend):
    *   Detail the composition and trends of major operating costs for {company_name} using data from financial statements [SSX]. Present in a **perfectly formatted Markdown table** if helpful and data is verifiable. Verify data accuracy. Use '-' for missing data points only if needed for table structure.
        | Cost Item        | FYXXXX (JPY M) | FYXXXX (% of Rev) | FYYYYY (JPY M) | FYYYYY (% of Rev) | FYZZZZ (JPY M) | FYZZZZ (% of Rev) | Source(s) |
        |------------------|----------------|-------------------|----------------|-------------------|----------------|-------------------|-----------|
        | COGS             |                |                   |                |                   |                |                   | [SSX]     |
        | SG&A Expenses    |                |                   |                |                   |                |                   | [SSY]     |
        |  - R&D (if sep)  |                |                   |                |                   |                |                   | [SSZ]     |
        |  - Personnel     |                |                   |                |                   |                |                   | [SSW]     |
        |  - Other SG&A    |                |                   |                |                   |                |                   | [SSV]     |
    *   Analyze drivers behind {company_name}'s cost trends (e.g., raw material prices, personnel costs, restructuring effects) and comment on cost control effectiveness based on commentary in reports [SSX]. Look for fixed vs variable cost commentary if available [SSY].

## 6. Cash Flow Statement Analysis (3-Year Trend):
    *   Analyze trends in Operating Cash Flow (OCF) for {company_name}. Explain key drivers, differentiating between changes in profit and changes in working capital components (receivables, payables, inventory) based on the cash flow statement details [SSX].
    *   Detail major Investing Cash Flow activities (e.g., CapEx, acquisitions) and Financing Cash Flow activities (e.g., debt issuance/repayment, dividends, share buybacks) for {company_name} with specific amounts (specify currency) and context [SSX].
    *   Calculate and analyze Free Cash Flow (FCF = OCF - CapEx) trend for {company_name} [SSX]. Cite base data sources [SSY, SSZ]. Comment on the company's capacity to fund operations, investments, and shareholder returns based on FCF generation [SSW].

## 7. Investment Activities (Last 3 Years):
    *   Describe major M&A deals involving {company_name} (target, deal value if public, date, strategic rationale) [SSX].
    *   Analyze {company_name}'s capital expenditure (CapEx) patterns (total amount, key areas like factories/equipment/software) [SSY].
    *   Detail any significant corporate venture capital (CVC) or R&D investments by {company_name} with specific amounts (specify currency and reporting period) and stated goals [SSZ].
    *   Analyze the strategic rationale and potential financial impact (if commented on by management) of these investments for {company_name} [SSX, SSY, SSZ].

## 8. Contextual Financial Factors:
    *   Identify significant one-time events impacting {company_name} (e.g., asset sales, restructuring charges, impairment losses, litigation settlements) reported in the last 3 years, specifying dates, financial impacts (gain/loss in specified currency), and source notes [SSX].
    *   Discuss any significant accounting standard changes that impacted {company_name}'s reported figures during the period [SSY].
    *   Mention any key external economic or regulatory factors explicitly cited by {company_name}'s management as impacting financial performance [SSZ].
    *   Critically analyze the quality and sustainability of {company_name}'s reported earnings, considering the impact of one-time items and accounting choices noted [SSX, SSY, SSZ].

## 9. Credit Ratings & Financial Health (if available):
    *   List current and historical credit ratings for {company_name} from major agencies (e.g., S&P, Moody's, Fitch, R&I, JCR) with reporting dates [SSX].
    *   Summarize key highlights or concerns mentioned in the rating agencies' commentary regarding {company_name} [SSY].
    *   Analyze the implications of these ratings (or lack thereof) for {company_name}'s financial flexibility and cost of capital [SSX, SSY].

## General Discussion:
    *   Provide a concluding single paragraph (300-500 words) that synthesizes the findings exclusively from Sections 1-9 regarding **{company_name}**. Explicitly connect the analysis (e.g., "The strong cash flow generation [SSX] supports the investment strategy outlined in Section 7 [SSY], despite the margin pressure noted in Section 3 [SSZ]..."). Explain *why* trends are occurring based on the analysis. Incorporate key quantitative results. Discuss implications for future financial performance and strategic options for {company_name}.
    *   Structure the discussion logically by starting with an overall assessment of {company_name}'s financial health and performance trends, then discussing profitability drivers, cash flow adequacy, investment effectiveness, and concluding with an outlook (including strengths/weaknesses) tailored to a Japanese audience.
    *   Do not introduce any new factual claims that are not supported by previous sections and citations about **{company_name}**.

Source and Accuracy Requirements:
*   **Accuracy:** All information must be current and verifiable for **{company_name}**. Specify currency (e.g., JPY millions) and reporting period (e.g., FY2023) for every monetary value. Silently omit unverified data after exhaustive search. Verify table data meticulously. **Every financial figure must have a grounding URL citation [SSX].**
*   **Source Specificity:** Every data point (in text, tables) must include an inline citation [SSX] that corresponds to a specific source in the final Sources list. Cite base data for calculations.
*   **Source Quality:** Rely primarily on official company sources for **{company_name}** (Financial Statements, Footnotes, Tanshin, IR Presentations, Annual Reports). Secondary sources may be used sparingly for context (like ratings) and must be clearly cited, verified, and grounded.

{formatted_completion_template}
{formatted_final_review}
{formatted_final_source_list}
{formatted_base_formatting}
"""
    return prompt

# Competitive Landscape Prompt
def get_competitive_landscape_prompt(company_name: str, language: str = "Japanese", ticker: Optional[str] = None, industry: Optional[str] = None, context_company_name: str = "NESIC"):
    """Generates a prompt for a detailed competitive analysis with nuanced grounding rules and expanded scope."""
    context_str = f"**{company_name}**"
    if ticker: context_str += f" (Ticker: {ticker})"
    if industry: context_str += f" (Industry: {industry})"

    # Prepare formatted instruction blocks
    formatted_additional_instructions = ADDITIONAL_REFINED_INSTRUCTIONS.format(company_name=company_name, ticker=ticker or "N/A", industry=industry or "N/A")
    formatted_research_depth = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    formatted_final_review = FINAL_REVIEW_INSTRUCTION.format(company_name=company_name)
    formatted_completion_template = COMPLETION_INSTRUCTION_TEMPLATE.format(company_name=company_name)
    formatted_final_source_list = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatted_base_formatting = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    formatted_audience_reminder = AUDIENCE_CONTEXT_REMINDER.format(language=language)

    competitive_research_instructions = textwrap.dedent(f"""\
    **Research & Grounding Strategy for Competitive Analysis:**

    1.  **Prioritize {company_name}'s Official Statements:** Use {company_name}'s own reports (Annual Report, IR materials) exhaustively to identify competitors *they* acknowledge [SSX] and their assessment of the market [SSY].
    2.  **Industry & Competitor Data Grounding:** For specific facts about the industry or competitors (e.g., market size/share, trends, competitor financials/products/strategies), use reliable third-party sources (reputable market research firms, financial news like Nikkei/Bloomberg, competitor's official reports) **only if** grounding URLs for these sources are provided by Vertex AI Search. Cite these using [SSY], [SSZ]. If no grounding URL is provided for an industry or competitor fact after exhaustive search, silently omit that specific data point. Do not invent facts or state unavailability. Ensure competitor data pertains to entities genuinely competing with {context_str}.
    3.  **Synthesis & Attribution:** When synthesizing competitive positioning or SWOT for {company_name}, clearly attribute claims. If based on {company_name}'s statements, use [SSX]. If based on grounded third-party data about the industry or a competitor, use [SSY], [SSZ]. Avoid unsourced analysis.
    4.  **Silent Omission Rule:** Silently omit any industry or competitor claim that cannot be traced back to either {company_name}'s statements [SSX] or a grounded third-party source [SSY, SSZ] after exhaustive search.
    5.  **Final Source List Integrity:** The final "Sources" list MUST include only the Vertex AI grounding URLs provided for this query (which may include links to {company_name}'s site or grounded third-party sites). Inline citations [SSX, SSY, SSZ] must match these sources.
    """)

    prompt = f"""
**CRITICAL FOCUS:** This entire request is *exclusively* about the specific entity: {context_str} and its competitive landscape. Verify the identity of the company for all sourced information. Do not include unrelated entities.

Detailed Competitive Analysis and Strategic Positioning of {company_name}

Objective: To conduct a comprehensive competitive analysis of **{company_name}** including industry overview, competitor identification, analysis of their market presence and strategies, and an assessment of {company_name}'s own competitive positioning, strategy, and detailed capabilities. Conclusions should include a synthesized discussion relevant to a Japanese corporate audience. Focus strictly on {context_str}.

Target Audience Context: This output is for strategic review by a **Japanese company**. Ensure all analysis is supported by explicit inline citations [SSX] for {company_name}'s data/statements and [SSY, SSZ] for grounded industry/competitor data. Clearly attribute synthesized points. {formatted_audience_reminder}

{get_language_instruction(language)}

Research Requirements:
Use **perfect Markdown tables**. Adhere strictly to grounding rules outlined below. Conduct exhaustive research before silently omitting unverified competitor or industry data. Use '-' for missing data points in tables only if needed for structure. Ensure all claims are verifiable.
{HANDLING_MISSING_INFO_INSTRUCTION}
{formatted_research_depth} # Focus on {company_name}'s view + grounded competitor/industry data
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION}
{competitive_research_instructions}
{ANALYSIS_SYNTHESIS_INSTRUCTION}

{formatted_additional_instructions}

### 1. Industry Overview & Trends
    *   Describe the overall industry {company_name} operates in, aligning with '{industry or "N/A"}'. Include market size and growth rate estimates if verifiable data is available [SSY].
    *   Identify key technological, regulatory, economic, and social trends impacting the industry, citing sources [SSY, SSZ].
    *   Discuss the overall health and competitive intensity of the sector based on available grounded information [SSX, SSY].

### 2. Major Competitors Identification & Profiling
    *   Identify primary global and key regional competitors of {company_name} based on {company_name}'s official statements [SSX] or grounded third-party reports [SSY]. Provide specific names.
    *   Present competitor information in a **perfectly formatted Markdown table** where possible, clearly indicating source for each piece of data. Use '-' for missing data points only if needed for table structure. Verify data accuracy.
        | Competitor Name | Primary Business Area(s) of Overlap with {company_name} | Estimated Market Share (Market, Year) | Key Geographic Overlap | Recent Key Moves (Date) | Source(s) |
        |-----------------|----------------------------------------------------------|---------------------------------------|------------------------|-------------------------|-----------|
        | Competitor A    | Describe relevant business [SSX]                         | X% (Specific Market, YYYY) [SSY]      | e.g., Japan, N. America [SSX] | Acquired Co. Z (YYYY-MM) [SSZ] | [SSX, SSY, SSZ] |
        | Competitor B    | Describe relevant business [SSX]                         | Y% (Specific Market, YYYY) [SSW]      | e.g., Global [SSX]     | Launched Product P (YYYY-MM) [SSV] | [SSX, SSW, SSV] |
        | Competitor C    | ...                                                      | -                                     | ...                    | ...                     |           |
    *   For key competitors identified, briefly analyze their relative positioning versus {company_name} on dimensions like technology, product range, price point, or regional strength, based *only* on grounded data [SSX, SSY]. Note strategic weaknesses if explicitly mentioned in sources [SSZ].

### 3. {company_name}'s Competitive Positioning
    *   **Strengths:** Detail {company_name}'s key competitive strengths as stated in official documents or evidenced by data (e.g., strong R&D pipeline [SSX], market leadership in Segment Y [SSY]). Provide specific examples.
    *   **Weaknesses:** Detail {company_name}'s potential competitive weaknesses or challenges acknowledged in official sources or implied by data (e.g., high cost structure compared to peers [SSX], dependence on a single market [SSY]).
    *   **Opportunities:** Identify potential opportunities for {company_name} arising from industry trends (from Section 1) or competitor weaknesses (from Section 2), based on grounded analysis [SSX, SSY].
    *   **Threats:** Identify potential threats to {company_name} arising from industry trends, competitor actions, or regulatory changes, based on grounded analysis [SSX, SSY].
    *   **Competitive Advantages:** Summarize {company_name}'s key sources of sustainable competitive advantage as stated or evidenced (e.g., proprietary technology [SSX], brand loyalty metrics [SSY], scale economies [SSZ]).

### 4. {company_name}'s Detailed Profile (Competitive Lens)
    *   **Products and Services:**
        *   Describe {company_name}'s main products/services and product line-up details [SSX].
        *   Discuss typical price range or positioning (e.g., premium, value) if stated [SSY].
        *   Highlight key quality/differentiation points mentioned in reports [SSZ].
        *   Comment on product development capabilities (e.g., frequency of new launches mentioned [SSX], R&D focus areas [SSY]).
        *   Mention track record/case studies if highlighted (especially for B2B) [SSZ].
    *   **Marketing and Sales Strategies:**
        *   Describe {company_name}'s primary sales channels (e.g., direct, EC, distributors) [SSX].
        *   Outline promotion strategies mentioned (advertising focus, SNS campaigns, etc.) [SSY].
        *   Summarize reported brand image or perception for {company_name} [SSZ].
        *   Note any mention of SEO/SNS utilization [SSX].
        *   Describe the customer support system if detailed [SSY].
    *   **Technological and Development Capabilities:**
        *   List any claimed patents or unique technologies for {company_name} [SSX].
        *   Report R&D expenditure trends (absolute and % of revenue if available) for {company_name} [SSY].
        *   Identify key development bases or centers for {company_name} [SSZ].
        *   Detail significant external collaborations (universities, research institutions, other companies) mentioned for {company_name} [SSX].
    *   **Other Relevant Factors (if information available for {company_name}):**
        *   Key aspects of Human Resources strategy mentioned (recruitment policy, training systems) [SSX].
        *   Reported Customer Satisfaction (CSAT/NPS) scores or word-of-mouth evaluations [SSY].
        *   Mention of external evaluations (awards, rankings) [SSZ].
        *   Commentary on responsiveness to price revisions or industry trends [SSX].

### 5. {company_name}'s Competitive Strategy
    *   Describe {company_name}'s stated competitive strategy (e.g., focus on premium segment [SSX], R&D leadership [SSY], operational efficiency [SSZ]). Use direct quotes or paraphrased statements with citations.
    *   Identify and describe {company_name}'s primary value discipline (e.g., operational excellence, customer intimacy, product leadership) if explicitly mentioned, with supporting evidence [SSX].
    *   List specific initiatives or investments by {company_name} aimed at enhancing its competitive position (e.g., "Invested ¥XB in new R&D facility targeting Y technology [SSX]"). Include funding amounts and timelines if available [SSY].
    *   Explain how {company_name} measures its competitive success according to official sources (e.g., target market share growth [SSX], customer satisfaction scores [SSY]).

### 6. General Discussion
    *   Provide a concluding single paragraph (300-500 words) that synthesizes the findings exclusively from Sections 1-5 regarding **{company_name}** and its competitive environment. Clearly link analytical statements using inline citations (e.g., "Given the industry trend towards X [SSY], {company_name}'s investment in Y technology [SSX] positions it well against Competitor A's recent moves [SSZ]..."). Evaluate the overall competitive strength and strategic effectiveness of {company_name}.
    *   Structure the analysis logically by starting with an overall assessment of the competitive landscape and {company_name}'s place within it, discussing strengths/weaknesses/strategy effectiveness in light of competitors and trends, and concluding with strategic implications and potential threats/opportunities from a Japanese perspective.
    *   Do not introduce new factual claims or unsourced analysis.

Source and Accuracy Requirements:
*   **Accuracy:** All information must be factual and current. Specify currency, dates, and reporting periods for any figures. Differentiate between {company_name}'s statements and grounded competitor/industry data. Silently omit unverified data after exhaustive search. Verify table data.
*   **Traceability:** Every claim must include an inline citation ([SSX] for company data, [SSY], [SSZ], etc. for grounded competitor/industry data) corresponding to a grounding URL in the final Sources list.
*   **Source Quality:** Use primarily {company_name}'s official sources. For competitor/industry data, use *only* information verifiable through provided Vertex AI grounding URLs (which might point to reputable third-party sources or competitor reports).

{formatted_completion_template}
{formatted_final_review}
{formatted_final_source_list}
{formatted_base_formatting}
"""
    return prompt

# Management Strategy Prompt
def get_management_strategy_prompt(company_name: str, language: str = "Japanese", ticker: Optional[str] = None, industry: Optional[str] = None, context_company_name: str = "NESIC"):
    """Generates a prompt for analyzing management strategy and mid-term business plan with enhanced entity focus."""
    context_str = f"**{company_name}**"
    if ticker: context_str += f" (Ticker: {ticker})"
    if industry: context_str += f" (Industry: {industry})"

    # Prepare formatted instruction blocks
    formatted_additional_instructions = ADDITIONAL_REFINED_INSTRUCTIONS.format(company_name=company_name, ticker=ticker or "N/A", industry=industry or "N/A")
    formatted_research_depth = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    formatted_final_review = FINAL_REVIEW_INSTRUCTION.format(company_name=company_name)
    formatted_completion_template = COMPLETION_INSTRUCTION_TEMPLATE.format(company_name=company_name)
    formatted_final_source_list = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatted_base_formatting = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    formatted_audience_reminder = AUDIENCE_CONTEXT_REMINDER.format(language=language)

    prompt = f"""
**CRITICAL FOCUS:** This entire request is *exclusively* about the specific entity: {context_str}. Verify the identity of the company for all sourced information. Do not include unrelated entities.

Comprehensive Analysis of {company_name}'s Management Strategy and Mid-Term Business Plan: Focus, Execution, and Progress

Objective: To conduct an extensive analysis of **{company_name}**'s management strategy and mid-term business plan (MTP) by evaluating strategic pillars, execution effectiveness, progress against targets, and challenges. Focus on explaining *why* strategic choices were made and *how* progress is tracked using specific data with inline citations [SSX]. Focus strictly on {context_str}.

Target Audience Context: This analysis is designed for a **Japanese company** needing deep strategic insights. Present all information with exact dates (e.g., MTP period FY2024-FY2026), reporting periods, financial figures in specified currency, and clear official source attributions [SSX]. {formatted_audience_reminder}

{get_language_instruction(language)}

Research Requirements:
Conduct in-depth research from official sources for **{company_name}** (IR documents, Annual/Integrated Reports, earnings call transcripts, strategic website sections, MTP presentations). Perform exhaustive checks across multiple sources before silently omitting unverified data. Ensure all claims include inline citations [SSX] and specific dates or reporting periods. Use **perfect Markdown tables** for presenting targets and progress, verifying data accuracy. Use '-' for missing data points only if needed for table structure.
{HANDLING_MISSING_INFO_INSTRUCTION}
{formatted_research_depth}
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION}

{formatted_additional_instructions}

## 1. Management Strategy and Vision Alignment:
    *   Outline **{company_name}**'s overall management strategy and analyze its alignment with the company's long-term vision or purpose statement. Include precise references (e.g., "as stated in the Vision 2030 document [SSX]") with inline citations [SSY].
    *   Explain the core management philosophy, values, and strategic approach for {company_name} (e.g., "focus on organic growth through R&D [SSX]", "pursuit of operational excellence [SSY]") with examples, including specific dates or document references [SSZ].
    *   Identify key strategic pillars or themes for {company_name} (e.g., "Digital Transformation", "Sustainability", "Global Expansion") for the upcoming 3-5 years, explaining the rationale and objectives for each based on official statements [SSX, SSY].
    *   Describe any significant strategic shifts from previous plans for {company_name} (e.g., "pivot from hardware to software solutions announced in FY2022 [SSX]"), with supporting data and source references [SSY].

## 2. Current Mid-Term Business Plan (MTP) Overview:
    *   Identify the official name and exact time period of the current MTP for {company_name} (e.g., "Mid-Term Plan 'Growth Forward' (FY2024-FY2026)") with source references [SSX].
    *   Detail the main objectives and specific quantitative targets (financial and non-financial) outlined in the MTP for {company_name}. Present **all** stated MTP targets/KPIs clearly in a **perfectly formatted Markdown table**, including KPI category, KPI name, target value (with currency/units), target year/period, and baseline values if available [SSX]. Verify data accuracy. Use '-' for missing data points only if needed for table structure.
        | KPI Category | KPI Name                     | Target Value (by FYZZZZ) | Baseline (FYXXXX) (if stated) | Source(s) |
        |--------------|------------------------------|--------------------------|-------------------------------|-----------|
        | Financial    | Revenue (JPY Billions)       | 500                      | 350                           | [SSX]     |
        | Financial    | Operating Margin (%)         | 10%                      | 7.5%                          | [SSX]     |
        | Non-Fin      | CO2 Emissions Reduction (%)  | 30%                      | (vs FY2020)                   | [SSY]     |
        | Non-Fin      | Customer Satisfaction Score  | 90                       | -                             | [SSX]     |
        | (Ensure ALL stated KPIs are listed...) | ... | ...                      | ...                           |           |
    *   Discuss key differences or areas of emphasis compared to the previous MTP for {company_name}, supported by specific examples and inline citations [SSX].

## 3. Strategic Focus Areas and Initiatives within MTP:
    *   For each major strategic pillar identified in the MTP for {company_name}:
        *   Detail the background and specific objectives of that pillar (e.g., "Pillar: Enhance Customer Experience through DX [SSX]"). Explain why it is a priority based on management commentary [SSY].
        *   Describe the relevant market conditions or industry trends cited by the company as influencing this pillar [SSZ].
        *   List specific initiatives, projects, or investments planned under this pillar (e.g., "Launch new CRM platform (Est. Cost: ¥Y Bn) [SSX]", "Invest ¥Z Bn in AI R&D [SSY]"). Include funding details, timelines, and expected outcomes if stated [SSZ].
        *   Assess the potential impact and feasibility of these initiatives based on management commentary or available data [SSX, SSY].

## 4. Execution, Progress Tracking, and Adaptation:
    *   Identify key internal and external challenges or risks acknowledged by {company_name}'s management that affect MTP execution (e.g., "Supply chain disruptions [SSX]", "Talent acquisition difficulties [SSY]").
    *   Describe the specific countermeasures or adjustments stated by {company_name} to address these challenges [SSZ].
    *   Provide the latest available progress updates against the MTP targets for {company_name} (from Section 2 table). Present progress in a **perfectly formatted Markdown table** showing KPI, Target, and Latest Actual/Forecast (with date) [SSX]. Verify data accuracy. Use '-' for missing data points only if needed for table structure.
        | KPI Name                     | Target (by FYZZZZ) | Latest Actual/Forecast (as of YYYY-MM-DD) | Progress Notes                                  | Source(s) |
        |------------------------------|--------------------|-------------------------------------------|-------------------------------------------------|-----------|
        | Revenue (JPY Billions)       | 500                | 410 (FYYYYY Actual)                       | On track / Slightly below forecast              | [SSX]     |
        | Operating Margin (%)         | 10%                | 8.2% (FYYYYY Actual)                      | Facing cost pressures, countermeasures underway | [SSY]     |
        | CO2 Emissions Reduction (%)  | 30%                | 15% (Achieved YYYY)                       | Progressing as planned                          | [SSZ]     |
        | Customer Satisfaction Score  | 90                 | -                                         | -                                               |           |
        | (Track progress for ALL KPIs listed in Sec 2) | ... | ...                                    | ...                                             |           |
    *   Highlight any significant strategic adjustments or MTP revisions announced by {company_name} in response to performance or external events (e.g., "Revised revenue target downwards in Q2 FYYYYY due to market slowdown [SSX]"), with inline citations [SSY].

## 5. General Discussion:
    *   Provide a single concluding paragraph (300-500 words) that synthesizes the key findings from Sections 1-4 regarding **{company_name}**. Clearly connect each analytical insight with inline citations (e.g., "The strategic focus on DX [SSX] aligns with the MTP targets [SSY], although execution progress shows challenges in margin improvement [SSZ]..."). Explain *why* progress is as reported, based on the analysis. Incorporate key quantitative points.
    *   Structure the discussion logically by starting with an overall assessment of the strategy and MTP ambition, discussing execution effectiveness and progress against targets, highlighting key challenges and adaptations, and concluding with strategic takeaways and outlook relevant for a Japanese audience.
    *   Do not introduce any new claims that are not derived from the previous sections and citations about **{company_name}**.

Source and Accuracy Requirements:
*   **Accuracy:** Information must be factually correct and current for **{company_name}**. Specify currency and exact dates/periods for all data, targets, and progress reports. Silently omit unverified data after exhaustive search. Verify table data meticulously. Ensure all stated MTP KPIs are captured.
*   **Traceability:** Every claim (in text, tables) must have an inline citation [SSX] linked to the final Sources list.
*   **Source Quality:** Use primarily official company sources for **{company_name}** (MTP documents, IR presentations, Annual Reports, financial results briefings) with clear and verifiable references.

{formatted_completion_template}
{formatted_final_review}
{formatted_final_source_list}
{formatted_base_formatting}
"""
    return prompt

# Regulatory Prompt
def get_regulatory_prompt(company_name: str, language: str = "Japanese", ticker: Optional[str] = None, industry: Optional[str] = None, context_company_name: str = "NESIC"):
    """Generates a prompt for analyzing the regulatory environment with enhanced entity focus."""
    context_str = f"**{company_name}**"
    if ticker: context_str += f" (Ticker: {ticker})"
    if industry: context_str += f" (Industry: {industry})"

    # Prepare formatted instruction blocks
    formatted_additional_instructions = ADDITIONAL_REFINED_INSTRUCTIONS.format(company_name=company_name, ticker=ticker or "N/A", industry=industry or "N/A")
    formatted_research_depth = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    formatted_final_review = FINAL_REVIEW_INSTRUCTION.format(company_name=company_name)
    formatted_completion_template = COMPLETION_INSTRUCTION_TEMPLATE.format(company_name=company_name)
    formatted_final_source_list = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatted_base_formatting = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    formatted_audience_reminder = AUDIENCE_CONTEXT_REMINDER.format(language=language)

    prompt = f'''
**CRITICAL FOCUS:** This entire request is *exclusively* about the specific entity: {context_str}. Verify the identity of the company for all sourced information. Do not include unrelated entities.

In-Depth Analysis of the Regulatory Environment for {company_name}

Objective: To analyze the regulatory environment impacting **{company_name}**, including key laws, licensing, supervisory bodies, market impacts, international comparisons, and recent trends, particularly as they relate to its core business and digital activities. Evaluate the company's stated compliance approaches and any enforcement actions with precise dates and references [SSX]. Focus strictly on {context_str}.

Target Audience Context: The output is for a **Japanese company** reviewing regulatory risks for potential partnership, investment, or competitive evaluation. Provide exact law/regulation names, dates, reporting periods, and detailed official source references [SSX]. {formatted_audience_reminder}

{get_language_instruction(language)}

Research Requirements:
Conduct deep research on **{company_name}**'s regulatory environment using official documents (e.g., sustainability reports, governance sections, risk factor disclosures in Annual Reports/Filings) and reputable publications (government sites, regulatory body websites, legal updates if grounded). Perform exhaustive checks across multiple sources before silently omitting unverified data. Each claim must be supported by an inline citation [SSX] with specific dates or reporting periods. Use **perfect Markdown formatting**.
{HANDLING_MISSING_INFO_INSTRUCTION}
{formatted_research_depth} # Focus on official statements and grounded regulatory info
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION}

{formatted_additional_instructions}

### 1. Key Laws, Regulations, and Systems
    *   **Major Applicable Laws/Regulations:** Identify major laws, ordinances, and ministerial regulations related to **{company_name}**'s industry ('{industry or "N/A"}') and operations (e.g., Pharmaceuticals and Medical Devices Act, Building Standards Act, Telecommunications Business Act, Financial Instruments and Exchange Act, sector-specific environmental laws) [SSX]. Specify jurisdiction (e.g., Japan, EU).
    *   **Government/Agency Guidelines & Standards:** Mention key relevant guidelines or standards issued by government bodies or agencies (e.g., METI's Green Growth Strategy Guidelines, specific cybersecurity frameworks referenced) applicable to {company_name} [SSY].
    *   **Potential Legal Amendments:** Discuss any significant upcoming or recent legal amendments mentioned by {company_name} or in grounded sources that could affect its operations (immediate to long term) [SSZ].

### 2. Licensing and Registration Systems
    *   **Industry-Specific Permits/Licenses:** Detail any necessary industry-specific permits, licenses, notifications, or registrations required for **{company_name}**'s core business (e.g., manufacturing licenses, financial services licenses, broadcast licenses) [SSX].
    *   **Acquisition & Renewal:** Comment on the perceived difficulty or cost of obtaining/maintaining these licenses for {company_name}, and any recent changes in renewal frequency or examination criteria, if discussed in sources [SSY].

### 3. Supervisory Authorities and Industry Influence
    *   **Supervisory Bodies:** Identify the main government bodies that supervise **{company_name}**'s industry or key activities (e.g., Financial Services Agency, Ministry of Health Labour and Welfare, Ministry of Internal Affairs and Communications, environmental agencies) [SSX].
    *   **Industry Associations:** Name key industry associations {company_name} is part of that issue regulations, policies, or exert lobbying influence [SSY]. Discuss the influence of these associations on {company_name} if commented upon in sources [SSZ].

### 4. Market and Business Model Impact
    *   **Competitive Environment Impact:**
        *   Analyze if regulations act as a barrier to new entrants in **{company_name}**'s market [SSX].
        *   Discuss any changes in competitive structure due to deregulation or stricter enforcement mentioned in sources affecting {company_name} [SSY].
        *   Note any competitive advantages derived by {company_name} from legislation (e.g., eligibility for specific subsidies or contracts) [SSZ].
    *   **Business Model Impact:**
        *   Detail key regulatory obligations for {company_name} (e.g., information disclosure, audit compliance, reporting requirements like ESG disclosures) [SSX].
        *   Identify regulatory restrictions impacting {company_name}'s business model (e.g., price controls, advertising restrictions, data usage limitations) [SSY].
        *   Discuss the costs and risks associated with compliance for {company_name} [SSZ].

### 5. International Context (if applicable)
    *   **Comparison for Overseas Expansion:** If **{company_name}** operates internationally or plans expansion, highlight key differences in regulations compared to major overseas markets (e.g., EU regulations, US laws relevant to the industry) based on source information related to {company_name} [SSX].
    *   **International Standards & Certifications:** Note {company_name}'s compliance status with international standards or certifications relevant to regulation (e.g., ISO standards, GDPR compliance statements, CE Mark for products) [SSY].
    *   **Trade Regulations:** Mention regulations or customs clearance systems related to imports and exports relevant to {company_name}'s business, if discussed [SSZ].

### 6. Recent Policy Trends & Developments
    *   **Latest Trends:** Summarize the latest trends in relevant policies, laws, and regulations mentioned by {company_name} or in grounded sources impacting it [SSX].
    *   **Specific Government Measures:** Detail relevant government initiatives like green policies (subsidies, carbon pricing), DX-related legislation, or support programs impacting {company_name} [SSY].
    *   **ESG-Related Mandates:** Discuss mandatory ESG reporting requirements (e.g., climate change compliance like TCFD, human capital disclosure) applicable to {company_name} [SSZ].
    *   **Social Pressure & Activism:** Mention any significant impact from social pressure or citizen/environmental group activism pushing for stricter regulations or specific corporate actions related to {company_name}, if documented [SSX].

### 7. Compliance Approach & History
    *   Detail **{company_name}**'s stated compliance approach and governance structure for regulatory matters (e.g., existence of compliance committees, specific policies, training programs) [SSX].
    *   Identify any significant publicly reported regulatory enforcement actions, fines, or controversies related to **{company_name}**'s operations (not just digital) in the last 3-5 years. Specify dates, regulatory bodies involved, outcomes (including fine amounts with currency), and company responses or remedial actions taken [SSY, SSZ]. Present clearly.

## 8. General Discussion:
    *   Provide a concluding single paragraph (300-500 words) that synthesizes the findings from Sections 1-7 regarding **{company_name}**. Clearly articulate the primary regulatory pressures {company_name} faces and assess its apparent compliance posture and risk management effectiveness, using inline citations [SSX, SSY].
    *   Structure the analysis by summarizing the key regulatory domains (general, industry-specific, international, emerging trends), evaluating the company's stated compliance strengths and any reported weaknesses or incidents, and concluding with an overall evaluation of regulatory risk tailored to a Japanese audience (considering factors like operational impact, reputational risk, potential fines, impact on strategy).
    *   Do not introduce new factual claims beyond the provided analysis and citations about **{company_name}**.

Source and Accuracy Requirements:
*   **Accuracy:** All regulatory details must be current and verifiable for **{company_name}**. Include specific law names, dates, certification details, and currency information for fines. Silently omit unverified data after exhaustive search.
*   **Traceability:** Each statement must have an inline citation [SSX] corresponding to the final Sources list.
*   **Source Quality:** Use official company disclosures for **{company_name}** (Annual Reports, Sustainability/ESG Reports, Governance sections, specific policy documents if available), government regulatory websites, and reputable news sources only if grounded by Vertex AI Search results.

{formatted_completion_template}
{formatted_final_review}
{formatted_final_source_list}
{formatted_base_formatting}
'''
    return prompt

# Crisis Prompt
def get_crisis_prompt(company_name: str, language: str = "Japanese", ticker: Optional[str] = None, industry: Optional[str] = None, context_company_name: str = "NESIC"):
    """Generates a prompt for analyzing digital crisis management and business continuity with enhanced entity focus."""
    context_str = f"**{company_name}**"
    if ticker: context_str += f" (Ticker: {ticker})"
    if industry: context_str += f" (Industry: {industry})"

    # Prepare formatted instruction blocks
    formatted_additional_instructions = ADDITIONAL_REFINED_INSTRUCTIONS.format(company_name=company_name, ticker=ticker or "N/A", industry=industry or "N/A")
    formatted_research_depth = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    formatted_final_review = FINAL_REVIEW_INSTRUCTION.format(company_name=company_name)
    formatted_completion_template = COMPLETION_INSTRUCTION_TEMPLATE.format(company_name=company_name)
    formatted_final_source_list = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatted_base_formatting = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    formatted_audience_reminder = AUDIENCE_CONTEXT_REMINDER.format(language=language)

    prompt = f'''
**CRITICAL FOCUS:** This entire request is *exclusively* about the specific entity: {context_str}. Verify the identity of the company for all sourced information. Do not include unrelated entities.

In-Depth Analysis of {company_name}'s Digital Crisis Management and Business Continuity

Objective: To analyze how **{company_name}** prepares for, manages, and responds to digital crises (e.g., cyberattacks, system outages, data breaches) and its business continuity plans (BCP) related to digital operations. Include details on past incidents with exact dates, impacts (including financial figures with specified currency if reported), company responses, and potential DX-based mitigation strategies linked to identified risks. Use inline citations [SSX]. Focus strictly on {context_str}.

Target Audience Context: This output is for a **Japanese company** assessing digital risk resilience for strategic decision-making. Provide precise data (with dates and reporting periods) and official source references [SSX]. {formatted_audience_reminder}

{get_language_instruction(language)}

Research Requirements:
Conduct thorough research on **{company_name}**'s crisis management and business continuity from official disclosures (e.g., Annual Reports, Security sections, specific incident reports if published) and reputable reports (cybersecurity news, regulatory filings if grounded). Perform exhaustive checks across multiple sources before silently omitting unverified data. Include inline citations [SSX] for every fact, with specific dates or periods. Use **perfect Markdown formatting**.
{HANDLING_MISSING_INFO_INSTRUCTION}
{formatted_research_depth} # Focus on official statements + grounded incident reports
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION}

{formatted_additional_instructions}

## 1. Crisis Management and Business Continuity:
    *   **Handling of Past Digital Crises (Last 5 Years):** Describe significant publicly reported digital crises impacting **{company_name}**. Use bullet points for each incident:
        *   **Incident Type & Date:** (e.g., Ransomware attack, approx. YYYY-MM [SSX]; Major system outage, YYYY-MM-DD [SSY]; Data breach discovered YYYY-MM [SSZ]).
        *   **Impact Details:** Describe affected systems/services, nature of data compromised (if applicable), estimated number of users/customers affected, duration of outage, and any reported financial impact (e.g., estimated recovery costs of $X million [SSX], fine of €Y million [SSY]). Be specific and cite sources.
        *   **Company Response:** Detail **{company_name}**'s public statements, communication strategy, remedial actions taken (e.g., systems restored by [Date] [SSX], external cybersecurity experts engaged [SSY], free credit monitoring offered [SSZ]), and any reported changes to security practices or governance resulting from the incident [SSW].
        *   **Lessons Learned (if stated):** Include any officially stated lessons learned or future preventative measures mentioned by **{company_name}** [SSX].
    *   **Stated Preparedness and Planning:**
        *   Explain **{company_name}**'s stated approach to digital crisis management. Mention existence of an Incident Response Plan (IRP), Cyber Incident Response Team (CIRT), or similar structures if documented [SSX].
        *   Describe **{company_name}**'s stated approach to Business Continuity Planning (BCP) specifically for digital operations. Mention existence of BCP documents, disaster recovery (DR) sites, recovery time objectives (RTOs) or recovery point objectives (RPOs) if disclosed [SSY].
        *   Outline the governance structure within **{company_name}** involved in overseeing digital risk, crisis management, and BCP (e.g., Board committee oversight [SSX], role of CISO/CIO [SSY]). Cite specific sources.
        *   Mention any regular drills, simulations, or third-party audits related to crisis response or BCP conducted by **{company_name}**, if disclosed [SSZ].
    *   **Risk Forecasting & DX Mitigation (Analysis):**
        *   Discuss any forward-looking risk assessments or forecasting of potential future crisis impacts mentioned in **{company_name}**'s reports (e.g., risk factors section: natural disasters affecting data centers, major supply chain digital disruptions) [SSX].
        *   Based on the identified risks for {company_name} [SSX] or past incident types [SSY], analyze and propose relevant Digital Transformation (DX) based solutions or mitigation strategies that could enhance its resilience (e.g., "Given {company_name}'s stated risk of seismic activity near HQ [SSX], DX solutions like geographically distributed cloud backups and enhanced remote work capabilities could mitigate operational disruption."). *This analysis should logically connect identified risks to known DX capabilities.*

## 2. General Discussion:
    *   Provide a concluding single paragraph (300-500 words) synthesizing the findings from Section 1 regarding **{company_name}**. Assess its apparent resilience to digital disruptions based on its history of incidents, responses, stated preparedness, and the potential application of DX for mitigation. Use inline citations explicitly (e.g., "The company's response to the YYYY incident [SSX] suggests an established protocol, though the stated RTO [SSY] raises questions... The identified risk of X [SSZ] could potentially be addressed by DX initiatives focused on Y...").
    *   Structure the discussion logically, starting with a summary of the incident history and response effectiveness, followed by an evaluation of the stated preparedness measures (IRP, BCP) and risk awareness, incorporating the potential role of DX, and concluding with an assessment of overall digital resilience for {company_name}, identifying potential strengths and weaknesses relevant to a Japanese audience considering partnership or investment.
    *   Do not introduce any new claims not supported by the previous analysis and citations about **{company_name}**.

Source and Accuracy Requirements:
*   **Accuracy:** All incident details, dates, financial impacts (with currency), and response measures must be current and verifiable against grounded sources for **{company_name}**. Silently omit unverified data after exhaustive search. Proposed DX solutions should be logical extensions of identified risks/tech capabilities.
*   **Traceability:** Every factual claim must include an inline citation [SSX] linked to a source in the final Sources list.
*   **Source Quality:** Prioritize official company disclosures for **{company_name}** (press releases on incidents, security sections in reports). Use reputable news or cybersecurity firm reports *only* if grounded by Vertex AI Search results.

{formatted_completion_template}
{formatted_final_review}
{formatted_final_source_list}
{formatted_base_formatting}
'''
    return prompt

# Digital Transformation Prompt
def get_digital_transformation_prompt(company_name: str, language: str = "Japanese", ticker: Optional[str] = None, industry: Optional[str] = None, context_company_name: str = "NESIC"):
    """Generates a prompt for analyzing DX strategy and execution with enhanced entity focus."""
    context_str = f"**{company_name}**"
    if ticker: context_str += f" (Ticker: {ticker})"
    if industry: context_str += f" (Industry: {industry})"

    # Prepare formatted instruction blocks
    formatted_additional_instructions = ADDITIONAL_REFINED_INSTRUCTIONS.format(company_name=company_name, ticker=ticker or "N/A", industry=industry or "N/A")
    formatted_research_depth = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    formatted_final_review = FINAL_REVIEW_INSTRUCTION.format(company_name=company_name)
    formatted_completion_template = COMPLETION_INSTRUCTION_TEMPLATE.format(company_name=company_name)
    formatted_final_source_list = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatted_base_formatting = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    formatted_audience_reminder = AUDIENCE_CONTEXT_REMINDER.format(language=language)

    prompt = f"""
**CRITICAL FOCUS:** This entire request is *exclusively* about the specific entity: {context_str}. Verify the identity of the company for all sourced information. Do not include unrelated entities.

In-Depth Analysis of {company_name}'s Digital Transformation (DX) Strategy and Execution

Objective: To analyze **{company_name}**'s Digital Transformation (DX) strategy, including its vision, the rationale behind it, key priorities, major investments, and specific case studies of digital initiatives. Evaluate also how DX integrates compliance and crisis management considerations. Use precise data (e.g., specific investment amounts with currency, dates) supported by inline citations [SSX]. Focus strictly on {context_str}.

Target Audience Context: The analysis is prepared for a **Japanese company** assessing {company_name}'s digital maturity and strategy. Therefore, it must be detailed, with exact figures (specifying currency and reporting periods) and official source references [SSX]. {formatted_audience_reminder}

{get_language_instruction(language)}

Research Requirements:
Conduct detailed research on **{company_name}**'s DX journey using official sources (company reports, dedicated DX sections on website, investor presentations, press releases) and reputable analyses (if grounded). Perform exhaustive checks across multiple sources before silently omitting unverified data. Every claim, financial figure, and example must include an inline citation [SSX] and specific dates or periods. Use **perfect Markdown formatting**. Use '-' for missing data points in tables only if needed for structure. Verify data accuracy.
{HANDLING_MISSING_INFO_INSTRUCTION}
{formatted_research_depth} # Focus on DX strategy documents, IR materials
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION}

{formatted_additional_instructions}

## 1. DX Strategy Overview:
    *   Outline **{company_name}**'s overall digital transformation vision and strategic goals (e.g., "To become a data-driven organization by YYYY [SSX]", "Enhance customer experience through personalized digital services [SSY]"). Use verbatim statements where possible, with precise references and inline citations [SSZ].
    *   **Analyze the Rationale:** Based on management commentary or strategic documents for {company_name}, explain the *reasons* behind its DX strategy (e.g., "What business problems is DX aiming to solve? How does it link to competitive pressures or the overall corporate vision?") [SSX, SSY].
    *   Identify the key strategic priorities or pillars of {company_name}'s DX strategy (e.g., "Cloud Migration", "AI & Analytics adoption", "Workforce Digital Upskilling", "Supply Chain Optimization") with specific details and start/end dates if part of a formal plan [SSX].
    *   List major DX initiatives or projects for {company_name} currently underway or recently completed under these pillars. Include specific objectives and target outcomes for each initiative if stated (e.g., "Project Phoenix: Cloud migration targeting X% cost reduction by YYYY [SSX]") [SSY].

## 2. DX Investments Analysis (Last 3 Fiscal Years):
    *   Analyze **{company_name}**'s investments specifically allocated to DX, if disclosed. Provide detailed breakdowns by initiative or area (e.g., cloud infrastructure, AI development, cybersecurity enhancements related to DX) if available, potentially in a **perfectly formatted Markdown table**. Include specific investment amounts (with currency), funding sources (if mentioned), timelines, and reporting periods, with inline citations [SSX]. Verify data accuracy. Use '-' for missing data points only if needed for table structure.
        | DX Investment Area        | FYXXXX (JPY M) | FYYYYY (JPY M) | FYZZZZ (JPY M) | Notes / Key Projects        | Source(s) |
        |---------------------------|----------------|----------------|----------------|---------------------------|-----------|
        | Cloud Migration           |                |                |                | e.g., AWS/Azure spend     | [SSX]     |
        | AI & Data Analytics       |                |                |                | e.g., Platform build      | [SSY]     |
        | Process Automation (RPA)  | -              |                |                |                           | [SSZ]     |
        | Customer Facing Platforms |                |                |                | e.g., New CRM/App dev     | [SSW]     |
        | Total DX Spend (if stated)|                |                |                |                           | [SSV]     |
    *   Describe overall investment trends in DX for {company_name} over the last 3 years (e.g., increasing significantly [SSX], stable focus on specific areas [SSY]) with supporting data and analysis of the investment allocation strategy [SSZ].

## 3. DX Case Studies & Implementation Examples:
    *   Provide detailed descriptions of 2-3 specific DX implementation examples or case studies highlighted by **{company_name}**. For each example, describe:
        *   **Initiative Name & Goal:** (e.g., "Smart Factory Project [SSX]", "Goal: Improve OEE by 15%")
        *   **Technology Involved:** (e.g., IoT sensors, predictive analytics platform, cloud data lake) [SSY]
        *   **Implementation Details:** (e.g., Phased rollout across 3 plants starting YYYY [SSX], Partnership with Vendor V [SSZ])
        *   **Measurable Outcomes & Business Impact:** Quantify results where possible (e.g., "Achieved 12% improvement in OEE in Plant A [SSX]", "Reduced manual reporting time by X hours/week [SSY]", "Enabled new service generating ¥Z million in first year [SSZ]"). Specify currency and reporting period. Use only company-reported outcomes for {company_name}.
        *   **Rationale for Highlighting:** Explain why this example was likely chosen by {company_name} (e.g., flagship project demonstrating AI capability [SSX], successful cross-functional collaboration [SSY]).

## 4. Regulatory Environment, Compliance, and Crisis Management (Integration with DX):
    *   Briefly summarize the key regulatory trends previously identified (in the Regulatory prompt context, if available) that directly impact **{company_name}**'s DX strategy (e.g., data localization requirements affecting cloud choices [SSX], security standards for connected devices [SSY]). Cite specific laws or standards and sources.
    *   Describe how **{company_name}** states it integrates compliance considerations into its DX efforts (e.g., "Privacy by Design principles applied in new app development [SSX]", "Mandatory security reviews for all new cloud services [SSY]"). Provide specific examples from official sources [SSZ].
    *   Mention how digital crisis management and business continuity considerations are addressed within the context of major DX initiatives at **{company_name}** (e.g., "Disaster recovery plans tested for new cloud platform [SSX]", "Redundancy built into critical digital infrastructure [SSY]"). Cite official examples where available [SSZ].

## 5. General Discussion:
    *   Provide a concluding single paragraph (300-500 words) that synthesizes the findings from Sections 1-4 regarding **{company_name}**. Assess the coherence, ambition, rationale, and execution progress of {company_name}'s DX strategy. Explicitly link data points and examples using inline citations (e.g., "The strategic rationale focusing on customer experience [SSX] drives the significant investment in CRM [SSY], and early results from case studies [SSZ] suggest potential, though scaling remains a challenge...").
    *   Structure your discussion logically—start with an overview of the DX strategy's clarity and focus, evaluate the investment commitment and implementation effectiveness based on examples, integrate the handling of compliance and risk, and conclude with an assessment of the DX maturity and outlook relevant for a Japanese audience.
    *   Do not introduce new facts outside of the presented analysis and citations about **{company_name}**.

Source and Accuracy Requirements:
*   **Accuracy:** All data must be current and verified for **{company_name}**. Specify currency and reporting period for every monetary value, investment figure, and outcome metric. Silently omit unverified data after exhaustive search. Verify table data meticulously.
*   **Traceability:** Every fact must include an inline citation [SSX] that corresponds to a source in the final Sources list.
*   **Source Quality:** Prioritize official company disclosures for **{company_name}** (Annual Reports, IR presentations, specific DX reports/webpages) and reputable research *only if grounded* by Vertex AI Search results.

{formatted_completion_template}
{formatted_final_review}
{formatted_final_source_list}
{formatted_base_formatting}
"""
    return prompt

# Business Structure Prompt
def get_business_structure_prompt(company_name: str, language: str = "Japanese", ticker: Optional[str] = None, industry: Optional[str] = None, context_company_name: str = "NESIC"):
    """Generates a prompt for analyzing business structure, geographic footprint, ownership, and leadership linkages with enhanced entity focus."""
    context_str = f"**{company_name}**"
    if ticker: context_str += f" (Ticker: {ticker})"
    if industry: context_str += f" (Industry: {industry})"

    # Prepare formatted instruction blocks
    formatted_additional_instructions = ADDITIONAL_REFINED_INSTRUCTIONS.format(company_name=company_name, ticker=ticker or "N/A", industry=industry or "N/A")
    formatted_research_depth = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    formatted_final_review = FINAL_REVIEW_INSTRUCTION.format(company_name=company_name)
    formatted_completion_template = COMPLETION_INSTRUCTION_TEMPLATE.format(company_name=company_name)
    formatted_final_source_list = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatted_base_formatting = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    formatted_audience_reminder = AUDIENCE_CONTEXT_REMINDER.format(language=language)

    business_structure_completion_guidance = textwrap.dedent(f"""\
    **Critical Data Focus for Business Structure:**

    *   **Priority Information:** Strive to provide, based on exhaustive search of verifiable sources for **{company_name}**:
        1. The business segment breakdown table using the company's reported segmentation and metrics (e.g., revenue, premiums in-force), with at least the most recent fiscal year data (% and absolute value) [SSX].
        2. The geographic segment breakdown table using the company's reported segmentation and metrics, with at least the most recent fiscal year data (% and absolute value) [SSX].
        3. The top 3-5 major shareholders table with percentages and as-of dates [SSX].

    *   **Check for Alternative Metrics:** If standard revenue segmentation is not the primary method used by {company_name} (e.g., in MTP targets, core reporting for industries like insurance), look for and report the segmentation based on the key metric the company uses (e.g., premiums in-force, assets under management). Clearly define the metric used based on the source.
    *   **Partial Data Handling:** If only partial data (e.g., 1-2 years instead of 3) is available for segments/geography after exhaustive search for {company_name}, present the available data clearly in the tables, noting the timeframe covered (e.g., in the text analyzing the table: "Data for FY2022-2023 shows..." [SSX]). Do not state unavailability. Proceed with analysis based on the available timeframe.

    *   **Verification:** Before completing each section, internally verify:
        * All priority information points are addressed using available grounded data for {company_name}.
        * At least one full fiscal year of data is provided for segments and geography tables if verifiable, using the correct metric/segmentation.
        * All available verified ownership information is included in the table.
        * Each data point includes proper inline citation [SSX] and data verified against source.
    """)

    prompt = f"""
**CRITICAL FOCUS:** This entire request is *exclusively* about the specific entity: {context_str}. Verify the identity of the company for all sourced information. Do not include unrelated entities.

In-Depth Analysis of {company_name}'s Business Structure, Geographic Footprint, Ownership, and Strategic Vision Linkages

Objective: To analytically review **{company_name}**'s operational structure (by business and geography, using company-reported metrics), ownership composition, and how these elements link to leadership's stated strategic vision. Include specific figures (with currency and fiscal year), and reference official sources (e.g., Annual Report, IR materials, Filings) with inline citations [SSX]. Focus strictly on {context_str}.

Target Audience Context: This output is intended for a **Japanese company** performing market analysis and partnership evaluation. Present all claims with exact dates, detailed quantitative figures, and clear source references [SSX]. {formatted_audience_reminder}

{get_language_instruction(language)}

Research Requirements:
Perform a critical analysis using official sources for **{company_name}** (Annual/Integrated Reports, IR materials, filings like Yukashoken Hokokusho, corporate governance documents). Supplement with reputable secondary sources only when necessary and grounded. Perform exhaustive checks across multiple sources before silently omitting unverified data. Ensure each claim includes an inline citation [SSX] and precise data (e.g., "as of YYYY-MM-DD"). Use **perfect Markdown tables**. Verify data accuracy. Use '-' for missing data points only if needed for table structure. Look for the primary segmentation metric used by the company (e.g., revenue, premiums in-force).
{HANDLING_MISSING_INFO_INSTRUCTION}
{formatted_research_depth}
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION}
{business_structure_completion_guidance}

{formatted_additional_instructions}

## 1. Business Segment Analysis (Last 3 Fiscal Years):
    *   List the reported business segments for **{company_name}** using official descriptions. Identify the primary metric used for segmentation (e.g., Revenue, Premiums In-Force). Include a **perfectly formatted Markdown table** with consolidated figures for that metric (specify metric, currency, and fiscal year) and composition ratios (%), with each data point referenced [SSX]. Ensure totals sum correctly if verifiable. Verify data accuracy. Use '-' for missing data points only if needed for table structure.
        | Segment Name | FYXXXX Metric Value (Unit) | FYXXXX (%) | FYYYYY Metric Value (Unit) | FYYYYY (%) | FYZZZZ Metric Value (Unit) | FYZZZZ (%) | Source(s) |
        |--------------|--------------------------|------------|--------------------------|------------|--------------------------|------------|-----------|
        | Segment A    |                          |            |                          |            |                          |            | [SSX]     |
        | Segment B    |                          |            |                          |            |                          |            | [SSY]     |
        | Segment C    |                          |            | -                      | -          |                          |            | [SSZ]     |
        | Adjustments  |                          |            |                          |            |                          |            | [SSW]     |
        | **Total**    |                          | **100%**   |                          | **100%**   |                          | **100%**   | [SSV]     |
        *(Note: Clearly label the 'Metric Value' column header with the specific metric used, e.g., "FYXXXX Revenue (JPY M)" or "FYXXXX Premiums In-Force (JPY Bn)")*
    *   For each major segment of {company_name}, briefly describe its products/services [SSX] and analyze significant trends (e.g., growth/decline rates YoY calculated from table data, changes in contribution ratio) with specific percentages and dates [SSY]. Identify the fastest growing and/or most profitable segments based on available data (growth in the reported metric, operating income/margin if reported per segment in source documents) [SSZ].

## 2. Geographic Segment Analysis (Last 3 Fiscal Years):
    *   List the geographic regions or segments as reported by **{company_name}** (e.g., Japan, North America, Europe, Asia). Identify the primary metric used for geographic segmentation. Include a **perfectly formatted Markdown table** with corresponding figures (specify metric, currency, fiscal year) and composition ratios (%), ensuring totals sum correctly if verifiable [SSX]. Verify data accuracy. Use '-' for missing data points only if needed for table structure.
        | Geographic Region | FYXXXX Metric Value (Unit) | FYXXXX (%) | FYYYYY Metric Value (Unit) | FYYYYY (%) | FYZZZZ Metric Value (Unit) | FYZZZZ (%) | Source(s) |
        |-------------------|--------------------------|------------|--------------------------|------------|--------------------------|------------|-----------|
        | Japan             |                          |            |                          |            |                          |            | [SSX]     |
        | North America     |                          |            |                          |            |                          |            | [SSY]     |
        | Europe            |                          |            |                          |            |                          |            | [SSZ]     |
        | Asia (ex-Japan)   |                          |            |                          |            |                          |            | [SSW]     |
        | Other             |                          |            | -                      | -          |                          |            | [SSV]     |
        | Adjustments       |                          |            |                          |            |                          |            | [SSU]     |
        | **Total**         |                          | **100%**   |                          | **100%**   |                          | **100%**   | [SST]     |
        *(Note: Clearly label the 'Metric Value' column header with the specific metric used, e.g., "FYXXXX Revenue (JPY M)" or "FYXXXX Premiums In-Force (JPY Bn)")*
    *   Analyze regional trends for {company_name} (growth/decline YoY calculated from table data, changes in contribution) with specific supporting data [SSX]. Identify key growth markets and declining markets with specific figures [SSY]. Note any stated plans for geographic expansion or contraction with dates and details mentioned in reports [SSZ].

## 3. Major Shareholders & Ownership Structure:
    *   Describe the overall ownership type for **{company_name}** (e.g., publicly traded on TSE Prime [SSX], privately held) with specific details [SSY].
    *   List the top 5-10 major shareholders of {company_name} in a **perfectly formatted Markdown table** with exact names (as reported, e.g., trust banks), precise ownership percentages, shareholder type (institutional, individual, government, etc.), and the 'as of' date for the data [SSX]. Note any significant changes in top holders over the past year if reported [SSY]. Verify data. Use '-' for missing data points only if needed for table structure.
        | Shareholder Name          | Ownership % | Shareholder Type     | As of Date   | Source(s) |
        |---------------------------|-------------|----------------------|--------------|-----------|
        | The Master Trust Bank ... | 9.8%        | Institutional (Trust)| YYYY-MM-DD   | [SSX]     |
        | Custody Bank of Japan ... | 7.5%        | Institutional (Trust)| YYYY-MM-DD   | [SSX]     |
        | [Individual Name]         | -           | Individual (Founder) | YYYY-MM-DD   | [SSY]     |
        | ...                       | ...         | ...                  | ...          |           |
    *   Include key figures for {company_name} like Total Shares Outstanding [SSX], Treasury Stock [SSY], and Free Float percentage (if available) [SSZ], all with 'as of' dates. Mention controlling shareholders or parent company relationships if applicable [SSX]. Discuss any known cross-shareholdings with major business partners if material and reported [SSY].
    *   Comment briefly on ownership concentration for {company_name} and potential implications (e.g., high institutional ownership suggests focus on governance [SSX], stable founder ownership may influence long-term strategy [SSY]).

## 4. Corporate Group Structure:
    *   Describe the parent-subsidiary relationships and overall corporate group structure for **{company_name}** based on official filings or reports (e.g., list of major subsidiaries in Annual Report Appendix [SSX]). Note existence/location of group structure charts if found [SSY].
    *   List key operating subsidiaries of {company_name} in a **perfectly formatted Markdown table**, including their official names, primary business functions/segments they operate in, country/region of incorporation, and ownership percentage by the parent company (if stated) [SSX]. Verify data. Use '-' for missing data points only if needed for table structure.
        | Subsidiary Name             | Primary Business Function / Segment | Country/Region | Ownership % | Source(s) |
        |-----------------------------|-------------------------------------|----------------|-------------|-----------|
        | [Company Name] USA Inc.     | Sales & Marketing (Segment A)       | USA            | 100%        | [SSX]     |
        | [Company Name] Europe GmbH  | R&D, Manufacturing (Segment B)      | Germany        | -           | [SSX]     |
        | Joint Venture XYZ Co., Ltd. | Specific Technology Development     | Japan          | 50%         | [SSY]     |
        | ...                         | ...                                 | ...            | ...         |           |
    *   Note any recent major restructuring, mergers, divestitures, or acquisitions impacting the group structure of {company_name}, providing specific dates and transaction details if available and material [SSY].

## 5. Leadership Strategic Outlook & Vision (Verbatim Quotes - Linkages):
    *   Provide verbatim quotes from key executives of **{company_name}** (CEO, Chairman, and optionally CFO/CSO) that specifically address:
        * Long-term strategic vision related to business segments or geographic focus [SSX].
        * Plans for specific business segment growth/rationalization or geographic expansion [SSY].
        * Comments linking the corporate structure (including subsidiaries or group reorganization) to strategy execution [SSZ].
        * Comments on ownership structure or major shareholder relations (if any and if public) [SSW].
    *   Each quote must have its source cited immediately after it (e.g., "(Source: Integrated Report 2023, p. 5)") and an inline citation [SSX] confirming the quote's origin.
    *   Where possible, explicitly connect a quote to a specific finding in Sections 1-4 (e.g., "Reflecting the growth in the Asian market shown in Section 2 [SSY], the CEO stated, '...' [SSX]").

## 6. General Discussion:
    *   Provide a single concluding paragraph (300-500 words) synthesizing the findings from Sections 1-5 regarding **{company_name}**. Clearly link analytical insights and comparisons using inline citations (e.g., "The shift in segment focus towards Segment B [SSX] aligns with the CEO's stated focus [SSY], but geographic concentration in Japan [SSZ] remains a key factor influencing growth prospects..."). Incorporate key quantitative points.
    *   Address specifically:
        * The alignment (or misalignment) between the business/geographic structure (using the relevant metric) and the stated strategic vision/MTP for {company_name} [SSX, SSY].
        * How the ownership structure may influence business decisions or governance at {company_name} [SSZ].
        * Key opportunities or challenges presented by {company_name}'s current segment mix and geographic footprint [SSW].
        * Potential future developments or necessary structural changes based on {company_name}'s current structure, trends, and leadership comments [SSX, SSY].
    *   Structure your discussion logically, starting with a summary of business and geographic drivers, assessing ownership influence and leadership vision alignment, and concluding with strategic implications for a Japanese audience.
    *   Do not introduce new unsupported claims about **{company_name}**.

Source and Accuracy Requirements:
*   **Accuracy:** Ensure all data is precise for **{company_name}**, with currency and fiscal year reported for numerical values. Use official names for segments, regions, shareholders, and subsidiaries. Use the correct segmentation metric as reported by the company. Silently omit unverified data after exhaustive search. Verify table data meticulously.
*   **Traceability:** Every fact (in text, tables) must include an inline citation [SSX] corresponding to the final Sources list.
*   **Source Quality:** Use only primary official sources for **{company_name}** (Annual/Integrated Reports, Financial Statements, Filings, IR Presentations, Governance Reports) with clear documentation references.

{formatted_completion_template}
{formatted_final_review}
{formatted_final_source_list}
{formatted_base_formatting}
"""
    return prompt

# Vision Prompt
def get_vision_prompt(company_name: str, language: str = "Japanese", ticker: Optional[str] = None, industry: Optional[str] = None, context_company_name: str = "NESIC"):
    """Generates a prompt focused on company vision and strategic purpose with enhanced entity focus."""
    context_str = f"**{company_name}**"
    if ticker: context_str += f" (Ticker: {ticker})"
    if industry: context_str += f" (Industry: {industry})"

    # Prepare formatted instruction blocks
    formatted_additional_instructions = ADDITIONAL_REFINED_INSTRUCTIONS.format(company_name=company_name, ticker=ticker or "N/A", industry=industry or "N/A")
    formatted_research_depth = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    formatted_final_review = FINAL_REVIEW_INSTRUCTION.format(company_name=company_name)
    formatted_completion_template = COMPLETION_INSTRUCTION_TEMPLATE.format(company_name=company_name)
    formatted_final_source_list = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatted_base_formatting = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    formatted_audience_reminder = AUDIENCE_CONTEXT_REMINDER.format(language=language)

    prompt = f"""
**CRITICAL FOCUS:** This entire request is *exclusively* about the specific entity: {context_str}. Verify the identity of the company for all sourced information. Do not include unrelated entities.

Analysis of {company_name}'s Strategic Vision and Purpose

Objective: To provide a detailed analysis of **{company_name}**'s officially stated vision, mission, or purpose. Break down its core components (pillars, strategic themes), explain how progress is measured using specific KPIs mentioned in relation to the vision, and assess stakeholder focus. Include exact quotes, dates, and reference all information using inline citations [SSX]. Use the latest available sources. Focus strictly on {context_str}.

Target Audience Context: This analysis is for a **Japanese company** assessing strategic alignment and long-term direction. Present precise information with clear source references and detailed explanations (e.g., "as per the Integrated Report 2023, p.12, [SSX]") {formatted_audience_reminder}

{get_language_instruction(language)}

Research Requirements:
Conduct in-depth research using official sources for **{company_name}** such as the company website (strategy, about us, IR, sustainability pages), Annual/Integrated Reports, MTP documents, and press releases detailing the corporate vision or purpose. Perform exhaustive checks across multiple sources before silently omitting unverified data. Every claim or data point must have an inline citation [SSX] and include specific dates or document references. Use **perfect Markdown formatting**. Verify data accuracy. Use '-' for missing data points in tables only if needed for structure.
{HANDLING_MISSING_INFO_INSTRUCTION}
{formatted_research_depth} # Focus on vision/mission statements, strategic pillars
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION}

{formatted_additional_instructions}

## 1. Company Vision and Strategy Elements:
    *   **Vision/Purpose/Mission Statement:** Present **{company_name}**'s official statement(s) verbatim (e.g., "Our Purpose is to...") with an inline citation [SSX] identifying the source document and date (e.g., Integrated Report 2023 [SSX]). Explain its core message and intended timescale (e.g., Vision 2030) [SSY].
    *   **Strategic Vision Components/Pillars:** List and explain the key strategic themes, values, or pillars that underpin the vision for {company_name} (e.g., "Innovation", "Sustainability", "Customer Centricity") as defined in official documents [SSX]. Provide brief definitions or explanations for each pillar based on the source [SSY].
    *   **Vision Measures / KPIs:** Identify specific measures or Key Performance Indicators (KPIs) that **{company_name}** explicitly links to tracking progress towards its overall vision or purpose (these might be high-level MTP targets or specific ESG goals mentioned in the vision context). Present these in a list or **perfectly formatted Markdown table** if multiple and verifiable, including the KPI name, the target (if specified, with date/period), and how it relates to the vision pillar [SSX]. Verify data. Use '-' for missing data points only if needed for table structure.
        | Vision Pillar      | Linked KPI                    | Target/Goal (if specified)     | Source(s) |
        |--------------------|-------------------------------|--------------------------------|-----------|
        | Sustainability     | Scope 1+2 CO2 Reduction       | 50% reduction by 2030 vs 2020  | [SSX]     |
        | Innovation         | % Revenue from New Products   | -                              | [SSY]     |
        | Customer Centricity| Net Promoter Score (NPS)      | > 50 by 2027                   | [SSZ]     |
        | ...                | ...                           | ...                            |           |
    *   ***Stakeholder Focus:*** Analyze how the vision statement and its supporting pillars for {company_name} explicitly address or prioritize key stakeholder groups (e.g., customers, employees, shareholders, society, environment) based on the language used in official communications [SSX]. Provide specific examples or quotes [SSY].

## 2. General Discussion:
    *   Provide a concluding single paragraph (300-500 words) that synthesizes the information in Section 1 regarding **{company_name}**. Evaluate the clarity, ambition, distinctiveness, and internal coherence of the stated vision and its components. Use inline citations to link back to specific elements (e.g., "The vision's focus on sustainability [SSX] is clearly measured by the CO2 reduction KPI [SSY], demonstrating commitment... However, the link between the 'Innovation' pillar and specific KPIs appears less defined [SSZ] based on available public disclosures..."). Incorporate key quantitative points if available.
    *   Structure the analysis logically—start with an overall summary of the vision's core message, discuss the strength and measurability of its components and stakeholder considerations, and finally evaluate its potential effectiveness in guiding strategy and its relevance for a Japanese audience assessing long-term direction.
    *   Do not introduce new claims beyond the synthesized findings from Section 1 and citations about **{company_name}**.

Source and Accuracy Requirements:
*   **Accuracy:** Ensure all statements, quotes, and KPIs for **{company_name}** are accurately represented from official sources and current as of the cited document date. Specify currency/units for KPIs where applicable. Silently omit unverified data after exhaustive search. Verify table data.
*   **Traceability:** Every claim must have an inline citation [SSX] that corresponds to a source in the final Sources list.
*   **Source Quality:** Use primarily official company documents for **{company_name}** (Integrated Reports, dedicated Vision/Purpose web pages, MTP overviews, Sustainability Reports) and well-documented press releases related to strategy announcements.

{formatted_completion_template}
{formatted_final_review}
{formatted_final_source_list}
{formatted_base_formatting}
"""
    return prompt

# Management Message Prompt
def get_management_message_prompt(company_name: str, language: str = "Japanese", ticker: Optional[str] = None, industry: Optional[str] = None, context_company_name: str = "NESIC"):
    """Generates a prompt for collecting strategic quotes from leadership with enhanced entity focus."""
    context_str = f"**{company_name}**"
    if ticker: context_str += f" (Ticker: {ticker})"
    if industry: context_str += f" (Industry: {industry})"

    # Prepare formatted instruction blocks
    formatted_additional_instructions = ADDITIONAL_REFINED_INSTRUCTIONS.format(company_name=company_name, ticker=ticker or "N/A", industry=industry or "N/A")
    formatted_research_depth = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name)
    formatted_final_review = FINAL_REVIEW_INSTRUCTION.format(company_name=company_name)
    formatted_completion_template = COMPLETION_INSTRUCTION_TEMPLATE.format(company_name=company_name)
    formatted_final_source_list = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language)
    formatted_base_formatting = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    formatted_audience_reminder = AUDIENCE_CONTEXT_REMINDER.format(language=language)

    prompt = f"""
**CRITICAL FOCUS:** This entire request is *exclusively* about the specific entity: {context_str}. Verify the identity of the company and the speaker for all sourced information. Do not include unrelated entities.

Detailed Leadership Strategic Outlook (Verbatim Quotes) for {company_name}

Objective: To compile a collection of direct, verbatim strategic quotes from **{company_name}**'s senior leadership (primarily CEO and Chairman, but also including other key C-suite executives like CFO, CSO, CTO, COO, or relevant BU Heads if their verifiable quotes offer significant strategic insight) that illustrate the company's strategic direction, key priorities, future plans, market outlook, and responses to major challenges. Each quote must be accurately transcribed with an immediate source citation in parentheses and an inline citation [SSX] confirming its origin. Focus strictly on leadership of {context_str}.

Target Audience Context: This information is for a **Japanese company** that requires a clear understanding of leadership's strategic communication and tone. Ensure that every quote includes the speaker's name and title, the exact source document/event, date, and page/timestamp if available [SSX]. {formatted_audience_reminder}

{get_language_instruction(language)}

Research Requirements:
Conduct focused research on recent (last 1-2 years) official communications from **{company_name}**'s leadership (e.g., CEO/Chairman messages in Annual/Integrated Reports, Earnings Call Transcripts Q&A sections, Investor Day presentations, Keynote speeches, official interviews published by reputable sources if grounded). Perform exhaustive checks across multiple sources before silently omitting unverified quotes. Extract strategically relevant verbatim quotes. Each quote must have an inline citation [SSX] and be followed by its specific source reference in parentheses. Use **perfect Markdown formatting**, especially for the quote blocks.
{HANDLING_MISSING_INFO_INSTRUCTION}
{formatted_research_depth} # Focus on primary comms: Reports, Transcripts, IR events
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION}
{ANALYSIS_SYNTHESIS_INSTRUCTION} # Focus synthesis on themes within quotes

{formatted_additional_instructions}

## 1. Leadership Strategic Outlook (Verbatim Quotes):

### [CEO Full Name], [CEO Title] (of {company_name})
*   Provide a brief 1-2 sentence summary of the key strategic themes reflected in the CEO's quotes below (e.g., Emphasis on digital transformation and global markets during FY2023 reporting [SSX]). Cite the source range.
*   **Quote 1 (Theme: e.g., Long-Term Vision):**
    > "..." [SSX]
    (Source: [Document/Event Name], [Date], [Page/Timestamp if available])
*   **Quote 2 (Theme: e.g., Key Challenge Response):**
    > "..." [SSY]
    (Source: [Document/Event Name], [Date], [Page/Timestamp if available])
*   **Quote 3 (Theme: e.g., Growth Strategy):**
    > "..." [SSZ]
    (Source: [Document/Event Name], [Date], [Page/Timestamp if available])
*   **Quote 4 (Theme: e.g., Market Outlook):**
    > "..." [SSW]
    (Source: [Document/Event Name], [Date], [Page/Timestamp if available])
*   *(Add more quotes if particularly insightful and verifiable, aim for 3-5 key strategic quotes)*

### [Chairman Full Name], [Chairman Title] (of {company_name}, if distinct from CEO and provides verifiable strategic commentary)
*   Provide a brief 1-2 sentence summary of key themes in the Chairman's quotes (include date range) [SSX].
*   **Quote 1 (Theme: e.g., Governance/Sustainability):**
    > "..." [SSV]
    (Source: [Document/Event Name], [Date], [Page/Timestamp if available])
*   **Quote 2 (Theme: e.g., Long-term Perspective):**
    > "..." [SSU]
    (Source: [Document/Event Name], [Date], [Page/Timestamp if available])
*   *(Add more quotes if available, verifiable, and strategically relevant, aim for 2-3)*

### [Other Key Executive Name], [Title] (e.g., CFO, CSO, CTO, COO, BU Head of {company_name} - Include significant, verifiable strategic quotes)
*   Provide a brief 1-2 sentence summary of their strategic focus area reflected in verifiable quotes [SSX].
*   **Quote 1 (Theme: e.g., Financial Strategy / Tech Roadmap / Operational Excellence):**
    > "..." [SST]
    (Source: [Document/Event Name], [Date], [Page/Timestamp if available])
*   *(Include 1-3 highly relevant, verifiable quotes per key executive if applicable)*

## 2. General Discussion:
    *   Provide a concluding single paragraph (300-500 words) synthesizing the key strategic messages, priorities, and tone conveyed *exclusively* through the collected, verifiable quotes from **{company_name}**'s leadership in Section 1. Identify recurring themes, potential shifts in focus, or areas where different executives provide complementary perspectives. Use inline citations to link back to specific quotes or speakers (e.g., "The CEO's emphasis on digital innovation [SSX, SSZ] aligns with the CTO's focus on AI investment [SST], suggesting a unified direction... However, the Chairman's cautionary note on governance [SSV] highlights potential execution risks..."). Consider potential DX opportunities or challenges implied by the leadership messages [SSX].
    *   Structure your analysis logically: summarize the dominant strategic narrative from leadership based on the quotes, highlight any nuances or potential tensions between messages, and conclude with an assessment of the clarity and consistency of the strategic communication relevant for a Japanese audience interpreting leadership signals.
    *   Do not introduce any new factual claims or analysis beyond what is directly supported by the quotes provided and cited about **{company_name}**.

Source and Accuracy Requirements:
*   **Accuracy:** Every quote must be verbatim, correctly attributed to the speaker (with title) from **{company_name}**, and include precise source details (document/event, date, page/time if possible). Silently omit quotes if not verifiable after exhaustive search.
*   **Traceability:** Each quote's origin must be confirmed by an inline citation [SSX] corresponding to the final Sources list.
*   **Source Quality:** Use only official communications from **{company_name}** (Annual/Integrated reports, earnings call transcripts, official IR presentations/webcasts, company-published interviews). Avoid secondary reporting of quotes unless the secondary source itself is grounded.

{formatted_completion_template}
{formatted_final_review}
{formatted_final_source_list}
{formatted_base_formatting}
"""
    return prompt

# --- Enhanced Account Strategy Prompt Function ---
def get_strategy_research_prompt(company_name: str, language: str = "Japanese", ticker: Optional[str] = None, industry: Optional[str] = None, context_company_name: str = "NESIC"):
    """
    Generates the BEST POSSIBLE prompt for creating a comprehensive, actionable 3-Year Account Strategy Action Plan
    FOR {context_company_name} TARGETING {company_name}. It leverages PROVIDED DOCUMENTS as PRIMARY context,
    supplemented by verifiable web grounding, and maps opportunities to {context_company_name}'s capabilities.
    """
    # --- Role Assignment ---
    persona = f"You are a Senior Account Strategist at {context_company_name} ({context_company_name}). Your task is to develop a comprehensive, data-driven 3-year account strategy plan for targeting {company_name}."

    # --- Context Setup ---
    context_str = f"**{company_name}**"
    if ticker: context_str += f" (Ticker: {ticker})"
    if industry: context_str += f" (Industry: {industry})"

    # --- Format Standard Instruction Blocks ---
    # (Ensure these are correctly defined and accessible)
    formatted_additional_instructions = ADDITIONAL_REFINED_INSTRUCTIONS.format(company_name=company_name, ticker=ticker or "N/A", industry=industry or "N/A")
    # MODIFIED: Enhance research depth specifically for this prompt context
    formatted_research_depth = RESEARCH_DEPTH_INSTRUCTION.format(company_name=company_name) + textwrap.dedent(f"""\

        *   **CRITICAL - Account Strategy Context:** When applying these research instructions for the Account Strategy Prompt, remember the goal is to gather intelligence *on* **{company_name}** specifically *to inform strategy FOR* **{context_company_name}**. Prioritize information revealing needs, plans, challenges, and organizational details relevant to potential {context_company_name} solutions.
        *   **Document Prioritization for Internal Context:** CRITICALLY, prioritize and deeply integrate information found within the **provided documents** [DOCX] as the primary source for internal strategy, plans, specific challenges, personnel, and relationship history. Supplement with the latest official primary web sources [SSX] for public facts (revenue, official structure, etc.) and broader market context. Use the correct citation type based on origin. If conflicts arise, prioritize latest official provided document for internal strategy/plans, and latest verifiable public web source for public facts.
    """)
    formatted_final_review_base = FINAL_REVIEW_INSTRUCTION.format(company_name=company_name) # Base for later enhancement
    formatted_completion_base = COMPLETION_INSTRUCTION_TEMPLATE.format(company_name=company_name) # Base for later enhancement
    # MODIFIED: Clarify SSX-only nature of final list
    formatted_final_source_list = FINAL_SOURCE_LIST_INSTRUCTIONS_TEMPLATE.format(language=language) + textwrap.dedent("""\

        **Note for Account Strategy:** This final "Sources" list is *exclusively* for the web grounding URLs cited as `[SSX]`. Document citations `[DOCX, reference]` are inline only and **must not** be included here.
    """)
    formatted_base_formatting = BASE_FORMATTING_INSTRUCTIONS.format(language=language)
    # MODIFIED: Ensure audience context is applied to NESIC's perspective
    formatted_audience_reminder = AUDIENCE_CONTEXT_REMINDER.format(language=language) + f" Ensure recommendations are actionable for **{context_company_name}**."

    # --- Format Document Analysis Instruction ---
    # MODIFIED: Slight wording tweak for synthesis context
    formatted_document_analysis = DOCUMENT_ANALYSIS_INSTRUCTION.format(company_name=company_name, context_company_name=context_company_name, language=language).replace(
        "analysis and the resulting Account Strategy **MUST** deeply integrate insights extracted",
        "analysis and the resulting Account Strategy **MUST** deeply synthesize and integrate insights extracted"
    ).replace(
        "Do not rely solely on web grounding when relevant document information is available.",
        "Prioritize document insights for internal context, but synthesize with web grounding for a complete picture."
    )


    # --- Assemble the Final Prompt ---
    # MODIFIED: Added persona clarification and mandatory dual-source emphasis
    prompt = f"""
{persona} Your goal is to create an actionable plan for {context_company_name}.

**CRITICAL FOCUS:** This entire request is *exclusively* about creating a strategic account plan FOR **{context_company_name}** targeting the specific entity: {context_str}. Verify the identity of **{company_name}** for all sourced information. Avoid unrelated entities.

# MODIFIED: Emphasize dual source mandate
**PRIMARY CONTEXT SOURCES (MANDATORY SYNTHESIS):** This plan **MUST** be built upon insights derived from **BOTH**:
1.  **Provided Documents (HIGHEST PRIORITY FOR INTERNAL CONTEXT):** Internal presentations, plans, meeting notes, org charts, etc., specific to {company_name} (Cite as `[DOCX, reference]`). Assume these provide the most current internal view unless contradicted by very recent, verifiable public sources.
2.  **Verifiable Web Grounding (FOR PUBLIC FACTS & WIDER CONTEXT):** Latest public information (financials, official strategy statements, market news) validated via grounding URLs (Cite as `[SSX]`). Use this to supplement and verify public aspects of the documents.

Comprehensive 3-Year Account Strategy Action Plan: {context_company_name} for {company_name}

Objective: Create a detailed, actionable, and strategically sound account plan for **{context_company_name}** covering the next three fiscal years (e.g., FY2025-FY2027), focused on **{company_name}**. This plan **MUST synthesize information from BOTH provided documents AND verifiable web grounding** to identify strategic opportunities where **{context_company_name}'s** known capabilities (see reference below) align with **{company_name}'s** needs, challenges, and initiatives (both stated publicly and detailed internally). The output must be tailored for internal use by **{context_company_name}** sales and strategy teams, highlighting clear value propositions and differentiators.

Target Audience Context: {formatted_audience_reminder} Recommendations must be actionable for {context_company_name}, focusing on strategic alignment and potential ROI.

{get_language_instruction(language)}

--- {context_company_name} Context (Reference) ---
{NESIC_CAPABILITIES_CONTEXT}
--- End {context_company_name} Context ---

--- Core Instructions & Constraints ---

Research & Analysis Requirements:
*   # MODIFIED: Explicit dual source synthesis and prioritization logic
    **Dual Source Synthesis (MANDATORY):** Deeply analyze and synthesize information from BOTH provided documents (`[DOCX]`) AND web grounding (`[SSX]`).
        *   Prioritize documents for internal strategy, specific plans/timelines, internal challenges/pain points, organizational details, and relationship history.
        *   Use latest verifiable public web grounding for official public facts (e.g., reported revenue, CEO name, major public announcements) and broader market/industry context.
        *   If conflicting information exists: Prioritize the **latest official provided document** for internal strategy/plans specific to {company_name}. Prioritize the **latest verifiable public web grounding source** for publicly stated facts. Note significant conflicts impacting strategy.
*   **Accurate & Distinct Citation (MANDATORY):** Every factual claim about {company_name} MUST have the correct inline citation: `[SSX]` for web grounding, `[DOCX, reference]` for provided documents.
*   **Exhaustive Review:** Perform thorough review of *all* provided document content (text, tables, visuals) and conduct exhaustive web searches before silently omitting unverified data.
*   **{context_company_name} Perspective (CRITICAL):** Frame ALL analysis and recommendations from **{context_company_name}'s** viewpoint – "How can WE ({context_company_name}) uniquely help {company_name} achieve their goals and overcome their challenges using OUR capabilities and strengths?".
*   **Actionable & Strategic Output:** Focus on extracting insights that inform concrete strategic engagement possibilities, value propositions, and potential risks for {context_company_name}.
*   **Perfect Formatting:** Adhere strictly to Markdown rules (esp. tables). Verify data accuracy. Use '-' sparingly in tables only if data is confirmed absent in source and needed for structure.

{formatted_document_analysis}
{HANDLING_MISSING_INFO_INSTRUCTION} # Includes check for alternate language sites
{formatted_research_depth} # Includes document prioritization logic
{SPECIFICITY_INSTRUCTION}
{INLINE_CITATION_INSTRUCTION} # Reminds of the two citation types
{ANALYSIS_SYNTHESIS_INSTRUCTION} # Synthesize from BOTH sources

{formatted_additional_instructions} # Includes single-entity focus, markdown rules etc.

--- Account Strategy Plan Structure ---

## 0. Executive Summary (for {context_company_name})
    *   Provide a concise (1-2 paragraph) overview of the 3-year strategy for engaging {company_name}, **based on synthesis of DOCX and SSX insights**.
    *   Highlight the top 2-3 strategic opportunities identified for {context_company_name}.
    *   Summarize the core value proposition {context_company_name} offers to {company_name}.
    *   Briefly mention the overall ambition level (e.g., expand footprint, become strategic partner).
    *   Cite key supporting data points [DOCX / SSX].

## 1. Target Customer Profile ({company_name})
    *   Company Name: {company_name} [SSX or DOCX]
    *   Ticker: {ticker or "N/A"} [SSX or DOCX]
    *   Industry: {industry or "N/A"} [SSX or DOCX]
    *   Headquarters Address: [Full Registered HQ Address] [SSX or DOCX]
    *   Current CEO: [Full Name and Title] [SSX or DOCX - Verify latest]
    *   Key Business Summary: Summarize main operations, markets, recent performance highlights, and overall business trajectory based on latest reports and documents [SSX, DOCX].
    *   Approximate Employee Range/Number: [Most recent figure with date] [SSX or DOCX]
    *   Reported Relationship with {context_company_name}: Summarize any existing relationship, past projects, or engagement level *if explicitly mentioned and verifiable* in provided documents or grounded sources [DOCX, SSY]. Otherwise, state "No verifiable relationship history found".

## 2. Key Insights from Provided Documents & Implications for {context_company_name}
    *   **Document Overview:** List provided documents (e.g., "DOC1: FY24 Internal Strategy PPT", "DOC2: Org Chart PDF").
    *   **Major Strategic Themes & Priorities (from Docs):** Summarize core goals, transformation efforts, investment areas stated within documents [DOCX, reference]. **Implication for {context_company_name}:** [Analyze what these themes mean for potential {context_company_name} engagement].
    *   **Recent Activities & Projects (from Docs):** Highlight significant ongoing/planned projects/initiatives mentioned [DOCX, reference]. **Implication for {context_company_name}:** [Identify specific, immediate opportunities or areas for {context_company_name} to align with].
    *   **Organizational Nuances & Key Stakeholders (from Docs):** Detail relevant structure insights, team names, key individuals [DOCX, reference]. **Implication for {context_company_name}:** [Identify key contacts, decision-makers, and potential relationship mapping targets].
    *   **Explicitly Stated Needs / Pain Points (from Docs):** List challenges, requirements, gaps directly articulated [DOCX, reference]. **Implication for {context_company_name}:** [Pinpoint where {context_company_name}'s solutions directly address these expressed needs].

## 3. Financial Health & Investment Capacity ({company_name})
    *   Present Revenue, Net Income (Parent), and Operating Margin (%) for last 3 fiscal years in a **perfectly formatted Markdown table** [SSX]. Calculate Revenue YoY Growth (%). Verify data. Use '-' minimally.
        | Metric                           | FYXXXX | FYYYYY | FYZZZZ | Source(s) |
        |----------------------------------|--------|--------|--------|-----------|
        | Total Revenue (JPY M)            |        |        |        | [SSX]     |
        | Revenue YoY Growth (%)           | N/A    |  X.X%  |  Y.Y%  | (Calc)    |
        | Net Income (Parent) (JPY M)      |        |        |        | [SSX]     |
        | Operating Margin (%)             |        |        |        | [SSY]     |
    *   Identify key profitable/high-growth divisions/segments [SSZ, DOCX].
    *   **Analyze Investment Capacity & Priorities (for {context_company_name}):** Based on financial trends [SSX] and investment plans/commentary in documents [DOCX], assess {company_name}'s likely capacity AND strategic priorities for IT/DX/Operations investments. Where are they most likely to spend? Are there signs of budget constraints {context_company_name} should be aware of? [DOCX, SSX].

## 4. Strategic Initiatives & {context_company_name} Opportunity Mapping ({company_name})
    *   Synthesize **{company_name}**'s major stated [SSX] AND internally documented [DOCX] strategic initiatives relevant to {context_company_name}'s offerings (DX, Cloud, Security, Network, ESG Tech, Ops Efficiency).
    *   For each key initiative (list 3-5):
        *   **Initiative Name/Focus:** [Specific name/goal] [Source: DOCX or SSX]
        *   **Objective & Timeline:** [Details] [Source: DOCX or SSX]
        *   **Investment (if known):** [Details] [Source: DOCX or SSX]
        *   **{context_company_name} Value Proposition & Differentiation (CRITICAL):** Explicitly map relevant **{context_company_name}** capabilities AND strengths (incl. NEC Group synergy). Crucially, articulate **WHY {context_company_name} is uniquely positioned** to help {company_name} succeed with this initiative compared to potential competitors. What is our specific value-add?

## 5. Decision-Making Landscape & Key Stakeholders ({company_name})
    *   Outline **{company_name}**'s relevant decision-making structure (IT/DX/Ops/Relevant BUs) based on BOTH public data [SSX] and insights from provided documents (e.g., Org charts, project roles) [DOCX]. Identify key departments, committees, individuals.
    *   Identify key executives AND relevant managers/leaders (names, titles, roles) based on latest verifiable information [SSY, DOCX].
    *   **Analyze Influence & Engagement Strategy (for {context_company_name}):** Who are the key decision-makers, influencers, and potential champions/detractors for {context_company_name}'s proposed offerings? Outline a high-level relationship mapping strategy for {context_company_name}.

## 6. Critical Business Challenges & {context_company_name} Solution Fit ({company_name})
    *   Enumerate **{company_name}**'s major challenges based on official sources [SSX] AND explicitly stated pain points from provided documents [DOCX]. Categorize if possible.
        *   **Challenge 1:** [Specific challenge] [Source: DOCX or SSX] -> **{context_company_name} Solution Fit & Value Proposition:** [Explain precisely how {context_company_name}'s specific service/capability directly addresses this challenge and delivers tangible value (e.g., cost savings, efficiency gains, risk reduction, enhanced capability)].
        *   *(List 3-5 key verifiable challenges)*
    *   Focus on challenges where {context_company_name} has a strong, differentiated solution.

## 7. Technology Environment & {context_company_name} Synergy ({company_name})
    *   Summarize **{company_name}**'s current technology landscape (key systems, vendors, platforms) based on available information [SSX, DOCX]. Identify potential areas of technological debt or opportunity.
    *   Identify likely technology focus areas/investments for the next 3 years [DOCX, SSX].
    *   **Analyze {context_company_name} Synergy & Integration Potential:** Map {company_name}'s tech focus to the **{context_company_name}** portfolio. Highlight where **NEC Group synergy** offers unique advantages. Assess how well {context_company_name} solutions can integrate with {company_name}'s existing environment.

## 8. 3-Year Engagement Strategy & Action Plan (for {context_company_name})
    *   Provide a high-level, phased engagement plan concept for **{context_company_name}**. Focus on strategic themes derived from {company_name}'s needs (identified via DOCX and SSX), aligned with {context_company_name}'s capabilities and differentiators. Use a **perfectly formatted Markdown table**.
        | Phase / Timeline        | Strategic Engagement Theme (for {context_company_name}) | Key {company_name} Need/Initiative Addressed | Potential {context_company_name} Offerings (Highlight Differentiation) | Target Stakeholders ({company_name}) | Source (Doc/Web) | Proposed Next Steps (Actionable for {context_company_name}) | Potential Hurdles / Considerations (for {context_company_name}) |
        |-------------------------|---------------------------------------------------------|-----------------------------------------------|------------------------------------------------------------------|--------------------------------------|------------------|---------------------------------------------------------|--------------------------------------------------------------------|
        | **Year 1: Build & Prove**|                                                         |                                               |                                                                  |                                      | [DOCX / SSX]     |                                                         |                                                                    |
        | (Q1-Q2)                 | Address network pain points; Build trust              | Network readiness for Cloud [Sec 4]           | Network Solutions (Assessment, SD-WAN Design - emphasize NESIC expertise) | IT Infra / CIO [Sec 5]               | DOC1, Slide 5    | Propose assessment workshop; Present relevant case study        | Budget cycle alignment; Internal resistance to change              |
        | (Q3-Q4)                 | Position for strategic DX security                      | Cybersecurity for New Platform [Sec 6]        | Cybersecurity (Consulting, MSSP intro - leverage NEC Group Intel)   | CISO / DX Team [Sec 5]               | DOC2             | Targeted security briefing; Proof of concept proposal             | Competition from incumbent security vendors                        |
        | **Year 2: Expand & Deepen** |                                                         |                                               |                                                                  |                                      | [DOCX / SSX]     |                                                         |                                                                    |
        | (Q1-Q2)                 | Enable data-driven insights                             | Data Silos Challenge [Sec 6]                  | SI (Integration - highlight multi-vendor skill), Data Analytics Support | DX Team / BU Lead [Sec 5]            | DOC1, p. 10      | Co-creation workshop on data strategy; Pilot proposal           | Data governance complexity; Resource availability at client      |
        | (Q3-Q4)                 | Demonstrate efficiency gains                            | Potential Margin Pressure [Sec 3]             | Managed Services (Network/Cloud - focus on ROI), BPO              | IT Ops / Finance [Sec 5]             | SSX              | Customized TCO/ROI analysis; Service level agreement draft      | Proving value beyond cost reduction; Contract negotiation          |
        | **Year 3: Partner & Grow**|                                                         |                                               |                                                                  |                                      | [DOCX / SSX]     |                                                         |                                                                    |
        | (Ongoing)               | Solidify Strategic Partnership                          | Scaling successes, Long-term DX roadmap       | Full Managed Services, DX Consulting, Joint Innovation Programs  | CIO / Strategy / BU Heads [Sec 5]    | Synthesis        | Joint strategic roadmap session; Executive sponsorship engagement | Maintaining momentum; Aligning with evolving client strategy       |
    *   Ensure each engagement theme links directly to verified needs/initiatives [DOCX, SSX], leverages specific {context_company_name} strengths, and includes concrete, actionable next steps for the {context_company_name} team.

## 9. Competitive Landscape & {context_company_name}'s Edge ({company_name} Context)
    *   Identify **{company_name}**'s key incumbent IT vendors/partners *if explicitly mentioned* [SSX, DOCX].
    *   **Analyze {context_company_name}'s Differentiators (MANDATORY):** Based on {company_name} info [SSX, DOCX] and {context_company_name} capabilities: Explicitly articulate **{context_company_name}'s** competitive advantages *for this specific client*. Focus on 2-3 key differentiators (e.g., unique NEC Group tech synergy relevant to {company_name}'s industry [DOCX], superior local support structure matching {company_name}'s footprint [DOCX], proven SI methodology for their specific challenge [Public Info]). Avoid generic statements. Silently omit if no verifiable competitor context is found.

## 10. Success Metrics & KPIs (for {context_company_name} Internal Use)
    *   Define 3-5 specific, measurable Key Performance Indicators (KPIs) for **{context_company_name}** to track this plan's success over 3 years. Base these on opportunities identified from verifiable {company_name} data [DOCX, SSX].
        *   KPI 1: Number of C-level / Key Stakeholder (Sec 5) meetings secured focusing on strategic initiatives (Sec 4) (Target: X/year).
        *   KPI 2: Pipeline Value (£/¥/$) generated specifically targeting opportunities identified in Sec 4 & 6 (Target: Y value/year).
        *   KPI 3: Win Rate for proposals leveraging key differentiators (Sec 9) (Target: Z%).
        *   KPI 4: Expansion into New {context_company_name} Core Service Areas within {company_name} (Target: Enter A new areas by Year 3).
        *   KPI 5: Client Satisfaction Score / Net Promoter Score from {company_name} (if measurable) (Target: Maintain/Improve score B).
    *   Briefly explain the rationale linking these internal KPIs to successful strategy execution based on the {company_name} analysis.

## 11. Potential Risks & Mitigation Strategies (for {context_company_name})
    *   Identify 2-4 key risks **to {context_company_name}** in pursuing this account strategy (e.g., strong incumbent relationship [DOCX/SSX?], budget cuts at client [DOCX/SSX?], internal {context_company_name} resource constraints, misalignment on strategic direction, failure to demonstrate ROI). Cite source if risk is documented.
    *   For each risk, propose a brief mitigation strategy for the {context_company_name} team (e.g., "Build multi-level relationships beyond IT", "Develop flexible pricing models", "Secure executive sponsorship internally", "Focus on quantifiable business outcomes in proposals").

## 12. Overall Strategic Recommendation & Rationale (for {context_company_name})
    *   Provide a concluding single paragraph (~300–500 words) synthesizing the most critical findings about **{company_name}** (from web [SSX] + docs [DOCX]) and presenting a clear **strategic recommendation** for {context_company_name}'s 3-year engagement.
    *   Reiterate the primary alignment opportunities, emphasizing the unique value proposition and differentiators {context_company_name} offers. Incorporate key quantitative points.
    *   Briefly incorporate the key risks (from Sec 11) and the overall confidence level in the proposed strategy.
    *   Example structure: "Based on {company_name}'s documented [DOCX] investment in X and stated challenge Y [SSX], the primary strategic thrust for {context_company_name} should be Z, leveraging our differentiated capability in A. Key opportunities lie in B and C over the next 3 years. While risks such as [Risk 1] exist, mitigation through [Mitigation 1] makes this a high-potential strategic account requiring focused executive engagement and resource allocation..."
    *   This summary is the final strategic directive for the {context_company_name} account team. Do not introduce new data or assumptions.

--- Final Checks & Formatting ---

Source and Accuracy Requirements:
*   **Accuracy:** All data about **{company_name}** MUST be grounded [SSX] or documented [DOCX]. Reflect latest info. {context_company_name} capability mapping based on provided context/public knowledge. Silently omit unverified data. Verify table data meticulously.
*   **Traceability:** Each fact/figure includes correct citation (`[SSX]` or `[DOCX, reference]`).
*   **Single-Entity Coverage:** Strictly reference **{company_name}**; omit similarly named entities.

# MODIFIED: Add enhanced completion checks
{formatted_completion_base + textwrap.dedent('''\
        7. Information from provided documents is integrated and cited correctly using `[DOCX, reference]` format.
        8. Executive Summary (Section 0) and {context_company_name} Risks (Section 11) are included and complete.
        9. Synthesis between document insights and web grounding is evident throughout the plan.
'''.format(context_company_name=context_company_name))}

# MODIFIED: Add enhanced review checks
{formatted_final_review_base + textwrap.dedent('''\

        *   **Document Insight Integration & Implications:**
            *   Insights AND their implications for {context_company_name} from provided documents are incorporated throughout, especially in Sections 2, 4, 5, 6, 7, 9, 12.
            *   Document citations `[DOCX, reference]` are used correctly and consistently.
            *   Web grounding `[SSX]` is used appropriately to supplement/verify public facts and provide context.
            *   **Synthesis:** The analysis clearly integrates insights from BOTH document and web sources where relevant.
        *   **{context_company_name} Perspective & Value Proposition:**
            *   The analysis, recommendations, and language consistently reflect the viewpoint, objectives, and value proposition of {context_company_name}.
            *   Opportunities clearly link {company_name}'s needs (from web/docs) to specific {context_company_name} capabilities AND differentiators.
        *   **Actionability & Completeness:**
            *   Executive Summary (Sec 0) provides a clear overview based on the synthesized analysis.
            *   Engagement Plan (Sec 8) includes actionable next steps for {context_company_name} and considers potential hurdles.
            *   {context_company_name} Risks (Sec 11) are identified with mitigation strategies relevant to {context_company_name}.
            *   Final Recommendation (Sec 12) is clear and synthesizes key findings, opportunities, and risks **from {context_company_name}'s perspective**.
'''.format(context_company_name=context_company_name, company_name=company_name))}

{formatted_final_source_list} # Reminder this is SSX only
{formatted_base_formatting}
"""

    # --- Dynamically Enhance Completion & Review Instructions ---
    # NOTE: The enhancement is now directly embedded above using + operator and f-strings/format method where needed.

    return prompt