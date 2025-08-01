"""
Real-time Audio Recording Component for BharatVerse
Provides live audio recording functionality with visualization
"""

import streamlit as st
import numpy as np
import threading
import time
import queue
import tempfile
import os
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Try to import audio libraries with proper error handling
try:
    import sounddevice as sd
    import soundfile as sf
    AUDIO_RECORDING_AVAILABLE = True
except (ImportError, OSError) as e:
    AUDIO_RECORDING_AVAILABLE = False
    # Create dummy modules for compatibility
    class DummySD:
        @staticmethod
        def InputStream(*args, **kwargs):
            raise RuntimeError("Audio recording not available in this environment")
        @staticmethod
        def query_devices():
            return []
    
    class DummySF:
        @staticmethod
        def write(*args, **kwargs):
            raise RuntimeError("Audio file writing not available")
    
    sd = DummySD()
    sf = DummySF()

# Detect if running in cloud environment
def is_cloud_environment():
    """Detect if running in a cloud environment where audio recording is not supported"""
    import os
    # Check for common cloud environment indicators
    cloud_indicators = [
        '/mount/src/',  # Streamlit Cloud
        '/app/',        # Heroku
        '/workspace/',  # GitHub Codespaces
        'STREAMLIT_CLOUD' in os.environ,
        'HEROKU' in os.environ,
        'CODESPACE_NAME' in os.environ
    ]
    
    current_path = os.getcwd()
    return any(indicator in current_path if isinstance(indicator, str) else indicator for indicator in cloud_indicators)

class AudioRecorder:
    def __init__(self, sample_rate=44100, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = False
        self.audio_data = []
        self.audio_queue = queue.Queue()
        self.recording_thread = None
        self.cloud_env = is_cloud_environment()
        
    def start_recording(self):
        """Start audio recording"""
        # Check if recording is available
        if self.cloud_env or not AUDIO_RECORDING_AVAILABLE:
            raise RuntimeError("Live audio recording is not available in this environment. Please use file upload instead.")
            
        if self.recording:
            return False
            
        self.recording = True
        self.audio_data = []
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio callback status: {status}")
            if self.recording:
                self.audio_queue.put(indata.copy())
        
        try:
            # Start recording stream
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=audio_callback,
                dtype=np.float32
            )
            
            self.stream.start()
            
            # Start data collection thread
            self.recording_thread = threading.Thread(target=self._collect_audio_data)
            self.recording_thread.start()
            
            return True
        except Exception as e:
            self.recording = False
            raise RuntimeError(f"Failed to start audio recording: {str(e)}")
    
    def stop_recording(self):
        """Stop audio recording"""
        if not self.recording:
            return None
            
        self.recording = False
        
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        
        if self.recording_thread:
            self.recording_thread.join()
        
        # Combine all audio data
        if self.audio_data:
            combined_audio = np.concatenate(self.audio_data, axis=0)
            return combined_audio.flatten()
        
        return None
    
    def _collect_audio_data(self):
        """Collect audio data from queue"""
        while self.recording:
            try:
                data = self.audio_queue.get(timeout=0.1)
                self.audio_data.append(data)
            except queue.Empty:
                continue
    
    def get_audio_level(self):
        """Get current audio level for visualization"""
        if not self.audio_data:
            return 0
        
        # Get the last chunk of audio data
        if len(self.audio_data) > 0:
            last_chunk = self.audio_data[-1]
            return np.sqrt(np.mean(last_chunk**2))
        
        return 0

