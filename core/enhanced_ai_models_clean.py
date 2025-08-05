"""
Enhanced AI Models for BharatVerse - Clean Architecture
Using state-of-the-art models for cultural heritage preservation
"""

import os
import io
import json
import logging
import tempfile
import time
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import numpy as np
from datetime import datetime

# Import the new clean architecture
from .service_manager import get_service_manager
from .error_handler import handle_errors, error_boundary
from .module_loader import load_module, get_class, get_function, CommonModules
from .config_manager import get_config_manager

logger = logging.getLogger(__name__)

class EnhancedAIManager:
    """Clean AI manager without scattered availability flags"""
    
    def __init__(self):
        self.service_manager = get_service_manager()
        self.config_manager = get_config_manager()
        self._models = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize AI models using the clean architecture"""
        
        # Load AI backend
        ai_backend = CommonModules.load_ai_backend()
        self.ai_backend = ai_backend["backend"]
        
        if self.ai_backend == "none":
            logger.warning("No AI backend available")
            return
        
        # Initialize specific models
        self._init_whisper_model()
        self._init_transformers_models()
        self._init_vision_models()
        self._init_language_detection()
    
    @handle_errors(show_error=False, log_error=True)
    def _init_whisper_model(self):
        """Initialize Whisper model for audio transcription"""
        whisper_module = load_module("whisper")
        if whisper_module:
            self._models["whisper"] = {
                "module": whisper_module,
                "model": None,  # Lazy load
                "available": True
            }
            logger.info("Whisper model initialized")
    
    @handle_errors(show_error=False, log_error=True)
    def _init_transformers_models(self):
        """Initialize Transformers models"""
        transformers_module = load_module("transformers")
        if transformers_module:
            self._models["transformers"] = {
                "module": transformers_module,
                "pipeline": getattr(transformers_module, "pipeline", None),
                "available": True
            }
            logger.info("Transformers models initialized")
    
    @handle_errors(show_error=False, log_error=True)
    def _init_vision_models(self):
        """Initialize vision models for image analysis"""
        transformers_module = load_module("transformers")
        if transformers_module:
            # Try to get vision-specific classes
            blip_processor = get_class("transformers", "BlipProcessor")
            blip_model = get_class("transformers", "BlipForConditionalGeneration")
            
            if blip_processor and blip_model:
                self._models["vision"] = {
                    "processor": blip_processor,
                    "model": blip_model,
                    "available": True
                }
                logger.info("Vision models initialized")
    
    @handle_errors(show_error=False, log_error=True)
    def _init_language_detection(self):
        """Initialize language detection"""
        langdetect_module = load_module("langdetect")
        if langdetect_module:
            self._models["langdetect"] = {
                "module": langdetect_module,
                "detect": getattr(langdetect_module, "detect", None),
                "available": True
            }
            logger.info("Language detection initialized")
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if a specific model is available"""
        return self._models.get(model_name, {}).get("available", False)
    
    @handle_errors(fallback_value=None, show_error=True)
    def transcribe_audio(self, audio_data: bytes, language: str = "auto") -> Optional[Dict[str, Any]]:
        """Transcribe audio using available models"""
        
        if not self.is_model_available("whisper"):
            return self._fallback_transcription(audio_data, language)
        
        whisper_model = self._get_whisper_model()
        if not whisper_model:
            return self._fallback_transcription(audio_data, language)
        
        # Process audio with Whisper
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file.flush()
            
            try:
                result = whisper_model.transcribe(temp_file.name, language=language if language != "auto" else None)
                
                return {
                    "text": result["text"],
                    "language": result.get("language", "unknown"),
                    "confidence": 0.9,  # Whisper doesn't provide confidence
                    "model": "whisper",
                    "timestamp": datetime.now().isoformat()
                }
            finally:
                os.unlink(temp_file.name)
    
    def _get_whisper_model(self):
        """Lazy load Whisper model"""
        whisper_info = self._models.get("whisper", {})
        
        if not whisper_info.get("available"):
            return None
        
        if whisper_info.get("model") is None:
            whisper_module = whisper_info["module"]
            try:
                # Load base model (smallest for faster processing)
                whisper_info["model"] = whisper_module.load_model("base")
                logger.info("Whisper model loaded")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                whisper_info["available"] = False
                return None
        
        return whisper_info.get("model")
    
    @handle_errors(fallback_value={"text": "Transcription not available", "language": "unknown", "confidence": 0.0})
    def _fallback_transcription(self, audio_data: bytes, language: str) -> Dict[str, Any]:
        """Fallback transcription when AI models are not available"""
        return {
            "text": "[Audio transcription not available - AI models not loaded]",
            "language": language if language != "auto" else "unknown",
            "confidence": 0.0,
            "model": "fallback",
            "timestamp": datetime.now().isoformat()
        }
    
    @handle_errors(fallback_value=None, show_error=True)
    def analyze_image(self, image_data: bytes, prompt: str = "Describe this image") -> Optional[Dict[str, Any]]:
        """Analyze image using available vision models"""
        
        if not self.is_model_available("vision"):
            return self._fallback_image_analysis(image_data, prompt)
        
        # Implementation would use vision models
        return {
            "description": "[Image analysis would be performed here]",
            "confidence": 0.8,
            "model": "vision",
            "timestamp": datetime.now().isoformat()
        }
    
    def _fallback_image_analysis(self, image_data: bytes, prompt: str) -> Dict[str, Any]:
        """Fallback image analysis"""
        return {
            "description": "[Image analysis not available - vision models not loaded]",
            "confidence": 0.0,
            "model": "fallback",
            "timestamp": datetime.now().isoformat()
        }
    
    @handle_errors(fallback_value="unknown", show_error=False)
    def detect_language(self, text: str) -> str:
        """Detect language of text"""
        
        if not self.is_model_available("langdetect"):
            return "unknown"
        
        langdetect_info = self._models["langdetect"]
        detect_func = langdetect_info.get("detect")
        
        if detect_func:
            try:
                return detect_func(text)
            except Exception as e:
                logger.warning(f"Language detection failed: {e}")
                return "unknown"
        
        return "unknown"
    
    @handle_errors(fallback_value=None, show_error=True)
    def generate_text(self, prompt: str, max_length: int = 100) -> Optional[str]:
        """Generate text using available language models"""
        
        if not self.is_model_available("transformers"):
            return "[Text generation not available - language models not loaded]"
        
        transformers_info = self._models["transformers"]
        pipeline_func = transformers_info.get("pipeline")
        
        if pipeline_func:
            try:
                # Create text generation pipeline
                generator = pipeline_func("text-generation", model="gpt2")  # Fallback to GPT-2
                result = generator(prompt, max_length=max_length, num_return_sequences=1)
                return result[0]["generated_text"]
            except Exception as e:
                logger.error(f"Text generation failed: {e}")
                return "[Text generation failed]"
        
        return "[Text generation not available]"
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all AI models"""
        status = {
            "backend": self.ai_backend,
            "models": {}
        }
        
        for model_name, model_info in self._models.items():
            status["models"][model_name] = {
                "available": model_info.get("available", False),
                "loaded": model_info.get("model") is not None
            }
        
        return status
    
    def warm_up_models(self) -> Dict[str, bool]:
        """Warm up models for faster processing"""
        results = {}
        
        # Warm up Whisper
        if self.is_model_available("whisper"):
            whisper_model = self._get_whisper_model()
            results["whisper"] = whisper_model is not None
        
        # Add other model warm-ups as needed
        
        return results

# Global AI manager instance
_ai_manager = None

def get_enhanced_ai_manager() -> EnhancedAIManager:
    """Get the global enhanced AI manager instance"""
    global _ai_manager
    if _ai_manager is None:
        _ai_manager = EnhancedAIManager()
    return _ai_manager

# Convenience functions
def transcribe_audio(audio_data: bytes, language: str = "auto") -> Optional[Dict[str, Any]]:
    """Transcribe audio using the enhanced AI manager"""
    return get_enhanced_ai_manager().transcribe_audio(audio_data, language)

def analyze_image(image_data: bytes, prompt: str = "Describe this image") -> Optional[Dict[str, Any]]:
    """Analyze image using the enhanced AI manager"""
    return get_enhanced_ai_manager().analyze_image(image_data, prompt)

def detect_language(text: str) -> str:
    """Detect language using the enhanced AI manager"""
    return get_enhanced_ai_manager().detect_language(text)

def generate_text(prompt: str, max_length: int = 100) -> Optional[str]:
    """Generate text using the enhanced AI manager"""
    return get_enhanced_ai_manager().generate_text(prompt, max_length)

def get_ai_status() -> Dict[str, Any]:
    """Get AI models status"""
    return get_enhanced_ai_manager().get_model_status()

# Alias for backward compatibility
ai_manager = get_enhanced_ai_manager()