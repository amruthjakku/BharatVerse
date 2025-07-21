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
import hashlib
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Performance optimization imports
from utils.performance_optimizer import (
    get_performance_optimizer, 
    cached_user_contributions,
    show_loading_placeholder,
    progressive_loading_container
)
from utils.memory_manager import get_memory_manager, MemoryTracker, show_memory_dashboard
from utils.redis_cache import get_cache_manager

# Initialize performance components
@st.cache_resource
def get_audio_performance_components():
    """Get cached performance components for audio module"""
    return {
        'optimizer': get_performance_optimizer(),
        'memory_manager': get_memory_manager(),
        'cache_manager': get_cache_manager()
    }

@st.cache_data(ttl=3600, show_spinner=False)
def get_audio_processing_config():
    """Get cached audio processing configuration"""
    return {
        'supported_formats': ['.wav', '.mp3', '.m4a', '.ogg', '.flac'],
        'max_file_size_mb': 50,
        'sample_rate': 16000,
        'channels': 1,
        'chunk_size': 1024,
        'processing_timeout': 300
    }

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
    from core.ai_models import ai_manager
    AI_MODELS_AVAILABLE = True
except ImportError:
    AI_MODELS_AVAILABLE = False

# Cloud AI imports
try:
    from core.cloud_ai_manager import get_cloud_ai_manager
    CLOUD_AI_AVAILABLE = True
except ImportError:
    CLOUD_AI_AVAILABLE = False

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

# Storage imports
try:
    from utils.minio_storage import get_storage_manager
    STORAGE_AVAILABLE = True
except ImportError:
    STORAGE_AVAILABLE = False

# API endpoint
API_URL = os.getenv("API_URL", "http://localhost:8000")

@st.cache_data(ttl=300, show_spinner=False)
def get_audio_formats():
    """Get supported audio formats (cached)"""
    return ['wav', 'mp3', 'ogg', 'm4a', 'flac']

@st.cache_data(ttl=3600, show_spinner=False)
def get_language_options():
    """Get language options (cached)"""
    return [
        "Auto-detect", "Hindi", "Bengali", "Tamil", "Telugu", "Marathi", "Gujarati", 
        "Kannada", "Malayalam", "Punjabi", "Odia", "Assamese", "Urdu", "Sanskrit"
    ]

@st.cache_data(ttl=3600, show_spinner=False)
def get_category_options():
    """Get category options (cached)"""
    return [
        "Folk Song", "Story", "Poetry", "Prayer", "Chant", "Lullaby", 
        "Historical Account", "Interview", "Other"
    ]

def generate_audio_hash(audio_data: bytes) -> str:
    """Generate hash for audio data for caching"""
    return hashlib.md5(audio_data).hexdigest()

@st.cache_data(ttl=1800, show_spinner=False)
def cached_transcription_result(audio_hash: str, language: str):
    """Cache transcription results using Streamlit caching"""
    # This will be populated by the actual transcription process
    return None

def warm_up_ai_services():
    """Warm up AI services to avoid cold starts"""
    if "ai_services_warmed" not in st.session_state:
        with st.spinner("🔥 Warming up AI services..."):
            warmup_results = {}
            
            # Warm up cloud AI manager
            if CLOUD_AI_AVAILABLE:
                try:
                    ai_manager = get_cloud_ai_manager()
                    # Test with small dummy data
                    test_result = ai_manager.process_text("test", user_id=None)
                    warmup_results["cloud_ai"] = test_result.get("status") == "success"
                except Exception as e:
                    warmup_results["cloud_ai"] = False
            
            st.session_state.ai_services_warmed = warmup_results
            
            if any(warmup_results.values()):
                st.success("✅ AI services ready!")
            else:
                st.warning("⚠️ Some AI services may have cold start delays")

def process_audio_with_caching(audio_data: bytes, language: str, user_id: int = None):
    """Process audio with intelligent caching"""
    optimizer = get_performance_optimizer()
    
    # Generate cache key
    audio_hash = generate_audio_hash(audio_data)
    cache_key = f"audio_transcription:{audio_hash}:{language}"
    
    # Check if already processing
    processing_key = f"processing_{cache_key}"
    if processing_key in st.session_state:
        st.info("🔄 Audio is currently being processed...")
        return None
    
    # Try to get from cache first
    cached_result = cached_transcription_result(audio_hash, language)
    if cached_result:
        st.success("⚡ Retrieved from cache!")
        return cached_result
    
    # Mark as processing
    st.session_state[processing_key] = True
    
    try:
        # Use cloud AI manager for processing
        if CLOUD_AI_AVAILABLE:
            ai_manager = get_cloud_ai_manager()
            result = ai_manager.process_audio(audio_data, language, user_id)
            
            # Cache the result if successful
            if result.get("status") == "success":
                # Store in session state for immediate access
                st.session_state[f"transcription_{audio_hash}"] = result
            
            return result
        else:
            return {
                "status": "error",
                "error": "AI services not available",
                "text": "",
                "language": "unknown"
            }
    
    finally:
        # Remove processing flag
        if processing_key in st.session_state:
            del st.session_state[processing_key]

