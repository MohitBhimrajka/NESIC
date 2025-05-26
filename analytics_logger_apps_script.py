"""
Enhanced Analytics logger for tracking user activity and report generation using Google Apps Script.
Uses HTTP requests to a Google Apps Script webhook instead of direct Google Sheets API.
"""

import os
import json
import time
import uuid
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
import streamlit as st


class EnhancedAnalyticsLogger:
    """Handles logging to Google Sheets via Google Apps Script webhook."""
    
    def __init__(self):
        self.enabled = self._is_analytics_enabled()
        self.apps_script_url = None
        self.initialization_error = None
        
        if self.enabled:
            try:
                self._setup_apps_script_connection()
                self._ensure_headers()
            except Exception as e:
                self.initialization_error = str(e)
                self.enabled = False

    def _is_analytics_enabled(self) -> bool:
        """Check if analytics is enabled via environment variable."""
        return os.getenv('ENABLE_ANALYTICS', 'true').lower() == 'true'

    def _setup_apps_script_connection(self):
        """Setup Google Apps Script webhook URL."""
        self.apps_script_url = os.getenv('GOOGLE_APPS_SCRIPT_URL')
        if not self.apps_script_url:
            raise ValueError("GOOGLE_APPS_SCRIPT_URL environment variable not found")
        
        # Validate URL format
        if not self.apps_script_url.startswith('https://script.google.com/'):
            raise ValueError("Invalid Google Apps Script URL format")

    def _ensure_headers(self):
        """Ensure both Google Sheets have the correct headers via Apps Script."""
        try:
            payload = {
                'action': 'ensure_headers',
                'data': {}
            }
            
            response = self._make_request(payload)
            if not response.get('success', False):
                self.initialization_error = f"Could not verify sheet headers: {response.get('error', 'Unknown error')}"
                
        except Exception as e:
            self.initialization_error = f"Could not verify sheet headers: {str(e)}"

    def _make_request(self, payload: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
        """Make HTTP request to Google Apps Script."""
        try:
            response = requests.post(
                self.apps_script_url,
                json=payload,
                timeout=timeout,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request to Apps Script failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response from Apps Script: {str(e)}")

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
        Log a user session to the User Sessions sheet via Apps Script.
        
        Args:
            user_name: User's full name
            business_email: User's business email
            company: User's company/organization
            session_id: Unique session identifier
            session_type: Type of session (LOGIN, VISIT, etc.)
        
        Returns:
            bool: True if logging was successful, False otherwise
        """
        if not self.enabled or not self.apps_script_url:
            return False
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            
            payload = {
                'action': 'log_user_session',
                'data': {
                    'timestamp': timestamp,
                    'user_name': user_name,
                    'business_email': business_email,
                    'company': company,
                    'session_id': session_id,
                    'session_type': session_type,
                    'user_agent': '-',  # Could be enhanced later
                    'ip_address': '-',  # Privacy considerations
                    'platform_status': 'ACTIVE'
                }
            }
            
            response = self._make_request(payload)
            return response.get('success', False)
            
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
        Log a report generation event to the Report Generation sheet via Apps Script.
        
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
        if not self.enabled or not self.apps_script_url:
            return False
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            sections_str = ', '.join(sections_generated) if sections_generated else 'None'
            
            # Extract token information
            total_tokens = token_stats.get('summary', {}).get('total_tokens', 0) if token_stats else 0
            input_tokens = token_stats.get('summary', {}).get('total_input_tokens', 0) if token_stats else 0
            output_tokens = token_stats.get('summary', {}).get('total_output_tokens', 0) if token_stats else 0
            
            payload = {
                'action': 'log_report_generation',
                'data': {
                    'timestamp': timestamp,
                    'user_name': user_name,
                    'business_email': business_email,
                    'target_company': target_company,
                    'context_company': context_company,
                    'language': language,
                    'sections_generated': sections_str,
                    'total_sections': len(sections_generated) if sections_generated else 0,
                    'report_success': report_success,
                    'session_id': session_id,
                    'generation_time': round(generation_time, 2),
                    'total_tokens': total_tokens,
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                    'error_message': error_message
                }
            }
            
            response = self._make_request(payload)
            return response.get('success', False)
            
        except Exception as e:
            return False


# Global analytics logger instance
enhanced_analytics_logger = EnhancedAnalyticsLogger()


def generate_session_id() -> str:
    """
    Generate a unique session ID.
    
    Returns:
        str: Unique session identifier
    """
    return enhanced_analytics_logger.generate_session_id()


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


def show_analytics_status():
    """Show the current analytics status in the Streamlit sidebar."""
    if enhanced_analytics_logger.enabled:
        if enhanced_analytics_logger.initialization_error:
            st.sidebar.error(f"📊 Analytics: Error - {enhanced_analytics_logger.initialization_error}")
        else:
            st.sidebar.success("📊 Analytics: Active (Apps Script)")
    else:
        st.sidebar.info("📊 Analytics: Disabled") 