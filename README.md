# Supervity PDF Report Generator

This project generates comprehensive company analysis reports in multiple languages using Google's Gemini API. It processes a set of prompts to create detailed sections on various aspects of a company and compiles them into a professionally formatted PDF report.

## Features

- Generate detailed company analysis reports covering 10 key aspects
- Multi-language support (Japanese, English, Chinese, Korean, Vietnamese, Thai, Indonesian, Spanish, German, French)
- Professional PDF generation with table of contents, section covers, and consistent styling
- Token usage tracking and execution time statistics
- Parallel processing for faster generation
- Graceful handling of interruptions

## Project Structure

- `test_agent_prompt.py`: Main script to generate all sections using the Gemini API
- `generate_pdf.py`: Standalone script to generate PDFs from existing markdown files
- `pdf_generator.py`: PDF generation logic and utilities
- `prompt_testing.py`: Contains prompt templates for each section
- `config.py`: Configuration constants and settings
- `templates/`: Contains HTML templates for PDF generation
- `output/`: Directory where generated content is stored

## Setup

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Gemini API key (see `.env.example`):

```
GEMINI_API_KEY=your_api_key_here
```

4. Optional: Configure LLM parameters in `.env`:

```
LLM_MODEL=gemini-2.5-pro-preview-03-25
LLM_TEMPERATURE=0.9
```

5. **Setup Analytics (Required for Streamlit app):**

The Streamlit app includes user tracking and analytics logging to Google Sheets. To set this up:

**a. Create a Google Sheets document:**
- Create a new Google Sheet for storing analytics data
- Copy the Sheet ID from the URL (the long string between `/d/` and `/edit`)

**b. Setup Google Service Account:**
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create a new project or select an existing one
- Enable the Google Sheets API and Google Drive API
- Create a Service Account:
  - Go to IAM & Admin > Service Accounts
  - Click "Create Service Account"
  - Fill in details and create
  - Generate a JSON key file
- Share your Google Sheet with the service account email (found in the JSON)

**c. Configure environment variables:**
Add these to your `.env` file:

```
# Analytics Configuration
ENABLE_ANALYTICS=true
GOOGLE_SHEETS_CREDENTIALS={"type":"service_account","project_id":"...","private_key":"..."}
ANALYTICS_SHEET_ID=your_google_sheet_id_here
```

For `GOOGLE_SHEETS_CREDENTIALS`, copy the entire JSON content from your service account key file as a single line.

**d. Disable analytics (optional):**
To disable analytics tracking, set `ENABLE_ANALYTICS=false` in your `.env` file.

## Usage

### Generate a Complete Report

Run the main script:

```bash
python test_agent_prompt.py
```

Follow the prompts to enter:
- Company name
- Language selection (1-10)

The script will:
1. Generate all sections in parallel
2. Save markdown files in `output/<company>_<language>_<timestamp>/markdown/`
3. Generate a PDF report in `output/<company>_<language>_<timestamp>/pdf/`
4. Save usage statistics in `output/<company>_<language>_<timestamp>/misc/`

### Generate a PDF from Existing Markdown Files

If you already have markdown files in the correct structure, you can generate a PDF without re-running the LLM:

```bash
python generate_pdf.py "Company Name" "Language" -o path/to/output/directory
```

## Output Structure

For each generation, the following directory structure is created:

```
output/
└── CompanyName_Language_YYYYMMDD_HHMMSS/
    ├── markdown/                # Individual markdown files for each section
    │   ├── basic.md
    │   ├── vision.md
    │   ├── management_strategy.md
    │   └── ...
    ├── pdf/                     # Generated PDF report
    │   └── CompanyName_Language_Report.pdf
    └── misc/                    # Metadata and statistics
        ├── generation_config.yaml
        └── token_usage_report.json
```

## Customization

- Modify section templates in `prompt_testing.py`
- Adjust PDF styling in `templates/enhanced_report_template.html`
- Configure section order and available languages in `config.py`

## License

This project is proprietary and confidential.

## Requirements

- Python 3.8+
- Google Generative AI API access
- Dependencies listed in `requirements.txt`

## Streamlit Web Interface

A Streamlit-based web interface is now available for easier report generation. This provides a user-friendly GUI that includes:

**User Authentication & Analytics:**
- User information collection (name and business email) on first visit
- Session-based tracking for analytics
- Automatic logging of report generation to Google Sheets

**Report Generation Features:**
1. Enter the target company name (the company to analyze)
2. Specify your company name as the context (who is generating the report)
3. Select language for the report
4. Choose which sections to include
5. Generate the report with a single click
6. Preview the PDF report directly in the browser
7. Download the completed report

### Running the Streamlit App

To run the Streamlit interface:

```bash
streamlit run app.py
```

The app will open in your default web browser at http://localhost:8501.

### Deploying to Render

This project includes a `render.yaml` configuration file that allows for easy deployment to Render.com. To deploy:

1. Create a new account or sign in to [Render](https://render.com)
2. Connect your GitHub repository
3. Click "New +" and select "Blueprint"
4. Select your repository and Render will automatically detect the configuration
5. Set environment variables in the Render dashboard:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `GOOGLE_SHEETS_CREDENTIALS`: Your service account JSON (as a single line)
   - `ANALYTICS_SHEET_ID`: Your Google Sheet ID for analytics
   - `ENABLE_ANALYTICS`: Set to `true` to enable analytics
6. Deploy the service

The application will be accessible at your Render URL.

**Note:** Make sure your Google Sheet is shared with the service account email before deploying. 