import streamlit as st


def load_enhanced_css():
    """Load enhanced CSS styles for the Streamlit app"""
    st.markdown(
        """
        <style>
        
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* Global font and color styles */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: #1a1a1a;
        }

        /* Main container styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
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
        """,
        unsafe_allow_html=True
    )