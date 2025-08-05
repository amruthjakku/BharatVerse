"""
Audio Processing and Storage Module for BharatVerse
Handles audio file processing, metadata extraction, and storage
"""

import os
import io
import tempfile
import hashlib
from datetime import datetime
from pathlib import Path
import numpy as np
import soundfile as sf
import librosa
import requests
import json

class AudioProcessor:
    def __init__(self, storage_path="audio_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
    def process_audio_file(self, audio_data, sample_rate, metadata=None):
        """Process audio file and extract features"""
        try:
            # Ensure audio is in the right format
            if isinstance(audio_data, np.ndarray):
                # Already numpy array
                audio_array = audio_data
            else:
                # Load from file-like object
                audio_array, sample_rate = sf.read(audio_data)
            
            # Extract audio features
            features = self._extract_audio_features(audio_array, sample_rate)
            
            # Generate unique filename
            audio_hash = self._generate_audio_hash(audio_array)
            filename = f"audio_{audio_hash}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            
            # Save audio file
            filepath = self.storage_path / filename
            sf.write(str(filepath), audio_array, sample_rate)
            
            # Create metadata
            audio_metadata = {
                'filename': filename,
                'filepath': str(filepath),
                'duration': len(audio_array) / sample_rate,
                'sample_rate': sample_rate,
                'channels': 1 if len(audio_array.shape) == 1 else audio_array.shape[1],
                'file_size': os.path.getsize(filepath),
                'created_at': datetime.now().isoformat(),
                'features': features,
                'hash': audio_hash
            }
            
            # Add user metadata
            if metadata:
                audio_metadata.update(metadata)
            
            return {
                'success': True,
                'filepath': str(filepath),
                'metadata': audio_metadata
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_audio_features(self, audio_array, sample_rate):
        """Extract audio features using librosa"""
        try:
            features = {}
            
            # Basic features
            features['duration'] = len(audio_array) / sample_rate
            features['sample_rate'] = sample_rate
            features['rms_energy'] = float(np.sqrt(np.mean(audio_array**2)))
            features['zero_crossing_rate'] = float(np.mean(librosa.feature.zero_crossing_rate(audio_array)))
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_array, sr=sample_rate)[0]
            features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
            features['spectral_centroid_std'] = float(np.std(spectral_centroids))
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_array, sr=sample_rate)[0]
            features['spectral_rolloff_mean'] = float(np.mean(spectral_rolloff))
            
            # MFCC features (first 13 coefficients)
            mfccs = librosa.feature.mfcc(y=audio_array, sr=sample_rate, n_mfcc=13)
            for i in range(13):
                features[f'mfcc_{i}_mean'] = float(np.mean(mfccs[i]))
                features[f'mfcc_{i}_std'] = float(np.std(mfccs[i]))
            
            # Tempo estimation
            tempo, _ = librosa.beat.beat_track(y=audio_array, sr=sample_rate)
            features['tempo'] = float(tempo)
            
            # Pitch features
            pitches, magnitudes = librosa.piptrack(y=audio_array, sr=sample_rate)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if pitch_values:
                features['pitch_mean'] = float(np.mean(pitch_values))
                features['pitch_std'] = float(np.std(pitch_values))
                features['pitch_min'] = float(np.min(pitch_values))
                features['pitch_max'] = float(np.max(pitch_values))
            else:
                features['pitch_mean'] = 0.0
                features['pitch_std'] = 0.0
                features['pitch_min'] = 0.0
                features['pitch_max'] = 0.0
            
            return features
            
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_audio_hash(self, audio_array):
        """Generate hash for audio content"""
        audio_bytes = audio_array.tobytes()
        return hashlib.md5(audio_bytes).hexdigest()[:16]
    
    def save_to_database(self, audio_metadata, transcription_result=None):
        """Save audio metadata to database"""
        try:
            # Prepare data for database
            content_data = {
                'title': audio_metadata.get('title', 'Untitled Audio'),
                'description': audio_metadata.get('description', ''),
                'content_type': 'audio',
                'language': audio_metadata.get('language', 'unknown'),
                'region': audio_metadata.get('region', 'unknown'),
                'category': audio_metadata.get('category', 'other'),
                'file_path': audio_metadata['filepath'],
                'file_size': audio_metadata['file_size'],
                'duration': audio_metadata['duration'],
                'metadata': {
                    'audio_features': audio_metadata.get('features', {}),
                    'sample_rate': audio_metadata['sample_rate'],
                    'channels': audio_metadata['channels'],
                    'hash': audio_metadata['hash']
                }
            }
            
            # Add transcription if available
            if transcription_result:
                content_data['transcription'] = transcription_result.get('transcription', '')
                content_data['metadata']['transcription_confidence'] = transcription_result.get('confidence', 0.0)
                content_data['metadata']['detected_language'] = transcription_result.get('language', 'unknown')
                
                # Add translation if available
                translation = transcription_result.get('translation', {})
                if translation and translation.get('success'):
                    content_data['translation'] = translation.get('translation', '')
                    content_data['metadata']['translation_confidence'] = translation.get('confidence', 0.0)
            
            # Try to save via API
            api_url = os.getenv("API_URL", "http://localhost:8000")
            response = requests.post(
                f"{api_url}/api/v1/content/create",
                json=content_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'content_id': result.get('id'),
                    'message': 'Audio saved to database successfully'
                }
            else:
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_audio_info(self, filepath):
        """Get information about an audio file"""
        try:
            info = sf.info(filepath)
            return {
                'duration': info.duration,
                'sample_rate': info.samplerate,
                'channels': info.channels,
                'format': info.format,
                'subtype': info.subtype
            }
        except Exception as e:
            return {'error': str(e)}
    
    def convert_audio_format(self, input_path, output_path, target_sr=44100):
        """Convert audio to standard format"""
        try:
            audio_data, sr = librosa.load(input_path, sr=target_sr)
            sf.write(output_path, audio_data, target_sr)
            return True
        except Exception as e:
            print(f"Audio conversion error: {e}")
            return False

