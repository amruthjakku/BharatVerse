"""
Free Tier AI Models - Optimized for Zero-Cost Deployment
Uses the smallest possible models that still provide real AI functionality
"""

import os
import logging
from typing import Dict, Any, Optional, List
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FreeTierAIManager:
    """Ultra-lightweight AI Manager for free hosting"""
    
    def __init__(self):
        self.deployment_mode = "free_tier"
        
        # Only load the most essential, smallest models
        self.sentiment_analyzer = None
        self.text_processor = None
        
        # Analytics tracking
        self.analytics = {
            "total_operations": 0,
            "text_analyses": 0,
            "image_analyses": 0,
            "audio_transcriptions": 0,
            "errors": 0
        }
        
        logger.info("FreeTierAIManager initialized for zero-cost deployment")
        self._load_minimal_models()
    
    def _load_minimal_models(self):
        """Load only the smallest, most essential models"""
        try:
            # Only load if we have enough memory
            import psutil
            available_memory = psutil.virtual_memory().available / (1024**3)  # GB
            
            if available_memory > 1.0:  # Only if we have >1GB available
                try:
                    from transformers import pipeline
                    
                    # Use the smallest sentiment model available
                    self.sentiment_analyzer = pipeline(
                        "sentiment-analysis",
                        model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                        return_all_scores=False,
                        device=-1  # Force CPU to save memory
                    )
                    logger.info("✅ Minimal sentiment analyzer loaded")
                except Exception as e:
                    logger.warning(f"Could not load sentiment analyzer: {e}")
                    self.sentiment_analyzer = None
            
            # Always available - rule-based processing
            self.text_processor = True
            logger.info("✅ Rule-based text processor ready")
            
        except Exception as e:
            logger.error(f"Failed to load minimal models: {e}")
            # Fallback to pure rule-based processing
            self.sentiment_analyzer = None
            self.text_processor = True
    
    def analyze_text(self, text: str, language: str = "auto") -> Dict[str, Any]:
        """Lightweight text analysis optimized for free tier"""
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
                "deployment_mode": "free_tier",
                "ai_features": "basic"
            }
            
            # Sentiment analysis if model is available
            if self.sentiment_analyzer:
                try:
                    sentiment_result = self.sentiment_analyzer(text[:512])  # Limit text length
                    analysis["sentiment"] = {
                        "label": sentiment_result[0]["label"],
                        "confidence": sentiment_result[0]["score"]
                    }
                    analysis["ai_features"] = "enhanced"
                except Exception as e:
                    logger.warning(f"Sentiment analysis failed: {e}")
                    analysis["sentiment"] = self._rule_based_sentiment(text)
            else:
                analysis["sentiment"] = self._rule_based_sentiment(text)
            
            # Cultural elements detection (rule-based)
            analysis["cultural_elements"] = self._detect_cultural_elements_simple(text)
            
            # Quality metrics (rule-based)
            analysis["quality_metrics"] = self._calculate_quality_metrics_simple(text)
            
            return analysis
            
        except Exception as e:
            self.analytics["errors"] += 1
            logger.error(f"Text analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "deployment_mode": "free_tier"
            }
    
    def analyze_image(self, image_data: Any, filename: str = "") -> Dict[str, Any]:
        """Basic image analysis for free tier"""
        try:
            self.analytics["total_operations"] += 1
            self.analytics["image_analyses"] += 1
            
            # Basic image processing without heavy models
            analysis = {
                "success": True,
                "filename": filename,
                "deployment_mode": "free_tier",
                "caption": "Basic image processing - cultural heritage content detected",
                "objects": ["Cultural artifact", "Heritage item", "Traditional element"],
                "cultural_elements": self._detect_image_cultural_elements(filename),
                "quality_score": 0.75,
                "description": "Free tier image analysis - upgrade for AI-powered detailed analysis",
                "ai_features": "rule_based"
            }
            
            return analysis
            
        except Exception as e:
            self.analytics["errors"] += 1
            logger.error(f"Image analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "deployment_mode": "free_tier"
            }
    
    def transcribe_audio(self, audio_data: Any, filename: str = "") -> Dict[str, Any]:
        """Basic audio processing for free tier"""
        try:
            self.analytics["total_operations"] += 1
            self.analytics["audio_transcriptions"] += 1
            
            return {
                "success": True,
                "filename": filename,
                "deployment_mode": "free_tier",
                "transcription": "Audio transcription available with full AI deployment",
                "language": "auto-detected",
                "confidence": 0.0,
                "duration": 0.0,
                "description": "Free tier - basic audio handling. Full Whisper AI available in premium deployment",
                "ai_features": "placeholder"
            }
            
        except Exception as e:
            self.analytics["errors"] += 1
            logger.error(f"Audio transcription failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "deployment_mode": "free_tier"
            }
    
    def translate_text(self, text: str, target_language: str = "en") -> Dict[str, Any]:
        """Basic translation for free tier"""
        return {
            "success": False,
            "error": "Translation available in full AI deployment",
            "translation": text,
            "deployment_mode": "free_tier",
            "upgrade_message": "Deploy with full AI models for real translation"
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information for free tier"""
        return {
            "deployment_mode": "free_tier",
            "cost": "$0",
            "whisper_available": False,
            "text_analysis_available": True,
            "image_analysis_available": True,
            "translation_available": False,
            "tracking_enabled": True,
            "models": {
                "sentiment": "twitter-roberta-base-sentiment" if self.sentiment_analyzer else "rule-based",
                "text_analysis": "rule-based",
                "image_analysis": "rule-based",
                "whisper": "not available (free tier)",
                "translation": "not available (free tier)"
            },
            "upgrade_info": {
                "message": "This is the free tier with basic AI features",
                "full_ai_features": [
                    "Whisper Large-v3 audio transcription",
                    "BLIP-2 image captioning", 
                    "Advanced multilingual translation",
                    "Cultural heritage specialized models"
                ]
            }
        }
    
    def get_real_time_analytics(self) -> Dict[str, Any]:
        """Get real-time analytics for free tier"""
        return {
            "deployment_mode": "free_tier",
            "cost": "$0",
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
                "Rule-based sentiment analysis", 
                "Cultural element detection",
                "Basic image processing",
                "File upload handling"
            ],
            "upgrade_message": "Deploy with full AI models for advanced features"
        }
    
    def _rule_based_sentiment(self, text: str) -> Dict[str, Any]:
        """Simple rule-based sentiment analysis"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'beautiful', 'love', 'like', 'happy', 'joy']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'sad', 'angry', 'disappointed', 'poor', 'worst']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return {"label": "POSITIVE", "confidence": 0.7}
        elif negative_count > positive_count:
            return {"label": "NEGATIVE", "confidence": 0.7}
        else:
            return {"label": "NEUTRAL", "confidence": 0.6}
    
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
            "festival": ["diwali", "holi", "eid", "christmas", "dussehra", "navratri", "pongal", "onam"],
            "food": ["curry", "biryani", "samosa", "dosa", "chapati", "dal", "rice", "spices"],
            "music": ["classical", "folk", "bhajan", "qawwali", "tabla", "sitar", "veena", "flute"],
            "dance": ["bharatanatyam", "kathak", "odissi", "kuchipudi", "folk dance", "classical dance"],
            "art": ["rangoli", "mehendi", "pottery", "weaving", "painting", "sculpture", "craft"],
            "tradition": ["wedding", "ceremony", "ritual", "custom", "heritage", "culture", "tradition"]
        }
        
        detected_elements = []
        text_lower = text.lower()
        
        for category, keywords in cultural_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_elements.append(category)
        
        return detected_elements or ["general_cultural"]
    
    def _detect_image_cultural_elements(self, filename: str) -> List[str]:
        """Detect cultural elements from image filename"""
        filename_lower = filename.lower()
        
        cultural_indicators = {
            "architecture": ["temple", "palace", "fort", "monument", "building"],
            "art": ["painting", "sculpture", "craft", "art", "design"],
            "festival": ["celebration", "festival", "ceremony", "ritual"],
            "food": ["food", "cuisine", "dish", "recipe", "cooking"],
            "clothing": ["dress", "costume", "traditional", "wear", "fabric"],
            "music": ["instrument", "music", "dance", "performance"]
        }
        
        detected = []
        for category, keywords in cultural_indicators.items():
            if any(keyword in filename_lower for keyword in keywords):
                detected.append(category)
        
        return detected or ["heritage_item"]
    
    def _calculate_quality_metrics_simple(self, text: str) -> Dict[str, float]:
        """Simple quality metrics calculation"""
        words = text.split()
        sentences = [s for s in text.split('.') if s.strip()]
        
        # Simple readability based on word and sentence count
        readability = min(1.0, len(words) / 50)  # Optimal around 50 words
        completeness = min(1.0, len(sentences) / 3)  # Optimal around 3 sentences
        
        # Cultural relevance based on cultural keywords
        cultural_elements = self._detect_cultural_elements_simple(text)
        cultural_relevance = min(1.0, len(cultural_elements) * 0.3)
        
        overall_score = (readability + completeness + cultural_relevance) / 3
        
        return {
            "readability": readability,
            "completeness": completeness,
            "cultural_relevance": cultural_relevance,
            "overall_score": overall_score
        }

# Global instance for free tier deployment
free_tier_ai_manager = FreeTierAIManager()

# Compatibility function
def get_ai_manager():
    """Get the appropriate AI manager based on deployment mode"""
    deployment_mode = os.getenv("AI_MODE", "free_tier")
    
    if deployment_mode == "free_tier":
        return free_tier_ai_manager
    else:
        # Try to import full AI manager if available
        try:
            from .enhanced_ai_models import ai_manager
            return ai_manager
        except ImportError:
            logger.info("Full AI manager not available, using free tier version")
            return free_tier_ai_manager