import streamlit as st

def load_clean_css():
    """Load clean CSS styles with proper contrast for the Streamlit app"""
    clean_css = """
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* Override Streamlit defaults for better visibility */
        .stApp {
            background-color: #fafbfc;
        }
        
        /* Text visibility fixes */
        .stMarkdown, .stText, p, span, div {
            color: #1f2937 !important;
        }
        
        /* Headers with better contrast */
        h1, h2, h3, h4, h5, h6 {
            color: #111827 !important;
            font-family: 'Inter', sans-serif;
            font-weight: 700;
        }
        
        /* Main container */
        .main .block-container {
            padding: 2rem 3rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e5e7eb;
        }
        
        section[data-testid="stSidebar"] .stMarkdown {
            color: #374151 !important;
        }
        
        /* Button styling with high contrast */
        .stButton > button {
            background-color: #3b82f6;
            color: white !important;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            transition: all 0.2s;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .stButton > button:hover {
            background-color: #2563eb;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }
        
        /* Metric containers */
        [data-testid="metric-container"] {
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 0.75rem;
            border: 1px solid #e5e7eb;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        [data-testid="metric-container"] [data-testid="metric-label"] {
            color: #6b7280 !important;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        [data-testid="metric-container"] [data-testid="metric-value"] {
            color: #1f2937 !important;
            font-size: 2rem;
            font-weight: 700;
        }
        
        /* Input fields */
        .stTextInput > div > div > input {
            background-color: #ffffff;
            border: 2px solid #e5e7eb;
            color: #1f2937 !important;
            border-radius: 0.5rem;
            padding: 0.75rem;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #3b82f6;
            outline: none;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        /* Select boxes */
        .stSelectbox > div > div > select {
            background-color: #ffffff;
            border: 2px solid #e5e7eb;
            color: #1f2937 !important;
            border-radius: 0.5rem;
        }
        
        /* Radio buttons */
        .stRadio > div {
            background-color: #ffffff;
            padding: 0.5rem;
            border-radius: 0.5rem;
        }
        
        .stRadio > div label {
            color: #374151 !important;
            font-weight: 500;
        }
        
        /* Custom card styling */
        .custom-card {
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        /* Hero gradient with white text */
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
        
        /* Feature cards with gradients */
        .feature-card-1 {
            background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
            color: white !important;
            padding: 2rem;
            border-radius: 0.75rem;
        }
        
        .feature-card-2 {
            background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
            color: white !important;
            padding: 2rem;
            border-radius: 0.75rem;
        }
        
        .feature-card-3 {
            background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
            color: white !important;
            padding: 2rem;
            border-radius: 0.75rem;
        }
        
        .feature-card-1 h3, .feature-card-2 h3, .feature-card-3 h3,
        .feature-card-1 p, .feature-card-2 p, .feature-card-3 p {
            color: white !important;
        }
        
        /* Info cards */
        .info-card {
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            padding: 1.5rem;
            border-radius: 0.75rem;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .info-card h2 {
            color: #3b82f6 !important;
            margin: 0;
        }
        
        .info-card p {
            color: #6b7280 !important;
            margin: 0.5rem 0 0 0;
        }
        
        /* Recent contribution cards */
        .contribution-card {
            background-color: #f3f4f6;
            padding: 1rem;
            border-radius: 0.5rem;
            text-align: center;
            border: 1px solid #e5e7eb;
        }
        
        .contribution-card h2 {
            color: #1f2937 !important;
            font-size: 2rem;
            margin: 0.5rem 0;
        }
        
        .contribution-card h5 {
            color: #374151 !important;
            margin: 0.5rem 0;
        }
        
        .contribution-card p {
            color: #6b7280 !important;
            font-size: 0.875rem;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 0.5rem;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab"] {
            background-color: #f3f4f6;
            color: #374151 !important;
            border-radius: 0.5rem;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #3b82f6;
            color: white !important;
        }
        
        /* File uploader */
        .stFileUploader > div > div > div {
            background-color: #f9fafb;
            border: 2px dashed #9ca3af;
            border-radius: 0.5rem;
        }
        
        /* Progress bar */
        .stProgress > div > div > div > div {
            background-color: #3b82f6;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f3f4f6;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #9ca3af;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #6b7280;
        }
        
        /* Mobile responsive */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 1rem;
            }
            
            .hero-gradient {
                padding: 2rem;
            }
        }
    </style>
    """
    st.markdown(clean_css, unsafe_allow_html=True)
