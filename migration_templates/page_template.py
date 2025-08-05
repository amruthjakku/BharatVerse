"""
Migrated Page Template
Replace old scattered logic with clean architecture
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.page_template import create_page, get_page_config
from core.service_manager import get_service_manager
from core.config_manager import get_config_manager
from core.error_handler import error_boundary, handle_errors

@create_page(
    title="Your Page Title",
    icon="🎯",
    description="Your page description",
    required_services=["service1", "service2"],  # Replace with actual services
    optional_services=["service3"]  # Replace with actual services
)
def your_page():
    """Clean page implementation"""
    
    service_manager = get_service_manager()
    config_manager = get_config_manager()
    
    # Your page logic here
    st.write("Page content")

if __name__ == "__main__":
    your_page()
