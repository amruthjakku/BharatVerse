import streamlit as st


def load_custom_css():
    """Load custom CSS styles for the Streamlit app"""
    st.markdown(
        """
        <style>

        /* Global font and color styles */
        body {
            font-family: 'Helvetica Neue', sans-serif;
            color: #3c3c3c;
        }

        /* Custom button styles */
        .stButton>button {
            border-radius: 6px;
            background-color: #ff4b4b;
            color: white;
            font-weight: bold;
            margin: 0.5em 0;
            padding: 0.75em 1em;
            transition: background-color 0.3s ease;
        }

        .stButton>button:hover {
            background-color: #d43f3f;
        }

        /* Sidebar styles */
        .css-18e3th9 {
            background-color: #f8f9fa;
        }

        /* Table styles */
        .css-1dp5vir tbody th, .css-1dp5vir tbody td {
            padding: 0.4em;
        }

        /* Card styles in columns */
        .card {
            background-color: #fff;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 1.5em;
            margin: 0.75em 0;
            transition: box-shadow 0.3s ease;
        }

        .card:hover {
            box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        }

        </style>
        """,
        unsafe_allow_html=True
    )
