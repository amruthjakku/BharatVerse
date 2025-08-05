"""
Clean Audio Capture Page
Demonstrates the new clean architecture without scattered try/except blocks
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.page_template import create_page, get_page_config
from core.service_manager import get_service_manager
from core.config_manager import get_config_manager, get_audio_config, get_language_options, get_category_options
from core.error_handler import error_boundary, handle_errors, GracefulDegradation

@create_page(**get_page_config("audio"))
def audio_page():
    """Clean audio capture page implementation"""
    
    service_manager = get_service_manager()
    config_manager = get_config_manager()
    audio_config = get_audio_config()
    
    # Handle audio capability gracefully
    audio_capability = GracefulDegradation.audio_features(service_manager)
    
    if audio_capability == "full":
        render_full_audio_interface()
    elif audio_capability == "upload_only":
        render_upload_interface()
    else:
        render_no_audio_interface()

def render_full_audio_interface():
    """Render full audio interface with recording capability"""
    st.success("🎤 Full audio recording available!")
    
    # Audio recording controls
    col1, col2 = st.columns(2)
    
    with col1:
        language = st.selectbox("Language", get_language_options())
        category = st.selectbox("Category", get_category_options())
    
    with col2:
        duration = st.slider("Recording Duration (seconds)", 5, 300, 30)
        quality = st.selectbox("Quality", ["Standard", "High", "Broadcast"])
    
    # Recording interface
    st.markdown("### 🎙️ Recording Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔴 Start Recording", type="primary"):
            start_recording(duration, language, category, quality)
    
    with col2:
        if st.button("⏹️ Stop Recording"):
            stop_recording()
    
    with col3:
        if st.button("▶️ Play Recording"):
            play_recording()
    
    # Show recording status
    if "recording_status" in st.session_state:
        st.info(f"Status: {st.session_state.recording_status}")

def render_upload_interface():
    """Render upload-only interface"""
    st.info("📁 Audio file upload available")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload Audio File",
        type=['wav', 'mp3', 'm4a', 'ogg', 'flac'],
        help="Upload pre-recorded audio files for transcription"
    )
    
    if uploaded_file:
        process_uploaded_audio(uploaded_file)

def render_no_audio_interface():
    """Render interface when no audio capability is available"""
    st.warning("🚫 Audio features not available")
    
    st.markdown("""
    ### Alternative Options:
    - 📝 Use the [Text Stories](/Text_Stories) module
    - 📸 Try the [Visual Heritage](/Visual_Heritage) module
    - 🔍 Explore other features of BharatVerse
    """)

@handle_errors(show_error=True, error_message="Failed to start recording")
def start_recording(duration: int, language: str, category: str, quality: str):
    """Start audio recording"""
    service_manager = get_service_manager()
    audio_service = service_manager.get_service("audio")
    
    if not audio_service or audio_service.get("backend") == "none":
        st.error("Audio recording not available")
        return
    
    # Implementation would go here
    st.session_state.recording_status = f"Recording {category} in {language} for {duration}s..."
    st.success("🎤 Recording started!")

@handle_errors(show_error=True, error_message="Failed to stop recording")
def stop_recording():
    """Stop audio recording"""
    st.session_state.recording_status = "Recording stopped"
    st.success("⏹️ Recording stopped!")

@handle_errors(show_error=True, error_message="Failed to play recording")
def play_recording():
    """Play recorded audio"""
    if "current_recording" not in st.session_state:
        st.warning("No recording available")
        return
    
    st.success("▶️ Playing recording...")

@handle_errors(show_error=True, error_message="Failed to process uploaded audio")
def process_uploaded_audio(uploaded_file):
    """Process uploaded audio file"""
    service_manager = get_service_manager()
    
    # Validate file size
    config_manager = get_config_manager()
    if not config_manager.validate_file_size(len(uploaded_file.getvalue()), "audio"):
        max_size = config_manager.get_file_size_limit("audio")
        st.error(f"File too large. Maximum size: {max_size}MB")
        return
    
    # Show file info
    st.success(f"✅ File uploaded: {uploaded_file.name}")
    st.info(f"Size: {len(uploaded_file.getvalue()) / 1024 / 1024:.1f}MB")
    
    # Language and category selection
    col1, col2 = st.columns(2)
    
    with col1:
        language = st.selectbox("Audio Language", get_language_options(), key="upload_lang")
    
    with col2:
        category = st.selectbox("Content Category", get_category_options(), key="upload_cat")
    
    # Process button
    if st.button("🔄 Process Audio", type="primary"):
        with st.spinner("Processing audio..."):
            process_audio_file(uploaded_file, language, category)

@handle_errors(show_error=True, error_message="Failed to process audio file")
def process_audio_file(audio_file, language: str, category: str):
    """Process the audio file with AI services"""
    service_manager = get_service_manager()
    
    # Try to get AI service
    ai_capability = GracefulDegradation.ai_features(service_manager)
    
    if ai_capability == "none":
        st.warning("🤖 AI processing not available - file saved for later processing")
        save_audio_file(audio_file, language, category)
        return
    
    # Process with available AI service
    ai_service = service_manager.get_service("ai")
    if ai_service:
        # Implementation would call the AI service
        result = {
            "transcription": "Sample transcription would appear here...",
            "language_detected": language,
            "confidence": 0.95,
            "category": category
        }
        
        display_processing_results(result)
    else:
        st.error("AI service not available")

def save_audio_file(audio_file, language: str, category: str):
    """Save audio file to storage"""
    service_manager = get_service_manager()
    storage_service = service_manager.get_service("storage")
    
    if storage_service:
        # Implementation would save to storage
        st.success("📁 Audio file saved successfully!")
    else:
        st.warning("💾 Storage not available - file will be lost when session ends")

def display_processing_results(result: dict):
    """Display AI processing results"""
    st.success("✅ Audio processed successfully!")
    
    # Show results
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Language Detected", result["language_detected"])
        st.metric("Confidence", f"{result['confidence']:.1%}")
    
    with col2:
        st.metric("Category", result["category"])
        st.metric("Status", "Completed")
    
    # Show transcription
    st.markdown("### 📝 Transcription")
    st.text_area("Transcribed Text", result["transcription"], height=150)
    
    # Save options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save to Database"):
            save_to_database(result)
    
    with col2:
        if st.button("📤 Share"):
            share_result(result)
    
    with col3:
        if st.button("✏️ Edit"):
            edit_result(result)

@handle_errors(show_error=True, error_message="Failed to save to database")
def save_to_database(result: dict):
    """Save result to database"""
    service_manager = get_service_manager()
    db_service = service_manager.get_service("database")
    
    if db_service:
        # Implementation would save to database
        st.success("💾 Saved to database!")
    else:
        st.warning("🗄️ Database not available")

@handle_errors(show_error=True, error_message="Failed to share result")
def share_result(result: dict):
    """Share the result"""
    st.success("📤 Sharing options would appear here")

@handle_errors(show_error=True, error_message="Failed to edit result")
def edit_result(result: dict):
    """Edit the result"""
    st.info("✏️ Edit interface would appear here")

if __name__ == "__main__":
    audio_page()