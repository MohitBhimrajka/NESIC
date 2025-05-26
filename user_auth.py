"""
User authentication and information collection for the ARA Streamlit app.
"""

import streamlit as st
import re
from email_validator import validate_email, EmailNotValidError
from analytics_logger import generate_session_id, log_user_session_start


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
    
    # Simple professional styling matching main app
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
        background-color: #f7f7f7;
    }
    
    /* Header styling matching main app */
    .auth-header {
        background-color: var(--primary-navy);
        padding: 1.5rem 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .auth-logo {
        max-width: 60px;
        max-height: 60px;
        margin: 0 auto 0.5rem auto;
        display: block;
    }
    
    .auth-title {
        color: white !important;
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .auth-subtitle {
        color: var(--primary-lime);
        font-size: 1rem;
        font-weight: 400;
        margin: 0;
    }
    
    /* Compact form container styling */
    .main-form-container {
        background: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border: 1px solid #e1e5e9;
        margin: 1rem auto;
        max-width: 700px;
    }
    
    .form-header {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .form-main-title {
        font-size: 1.6rem;
        font-weight: 600;
        color: var(--primary-navy);
        margin-bottom: 0.3rem;
    }
    
    .form-subtitle {
        font-size: 0.95rem;
        color: var(--secondary-dark-gray);
        margin: 0;
        line-height: 1.4;
    }
    
    /* Benefits section below form styling */
    .benefits-section-bottom {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 3rem 2rem;
        border-radius: 15px;
        margin-top: 2rem;
        border: 1px solid #e1e5e9;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    
    .benefits-header {
        text-align: center;
        margin-bottom: 2.5rem;
    }
    
    .benefits-main-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--primary-navy);
        margin-bottom: 0.5rem;
    }
    
    .benefits-description {
        font-size: 1.1rem;
        color: var(--secondary-dark-gray);
        margin: 0;
        font-style: italic;
    }
    
    .benefits-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .benefit-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-left: 4px solid var(--primary-lime);
    }
    
    .benefit-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    }
    
    .benefit-card-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .benefit-card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--primary-navy);
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .benefit-card-desc {
        font-size: 0.9rem;
        color: var(--secondary-dark-gray);
        line-height: 1.5;
        text-align: center;
        margin: 0;
    }
    
    .trust-section {
        display: flex;
        justify-content: center;
        gap: 2rem;
        flex-wrap: wrap;
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid #cbd5e1;
    }
    
    .trust-badge {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background: white;
        padding: 0.8rem 1.2rem;
        border-radius: 25px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--primary-navy);
    }
    
    .trust-badge-icon {
        font-size: 1.1rem;
    }
    
    .privacy-notice {
        background: #f0f2f6;
        border: 1px solid var(--secondary-light-gray);
        border-radius: 6px;
        padding: 0.8rem;
        margin: 1rem 0;
        font-size: 0.8rem;
        color: var(--secondary-dark-gray);
    }
    
    .email-hint {
        background: #fff3cd;
        border: 1px solid #f59e0b;
        border-radius: 6px;
        padding: 0.6rem;
        margin-top: 0.5rem;
        font-size: 0.8rem;
        color: #92400e;
    }
    
    /* Compact professional button styling */
    .stButton>button {
        width: 100%;
        padding: 0.7rem 1.5rem;
        background: linear-gradient(135deg, var(--primary-lime) 0%, var(--secondary-light-lime) 100%);
        color: var(--primary-navy);
        font-weight: 600;
        font-size: 0.95rem;
        border: none;
        border-radius: 8px;
        transition: all 0.3s ease;
        letter-spacing: 0.5px;
        margin-top: 0.5rem;
        box-shadow: 0 3px 12px rgba(133, 194, 11, 0.25);
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, var(--secondary-light-lime) 0%, var(--primary-lime) 100%);
        box-shadow: 0 4px 15px rgba(133, 194, 11, 0.35);
        transform: translateY(-2px);
    }

    .stButton>button:active {
        transform: translateY(0px);
        box-shadow: 0 2px 8px rgba(133, 194, 11, 0.3);
    }
    
    /* Enhanced input fields styling */
    div[data-baseweb="input"] {
        border-radius: 10px;
        border: 2px solid #cbd5e1;
        background: #f8fafc;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    div[data-baseweb="input"]:focus-within {
        border-color: var(--primary-lime);
        background: white;
        box-shadow: 0 0 0 3px rgba(133, 194, 11, 0.15), 0 4px 12px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }

    div[data-baseweb="input"]:hover {
        border-color: var(--primary-navy);
        background: white;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.08);
        transform: translateY(-1px);
    }

    /* Input labels styling */
    .stTextInput > label {
        font-weight: 600;
        color: var(--primary-navy);
        font-size: 0.95rem;
    }
    
    /* Placeholder text enhancement */
    input::placeholder {
        color: #94a3b8;
        font-style: italic;
        font-weight: 400;
    }
    
    /* Ultra compact spacing */
    .main .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
        max-width: 900px;
    }
    
    /* Reduce gaps between sections */
    .element-container {
        margin-bottom: 0.5rem;
    }
    
    /* Benefit card hover effects */
    .benefit-card-hover:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get logo for display
    from pathlib import Path
    import base64
    
    @st.cache_data
    def get_auth_logo_base64():
        try:
            logo_path = Path("templates/assets/supervity_light_logo.png")
            if not logo_path.exists():
                return ""
            with open(logo_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except Exception:
            return ""
    
    # Header section with logo
    logo_base64 = get_auth_logo_base64()
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="auth-logo">' if logo_base64 else ""
    
    st.markdown(f"""
    <div class="auth-header">
        {logo_html}
        <h1 class="auth-title">Account Research AI Agent</h1>
        <p class="auth-subtitle">Your intelligent research assistant for comprehensive company analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Compact form container
    with st.form("user_info_form", clear_on_submit=False):
        st.markdown("""
        <div class="main-form-container">
            <div class="form-header">
                <h2 class="form-main-title">Get Started</h2>
                <p class="form-subtitle">Enter your details to access the platform and generate professional company research reports</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Single row: All fields side by side for compact layout
        form_col1, form_col2, form_col3 = st.columns([2, 2, 3], gap="medium")
        
        with form_col1:
            user_name = st.text_input(
                "👤 Full Name",
                placeholder="Your Name",
                label_visibility="collapsed"
            )
        
        with form_col2:
            user_company = st.text_input(
                "🏢 Company",
                placeholder="Your Company",
                label_visibility="collapsed"
            )
        
        with form_col3:
            business_email = st.text_input(
                "📧 Business Email",
                placeholder="your.namee@yourcompany.com",
                label_visibility="collapsed"
            )
        
        # Email validation hint (compact)
        st.markdown("""
        <div style="text-align: center; font-size: 0.8rem; color: #92400e; background: #fff3cd; 
                    border-radius: 6px; padding: 0.4rem; margin: 0.5rem 0;">
            📝 Use your business email address (no Gmail, Yahoo, etc.)
        </div>
        """, unsafe_allow_html=True)
        
        # Submit button (centered, compact)
        col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 2])
        with col_btn2:
            submit_button = st.form_submit_button(
                "🚪 Enter Platform",
                use_container_width=True,
                type="primary"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close form container
    
    # Benefits section below the form
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Benefits header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <h3 style="font-size: 1.5rem; font-weight: 600; color: #000b37; margin-bottom: 0.3rem;">What Awaits You Inside</h3>
        <p style="font-size: 0.95rem; color: #474747; margin: 0; font-style: italic;">Unlock powerful insights and comprehensive analysis tools</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Benefits cards using Streamlit columns
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); padding: 1.2rem; 
                    border-radius: 12px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); 
                    border: 1px solid #e2e8f0; text-align: center; height: 180px;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                    position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 4px; 
                        background: linear-gradient(90deg, #85c20b 0%, #c3fb54 100%);"></div>
            <div style="font-size: 2.2rem; margin-bottom: 0.8rem; 
                        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));">🏢</div>
            <h4 style="font-size: 1.05rem; font-weight: 700; color: #000b37; margin-bottom: 0.5rem;">Professional Reports</h4>
            <p style="font-size: 0.85rem; color: #475569; line-height: 1.4; margin: 0;">Comprehensive company analysis with detailed insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); padding: 1.2rem; 
                    border-radius: 12px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); 
                    border: 1px solid #e2e8f0; text-align: center; height: 180px;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                    position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 4px; 
                        background: linear-gradient(90deg, #31b8e1 0%, #8289ec 100%);"></div>
            <div style="font-size: 2.2rem; margin-bottom: 0.8rem; 
                        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));">🌍</div>
            <h4 style="font-size: 1.05rem; font-weight: 700; color: #000b37; margin-bottom: 0.5rem;">Multi-Language</h4>
            <p style="font-size: 0.85rem; color: #475569; line-height: 1.4; margin: 0;">Generate reports in 10+ languages for global reach</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); padding: 1.2rem; 
                    border-radius: 12px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); 
                    border: 1px solid #e2e8f0; text-align: center; height: 180px;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                    position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 4px; 
                        background: linear-gradient(90deg, #ff9a5a 0%, #ff94a8 100%);"></div>
            <div style="font-size: 2.2rem; margin-bottom: 0.8rem; 
                        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));">📊</div>
            <h4 style="font-size: 1.05rem; font-weight: 700; color: #000b37; margin-bottom: 0.5rem;">Deep Analysis</h4>
            <p style="font-size: 0.85rem; color: #475569; line-height: 1.4; margin: 0;">Financials, strategy, management, and competitive insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); padding: 1.2rem; 
                    border-radius: 12px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); 
                    border: 1px solid #e2e8f0; text-align: center; height: 180px;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                    position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 4px; 
                        background: linear-gradient(90deg, #b181ff 0%, #8289ec 100%);"></div>
            <div style="font-size: 2.2rem; margin-bottom: 0.8rem; 
                        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));">⚡</div>
            <h4 style="font-size: 1.05rem; font-weight: 700; color: #000b37; margin-bottom: 0.5rem;">AI-Powered Speed</h4>
            <p style="font-size: 0.85rem; color: #475569; line-height: 1.4; margin: 0;">Generate detailed reports in minutes, not hours</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Trust badges
    trust_col1, trust_col2, trust_col3 = st.columns([1, 2, 1])
    with trust_col2:
        st.markdown("""
        <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap; margin-top: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.4rem; background: white; padding: 0.5rem 1rem; 
                        border-radius: 20px; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05); font-weight: 500; color: #000b37; font-size: 0.85rem;">
                <span style="font-size: 1rem;">🔒</span> Enterprise Security
            </div>
            <div style="display: flex; align-items: center; gap: 0.4rem; background: white; padding: 0.5rem 1rem; 
                        border-radius: 20px; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05); font-weight: 500; color: #000b37; font-size: 0.85rem;">
                <span style="font-size: 1rem;">✨</span> Instant Access
            </div>
            <div style="display: flex; align-items: center; gap: 0.4rem; background: white; padding: 0.5rem 1rem; 
                        border-radius: 20px; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05); font-weight: 500; color: #000b37; font-size: 0.85rem;">
                <span style="font-size: 1rem;">🎯</span> Precision Analytics
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Handle form submission
    if submit_button:
        # Create an error container at the top for immediate visibility
        error_container = st.container()
        
        # Validation
        errors = []
        
        if not user_name or not user_name.strip():
            errors.append("❌ Full name is required")
        
        if not business_email or not business_email.strip():
            errors.append("❌ Business email is required")
        else:
            email_valid, email_error = is_valid_business_email(business_email.strip())
            if not email_valid:
                errors.append(f"❌ {email_error}")
        
        # Display errors prominently at the top if any
        if errors:
            with error_container:
                st.markdown("### ⚠️ Please fix the following issues:")
                for error in errors:
                    st.error(error)
                st.markdown("---")
            return False
        
        # If validation passes, store user info
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
        
        st.success("✅ Information saved! Redirecting to the app...")
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