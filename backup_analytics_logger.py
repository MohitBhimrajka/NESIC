"""
Enhanced Analytics logger for tracking user activity and report generation in Google Sheets.
Uses two separate sheets:
1. User Sessions Sheet: Tracks platform visits and user logins
2. Report Generation Sheet: Tracks detailed report generation data
"""

import os
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st


class EnhancedAnalyticsLogger:
    """Handles logging to two separate Google Sheets for better data organization."""
    
    def __init__(self):
        self.sessions_sheet = None
        self.reports_sheet = None
        self.enabled = self._is_analytics_enabled()
        self.initialization_error = None
        
        if self.enabled:
            try:
                self._setup_google_sheets()
                self._ensure_headers()
            except Exception as e:
                self.initialization_error = str(e)
                self.enabled = False

    def _is_analytics_enabled(self) -> bool:
        """Check if analytics is enabled via environment variable."""
        return os.getenv('ENABLE_ANALYTICS', 'true').lower() == 'true'

    def _setup_google_sheets(self):
        """Setup Google Sheets connection for both sheets."""
        # Get credentials from environment variable
        creds_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
        if not creds_json:
            raise ValueError("GOOGLE_SHEETS_CREDENTIALS environment variable not found")
        
        # Parse credentials JSON
        try:
            creds_dict = json.loads(creds_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in GOOGLE_SHEETS_CREDENTIALS: {str(e)}. Check for proper escaping of quotes and backslashes.")
        
        # Setup credentials with required scopes
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(credentials)
        
        # Get sheet ID from environment
        sheet_id = os.getenv('ANALYTICS_SHEET_ID')
        if not sheet_id:
            raise ValueError("ANALYTICS_SHEET_ID environment variable not found")
        
        # Open the spreadsheet
        spreadsheet = client.open_by_key(sheet_id)
        
        # Get or create the two sheets
        try:
            self.sessions_sheet = spreadsheet.worksheet("User_Sessions")
        except gspread.WorksheetNotFound:
            self.sessions_sheet = spreadsheet.add_worksheet(title="User_Sessions", rows=1000, cols=10)
        
        try:
            self.reports_sheet = spreadsheet.worksheet("Report_Generation")
        except gspread.WorksheetNotFound:
            self.reports_sheet = spreadsheet.add_worksheet(title="Report_Generation", rows=1000, cols=15)

    def _ensure_headers(self):
        """Ensure both Google Sheets have the correct headers."""
        
        # Headers for User Sessions sheet
        sessions_headers = [
            'Timestamp',
            'User Name',
            'Business Email',
            'Company/Organization',
            'Session ID',
            'Session Type',  # 'LOGIN', 'VISIT', etc.
            'User Agent',
            'IP Address (if available)',
            'Platform Status'
        ]
        
        # Headers for Report Generation sheet  
        reports_headers = [
            'Timestamp',
            'User Name',
            'Business Email',
            'Target Company',
            'Context Company', 
            'Language',
            'Sections Generated',
            'Total Sections',
            'Report Success',
            'Session ID',
            'Generation Time (seconds)',
            'Total Tokens',
            'Input Tokens',
            'Output Tokens',
            'Error Message (if any)'
        ]
        
        try:
            # Setup sessions sheet headers
            current_sessions_headers = self.sessions_sheet.row_values(1)
            if not current_sessions_headers or current_sessions_headers != sessions_headers:
                self.sessions_sheet.clear()
                self.sessions_sheet.append_row(sessions_headers)
            
            # Setup reports sheet headers  
            current_reports_headers = self.reports_sheet.row_values(1)
            if not current_reports_headers or current_reports_headers != reports_headers:
                self.reports_sheet.clear()
                self.reports_sheet.append_row(reports_headers)
                
        except Exception as e:
            if not hasattr(self, 'initialization_error') or not self.initialization_error:
                self.initialization_error = f"Could not verify sheet headers: {str(e)}"

    def generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return str(uuid.uuid4())[:8]

    def log_user_session(self,
                        user_name: str,
                        business_email: str,
                        company: str,
                        session_id: str,
                        session_type: str = "LOGIN") -> bool:
        """
        Log a user session to the User Sessions sheet.
        
        Args:
            user_name: User's full name
            business_email: User's business email
            company: User's company/organization
            session_id: Unique session identifier
            session_type: Type of session (LOGIN, VISIT, etc.)
        
        Returns:
            bool: True if logging was successful, False otherwise
        """
        if not self.enabled or not self.sessions_sheet:
            return False
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            
            row_data = [
                timestamp,
                user_name,
                business_email,
                company or '-',
                session_id,
                session_type,
                '-',  # User Agent (could be enhanced later)
                '-',  # IP Address (privacy considerations)
                'ACTIVE'
            ]
            
            self.sessions_sheet.append_row(row_data)
            return True
            
        except Exception as e:
            return False

    def log_report_generation(self,
                            user_name: str,
                            business_email: str,
                            target_company: str,
                            context_company: str,
                            language: str,
                            sections_generated: List[str],
                            report_success: bool,
                            session_id: str,
                            generation_time: float,
                            token_stats: Dict[str, Any],
                            error_message: str = None) -> bool:
        """
        Log a report generation event to the Report Generation sheet.
        
        Args:
            user_name: User's full name
            business_email: User's business email
            target_company: Company being researched
            context_company: User's company (context)
            language: Report language
            sections_generated: List of sections that were generated
            report_success: Whether the report was successful
            session_id: Unique session identifier
            generation_time: Time taken to generate (seconds)
            token_stats: Dictionary with token usage statistics
            error_message: Error message if generation failed
        
        Returns:
            bool: True if logging was successful, False otherwise
        """
        if not self.enabled or not self.reports_sheet:
            return False
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            sections_str = ', '.join(sections_generated) if sections_generated else 'None'
            
            # Extract token information
            total_tokens = token_stats.get('summary', {}).get('total_tokens', 0) if token_stats else 0
            input_tokens = token_stats.get('summary', {}).get('total_input_tokens', 0) if token_stats else 0
            output_tokens = token_stats.get('summary', {}).get('total_output_tokens', 0) if token_stats else 0
            
            row_data = [
                timestamp,
                user_name,
                business_email,
                target_company,
                context_company,
                language,
                sections_str,
                len(sections_generated) if sections_generated else 0,
                'TRUE' if report_success else 'FALSE',
                session_id,
                round(generation_time, 2),
                total_tokens,
                input_tokens,
                output_tokens,
                error_message or '-'
            ]
            
            self.reports_sheet.append_row(row_data)
            return True
            
        except Exception as e:
            return False


# Global analytics logger instance
enhanced_analytics_logger = EnhancedAnalyticsLogger()


def log_user_session_start(user_name: str,
                         business_email: str,
                         company: str,
                         session_id: str) -> bool:
    """
    Log when a user starts a new session.
    
    Returns:
        bool: True if logging was successful, False otherwise
    """
    return enhanced_analytics_logger.log_user_session(
        user_name=user_name,
        business_email=business_email,
        company=company,
        session_id=session_id,
        session_type="LOGIN"
    )


def log_report_generation(user_name: str,
                        business_email: str,
                        target_company: str,
                        language: str,
                        sections_generated: List[str],
                        report_success: bool,
                        session_id: str,
                        generation_time: float,
                        token_count: int,
                        context_company: str) -> bool:
    """
    Log a report generation event.
    
    Returns:
        bool: True if logging was successful, False otherwise
    """
    # Convert old format to new format for compatibility
    token_stats = {
        'summary': {
            'total_tokens': token_count,
            'total_input_tokens': 0,  # Not tracked in old format
            'total_output_tokens': token_count  # Assume all are output tokens
        }
    }
    
    return enhanced_analytics_logger.log_report_generation(
        user_name=user_name,
        business_email=business_email,
        target_company=target_company,
        context_company=context_company,
        language=language,
        sections_generated=sections_generated,
        report_success=report_success,
        session_id=session_id,
        generation_time=generation_time,
        token_stats=token_stats
    )


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return enhanced_analytics_logger.generate_session_id()


def show_analytics_status():
    """Display analytics status in the Streamlit app (hidden for clean UI)."""
    # Analytics status is now hidden to keep UI clean
    # Only show errors in development/debug mode
    if enhanced_analytics_logger.initialization_error and os.getenv('DEBUG_ANALYTICS', 'false').lower() == 'true':
        st.error(f"📊 Analytics Error: {enhanced_analytics_logger.initialization_error}") 