"""
AI Inference Manager for BharatVerse Cloud Deployment  
Executes HuggingFace API calls for text, image, and audio processing

Module: inference_manager.py
Purpose: Direct API interface to HuggingFace Inference API
- Makes actual HTTP requests to AI model endpoints
- Handles API rate limiting and error responses  
- Processes model outputs into standardized formats
- Used by cloud_ai_manager.py for orchestration
"""
import streamlit as st
import requests
import aiohttp
import asyncio
import json
import io
import base64
from typing import Dict, Any, Optional, List
import logging
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

class InferenceAPIManager:
    """Manages AI model inference via external APIs"""
    
    def __init__(self):
        """Initialize inference API manager using Streamlit secrets"""
        try:
            inference_config = st.secrets.get("inference", {})
            
            # API endpoints
            self.whisper_api = inference_config.get("whisper_api", "")
            self.text_analysis_api = inference_config.get("text_analysis_api", "")
            self.image_analysis_api = inference_config.get("image_analysis_api", "")
            self.translation_api = inference_config.get("translation_api", "")
            
            # API keys
            self.hf_token = inference_config.get("huggingface_token", "")
            self.runpod_token = inference_config.get("runpod_token", "")
            
            # Request timeout
            self.timeout = 30
            
            logger.info("Inference API Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize inference API manager: {e}")
    
    def _make_request(self, url: str, data: Dict, headers: Dict = None) -> Optional[Dict]:
        """Make HTTP request to inference API"""
        try:
            default_headers = {"Content-Type": "application/json"}
            if headers:
                default_headers.update(headers)
            
            response = requests.post(
                url,
                json=data,
                headers=default_headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in API request: {e}")
            return None
    
    async def _make_async_request(self, url: str, data: Dict, headers: Dict = None) -> Optional[Dict]:
        """Make async HTTP request to inference API"""
        try:
            default_headers = {"Content-Type": "application/json"}
            if headers:
                default_headers.update(headers)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=data,
                    headers=default_headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response.raise_for_status()
                    return await response.json()
                    
        except aiohttp.ClientError as e:
            logger.error(f"Async API request failed for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in async API request: {e}")
            return None
    
    def transcribe_audio(self, audio_data: bytes, language: str = None) -> Optional[Dict]:
        """
        Transcribe audio using Whisper API
        
        Args:
            audio_data: Audio file bytes
            language: Optional language hint
            
        Returns:
            Transcription result with text, timestamps, and confidence
        """
        if not self.whisper_api:
            logger.warning("Whisper API not configured")
            return self._fallback_whisper(audio_data)
        
        try:
            # Convert audio data to base64
            audio_b64 = base64.b64encode(audio_data).decode()
            
            request_data = {
                "inputs": {
                    "audio": audio_b64,
                    "language": language or "auto",
                    "return_timestamps": True,
                    "return_confidence": True
                }
            }
            
            headers = {}
            if self.hf_token:
                headers["Authorization"] = f"Bearer {self.hf_token}"
            
            result = self._make_request(self.whisper_api, request_data, headers)
            
            if result:
                return {
                    "text": result.get("text", ""),
                    "language": result.get("language", "unknown"),
                    "confidence": result.get("confidence", 0.0),
                    "timestamps": result.get("timestamps", []),
                    "status": "success"
                }
            
            return self._fallback_whisper(audio_data)
            
        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            return self._fallback_whisper(audio_data)
    
    def analyze_text(self, text: str, language: str = None) -> Optional[Dict]:
        """
        Analyze text for sentiment, emotion, and cultural context
        
        Args:
            text: Text to analyze
            language: Text language (optional)
            
        Returns:
            Analysis result with sentiment, emotion, and cultural insights
        """
        if not self.text_analysis_api:
            logger.warning("Text analysis API not configured")
            return self._fallback_text_analysis(text)
        
        try:
            request_data = {
                "inputs": {
                    "text": text,
                    "language": language or "auto",
                    "analyze_sentiment": True,
                    "analyze_emotion": True,
                    "analyze_culture": True
                }
            }
            
            headers = {}
            if self.hf_token:
                headers["Authorization"] = f"Bearer {self.hf_token}"
            
            result = self._make_request(self.text_analysis_api, request_data, headers)
            
            if result:
                return {
                    "sentiment": result.get("sentiment", {"label": "neutral", "score": 0.5}),
                    "emotion": result.get("emotion", {"label": "neutral", "score": 0.5}),
                    "language": result.get("language", language or "unknown"),
                    "cultural_elements": result.get("cultural_elements", []),
                    "quality_score": result.get("quality_score", 0.5),
                    "status": "success"
                }
            
            return self._fallback_text_analysis(text)
            
        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            return self._fallback_text_analysis(text)
    
    def analyze_image(self, image_data: bytes) -> Optional[Dict]:
        """
        Analyze image for content and cultural context
        
        Args:
            image_data: Image file bytes
            
        Returns:
            Analysis result with captions, objects, and cultural insights
        """
        if not self.image_analysis_api:
            logger.warning("Image analysis API not configured")
            return self._fallback_image_analysis(image_data)
        
        try:
            # Convert image to base64
            image_b64 = base64.b64encode(image_data).decode()
            
            request_data = {
                "inputs": {
                    "image": image_b64,
                    "generate_caption": True,
                    "detect_objects": True,
                    "analyze_culture": True
                }
            }
            
            headers = {}
            if self.hf_token:
                headers["Authorization"] = f"Bearer {self.hf_token}"
            
            result = self._make_request(self.image_analysis_api, request_data, headers)
            
            if result:
                return {
                    "caption": result.get("caption", ""),
                    "objects": result.get("objects", []),
                    "cultural_elements": result.get("cultural_elements", []),
                    "quality_score": result.get("quality_score", 0.5),
                    "status": "success"
                }
            
            return self._fallback_image_analysis(image_data)
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return self._fallback_image_analysis(image_data)
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Optional[Dict]:
        """
        Translate text between languages
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translation result
        """
        if not self.translation_api:
            logger.warning("Translation API not configured")
            return self._fallback_translation(text, source_lang, target_lang)
        
        try:
            request_data = {
                "inputs": {
                    "text": text,
                    "source_lang": source_lang,
                    "target_lang": target_lang
                }
            }
            
            headers = {}
            if self.hf_token:
                headers["Authorization"] = f"Bearer {self.hf_token}"
            
            result = self._make_request(self.translation_api, request_data, headers)
            
            if result:
                return {
                    "translated_text": result.get("translation", text),
                    "source_language": source_lang,
                    "target_language": target_lang,
                    "confidence": result.get("confidence", 0.5),
                    "status": "success"
                }
            
            return self._fallback_translation(text, source_lang, target_lang)
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return self._fallback_translation(text, source_lang, target_lang)
    
    # Fallback methods for when APIs are not available
    def _fallback_whisper(self, audio_data: bytes) -> Dict:
        """Fallback audio transcription"""
        return {
            "text": "Audio transcription not available - configure Whisper API endpoint",
            "language": "unknown",
            "confidence": 0.0,
            "timestamps": [],
            "status": "fallback"
        }
    
    def _fallback_text_analysis(self, text: str) -> Dict:
        """Fallback text analysis using basic heuristics"""
        import langdetect
        from textstat import flesch_reading_ease
        
        try:
            # Detect language
            language = langdetect.detect(text)
        except:
            language = "unknown"
        
        # Basic sentiment (simple heuristic)
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'horrible', 'worst']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            sentiment = {"label": "positive", "score": 0.7}
        elif neg_count > pos_count:
            sentiment = {"label": "negative", "score": 0.7}
        else:
            sentiment = {"label": "neutral", "score": 0.6}
        
        return {
            "sentiment": sentiment,
            "emotion": {"label": "neutral", "score": 0.5},
            "language": language,
            "cultural_elements": [],
            "quality_score": min(flesch_reading_ease(text) / 100.0, 1.0) if text else 0.0,
            "status": "fallback"
        }
    
    def _fallback_image_analysis(self, image_data: bytes) -> Dict:
        """Fallback image analysis"""
        try:
            # Basic image info
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            
            return {
                "caption": f"Image ({width}x{height}px) - Configure image analysis API for detailed analysis",
                "objects": [],
                "cultural_elements": [],
                "quality_score": 0.5,
                "status": "fallback"
            }
        except Exception:
            return {
                "caption": "Image analysis not available",
                "objects": [],
                "cultural_elements": [],
                "quality_score": 0.0,
                "status": "error"
            }
    
    def _fallback_translation(self, text: str, source_lang: str, target_lang: str) -> Dict:
        """Fallback translation"""
        return {
            "translated_text": f"[Translation from {source_lang} to {target_lang} not available - configure translation API]",
            "source_language": source_lang,
            "target_language": target_lang,
            "confidence": 0.0,
            "status": "fallback"
        }

# Global inference manager instance
@st.cache_resource
def get_inference_manager() -> InferenceAPIManager:
    """Get cached inference manager instance"""
    return InferenceAPIManager()

# Convenience functions
def transcribe_audio(audio_data: bytes, language: str = None) -> Optional[Dict]:
    """Transcribe audio using global inference manager"""
    manager = get_inference_manager()
    return manager.transcribe_audio(audio_data, language)

def analyze_text(text: str, language: str = None) -> Optional[Dict]:
    """Analyze text using global inference manager"""
    manager = get_inference_manager()
    return manager.analyze_text(text, language)

def analyze_image(image_data: bytes) -> Optional[Dict]:
    """Analyze image using global inference manager"""
    manager = get_inference_manager()
    return manager.analyze_image(image_data)

def translate_text(text: str, source_lang: str, target_lang: str) -> Optional[Dict]:
    """Translate text using global inference manager"""
    manager = get_inference_manager()
    return manager.translate_text(text, source_lang, target_lang)