def create_audio_submission_form(audio_metadata, transcription_result=None):
    """Create form for submitting processed audio"""
    import streamlit as st
    
    st.markdown("### 📋 Audio Submission")
    
    with st.form("audio_submission_form"):
        # Basic information
        title = st.text_input("Title", value=audio_metadata.get('title', ''))
        description = st.text_area("Description", value=audio_metadata.get('description', ''))
        
        # Metadata
        col1, col2 = st.columns(2)
        
        with col1:
            language = st.selectbox(
                "Language",
                ["Hindi", "Bengali", "Tamil", "Telugu", "Marathi", "Gujarati", 
                 "Kannada", "Malayalam", "Punjabi", "Odia", "Assamese", "Urdu", "Other"],
                index=0
            )
            
            category = st.selectbox(
                "Category",
                ["Folk Song", "Story", "Poetry", "Prayer", "Chant", "Lullaby", "Other"],
                index=0
            )
        
        with col2:
            region = st.selectbox(
                "Region",
                ["North India", "South India", "East India", "West India", "Northeast India", "Central India"],
                index=0
            )
            
            tags = st.text_input("Tags (comma-separated)", placeholder="traditional, folk, cultural")
        
        # Show transcription if available
        if transcription_result:
            st.markdown("#### 📝 Transcription")
            transcription = st.text_area(
                "Transcribed Text", 
                value=transcription_result.get('transcription', ''),
                height=100
            )
            
            # Show translation if available
            translation = transcription_result.get('translation', {})
            if translation and translation.get('success'):
                st.text_area(
                    "English Translation",
                    value=translation.get('translation', ''),
                    height=80,
                    disabled=True
                )
        
        # Submit button
        submitted = st.form_submit_button("🚀 Submit Audio", use_container_width=True)
        
        if submitted:
            # Update metadata with form data
            updated_metadata = audio_metadata.copy()
            updated_metadata.update({
                'title': title,
                'description': description,
                'language': language,
                'region': region,
                'category': category,
                'tags': [tag.strip() for tag in tags.split(',') if tag.strip()]
            })
            
            # Process and save
            processor = AudioProcessor()
            result = processor.save_to_database(updated_metadata, transcription_result)
            
            if result['success']:
                st.success(f"✅ {result['message']}")
                st.balloons()
                
                # Clear session state
                for key in ['recorded_audio', 'uploaded_audio', 'transcription_result']:
                    if key in st.session_state:
                        del st.session_state[key]
                
                st.rerun()
            else:
                st.error(f"❌ Failed to save: {result['error']}")
    
    return submitted