def audio_page():
    st.markdown("## 🎙️ Audio Capture & Transcription")
    st.markdown("Record folk songs, stories, and oral traditions in your language.")
    
    # Initialize performance components
    perf_components = get_audio_performance_components()
    optimizer = perf_components['optimizer']
    memory_manager = perf_components['memory_manager']
    cache_manager = perf_components['cache_manager']
    
    # Get audio configuration
    audio_config = get_audio_processing_config()
    
    # Performance monitoring for admins
    if st.session_state.get("user_role") == "admin":
        with st.expander("⚡ Performance Monitoring", expanded=False):
            show_memory_dashboard()
    
    # Memory tracking for audio operations
    with MemoryTracker("audio_page_load"):
        # Warm up services on first load
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🔥 Warm Up AI Services", help="Pre-load AI services to reduce processing time"):
                with st.spinner("Warming up services..."):
                    warm_up_ai_services()
        
        with col2:
            # Show current memory usage
            memory_usage = memory_manager.get_memory_usage()
            st.metric("Memory", f"{memory_usage['rss_mb']:.0f}MB")
    
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
            
            # Real transcription interface
            if st.button("🔤 Transcribe Audio"):
                with st.spinner("Transcribing audio with advanced AI..."):
                    try:
                        # Use enhanced AI models for real transcription
                        from core.enhanced_ai_models import ai_manager
                        
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name
                        
                        # Transcribe with advanced features
                        result = ai_manager.transcribe_audio(tmp_path, language)
                        
                        if result.get("success"):
                            st.success("✅ Transcription completed!")
                            
                            # Display results
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Detected Language", result.get("language", "Unknown"))
                                st.metric("Duration", f"{result.get('duration', 0):.1f}s")
                            with col2:
                                st.metric("Confidence", f"{result.get('confidence', 0):.2f}")
                                st.metric("Word Count", result.get("word_count", 0))
                            
                            # Show transcription
                            st.subheader("📝 Transcription")
                            st.text_area("Transcribed Text", result.get("transcription", ""), height=150)
                            
                            # Show segments if available
                            if result.get("segments"):
                                st.subheader("🎯 Detailed Segments")
                                for i, segment in enumerate(result["segments"][:5]):  # Show first 5 segments
                                    with st.expander(f"Segment {i+1} ({segment.get('start', 0):.1f}s - {segment.get('end', 0):.1f}s)"):
                                        st.write(segment.get("text", ""))
                                        st.caption(f"Confidence: {segment.get('confidence', 0):.2f}")
                            
                            # Store transcription for saving
                            st.session_state.transcription_result = result
                        else:
                            st.error(f"❌ Transcription failed: {result.get('error', 'Unknown error')}")
                        
                        # Clean up
                        os.unlink(tmp_path)
                        
                    except Exception as e:
                        st.error(f"❌ Transcription error: {str(e)}")
                        st.info("💡 Make sure you have the enhanced AI models installed. Run: pip install -r requirements/enhanced_ai.txt")
        
        return
    
    # Language selection with cached options
    col1, col2 = st.columns(2)
    with col1:
        language_options = get_language_options()
        language = st.selectbox(
            "Select Language",
            language_options,
            help="Choose the primary language of your audio content"
        )
    
    with col2:
        category_options = get_category_options()
        category = st.selectbox(
            "Content Category",
            category_options,
            help="Select the type of cultural content you're recording"
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
                        
                        # Check if ai_manager is actually available
                        if 'ai_manager' in globals():
                            result = ai_manager.process_audio(
                                audio_data, 
                                language=lang_code, 
                                translate=True
                            )
                        else:
                            raise NameError("ai_manager not available")
                        
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
                        # Fallback to basic transcription placeholder
                        st.info("Falling back to basic transcription...")
                        try:
                            # Try API call first
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
                                },
                                timeout=10
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
                            # Provide manual transcription option
                            st.info("💡 **Manual Transcription Available**")
                            st.markdown("Since automatic transcription is not available, you can manually transcribe the audio:")
                            manual_transcription = st.text_area(
                                "Manual Transcription", 
                                "", 
                                height=150,
                                placeholder="Please listen to the audio and type the transcription here..."
                            )
                            if manual_transcription.strip():
                                st.session_state.transcription_result = {
                                    'success': True,
                                    'transcription': manual_transcription,
                                    'language': language if language != "Auto-detect" else "unknown",
                                    'confidence': 1.0,
                                    'method': 'manual'
                                }
                                st.success("✅ Manual transcription saved!")
                
                else:
                    st.warning("🚧 AI models not available. Install dependencies with: pip install -r requirements.txt")
                    st.info("💡 **Manual Transcription Available**")
                    st.markdown("You can still contribute by manually transcribing the audio:")
                    manual_transcription = st.text_area(
                        "Manual Transcription", 
                        "", 
                        height=150,
                        placeholder="Please listen to the audio and type the transcription here..."
                    )
                    if manual_transcription.strip():
                        st.session_state.transcription_result = {
                            'success': True,
                            'transcription': manual_transcription,
                            'language': language if language != "Auto-detect" else "unknown",
                            'confidence': 1.0,
                            'method': 'manual'
                        }
                        st.success("✅ Manual transcription saved!")
                
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
