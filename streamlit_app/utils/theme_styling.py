import streamlit as st

def load_theme_css(theme="Light"):
    """Load theme-aware CSS styles for light and dark modes"""
    
    # Base CSS that's common to both themes
    base_css = """
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Smooth transitions for theme switching */
    * {
        transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
    }
    """
    
    # Light theme CSS
    light_theme_css = """
    /* Light Theme Variables */
    :root {
        --bg-primary: #ffffff;
        --bg-secondary: #f8f9fa;
        --bg-tertiary: #e9ecef;
        --text-primary: #212529;
        --text-secondary: #495057;
        --text-tertiary: #6c757d;
        --border-color: #dee2e6;
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.15);
        --accent-primary: #3b82f6;
        --accent-secondary: #8b5cf6;
        --accent-success: #10b981;
        --accent-warning: #f59e0b;
        --accent-danger: #ef4444;
    }
    
    /* Light theme specific styles */
    .stApp {
        background-color: var(--bg-secondary);
    }
    
    section[data-testid="stSidebar"] {
        background-color: var(--bg-primary);
        border-right: 1px solid var(--border-color);
    }
    
    .info-card {
        background-color: var(--bg-primary);
        border: 1px solid var(--border-color);
    }
    
    .contribution-card {
        background-color: var(--bg-tertiary);
        border: 1px solid var(--border-color);
    }
    """
    
    # Dark theme CSS
    dark_theme_css = """
    /* Dark Theme Variables */
    :root {
        --bg-primary: #1a1b26;
        --bg-secondary: #16161e;
        --bg-tertiary: #24283b;
        --text-primary: #c0caf5;
        --text-secondary: #a9b1d6;
        --text-tertiary: #9aa5ce;
        --border-color: #414868;
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
        --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
        --accent-primary: #7aa2f7;
        --accent-secondary: #bb9af7;
        --accent-success: #9ece6a;
        --accent-warning: #e0af68;
        --accent-danger: #f7768e;
    }
    
    /* Dark theme specific styles */
    .stApp {
        background-color: var(--bg-secondary);
    }
    
    section[data-testid="stSidebar"] {
        background-color: var(--bg-primary);
        border-right: 1px solid var(--border-color);
    }
    
    .info-card {
        background-color: var(--bg-primary);
        border: 1px solid var(--border-color);
    }
    
    .contribution-card {
        background-color: var(--bg-tertiary);
        border: 1px solid var(--border-color);
    }
    
    /* Dark mode metric styling */
    [data-testid="metric-container"] {
        background-color: var(--bg-primary) !important;
        border-color: var(--border-color) !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: var(--accent-primary) !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: var(--text-secondary) !important;
    }
    """
    
    # Common CSS for both themes
    common_css = """
    <style>
    """ + base_css + """
    
    /* Apply theme variables */
    """ + (dark_theme_css if theme == "Dark" else light_theme_css) + """
    
    /* Common styles that use CSS variables */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary) !important;
        background-color: var(--bg-secondary);
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        font-weight: 700;
    }
    
    /* Paragraphs and text */
    p, span, div {
        color: var(--text-primary) !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] .stMarkdown {
        color: var(--text-primary) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: var(--accent-primary);
        color: white !important;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: 600;
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button:hover {
        filter: brightness(1.1);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: var(--bg-primary) !important;
        border: 2px solid var(--border-color) !important;
        color: var(--text-primary) !important;
        border-radius: 0.5rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Select boxes */
    .stSelectbox > div > div > select {
        background-color: var(--bg-primary) !important;
        border: 2px solid var(--border-color) !important;
        color: var(--text-primary) !important;
        border-radius: 0.5rem;
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: var(--shadow-sm);
    }
    
    /* Info cards */
    .info-card {
        padding: 1.5rem;
        border-radius: 0.75rem;
        text-align: center;
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    .info-card h2 {
        color: var(--accent-primary) !important;
        margin: 0;
    }
    
    .info-card p {
        color: var(--text-secondary) !important;
        margin: 0.5rem 0 0 0;
    }
    
    /* Contribution cards */
    .contribution-card {
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        box-shadow: var(--shadow-sm);
    }
    
    .contribution-card h2 {
        color: var(--text-primary) !important;
        font-size: 2rem;
        margin: 0.5rem 0;
    }
    
    .contribution-card h5 {
        color: var(--text-primary) !important;
        margin: 0.5rem 0;
    }
    
    .contribution-card p {
        color: var(--text-secondary) !important;
        font-size: 0.875rem;
    }
    
    /* Hero gradient (same for both themes) */
    .hero-gradient {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white !important;
        padding: 3rem;
        border-radius: 1rem;
        text-align: center;
    }
    
    .hero-gradient h1, .hero-gradient h2, .hero-gradient p {
        color: white !important;
    }
    
    /* Feature cards (same gradients for both themes) */
    .feature-card-1 {
        background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
        color: white !important;
        padding: 2rem;
        border-radius: 0.75rem;
        height: 200px;
    }
    
    .feature-card-2 {
        background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
        color: white !important;
        padding: 2rem;
        border-radius: 0.75rem;
        height: 200px;
    }
    
    .feature-card-3 {
        background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
        color: white !important;
        padding: 2rem;
        border-radius: 0.75rem;
        height: 200px;
    }
    
    .feature-card-1 h3, .feature-card-2 h3, .feature-card-3 h3,
    .feature-card-1 p, .feature-card-2 p, .feature-card-3 p {
        color: white !important;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background-color: var(--bg-primary);
        padding: 0.5rem;
        border-radius: 0.5rem;
        border: 1px solid var(--border-color);
    }
    
    .stRadio label {
        color: var(--text-primary) !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: var(--bg-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 0.5rem;
        color: var(--text-primary) !important;
    }
    
    /* File uploader */
    .stFileUploader > div > div > div {
        background-color: var(--bg-tertiary) !important;
        border: 2px dashed var(--border-color) !important;
        border-radius: 0.5rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        background-color: var(--bg-tertiary);
        color: var(--text-primary) !important;
        border-radius: 0.5rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--accent-primary);
        color: white !important;
    }
    
    /* Links */
    a {
        color: var(--accent-primary) !important;
    }
    
    a:hover {
        color: var(--accent-secondary) !important;
    }
    
    /* Markdown */
    .stMarkdown {
        color: var(--text-primary) !important;
    }
    
    /* Dividers */
    hr {
        border-color: var(--border-color) !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-tertiary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-tertiary);
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .hero-gradient {
            padding: 2rem;
        }
        
        .feature-card-1, .feature-card-2, .feature-card-3 {
            height: auto;
            min-height: 150px;
        }
    }
    </style>
    """
    
    st.markdown(common_css, unsafe_allow_html=True)
