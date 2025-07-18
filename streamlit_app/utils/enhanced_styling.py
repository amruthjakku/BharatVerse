import streamlit as st


def load_enhanced_css():
    """Load enhanced CSS styles for the Streamlit app"""
    enhanced_css = """
    <style>
        
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Playfair+Display:wght@400;700;900&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@300;400;500;600;700&display=swap');

        /* CSS Variables for consistent theming */
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --success-gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            --warning-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --text-primary: #1a1a1a;
            --text-secondary: #6b7280;
            --bg-primary: #ffffff;
            --bg-secondary: #f9fafb;
            --border-color: #e5e7eb;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
            --transition-base: 300ms cubic-bezier(0.4, 0, 0.2, 1);
            --transition-slow: 500ms cubic-bezier(0.4, 0, 0.2, 1);
        }

        /* Global font and color styles */
        html, body, [class*="css"] {
            font-family: 'Poppins', 'Noto Sans Devanagari', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: var(--text-primary);
            line-height: 1.6;
            font-weight: 400;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        /* Headings with Playfair Display */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Playfair Display', 'Noto Sans Devanagari', serif;
            font-weight: 700;
            line-height: 1.3;
            color: var(--text-primary);
        }

        /* Main app background */
        .stApp {
            background: linear-gradient(180deg, #ffffff 0%, #f9fafb 50%, #f3f4f6 100%);
            background-attachment: fixed;
        }

        /* Main container styling */
        .main .block-container {
            padding-top: 3rem;
            padding-bottom: 3rem;
            max-width: 1280px;
            margin: 0 auto;
        }

        /* Beautiful sidebar styling */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #fafbfc 0%, #f4f5f7 100%);
            border-right: 1px solid rgba(0, 0, 0, 0.05);
        }

        section[data-testid="stSidebar"] .block-container {
            padding-top: 2rem;
        }

        /* Sidebar navigation items */
        section[data-testid="stSidebar"] .stRadio > label {
            font-weight: 500;
            transition: all var(--transition-fast);
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin: 0.25rem 0;
        }

        section[data-testid="stSidebar"] .stRadio > label:hover {
            background: rgba(102, 126, 234, 0.1);
            transform: translateX(4px);
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

        /* Enhanced button styles */
        .stButton>button {
            border-radius: 8px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 500;
            border: none;
            padding: 0.75rem 1.5rem;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .stButton>button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        /* Primary button variant */
        .stButton>button[kind="primary"] {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        }

        .stButton>button[kind="primary"]:hover {
            box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4);
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

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding: 0px 24px;
            background-color: #f8f9fa;
            border-radius: 8px;
            color: #495057;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        /* Input field enhancements */
        .stTextInput>div>div>input {
            border-radius: 8px;
            border: 2px solid #e9ecef;
            padding: 0.75rem;
            transition: border-color 0.3s ease;
        }

        .stTextInput>div>div>input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        /* Selectbox styling */
        .stSelectbox>div>div>select {
            border-radius: 8px;
            border: 2px solid #e9ecef;
            transition: border-color 0.3s ease;
        }

        /* Card component styles */
        .custom-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
            padding: 1.5rem;
            margin: 1rem 0;
            transition: all 0.3s ease;
            border: 1px solid #f1f3f4;
        }

        .custom-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
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
