"""
Test script to verify Google Apps Script integration works correctly.
Run this after setting up the Apps Script and environment variables.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append('.')

from analytics_logger_apps_script import enhanced_analytics_logger

def test_apps_script_integration():
    """Test the Apps Script integration."""
    
    print("🧪 Testing Google Apps Script Integration")
    print("=" * 50)
    
    # Check if analytics is enabled
    if not enhanced_analytics_logger.enabled:
        print("❌ Analytics is disabled")
        if enhanced_analytics_logger.initialization_error:
            print(f"   Error: {enhanced_analytics_logger.initialization_error}")
        return False
    
    print("✅ Analytics is enabled")
    
    # Check Apps Script URL
    if not enhanced_analytics_logger.apps_script_url:
        print("❌ Apps Script URL not configured")
        return False
    
    print(f"✅ Apps Script URL: {enhanced_analytics_logger.apps_script_url}")
    
    # Test header initialization
    print("\n📝 Testing header initialization...")
    try:
        enhanced_analytics_logger._ensure_headers()
        if enhanced_analytics_logger.initialization_error:
            print(f"❌ Header initialization failed: {enhanced_analytics_logger.initialization_error}")
            return False
        print("✅ Headers initialized successfully")
    except Exception as e:
        print(f"❌ Header initialization error: {str(e)}")
        return False
    
    # Test user session logging
    print("\n👤 Testing user session logging...")
    session_id = enhanced_analytics_logger.generate_session_id()
    success = enhanced_analytics_logger.log_user_session(
        user_name="Test User",
        business_email="test@example.com",
        company="Test Company",
        session_id=session_id,
        session_type="TEST"
    )
    
    if success:
        print("✅ User session logged successfully")
    else:
        print("❌ User session logging failed")
        return False
    
    # Test report generation logging
    print("\n📊 Testing report generation logging...")
    token_stats = {
        'summary': {
            'total_tokens': 1000,
            'total_input_tokens': 500,
            'total_output_tokens': 500
        }
    }
    
    success = enhanced_analytics_logger.log_report_generation(
        user_name="Test User",
        business_email="test@example.com",
        target_company="Target Corp",
        context_company="Test Company",
        language="English",
        sections_generated=["basic", "financial"],
        report_success=True,
        session_id=session_id,
        generation_time=30.5,
        token_stats=token_stats
    )
    
    if success:
        print("✅ Report generation logged successfully")
    else:
        print("❌ Report generation logging failed")
        return False
    
    print("\n🎉 All tests passed! Apps Script integration is working correctly.")
    return True

if __name__ == "__main__":
    try:
        success = test_apps_script_integration()
        if not success:
            print("\n❌ Some tests failed. Please check your configuration.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {str(e)}")
        sys.exit(1) 