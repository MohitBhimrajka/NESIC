"""
User authentication and information collection for the ARA Streamlit app.
"""

import streamlit as st
import re
from email_validator import validate_email, EmailNotValidError
from analytics_logger_apps_script import generate_session_id, log_user_session_start


def is_valid_business_email(email: str) -> tuple[bool, str]:
    """
    Validate business email address format and domain.
    
    Args:
        email: Email address to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Use email-validator library for robust validation
        valid = validate_email(email)
        email = valid.email  # Get normalized email
        
        # Get domain from email
        domain = email.split('@')[1].lower()
        
        # List of personal email providers to block
        personal_domains = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 
            'yahoo.co.uk', 'yahoo.co.in', 'yahoo.ca', 'yahoo.com.au',
            'hotmail.co.uk', 'hotmail.fr', 'live.com', 'msn.com',
            'aol.com', 'icloud.com', 'me.com', 'mac.com',
            'protonmail.com', 'proton.me', 'mail.com', 'yandex.com',
            'rediffmail.com', 'zoho.com', 'mailinator.com'
        }
        
        if domain in personal_domains:
            return False, f"Please use a business email address. {domain} is not allowed."
        
        # Additional check for common personal email patterns
        if any(pattern in domain for pattern in ['mail.', 'email.', 'webmail.']):
            return False, "Please use a business email address."
            
        return True, ""
        
    except EmailNotValidError as e:
        return False, "Please enter a valid email address format."


def show_user_info_form() -> bool:
    """
    Display user information collection form and handle validation.
    
    Returns:
        bool: True if user info was successfully collected, False otherwise
    """
    
    # Clean, professional authentication styling
    st.markdown("""
    <style>
    /* Brand Colors */
    :root {
        --primary-navy: #000b37;
        --primary-lime: #85c20b;
        --secondary-dark-gray: #474747;
        --secondary-light-gray: #c7c7c7;
        --secondary-light-lime: #c3fb54;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Hide sidebar completely */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Authentication container */
    .auth-container {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
    }
    
    .auth-card {
        background: white;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 11, 55, 0.12);
        padding: 2rem;
        width: 100%;
        max-width: 100%;
        border: 1px solid rgba(133, 194, 11, 0.1);
        position: relative;
        overflow: hidden;
        margin-bottom: 1rem;
    }
    
    .auth-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-lime) 0%, var(--secondary-light-lime) 100%);
    }
    
    /* Logo and header */
    .auth-logo {
        max-width: 60px;
        max-height: 60px;
        margin: 0 auto 1rem auto;
        display: block;
    }
    
    .auth-title {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-navy);
        text-align: center;
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }
    
    .auth-subtitle {
        font-size: 1rem;
        color: var(--secondary-dark-gray);
        text-align: center;
        margin-bottom: 1.5rem;
        line-height: 1.3;
    }
    
    .auth-highlight {
        color: var(--primary-lime);
        font-weight: 600;
    }
    
    /* Form styling */
    .auth-form-header {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .auth-form-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--primary-navy);
        margin-bottom: 0.3rem;
    }
    
    .auth-form-subtitle {
        font-size: 0.9rem;
        color: var(--secondary-dark-gray);
        margin: 0;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border: 2px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
        background: #f8fafc !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-lime) !important;
        background: white !important;
        box-shadow: 0 0 0 3px rgba(133, 194, 11, 0.1) !important;
    }
    
    .stTextInput > div > div > input:hover {
        border-color: var(--primary-navy) !important;
        background: white !important;
    }
    
    .stTextInput > label {
        font-weight: 600 !important;
        color: var(--primary-navy) !important;
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-lime) 0%, var(--secondary-light-lime) 100%) !important;
        color: var(--primary-navy) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem 2rem !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(133, 194, 11, 0.3) !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--secondary-light-lime) 0%, var(--primary-lime) 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(133, 194, 11, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Email hint */
    .email-hint {
        background: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 0.75rem;
        margin: 1rem 0;
        font-size: 0.9rem;
        color: #92400e;
        text-align: center;
    }
    
    /* Simple benefits */
    .auth-benefits {
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e2e8f0;
    }
    
    .benefit-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
        font-size: 0.95rem;
        color: var(--secondary-dark-gray);
    }
    
    .benefit-icon {
        font-size: 1.2rem;
        color: var(--primary-lime);
    }
    
    /* Compact spacing */
    .main .block-container {
        padding: 0.5rem 1rem !important;
        max-width: 100% !important;
    }
    
    /* Error styling */
    .stAlert {
        border-radius: 8px !important;
        margin: 0.5rem 0 !important;
    }

    /* Loading state */
    .auth-loading {
        opacity: 0.7;
        pointer-events: none;
    }
    
    /* Success message */
    .auth-success {
        background: #f0f9ff;
        border: 1px solid #0ea5e9;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        margin: 1rem 0;
        color: #0369a1;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get logo for display
    from pathlib import Path
    import base64
    
    @st.cache_data
    def get_auth_logo_base64():
        try:
            logo_path = Path("templates/assets/supervity_logo.png")
            if not logo_path.exists():
                return ""
            with open(logo_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except Exception:
            return ""
    
    # Single clean authentication card
    logo_base64 = get_auth_logo_base64()
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="auth-logo">' if logo_base64 else ""
    
    st.markdown(f"""
    <div class="auth-card">
        {logo_html}
        <h1 class="auth-title">Account Research <span class="auth-highlight">AI Agent</span></h1>
        <p class="auth-subtitle">Professional company intelligence reports in minutes</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Form header section
    st.markdown("""
    <div class="auth-form-header">
        <h2 class="auth-form-title">Access Platform</h2>
        <p class="auth-form-subtitle">Start generating comprehensive business research reports</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Clean form without cluttered layout
    with st.form("user_info_form", clear_on_submit=False):
        # Full name
        user_name = st.text_input(
            "Full Name",
            placeholder="Enter your full name",
            help="Required for professional report attribution"
        )
        
        # Business email (most important field)
        business_email = st.text_input(
            "Business Email",
            placeholder="yourname@company.com",
            help="Must be a business email address (no Gmail, Yahoo, etc.)"
        )
        
        # Company name (optional but helpful)
        user_company = st.text_input(
            "Company Name (Optional)",
            placeholder="Your company or organization",
            help="Helps personalize your reports"
        )
        
        # Clear email hint
        st.markdown("""
        <div class="email-hint">
            💡 <strong>Business Email Required:</strong> Use your company email address. Personal emails (Gmail, Yahoo, Hotmail, etc.) are not accepted.
        </div>
        """, unsafe_allow_html=True)
        
        # Single, prominent submit button
        submit_button = st.form_submit_button(
            "Access Platform",
            use_container_width=True,
            type="primary"
        )
    
    # Simple benefits below form
    st.markdown("""
    <div class="auth-benefits">
        <div class="benefit-item">
            <span class="benefit-icon">🏢</span>
            <span>Professional company analysis reports</span>
        </div>
        <div class="benefit-item">
            <span class="benefit-icon">⚡</span>
            <span>Generate comprehensive reports in 15-20 minutes</span>
        </div>
        <div class="benefit-item">
            <span class="benefit-icon">🌍</span>
            <span>Multi-language support for global reach</span>
        </div>
        <div class="benefit-item">
            <span class="benefit-icon">📊</span>
            <span>Financial, strategic, and competitive insights</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Handle form submission
    if submit_button:
        # Validation with clean error display
        errors = []
        
        if not user_name or not user_name.strip():
            errors.append("Please enter your full name")
        
        if not business_email or not business_email.strip():
            errors.append("Please enter your business email address")
        else:
            email_valid, email_error = is_valid_business_email(business_email.strip())
            if not email_valid:
                errors.append(email_error)
        
        # Display errors if any
        if errors:
            for error in errors:
                st.error(f"⚠️ {error}")
            return False
        
        # If validation passes, store user info and show success
        session_id = generate_session_id()
        
        # Store in session state
        st.session_state.user_authenticated = True
        st.session_state.user_name = user_name.strip()
        st.session_state.business_email = business_email.strip().lower()
        st.session_state.user_company = user_company.strip() if user_company else ""
        st.session_state.session_id = session_id
        
        # Log session start
        log_user_session_start(
            user_name=st.session_state.user_name,
            business_email=st.session_state.business_email,
            company=st.session_state.user_company,
            session_id=session_id
        )
        
        # Show professional success message
        st.markdown("""
        <div class="auth-success">
            🎉 <strong>Welcome aboard!</strong> Redirecting you to the platform...
        </div>
        """, unsafe_allow_html=True)
        
        # Smooth transition without jarring rerun
        import time
        time.sleep(1)  # Brief pause for better UX
        st.rerun()
        
    return False


def check_user_authentication() -> bool:
    """
    Check if user is authenticated and has provided required information.
    
    Returns:
        bool: True if user is authenticated, False otherwise
    """
    return (
        st.session_state.get('user_authenticated', False) and
        st.session_state.get('user_name') and
        st.session_state.get('business_email') and
        st.session_state.get('session_id')
    )


def get_user_info() -> dict:
    """
    Get current user information from session state.
    
    Returns:
        dict: User information including name, email, company, and session_id
    """
    return {
        'name': st.session_state.get('user_name', ''),
        'email': st.session_state.get('business_email', ''),
        'company': st.session_state.get('user_company', ''),
        'session_id': st.session_state.get('session_id', '')
    }


def reset_user_session():
    """Reset user session - useful for debugging or logout functionality."""
    keys_to_remove = [
        'user_authenticated',
        'user_name', 
        'business_email',
        'user_company',
        'session_id'
    ]
    
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]


def show_user_info_header():
    """Display current user info in a compact footer area."""
    if check_user_authentication():
        user_info = get_user_info()
        
        # Compact user info display for footer
        st.markdown("""
        <style>
        .user-info-footer {
            background: linear-gradient(90deg, #f8fafc 0%, #e2e8f0 100%);
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin: 1rem 0 0.5rem 0;
            font-size: 0.85rem;
            color: #475569;
            text-align: center;
        }
        
        .user-info-content {
            display: flex;
            align-items: center;
            justify-content: center;
            flex-wrap: wrap;
            gap: 1.5rem;
        }
        
        .user-badge-footer {
            background: #000b37;
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        </style>
        """, unsafe_allow_html=True)
        
        company_display = f" • {user_info['company']}" if user_info['company'] else ""
        
        st.markdown(f"""
        <div class="user-info-footer">
            <div class="user-info-content">
                <span><strong>👤 {user_info['name']}</strong></span>
                <span>📧 {user_info['email']}{company_display}</span>
                <span class="user-badge-footer">Session: {user_info['session_id']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def require_authentication(func):
    """
    Decorator to require user authentication before accessing a function.
    
    Args:
        func: Function to wrap with authentication requirement
        
    Returns:
        Wrapped function that checks authentication first
    """
    def wrapper(*args, **kwargs):
        if not check_user_authentication():
            show_user_info_form()
            return None
        return func(*args, **kwargs)
    
    return wrapper 