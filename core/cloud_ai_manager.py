"""
Cloud AI Manager for BharatVerse
Orchestrates AI processing tasks and routes them to appropriate inference modules

Module: cloud_ai_manager.py
Purpose: High-level orchestration of AI workflows, caching, and result management
- Routes tasks to inference_manager.py for actual API calls
- Manages caching via redis_cache.py  
- Logs analytics via supabase_db.py
- Validates configurations via config_validator.py
"""
import streamlit as st
import hashlib
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import asyncio

# Import our cloud utilities
from utils.inference_manager import get_inference_manager, transcribe_audio, analyze_text, analyze_image, translate_text
from utils.redis_cache import get_cache_manager, cache_ai_result, get_cached_ai_result
from utils.supabase_db import get_database_manager, log_analytics
from utils.config_validator import get_config_validator

logger = logging.getLogger(__name__)

class CloudAIManager:
    """
    Cloud-based AI Manager that uses external APIs for all AI processing
    Optimized for free-tier cloud services with caching and rate limiting
    """
    
    def __init__(self):
        """Initialize cloud AI manager"""
        self.inference_manager = get_inference_manager()
        self.cache_manager = get_cache_manager()
        self.db_manager = get_database_manager()
        
        # Configuration from secrets
        app_config = st.secrets.get("app", {})
        self.cache_enabled = app_config.get("enable_caching", True)
        self.cache_ttl_hours = int(app_config.get("cache_ttl_hours", 24))
        
        rate_limits = st.secrets.get("rate_limits", {})
        self.api_calls_per_minute = int(rate_limits.get("api_calls_per_minute", 60))
        
        logger.info("Cloud AI Manager initialized successfully")
    
    def _generate_cache_key(self, data: str, operation_type: str) -> str:
        """Generate cache key for AI operations"""
        combined = f"{operation_type}:{data}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _check_rate_limit(self, user_id: str = None) -> bool:
        """Check if user/system is within rate limits"""
        if not self.cache_manager.is_connected():
            return True  # Allow if cache is not available
        
        # Use session-based rate limiting if no user_id
        identifier = user_id or st.session_state.get("session_id", "anonymous")
        
        current_minute = datetime.now().strftime("%Y%m%d%H%M")
        rate_key = f"rate_limit:{identifier}:{current_minute}"
        
        try:
            current_calls = self.cache_manager.get(rate_key) or 0
            if current_calls >= self.api_calls_per_minute:
                return False
            
            # Increment counter
            self.cache_manager.increment(rate_key, 1)
            self.cache_manager.expire(rate_key, 60)  # Expire after 1 minute
            return True
            
        except Exception as e:
            logger.error(f"Rate limiting check failed: {e}")
            return True  # Allow on error
    
    def process_audio(self, audio_data: bytes, language: str = None, 
                     user_id: int = None) -> Dict[str, Any]:
        """
        Process audio using cloud Whisper API with caching
        
        Args:
            audio_data: Audio file bytes
            language: Optional language hint
            user_id: User ID for analytics
            
        Returns:
            Transcription result with text, timestamps, and metadata
        """
        start_time = datetime.now()
        
        try:
            # Check rate limits
            if not self._check_rate_limit(str(user_id) if user_id else None):
                return {
                    "status": "error",
                    "error": "Rate limit exceeded. Please wait a moment.",
                    "text": "",
                    "language": "unknown",
                    "confidence": 0.0,
                    "processing_time": 0
                }
            
            # Generate cache key
            audio_hash = hashlib.md5(audio_data).hexdigest()
            cache_key = self._generate_cache_key(f"{audio_hash}:{language}", "whisper")
            
            # Check cache first
            if self.cache_enabled:
                cached_result = get_cached_ai_result(cache_key)
                if cached_result:
                    logger.info("Returning cached audio transcription")
                    
                    # Log analytics
                    if self.db_manager:
                        log_analytics(
                            action="audio_transcription_cached",
                            user_id=user_id,
                            metadata={"cache_key": cache_key}
                        )
                    
                    return {**cached_result, "cached": True}
            
            # Process with cloud API
            result = transcribe_audio(audio_data, language)
            
            if result:
                # Add processing metadata
                processing_time = (datetime.now() - start_time).total_seconds()
                result["processing_time"] = processing_time
                result["processed_at"] = datetime.now().isoformat()
                result["cached"] = False
                
                # Cache the result
                if self.cache_enabled and result.get("status") == "success":
                    cache_ai_result(cache_key, result, self.cache_ttl_hours)
                
                # Log analytics
                if self.db_manager:
                    log_analytics(
                        action="audio_transcription_processed",
                        user_id=user_id,
                        metadata={
                            "language": result.get("language"),
                            "confidence": result.get("confidence"),
                            "processing_time": processing_time,
                            "audio_size": len(audio_data)
                        }
                    )
                
                logger.info(f"Audio processed successfully in {processing_time:.2f}s")
                return result
            
            # Fallback result
            return {
                "status": "error",
                "error": "Audio processing service unavailable",
                "text": "",
                "language": "unknown",
                "confidence": 0.0,
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
        
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "text": "",
                "language": "unknown",
                "confidence": 0.0,
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
    
    def process_text(self, text: str, language: str = None,
                    user_id: int = None) -> Dict[str, Any]:
        """
        Process text using cloud NLP APIs with caching
        
        Args:
            text: Text to analyze
            language: Optional language hint
            user_id: User ID for analytics
            
        Returns:
            Analysis result with sentiment, emotion, and cultural insights
        """
        start_time = datetime.now()
        
        try:
            # Check rate limits
            if not self._check_rate_limit(str(user_id) if user_id else None):
                return {
                    "status": "error",
                    "error": "Rate limit exceeded. Please wait a moment.",
                    "sentiment": {"label": "neutral", "score": 0.0},
                    "emotion": {"label": "neutral", "score": 0.0},
                    "language": "unknown"
                }
            
            # Generate cache key
            text_hash = hashlib.md5(text.encode()).hexdigest()
            cache_key = self._generate_cache_key(f"{text_hash}:{language}", "text_analysis")
            
            # Check cache first
            if self.cache_enabled:
                cached_result = get_cached_ai_result(cache_key)
                if cached_result:
                    logger.info("Returning cached text analysis")
                    
                    # Log analytics
                    if self.db_manager:
                        log_analytics(
                            action="text_analysis_cached",
                            user_id=user_id,
                            metadata={"cache_key": cache_key}
                        )
                    
                    return {**cached_result, "cached": True}
            
            # Process with cloud API
            result = analyze_text(text, language)
            
            if result:
                # Add processing metadata
                processing_time = (datetime.now() - start_time).total_seconds()
                result["processing_time"] = processing_time
                result["processed_at"] = datetime.now().isoformat()
                result["cached"] = False
                
                # Cache the result
                if self.cache_enabled and result.get("status") == "success":
                    cache_ai_result(cache_key, result, self.cache_ttl_hours)
                
                # Log analytics
                if self.db_manager:
                    log_analytics(
                        action="text_analysis_processed",
                        user_id=user_id,
                        metadata={
                            "language": result.get("language"),
                            "sentiment": result.get("sentiment", {}).get("label"),
                            "emotion": result.get("emotion", {}).get("label"),
                            "processing_time": processing_time,
                            "text_length": len(text)
                        }
                    )
                
                logger.info(f"Text analyzed successfully in {processing_time:.2f}s")
                return result
            
            # Fallback result
            return {
                "status": "error",
                "error": "Text analysis service unavailable",
                "sentiment": {"label": "neutral", "score": 0.0},
                "emotion": {"label": "neutral", "score": 0.0},
                "language": "unknown",
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
        
        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "sentiment": {"label": "neutral", "score": 0.0},
                "emotion": {"label": "neutral", "score": 0.0},
                "language": "unknown",
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
    
    def process_image(self, image_data: bytes, user_id: int = None) -> Dict[str, Any]:
        """
        Process image using cloud vision APIs with caching
        
        Args:
            image_data: Image file bytes
            user_id: User ID for analytics
            
        Returns:
            Analysis result with captions, objects, and cultural insights
        """
        start_time = datetime.now()
        
        try:
            # Check rate limits
            if not self._check_rate_limit(str(user_id) if user_id else None):
                return {
                    "status": "error",
                    "error": "Rate limit exceeded. Please wait a moment.",
                    "caption": "",
                    "objects": [],
                    "cultural_elements": []
                }
            
            # Generate cache key
            image_hash = hashlib.md5(image_data).hexdigest()
            cache_key = self._generate_cache_key(image_hash, "image_analysis")
            
            # Check cache first
            if self.cache_enabled:
                cached_result = get_cached_ai_result(cache_key)
                if cached_result:
                    logger.info("Returning cached image analysis")
                    
                    # Log analytics
                    if self.db_manager:
                        log_analytics(
                            action="image_analysis_cached",
                            user_id=user_id,
                            metadata={"cache_key": cache_key}
                        )
                    
                    return {**cached_result, "cached": True}
            
            # Process with cloud API
            result = analyze_image(image_data)
            
            if result:
                # Add processing metadata
                processing_time = (datetime.now() - start_time).total_seconds()
                result["processing_time"] = processing_time
                result["processed_at"] = datetime.now().isoformat()
                result["cached"] = False
                
                # Cache the result
                if self.cache_enabled and result.get("status") == "success":
                    cache_ai_result(cache_key, result, self.cache_ttl_hours)
                
                # Log analytics
                if self.db_manager:
                    log_analytics(
                        action="image_analysis_processed",
                        user_id=user_id,
                        metadata={
                            "caption_length": len(result.get("caption", "")),
                            "objects_detected": len(result.get("objects", [])),
                            "cultural_elements": len(result.get("cultural_elements", [])),
                            "processing_time": processing_time,
                            "image_size": len(image_data)
                        }
                    )
                
                logger.info(f"Image analyzed successfully in {processing_time:.2f}s")
                return result
            
            # Fallback result
            return {
                "status": "error",
                "error": "Image analysis service unavailable",
                "caption": "",
                "objects": [],
                "cultural_elements": [],
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
        
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "caption": "",
                "objects": [],
                "cultural_elements": [],
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
    
    def translate_text_content(self, text: str, source_lang: str, target_lang: str,
                              user_id: int = None) -> Dict[str, Any]:
        """
        Translate text using cloud translation APIs with caching
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            user_id: User ID for analytics
            
        Returns:
            Translation result
        """
        start_time = datetime.now()
        
        try:
            # Check rate limits
            if not self._check_rate_limit(str(user_id) if user_id else None):
                return {
                    "status": "error",
                    "error": "Rate limit exceeded. Please wait a moment.",
                    "translated_text": text,
                    "source_language": source_lang,
                    "target_language": target_lang
                }
            
            # Generate cache key
            text_hash = hashlib.md5(text.encode()).hexdigest()
            cache_key = self._generate_cache_key(
                f"{text_hash}:{source_lang}:{target_lang}", 
                "translation"
            )
            
            # Check cache first
            if self.cache_enabled:
                cached_result = get_cached_ai_result(cache_key)
                if cached_result:
                    logger.info("Returning cached translation")
                    
                    # Log analytics
                    if self.db_manager:
                        log_analytics(
                            action="translation_cached",
                            user_id=user_id,
                            metadata={"cache_key": cache_key}
                        )
                    
                    return {**cached_result, "cached": True}
            
            # Process with cloud API
            result = translate_text(text, source_lang, target_lang)
            
            if result:
                # Add processing metadata
                processing_time = (datetime.now() - start_time).total_seconds()
                result["processing_time"] = processing_time
                result["processed_at"] = datetime.now().isoformat()
                result["cached"] = False
                
                # Cache the result
                if self.cache_enabled and result.get("status") == "success":
                    cache_ai_result(cache_key, result, self.cache_ttl_hours)
                
                # Log analytics
                if self.db_manager:
                    log_analytics(
                        action="translation_processed",
                        user_id=user_id,
                        metadata={
                            "source_lang": source_lang,
                            "target_lang": target_lang,
                            "text_length": len(text),
                            "processing_time": processing_time
                        }
                    )
                
                logger.info(f"Translation completed successfully in {processing_time:.2f}s")
                return result
            
            # Fallback result
            return {
                "status": "error",
                "error": "Translation service unavailable",
                "translated_text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
        
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "translated_text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status for all cloud services"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }
        
        # Check inference APIs
        status["services"]["inference_api"] = {
            "status": "available" if self.inference_manager else "unavailable",
            "whisper_configured": bool(st.secrets.get("inference", {}).get("whisper_api")),
            "text_analysis_configured": bool(st.secrets.get("inference", {}).get("text_analysis_api")),
            "image_analysis_configured": bool(st.secrets.get("inference", {}).get("image_analysis_api")),
            "translation_configured": bool(st.secrets.get("inference", {}).get("translation_api"))
        }
        
        # Check cache
        status["services"]["redis_cache"] = {
            "status": "connected" if self.cache_manager.is_connected() else "disconnected",
            "caching_enabled": self.cache_enabled,
            "cache_ttl_hours": self.cache_ttl_hours
        }
        
        # Check database
        try:
            db_connected = self.db_manager and self.db_manager.engine is not None
            status["services"]["database"] = {
                "status": "connected" if db_connected else "disconnected",
                "type": "postgresql"
            }
        except Exception:
            status["services"]["database"] = {
                "status": "error",
                "type": "postgresql"
            }
        
        # Rate limiting status
        status["rate_limits"] = {
            "api_calls_per_minute": self.api_calls_per_minute,
            "current_minute": datetime.now().strftime("%Y%m%d%H%M")
        }
        
        return status

# Global cloud AI manager instance
@st.cache_resource
def get_cloud_ai_manager() -> CloudAIManager:
    """Get cached cloud AI manager instance"""
    return CloudAIManager()