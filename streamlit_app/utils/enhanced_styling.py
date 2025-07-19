import streamlit as st


def load_enhanced_css():
    """Load enhanced CSS styles for the Streamlit app"""
    enhanced_css = """
    <style>
        
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=DM+Serif+Display&family=JetBrains+Mono:wght@400;500;600&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@300;400;500;600;700&display=swap');

        /* CSS Variables for professional theming */
        :root {
            /* Modern Color Palette */
            --primary-gradient: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
            --accent-gradient: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
            --success-gradient: linear-gradient(135deg, #10B981 0%, #34D399 100%);
            --danger-gradient: linear-gradient(135deg, #EF4444 0%, #F87171 100%);
            --glass-gradient: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
            
            /* Base Colors */
            --primary-color: #0F172A;
            --secondary-color: #1E293B;
            --accent-color: #3B82F6;
            --accent-hover: #2563EB;
            
            /* Text Colors */
            --text-primary: #0F172A;
            --text-secondary: #64748B;
            --text-muted: #94A3B8;
            --text-inverse: #F8FAFC;
            
            /* Background Colors */
            --bg-primary: #FFFFFF;
            --bg-secondary: #F8FAFC;
            --bg-tertiary: #F1F5F9;
            --bg-dark: #0F172A;
            --bg-glass: rgba(255, 255, 255, 0.95);
            
            /* Border Colors */
            --border-color: #E2E8F0;
            --border-light: #F1F5F9;
            --border-dark: #CBD5E1;
            
            /* Shadows - Professional Depth */
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            --shadow-glow: 0 0 50px rgba(59, 130, 246, 0.5);
            
            /* Transitions */
            --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
            --transition-base: 300ms cubic-bezier(0.4, 0, 0.2, 1);
            --transition-slow: 500ms cubic-bezier(0.4, 0, 0.2, 1);
            --transition-spring: 600ms cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }

        /* Global font and color styles */
        html, body, [class*="css"] {
            font-family: 'Inter', 'Noto Sans Devanagari', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: var(--text-primary);
            line-height: 1.6;
            font-weight: 400;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        /* Professional Headings */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'DM Serif Display', 'Noto Sans Devanagari', serif;
            font-weight: 400;
            line-height: 1.2;
            color: var(--text-primary);
            letter-spacing: -0.02em;
        }

        /* Main app background - Modern gradient */
        .stApp {
            background: linear-gradient(180deg, #FAFBFC 0%, #F3F4F6 100%);
            background-attachment: fixed;
            min-height: 100vh;
        }

        /* Main container styling */
        .main .block-container {
            padding-top: 3rem;
            padding-bottom: 3rem;
            max-width: 1280px;
            margin: 0 auto;
        }

        /* Professional sidebar styling */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #F8FAFC 0%, #E2E8F0 100%);
            border-right: 1px solid var(--border-color);
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.05);
        }

        section[data-testid="stSidebar"] .block-container {
            padding-top: 2rem;
        }

        /* Sidebar text color */
        section[data-testid="stSidebar"] p, 
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3, 
        section[data-testid="stSidebar"] h4, 
        section[data-testid="stSidebar"] h5, 
        section[data-testid="stSidebar"] h6,
        section[data-testid="stSidebar"] label {
            color: var(--text-primary) !important;
        }

        /* Sidebar navigation items */
        section[data-testid="stSidebar"] .stRadio > label {
            color: var(--text-primary);
            font-weight: 600;
            transition: all var(--transition-base);
            padding: 0.875rem 1.25rem;
            border-radius: 12px;
            margin: 0.5rem 0;
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border-light);
        }

        section[data-testid="stSidebar"] .stRadio > label:hover {
            background: var(--bg-primary);
            transform: translateX(8px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            color: var(--accent-color);
        }

        /* Beautiful metric containers */
        [data-testid="metric-container"] {
            background: white;
            border: none;
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: var(--shadow-md);
            transition: all var(--transition-base);
            position: relative;
            overflow: hidden;
        }

        [data-testid="metric-container"]:before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--primary-gradient);
            opacity: 0;
            transition: opacity var(--transition-base);
        }

        [data-testid="metric-container"]:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-xl);
        }

        [data-testid="metric-container"]:hover:before {
            opacity: 1;
        }

        /* Metric value styling */
        [data-testid="metric-container"] [data-testid="metric-value"] {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 2rem;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        /* Metric label styling */
        [data-testid="metric-container"] [data-testid="metric-label"] {
            font-weight: 500;
            color: var(--text-secondary);
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.025em;
        }

        /* Modern button styles */
        .stButton>button {
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 0.875rem;
            letter-spacing: 0.025em;
            padding: 0.75rem 2rem;
            border-radius: 10px;
            border: none;
            background: var(--accent-gradient);
            color: white;
            box-shadow: 0 4px 14px 0 rgba(59, 130, 246, 0.25);
            transition: all var(--transition-base);
            position: relative;
            overflow: hidden;
        }

        .stButton>button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }

        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px 0 rgba(59, 130, 246, 0.35);
        }

        .stButton>button:hover::before {
            left: 100%;
        }

        /* Primary button variant */
        .stButton>button[kind="primary"] {
            background: var(--primary-gradient);
            box-shadow: 0 4px 14px 0 rgba(15, 23, 42, 0.25);
        }

        .stButton>button[kind="primary"]:hover {
            box-shadow: 0 6px 20px 0 rgba(15, 23, 42, 0.35);
        }

        /* Metric cards styling */
        [data-testid="metric-container"] {
            background: white;
            border: 1px solid #e9ecef;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }

        [data-testid="metric-container"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        /* Modern Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            border-bottom: 2px solid var(--border-light);
            padding-bottom: 0;
        }

        .stTabs [data-baseweb="tab"] {
            height: 48px;
            padding: 0px 28px;
            background: transparent;
            border: none;
            border-bottom: 3px solid transparent;
            border-radius: 0;
            color: var(--text-secondary);
            font-weight: 600;
            font-size: 0.9rem;
            transition: all var(--transition-base);
            position: relative;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: var(--accent-color);
            background: rgba(59, 130, 246, 0.05);
        }

        .stTabs [aria-selected="true"] {
            background: transparent;
            color: var(--accent-color);
            border-bottom-color: var(--accent-color);
        }

        /* Modern Input field styling */
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea {
            font-family: 'Inter', sans-serif;
            font-size: 0.95rem;
            border-radius: 10px;
            border: 2px solid var(--border-color);
            padding: 0.875rem 1rem;
            background: var(--bg-primary);
            transition: all var(--transition-base);
        }

        .stTextInput>div>div>input:focus,
        .stTextArea>div>div>textarea:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
            outline: none;
        }

        .stTextInput>div>div>input::placeholder,
        .stTextArea>div>div>textarea::placeholder {
            color: var(--text-muted);
        }

        /* Modern Selectbox styling */
        .stSelectbox>div>div>select {
            font-family: 'Inter', sans-serif;
            font-size: 0.95rem;
            border-radius: 10px;
            border: 2px solid var(--border-color);
            padding: 0.875rem 1rem;
            background: var(--bg-primary);
            transition: all var(--transition-base);
            cursor: pointer;
        }

        .stSelectbox>div>div>select:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
            outline: none;
        }

        /* Glass morphism card styles */
        .custom-card {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 16px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.18);
            padding: 2rem;
            margin: 1.5rem 0;
            transition: all var(--transition-base);
        }

        .custom-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.25);
        }

        /* Progress bar styling */
        .stProgress .st-bo {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }

        /* Alert enhancements */
        .stAlert {
            border-radius: 8px;
            border: none;
        }

        /* File uploader styling */
        .stFileUploader>div>div>div>div {
            border-radius: 8px;
            border: 2px dashed #667eea;
            background: #f8f9ff;
            transition: all 0.3s ease;
        }

        .stFileUploader>div>div>div>div:hover {
            border-color: #5a67d8;
            background: #f0f4ff;
        }

        /* Sidebar enhancements */
        .css-1d391kg {
            background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        }

        /* Radio button styling */
        .stRadio > div {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 0.5rem;
        }

        /* Checkbox styling */
        .stCheckbox > label {
            background: #f8f9fa;
            border-radius: 6px;
            padding: 0.5rem;
            transition: background-color 0.3s ease;
        }

        .stCheckbox > label:hover {
            background: #e9ecef;
        }

        /* Expander styling */
        .streamlit-expanderHeader {
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            transition: all 0.3s ease;
        }

        .streamlit-expanderHeader:hover {
            background: #e9ecef;
        }

        /* Animation classes */
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .slide-in {
            animation: slideIn 0.6s ease-out;
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-30px); }
            to { opacity: 1; transform: translateX(0); }
        }

        /* Gradient backgrounds */
        .gradient-bg-1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .gradient-bg-2 {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }

        .gradient-bg-3 {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }

        .gradient-bg-4 {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }

        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
        }

        /* Responsive design */
        @media (max-width: 768px) {
            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            
            .custom-card {
                padding: 1rem;
            }
            
            .stButton>button {
                padding: 0.5rem 1rem;
                font-size: 0.9rem;
            }
        }

        /* Loading spinner enhancement */
        .stSpinner > div {
            border-top-color: #667eea !important;
        }

        /* Plotly chart enhancements */
        .js-plotly-plot {
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

    </style>
    """
    st.markdown(enhanced_css, unsafe_allow_html=True)


def apply_enhanced_styling():
    """Apply enhanced styling to the Streamlit app"""
    load_enhanced_css()
