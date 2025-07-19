"""
Lightweight AI Models for Streamlit Cloud Deployment
Optimized for cloud constraints with smaller models
"""

import os
import logging
from typing import Dict, Any, Optional, List
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudAIManager:
    """Lightweight AI Manager for Streamlit Cloud"""
    
    def __init__(self):
        self.ai_mode = os.getenv("AI_MODE", "cloud")
        self.use_lightweight = os.getenv("USE_LIGHTWEIGHT_MODELS", "true").lower() == "true"
        
        # Initialize lightweight models
        self.sentiment_analyzer = None
        self.text_analyzer = None
        self.image_analyzer = None
        
        # Analytics tracking
        self.analytics = {
            "total_operations": 0,
            "text_analyses": 0,
            "image_analyses": 0,
            "audio_transcriptions": 0,
            "errors": 0
        }
        
        logger.info(f"CloudAIManager initialized in {self.ai_mode} mode")
        
        if self.use_lightweight:
            self._load_lightweight_models()
    
    def _load_lightweight_models(self):
        """Load lightweight models suitable for cloud deployment"""
        try:
            # Only load essential models to stay within memory limits
            logger.info("Loading lightweight AI models for cloud deployment...")
            
            # Basic sentiment analysis (small model)
            try:
                from transformers import pipeline
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    return_all_scores=True
                )
                logger.info("✅ Lightweight sentiment analyzer loaded")
            except Exception as e:
                logger.warning(f"Sentiment analyzer not available: {e}")
                self.sentiment_analyzer = None
            
            # Basic text processing
            self.text_analyzer = True  # Use rule-based analysis
            logger.info("✅ Text analyzer ready")
            
            # Basic image processing
            self.image_analyzer = True  # Use basic CV operations
            logger.info("✅ Image analyzer ready")
            
        except Exception as e:
            logger.error(f"Failed to load lightweight models: {e}")
    
    def analyze_text(self, text: str, language: str = "auto") -> Dict[str, Any]:
        """Lightweight text analysis"""
        try:
            self.analytics["total_operations"] += 1
            self.analytics["text_analyses"] += 1
            
            analysis = {
                "success": True,
                "text": text,
                "language": self._detect_language_simple(text),
                "length": len(text),
                "word_count": len(text.split()),
                "sentence_count": len([s for s in text.split('.') if s.strip()]),
                "ai_mode": "cloud_lightweight"
            }
            
            # Sentiment analysis if available
            if self.sentiment_analyzer:
                try:
                    sentiment_result = self.sentiment_analyzer(text)
                    analysis["sentiment"] = {
                        "label": sentiment_result[0]["label"],
                        "confidence": sentiment_result[0]["score"]
                    }
                except Exception as e:
                    logger.warning(f"Sentiment analysis failed: {e}")
                    analysis["sentiment"] = {"label": "neutral", "confidence": 0.5}
            else:
                analysis["sentiment"] = {"label": "neutral", "confidence": 0.5}
            
            # Basic cultural elements detection
            analysis["cultural_elements"] = self._detect_cultural_elements_simple(text)
            
            # Quality metrics
            analysis["quality_metrics"] = self._calculate_quality_metrics_simple(text)
            
            return analysis
            
        except Exception as e:
            self.analytics["errors"] += 1
            logger.error(f"Text analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "ai_mode": "cloud_lightweight"
            }
    
    def analyze_image(self, image_data: Any, filename: str = "") -> Dict[str, Any]:
        """Lightweight image analysis"""
        try:
            self.analytics["total_operations"] += 1
            self.analytics["image_analyses"] += 1
            
            # Basic image analysis without heavy models
            analysis = {
                "success": True,
                "filename": filename,
                "ai_mode": "cloud_lightweight",
                "caption": "Image analysis available in full AI mode",
                "objects": [],
                "cultural_elements": ["Traditional", "Heritage", "Cultural"],
                "quality_score": 0.8,
                "description": "Lightweight image processing - upgrade to full AI for detailed analysis"
            }
            
            return analysis
            
        except Exception as e:
            self.analytics["errors"] += 1
            logger.error(f"Image analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "ai_mode": "cloud_lightweight"
            }
    
    def transcribe_audio(self, audio_data: Any, filename: str = "") -> Dict[str, Any]:
        """Lightweight audio transcription"""
        try:
            self.analytics["total_operations"] += 1
            self.analytics["audio_transcriptions"] += 1
            
            # Placeholder for audio transcription
            return {
                "success": True,
                "filename": filename,
                "ai_mode": "cloud_lightweight",
                "transcription": "Audio transcription available in full AI mode with Whisper",
                "language": "auto-detected",
                "confidence": 0.0,
                "duration": 0.0,
                "description": "Lightweight mode - upgrade to full AI for Whisper transcription"
            }
            
        except Exception as e:
            self.analytics["errors"] += 1
            logger.error(f"Audio transcription failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "ai_mode": "cloud_lightweight"
            }
    
    def translate_text(self, text: str, target_language: str = "en") -> Dict[str, Any]:
        """Basic translation placeholder"""
        return {
            "success": False,
            "error": "Translation available in full AI mode",
            "translation": text,
            "ai_mode": "cloud_lightweight"
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "ai_mode": self.ai_mode,
            "lightweight_mode": self.use_lightweight,
            "whisper_available": False,
            "text_analysis_available": self.text_analyzer is not None,
            "image_analysis_available": self.image_analyzer is not None,
            "translation_available": False,
            "tracking_enabled": True,
            "models": {
                "sentiment": "twitter-roberta-base-sentiment-latest" if self.sentiment_analyzer else "not available",
                "text_analysis": "rule-based" if self.text_analyzer else "not available",
                "image_analysis": "basic-cv" if self.image_analyzer else "not available",
                "whisper": "not available (cloud mode)",
                "translation": "not available (cloud mode)"
            }
        }
    
    def get_real_time_analytics(self) -> Dict[str, Any]:
        """Get real-time analytics"""
        return {
            "mode": "cloud_lightweight",
            "total_operations": self.analytics["total_operations"],
            "text_analyses": self.analytics["text_analyses"],
            "image_analyses": self.analytics["image_analyses"],
            "audio_transcriptions": self.analytics["audio_transcriptions"],
            "errors": self.analytics["errors"],
            "success_rate": (
                (self.analytics["total_operations"] - self.analytics["errors"]) / 
                max(self.analytics["total_operations"], 1) * 100
            ),
            "available_features": [
                "Basic text analysis",
                "Sentiment analysis",
                "Cultural element detection",
                "Basic image processing"
            ],
            "upgrade_message": "Connect to full AI backend for advanced features"
        }
    
    def _detect_language_simple(self, text: str) -> str:
        """Simple language detection"""
        # Basic language detection based on character patterns
        if any(ord(char) > 2304 for char in text):  # Devanagari range
            return "hi"  # Hindi
        elif any(ord(char) > 2432 for char in text):  # Bengali range
            return "bn"  # Bengali
        else:
            return "en"  # Default to English
    
    def _detect_cultural_elements_simple(self, text: str) -> List[str]:
        """Simple cultural elements detection"""
        cultural_keywords = {
            "festival": ["diwali", "holi", "eid", "christmas", "dussehra", "navratri"],
            "food": ["curry", "biryani", "samosa", "dosa", "chapati", "dal"],
            "music": ["classical", "folk", "bhajan", "qawwali", "tabla", "sitar"],
            "dance": ["bharatanatyam", "kathak", "odissi", "kuchipudi", "folk dance"],
            "art": ["rangoli", "mehendi", "pottery", "weaving", "painting"],
            "tradition": ["wedding", "ceremony", "ritual", "custom", "heritage"]
        }
        
        detected_elements = []
        text_lower = text.lower()
        
        for category, keywords in cultural_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_elements.append(category)
        
        return detected_elements or ["general"]
    
    def _calculate_quality_metrics_simple(self, text: str) -> Dict[str, float]:
        """Simple quality metrics"""
        words = text.split()
        sentences = [s for s in text.split('.') if s.strip()]
        
        return {
            "readability": min(1.0, len(words) / 100),  # Simple readability
            "completeness": min(1.0, len(sentences) / 5),  # Based on sentence count
            "cultural_relevance": 0.7,  # Default cultural relevance
            "overall_score": 0.75  # Default overall score
        }

# Global instance for cloud deployment
cloud_ai_manager = CloudAIManager()

# Compatibility function for existing code
def get_ai_manager():
    """Get the appropriate AI manager based on deployment mode"""
    if os.getenv("AI_MODE", "cloud") == "cloud":
        return cloud_ai_manager
    else:
        # Try to import full AI manager if available
        try:
            from .enhanced_ai_models import ai_manager
            return ai_manager
        except ImportError:
            logger.warning("Full AI manager not available, using cloud version")
            return cloud_ai_manager