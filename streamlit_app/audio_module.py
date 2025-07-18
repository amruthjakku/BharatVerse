import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import io
import wave
import tempfile
import os
import requests
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Try to import audio libraries with fallback
try:
    import sounddevice as sd
    import soundfile as sf
    AUDIO_AVAILABLE = True
except (ImportError, OSError) as e:
    AUDIO_AVAILABLE = False
    # Don't show warning here as it will show on every import

# Try to import enhanced AI models
try:
    from core.ai_models_enhanced import ai_manager
    AI_MODELS_AVAILABLE = True
except ImportError:
    AI_MODELS_AVAILABLE = False

# Database imports
try:
    from streamlit_app.utils.database import add_contribution
    from core.database import DatabaseManager, ContentRepository
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# User management imports
try:
    from streamlit_app.utils.auth import GitLabAuth
    from streamlit_app.utils.user_manager import user_manager
    USER_MANAGEMENT_AVAILABLE = True
except ImportError:
    USER_MANAGEMENT_AVAILABLE = False

# API endpoint
API_URL = os.getenv("API_URL", "http://localhost:8000")

def audio_page():
    st.markdown("## 🎙️ Audio Capture & Transcription")
    st.markdown("Record folk songs, stories, and oral traditions in your language.")
    
    # Check if audio libraries are available
    if not AUDIO_AVAILABLE:
        st.error("🚫 Audio recording is not available on this system.")
        st.info("""
        **To enable audio recording, you need to install:**
        - PortAudio library (system dependency)
        - Python audio packages: `pip install sounddevice soundfile`
        
        **For now, you can:**
        - Upload pre-recorded audio files
        - Use the text and image modules
        - Explore other features of BharatVerse
        """)
        
        # Show file upload as alternative
        st.markdown("---")
        st.markdown("### 📁 Upload Audio File")
        uploaded_file = st.file_uploader(
            "Choose an audio file", 
            type=['wav', 'mp3', 'ogg', 'm4a'],
            help="Upload a pre-recorded audio file for transcription"
        )
        
        if uploaded_file is not None:
            st.audio(uploaded_file, format='audio/wav')
            st.success("Audio file uploaded successfully!")
            
            # Show mock transcription interface
            if st.button("🔤 Transcribe Audio"):
                with st.spinner("Transcribing audio..."):
                    st.info("Transcription feature would process the uploaded audio here.")
        
        return
    
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
    
    if AUDIO_AVAILABLE:
        # Import and use the real audio recorder
        try:
            from streamlit_app.audio_recorder import audio_recorder_component
            recorded_audio, sample_rate = audio_recorder_component()
        except ImportError as e:
            st.error(f"Audio recorder component not available: {e}")
            # Fallback to file upload
            st.markdown("### 📁 Upload Audio File")
            uploaded_file = st.file_uploader("Upload Audio File", type=['wav', 'mp3', 'ogg', 'm4a'])
            if uploaded_file:
                st.session_state.uploaded_audio = uploaded_file
    else:
        st.warning("🚫 Live recording not available. Please upload an audio file instead.")
        st.markdown("### 📁 Upload Audio File")
        uploaded_file = st.file_uploader("Upload Audio File", type=['wav', 'mp3', 'ogg', 'm4a'])
        if uploaded_file:
            st.session_state.uploaded_audio = uploaded_file
            st.audio(uploaded_file)
    
    # Transcription section
    if st.session_state.get('recorded_audio') is not None or st.session_state.get('uploaded_audio') is not None:
        st.markdown("---")
        st.markdown("### 📝 Transcription")
        
        if st.button("🤖 Transcribe Audio", use_container_width=True):
            with st.spinner("Transcribing audio..."):
                if AI_MODELS_AVAILABLE:
                    try:
                        # Get audio data
                        audio_data = None
                        if st.session_state.get('recorded_audio') is not None:
                            audio_data = st.session_state.recorded_audio
                        elif st.session_state.get('uploaded_audio') is not None:
                            uploaded_file = st.session_state.get('uploaded_audio')
                            audio_data = uploaded_file.read()
                        
                        if audio_data is None:
                            st.error("No audio data found")
                            return
                        
                        # Determine language code
                        lang_code = None if language == "Auto-detect" else language.lower()[:2]
                        
                        # Use enhanced AI models for transcription
                        st.info("🤖 Using real AI models for transcription...")
                        result = ai_manager.process_audio(
                            audio_data, 
                            language=lang_code, 
                            translate=True
                        )
                        
                        if result.get('success'):
                            st.success("✅ Transcription complete!")
                            
                            # Show transcription
                            transcription = result.get('transcription', '')
                            detected_lang = result.get('language', 'unknown')
                            confidence = result.get('confidence', 0.0)
                            
                            st.text_area("Transcribed Text", transcription, height=150)
                            
                            # Show confidence and language info
                            col1, col2 = st.columns(2)
                            with col1:
                                st.caption(f"🌐 Detected language: {detected_lang}")
                            with col2:
                                st.caption(f"🎯 Confidence: {confidence:.2%}")
                            
                            # Show translation if available
                            translation_result = result.get('translation', {})
                            if translation_result and translation_result.get('success'):
                                translation = translation_result.get('translation', '')
                                st.text_area("English Translation", translation, height=100)
                                st.caption(f"🔄 Translation confidence: {translation_result.get('confidence', 0.0):.2%}")
                            
                            # Show text analysis if available
                            text_analysis = result.get('text_analysis', {})
                            if text_analysis and text_analysis.get('success'):
                                with st.expander("📊 Text Analysis"):
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Word Count", text_analysis.get('word_count', 0))
                                    with col2:
                                        sentiment = text_analysis.get('sentiment', {})
                                        st.metric("Sentiment", sentiment.get('label', 'Unknown'))
                                    with col3:
                                        readability = text_analysis.get('readability', {})
                                        st.metric("Readability", readability.get('difficulty', 'Unknown'))
                                    
                                    # Show cultural indicators
                                    cultural_indicators = text_analysis.get('cultural_indicators', [])
                                    if cultural_indicators:
                                        st.write("🏛️ **Cultural Elements Detected:**")
                                        st.write(", ".join(cultural_indicators))
                                    
                                    # Show keywords
                                    keywords = text_analysis.get('keywords', [])
                                    if keywords:
                                        st.write("🔑 **Keywords:**")
                                        st.write(", ".join(keywords[:10]))
                            
                            # Store results for submission
                            st.session_state.transcription_result = result
                        else:
                            st.error(f"Transcription failed: {result.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        st.error(f"Error during transcription: {str(e)}")
                        # Fallback to API call
                        st.info("Falling back to API transcription...")
                        try:
                            # Prepare audio file for API
                            if st.session_state.get('recorded_audio') is not None:
                                # Convert numpy array to audio file
                                audio_buffer = io.BytesIO()
                                sf.write(audio_buffer, st.session_state.recorded_audio, 
                                        st.session_state.sample_rate, format='WAV')
                                audio_buffer.seek(0)
                                files = {'file': ('recording.wav', audio_buffer, 'audio/wav')}
                            else:
                                # Use uploaded file
                                uploaded_file = st.session_state.get('uploaded_audio')
                                files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
                            
                            # Call API for transcription
                            response = requests.post(
                                f"{API_URL}/api/v1/audio/transcribe",
                                files=files,
                                data={
                                    'language': lang_code or '',
                                    'translate': 'true'
                                }
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                if result.get('success'):
                                    st.success("✅ API Transcription complete!")
                                    transcription = result.get('transcription', '')
                                    st.text_area("Transcribed Text", transcription, height=150)
                                    st.session_state.transcription_result = result
                                else:
                                    st.error(f"API Transcription failed: {result.get('error', 'Unknown error')}")
                            else:
                                st.error(f"API error: {response.status_code}")
                        except Exception as api_e:
                            st.error(f"API fallback also failed: {str(api_e)}")
                
                else:
                    st.warning("🚧 AI models not available. Install dependencies with: pip install -r requirements.txt")
                    st.info("Please provide manual transcription below or install AI models for automatic transcription.")
                
                # Metadata
                st.markdown("### 🏷️ Metadata & Tags")
                
                col1, col2 = st.columns(2)
                with col1:
                    title = st.text_input("Title", "", placeholder="Enter title...")
                    region = st.text_input("Region/State", "", placeholder="Enter region/state...")
                    performer = st.text_input("Performer Name (Optional)", "", placeholder="Enter performer name...")
                
                with col2:
                    occasion = st.text_input("Occasion/Context", "", placeholder="Enter occasion/context...")
                    year_recorded = st.number_input("Year Recorded", 1900, 2024, 2024)
                    tags = st.text_input("Tags (comma-separated)", "", placeholder="Enter tags...")
                
                # Additional notes
                notes = st.text_area("Additional Notes", "", 
                    placeholder="Any additional context, history, or significance of this recording...")
                
                # Consent checkbox
                consent = st.checkbox(
                    "I confirm that I have the right to share this content and agree to the "
                    "terms of use and CC-BY 4.0 license for the contributed data."
                )
                
                # Submit button
                if consent:
                    if st.button("📤 Submit Contribution", type="primary", use_container_width=True):
                        # Process and save the audio
                        try:
                            from streamlit_app.audio_processor import AudioProcessor
                            
                            processor = AudioProcessor()
                            
                            # Prepare audio data
                            audio_data = None
                            sample_rate = 44100
                            
                            if st.session_state.get('recorded_audio') is not None:
                                audio_data = st.session_state.recorded_audio
                                sample_rate = st.session_state.get('sample_rate', 44100)
                            elif st.session_state.get('uploaded_audio') is not None:
                                uploaded_file = st.session_state.uploaded_audio
                                audio_data = uploaded_file
                            
                            if audio_data is not None:
                                # Prepare metadata
                                metadata = {
                                    'title': title,
                                    'description': notes,
                                    'language': language,
                                    'category': category,
                                    'region': region,
                                    'performer': performer,
                                    'occasion': occasion,
                                    'year_recorded': year_recorded,
                                    'tags': [tag.strip() for tag in tags.split(',') if tag.strip()],
                                    'contributor': 'Anonymous'  # TODO: Add user system
                                }
                                
                                # Process audio file
                                with st.spinner("Processing audio file..."):
                                    result = processor.process_audio_file(audio_data, sample_rate, metadata)
                                
                                if result['success']:
                                    # Get transcription result if available
                                    transcription_result = st.session_state.get('transcription_result')
                                    
                                    # Save to database
                                    with st.spinner("Saving to database..."):
                                        db_result = processor.save_to_database(result['metadata'], transcription_result)
                                    
                                    if db_result['success']:
                                        st.success("🎉 Thank you for your contribution! Your audio has been added to BharatVerse.")
                                        st.balloons()
                                        
                                        # Show contribution summary
                                        st.markdown("### 📋 Contribution Summary")
                                        summary = {
                                            "type": "audio",
                                            "title": title,
                                            "language": language,
                                            "category": category,
                                            "region": region,
                                            "duration": f"{result['metadata']['duration']:.2f} seconds",
                                            "file_size": f"{result['metadata']['file_size'] / 1024:.1f} KB",
                                            "transcription_available": transcription_result is not None,
                                            "translation_available": transcription_result and transcription_result.get('translation', {}).get('success', False),
                                            "tags": metadata['tags'],
                                            "timestamp": datetime.now().isoformat(),
                                            "content_id": db_result.get('content_id', 'N/A')
                                        }
                                        st.json(summary)
                                        
                                        # Clear session state
                                        for key in ['recorded_audio', 'uploaded_audio', 'transcription_result', 'sample_rate']:
                                            if key in st.session_state:
                                                del st.session_state[key]
                                    else:
                                        st.error(f"Failed to save to database: {db_result['error']}")
                                else:
                                    st.error(f"Failed to process audio: {result['error']}")
                            else:
                                st.error("No audio data found. Please record or upload audio first.")
                                
                        except ImportError:
                            st.error("Audio processor not available. Please check installation.")
                        except Exception as e:
                            st.error(f"Error processing submission: {str(e)}")
    
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
