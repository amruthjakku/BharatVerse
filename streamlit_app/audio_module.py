import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import io
import wave
import tempfile
import os

# Try to import audio libraries with fallback
try:
    import sounddevice as sd
    import soundfile as sf
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    st.warning("Audio recording libraries not available. Install with: pip install sounddevice soundfile")

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

def audio_page():
    st.markdown("## 🎙️ Audio Capture & Transcription")
    st.markdown("Record folk songs, stories, and oral traditions in your language.")
    
    # Language selection
    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox(
            "Select Language",
            ["Auto-detect", "Hindi", "Bengali", "Tamil", "Telugu", "Marathi", "Gujarati", 
             "Kannada", "Malayalam", "Punjabi", "Odia", "Assamese", "Urdu"]
        )
    
    with col2:
        category = st.selectbox(
            "Content Category",
            ["Folk Song", "Story", "Poetry", "Prayer", "Chant", "Lullaby", "Other"]
        )
    
    # Recording section
    st.markdown("---")
    st.markdown("### 🎤 Record Audio")
    
    # Recording controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        duration = st.slider("Recording Duration (seconds)", 10, 300, 60)
    
    with col2:
        st.markdown("#### Recording Status")
        recording_placeholder = st.empty()
        recording_placeholder.info("Ready to record")
    
    with col3:
        st.markdown("#### Audio Preview")
        audio_placeholder = st.empty()
    
    # Recording buttons
    col1, col2, col3 = st.columns(3)
    
    if AUDIO_AVAILABLE:
        with col1:
            if st.button("🔴 Start Recording", use_container_width=True):
                recording_placeholder.warning("🔴 Recording in progress...")
                
                # Simulate recording (in real app, this would use sounddevice)
                fs = 44100  # Sample rate
                duration_samples = int(duration * fs)
                
                # Generate dummy audio data (sine wave)
                t = np.linspace(0, duration, duration_samples)
                frequency = 440  # A4 note
                audio_data = 0.3 * np.sin(2 * np.pi * frequency * t)
                
                # Add some noise to make it more realistic
                audio_data += 0.05 * np.random.randn(len(audio_data))
                
                # Store in session state
                st.session_state.recorded_audio = audio_data
                st.session_state.sample_rate = fs
                
                recording_placeholder.success("✅ Recording complete!")
                
                # Create audio file for preview
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                    sf.write(tmp_file.name, audio_data, fs)
                    audio_placeholder.audio(tmp_file.name)
    else:
        with col1:
            uploaded_file = st.file_uploader("Upload Audio File", type=['wav', 'mp3', 'ogg', 'm4a'])
            if uploaded_file:
                st.session_state.uploaded_audio = uploaded_file
                audio_placeholder.audio(uploaded_file)
    
    # Transcription section
    if st.session_state.get('recorded_audio') is not None or st.session_state.get('uploaded_audio') is not None:
        st.markdown("---")
        st.markdown("### 📝 Transcription")
        
        if st.button("🤖 Transcribe Audio", use_container_width=True):
            with st.spinner("Transcribing audio..."):
                # Simulate transcription
                st.success("✅ Transcription complete!")
                
                # Sample transcription
                transcription = """
                पानी रे पानी तेरा रंग कैसा
                जिसमें मिला दो लागे जैसा
                
                This is a traditional folk song about water and its ability to take the color 
                of whatever it is mixed with, often used as a metaphor for adaptability and unity.
                """
                
                st.text_area("Transcribed Text", transcription, height=150)
                
                # Translation option
                if st.checkbox("Translate to English"):
                    translation = """
                    Water, oh water, what is your color?
                    You become like whatever you're mixed with.
                    """
                    st.text_area("English Translation", translation, height=100)
                
                # Metadata
                st.markdown("### 🏷️ Metadata & Tags")
                
                col1, col2 = st.columns(2)
                with col1:
                    title = st.text_input("Title", "Traditional Water Song")
                    region = st.text_input("Region/State", "Rajasthan")
                    performer = st.text_input("Performer Name (Optional)", "")
                
                with col2:
                    occasion = st.text_input("Occasion/Context", "Harvest Festival")
                    year_recorded = st.number_input("Year Recorded", 1900, 2024, 2024)
                    tags = st.text_input("Tags (comma-separated)", "folk song, water, metaphor, traditional")
                
                # Additional notes
                notes = st.text_area("Additional Notes", 
                    "Any additional context, history, or significance of this recording...")
                
                # Consent checkbox
                consent = st.checkbox(
                    "I confirm that I have the right to share this content and agree to the "
                    "terms of use and CC-BY 4.0 license for the contributed data."
                )
                
                # Submit button
                if consent:
                    if st.button("📤 Submit Contribution", type="primary", use_container_width=True):
                        st.success("🎉 Thank you for your contribution! Your audio has been added to TeluguVerse.")
                        st.balloons()
                        
                        # Show contribution summary
                        st.markdown("### 📋 Contribution Summary")
                        st.json({
                            "type": "audio",
                            "title": title,
                            "language": language,
                            "category": category,
                            "region": region,
                            "duration": f"{duration} seconds",
                            "transcription_available": True,
                            "translation_available": True,
                            "tags": tags.split(", "),
                            "timestamp": datetime.now().isoformat()
                        })
    
    # Tips section
    with st.expander("💡 Recording Tips"):
        st.markdown("""
        - **Find a quiet space** with minimal background noise
        - **Speak clearly** and at a moderate pace
        - **Test your microphone** before recording
        - **Keep recordings under 5 minutes** for best results
        - **Include context** about when/where the song or story is traditionally performed
        """)
    
    # Examples section
    with st.expander("🎵 Example Recordings"):
        st.markdown("### Listen to these examples for inspiration:")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🎵 Baul Song (Bengali)**")
            st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
            
        with col2:
            st.markdown("**🎵 Lavani (Marathi)**")
            st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3")