def create_audio_visualizer(audio_data, sample_rate):
    """Create audio waveform visualization"""
    if audio_data is None or len(audio_data) == 0:
        return None
    
    # Create time axis
    duration = len(audio_data) / sample_rate
    time_axis = np.linspace(0, duration, len(audio_data))
    
    # Create waveform plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=time_axis,
        y=audio_data,
        mode='lines',
        name='Waveform',
        line=dict(color='#1f77b4', width=1)
    ))
    
    fig.update_layout(
        title="Audio Waveform",
        xaxis_title="Time (seconds)",
        yaxis_title="Amplitude",
        height=300,
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig

def create_audio_spectrum(audio_data, sample_rate):
    """Create audio frequency spectrum"""
    if audio_data is None or len(audio_data) == 0:
        return None
    
    # Compute FFT
    fft = np.fft.fft(audio_data)
    freqs = np.fft.fftfreq(len(fft), 1/sample_rate)
    
    # Take only positive frequencies
    positive_freqs = freqs[:len(freqs)//2]
    magnitude = np.abs(fft[:len(fft)//2])
    
    # Create spectrum plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=positive_freqs,
        y=magnitude,
        mode='lines',
        name='Spectrum',
        line=dict(color='#ff7f0e', width=1)
    ))
    
    fig.update_layout(
        title="Frequency Spectrum",
        xaxis_title="Frequency (Hz)",
        yaxis_title="Magnitude",
        height=300,
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig

def audio_recorder_component():
    """Main audio recorder component"""
    # Check if we're in a cloud environment
    cloud_env = is_cloud_environment()
    recording_available = AUDIO_RECORDING_AVAILABLE and not cloud_env
    
    if not recording_available:
        st.markdown("### 📁 Audio File Upload")
        st.info("🌐 Live audio recording is not available in cloud environments. Please upload an audio file instead.")
        
        uploaded_file = st.file_uploader(
            "Upload Audio File", 
            type=['wav', 'mp3', 'ogg', 'm4a', 'flac'],
            help="Upload your audio recording (folk songs, stories, oral traditions)"
        )
        
        if uploaded_file:
            st.session_state.uploaded_audio = uploaded_file
            st.audio(uploaded_file)
            st.success("✅ Audio file uploaded successfully!")
            
            # Try to extract basic info
            try:
                # For WAV files, we can get some basic info
                if uploaded_file.name.lower().endswith('.wav'):
                    file_size = len(uploaded_file.getvalue())
                    st.info(f"📊 File size: {file_size / 1024:.1f} KB")
            except:
                pass
        
        return None, None
    
    st.markdown("### 🎤 Live Audio Recording")
    
    # Initialize recorder in session state
    if 'audio_recorder' not in st.session_state:
        st.session_state.audio_recorder = AudioRecorder()
    
    recorder = st.session_state.audio_recorder
    
    # Recording controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        duration = st.slider("Max Duration (seconds)", 10, 300, 60)
    
    with col2:
        st.markdown("#### Recording Status")
        status_placeholder = st.empty()
        
        if recorder.recording:
            status_placeholder.warning("🔴 Recording...")
        else:
            status_placeholder.info("⚪ Ready to record")
    
    with col3:
        st.markdown("#### Audio Level")
        level_placeholder = st.empty()
    
    # Recording buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔴 Start Recording", disabled=recorder.recording):
            try:
                if recorder.start_recording():
                    st.session_state.recording_start_time = time.time()
                    st.rerun()
            except RuntimeError as e:
                st.error(f"❌ Recording failed: {str(e)}")
                st.info("💡 Try uploading an audio file instead using the file uploader below.")
    
    with col2:
        if st.button("⏹️ Stop Recording", disabled=not recorder.recording):
            try:
                audio_data = recorder.stop_recording()
                if audio_data is not None:
                    st.session_state.recorded_audio = audio_data
                    st.session_state.sample_rate = recorder.sample_rate
                    st.success("✅ Recording saved!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to stop recording: {str(e)}")
    
    with col3:
        if st.button("🗑️ Clear Recording"):
            if 'recorded_audio' in st.session_state:
                del st.session_state.recorded_audio
            if 'sample_rate' in st.session_state:
                del st.session_state.sample_rate
            st.rerun()
    
    # Live audio level visualization during recording
    if recorder.recording:
        # Auto-stop after duration
        if 'recording_start_time' in st.session_state:
            elapsed = time.time() - st.session_state.recording_start_time
            if elapsed >= duration:
                audio_data = recorder.stop_recording()
                if audio_data is not None:
                    st.session_state.recorded_audio = audio_data
                    st.session_state.sample_rate = recorder.sample_rate
                st.success("✅ Recording completed (max duration reached)")
                st.rerun()
            else:
                # Show progress
                progress = elapsed / duration
                st.progress(progress, text=f"Recording: {elapsed:.1f}s / {duration}s")
                
                # Show audio level
                level = recorder.get_audio_level()
                level_placeholder.metric("Level", f"{level:.3f}")
                
                # Auto-refresh every 0.1 seconds
                time.sleep(0.1)
                st.rerun()
    
    # Display recorded audio
    if 'recorded_audio' in st.session_state:
        st.markdown("---")
        st.markdown("### 🎵 Recorded Audio")
        
        audio_data = st.session_state.recorded_audio
        sample_rate = st.session_state.get('sample_rate', 44100)
        
        # Save to temporary file for playback
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            sf.write(tmp_file.name, audio_data, sample_rate)
            
            # Audio player
            st.audio(tmp_file.name)
            
            # Audio info
            duration = len(audio_data) / sample_rate
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Duration", f"{duration:.2f}s")
            with col2:
                st.metric("Sample Rate", f"{sample_rate} Hz")
            with col3:
                st.metric("Samples", len(audio_data))
        
        # Audio visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            waveform_fig = create_audio_visualizer(audio_data, sample_rate)
            if waveform_fig:
                st.plotly_chart(waveform_fig, use_container_width=True)
        
        with col2:
            spectrum_fig = create_audio_spectrum(audio_data, sample_rate)
            if spectrum_fig:
                st.plotly_chart(spectrum_fig, use_container_width=True)
        
        # Clean up temp file
        try:
            os.unlink(tmp_file.name)
        except:
            pass
    
    # Add file upload option as alternative
    if recording_available:
        st.markdown("---")
        st.markdown("### 📁 Alternative: Upload Audio File")
        st.info("💡 You can also upload a pre-recorded audio file instead of recording live.")
        
        uploaded_file = st.file_uploader(
            "Upload Audio File", 
            type=['wav', 'mp3', 'ogg', 'm4a', 'flac'],
            help="Upload your audio recording (folk songs, stories, oral traditions)",
            key="fallback_uploader"
        )
        
        if uploaded_file:
            st.session_state.uploaded_audio = uploaded_file
            st.audio(uploaded_file)
            st.success("✅ Audio file uploaded successfully!")
    
    return st.session_state.get('recorded_audio'), st.session_state.get('sample_rate', 44100)

def save_audio_file(audio_data, sample_rate, filename=None):
    """Save audio data to file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
    
    # Create recordings directory if it doesn't exist
    recordings_dir = Path("recordings")
    recordings_dir.mkdir(exist_ok=True)
    
    filepath = recordings_dir / filename
    sf.write(str(filepath), audio_data, sample_rate)
    
    return str(filepath)