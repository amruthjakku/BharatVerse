"""
Enhanced AI Models for BharatVerse - Latest Open Source Models
Using state-of-the-art models for real cultural heritage preservation
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

# Core ML libraries
try:
    import torch
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    from transformers import (
        pipeline, 
        AutoTokenizer, 
        AutoModelForSequenceClassification,
        AutoModelForCausalLM,
        AutoProcessor,
        Qwen2VLForConditionalGeneration,
        BlipProcessor, 
        BlipForConditionalGeneration,
        WhisperProcessor,
        WhisperForConditionalGeneration,
        AutoFeatureExtractor,
        Wav2Vec2ForCTC,
        Wav2Vec2Processor
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from langdetect import detect, detect_langs
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

try:
    import librosa
    import soundfile as sf
    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class AdvancedWhisperTranscriber:
    """Advanced Whisper-based transcription with latest models"""
    
    def __init__(self, model_size: str = "large-v3"):
        self.model = None
        self.processor = None
        self.model_size = model_size
        self._load_model()
    
    def _load_model(self):
        """Load latest Whisper model"""
        if not WHISPER_AVAILABLE or not TRANSFORMERS_AVAILABLE:
            logger.warning("Whisper/Transformers not available")
            return
        
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            # Use OpenAI Whisper for best performance
            self.model = whisper.load_model(self.model_size)
            logger.info("Advanced Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            # Fallback to smaller model
            try:
                self.model = whisper.load_model("base")
                logger.info("Loaded fallback Whisper base model")
            except:
                logger.error("Failed to load any Whisper model")
    
    def transcribe(self, audio_data: Union[bytes, str, np.ndarray], language: str = None) -> Dict[str, Any]:
        """Advanced transcription with cultural context awareness"""
        if not self.model:
            return {
                "success": False,
                "error": "Whisper model not available",
                "transcription": "",
                "language": "unknown"
            }
        
        try:
            # Handle different input types
            if isinstance(audio_data, bytes):
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    tmp_file.write(audio_data)
                    audio_path = tmp_file.name
            elif isinstance(audio_data, str):
                audio_path = audio_data
            else:
                # numpy array
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    sf.write(tmp_file.name, audio_data, 16000)
                    audio_path = tmp_file.name
            
            # Transcribe with advanced options
            result = self.model.transcribe(
                audio_path,
                language=language.lower() if language and language != "Auto-detect" else None,
                task="transcribe",
                verbose=False,
                word_timestamps=True,
                condition_on_previous_text=True,
                temperature=0.0,
                compression_ratio_threshold=2.4,
                logprob_threshold=-1.0,
                no_speech_threshold=0.6
            )
            
            # Extract detailed information
            segments = []
            for segment in result.get("segments", []):
                segments.append({
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0),
                    "text": segment.get("text", "").strip(),
                    "confidence": segment.get("avg_logprob", 0),
                    "words": segment.get("words", [])
                })
            
            # Clean up temporary file
            if isinstance(audio_data, (bytes, np.ndarray)):
                os.unlink(audio_path)
            
            return {
                "success": True,
                "transcription": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "duration": result.get("duration", 0),
                "segments": segments,
                "confidence": np.mean([seg.get("confidence", 0) for seg in segments]) if segments else 0,
                "word_count": len(result["text"].split()),
                "detected_language_probability": result.get("language_probability", 0)
            }
            
        except Exception as e:
            logger.error(f"Advanced transcription failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcription": "",
                "language": "unknown"
            }


class CulturalTextAnalyzer:
    """Advanced text analysis with cultural context understanding"""
    
    def __init__(self):
        self.sentiment_analyzer = None
        self.emotion_analyzer = None
        self.cultural_classifier = None
        self.language_detector = None
        self.summarizer = None
        self.translator = None
        self._load_models()
    
    def _load_models(self):
        """Load latest text analysis models"""
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Transformers not available for text analysis")
            return
        
        try:
            # Latest multilingual sentiment analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Emotion analysis
            self.emotion_analyzer = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Summarization
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Translation
            self.translator = pipeline(
                "translation",
                model="facebook/nllb-200-distilled-600M",
                device=0 if torch.cuda.is_available() else -1
            )
            
            logger.info("Advanced text analysis models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load text analysis models: {e}")
    
    def analyze_text(self, text: str, language: str = "auto") -> Dict[str, Any]:
        """Comprehensive text analysis with cultural insights"""
        try:
            analysis = {
                "success": True,
                "text": text,
                "language": self._detect_language(text),
                "length": len(text),
                "word_count": len(text.split()),
                "sentence_count": len([s for s in text.split('.') if s.strip()]),
                "timestamp": datetime.now().isoformat()
            }
            
            # Sentiment analysis
            if self.sentiment_analyzer:
                sentiment = self._analyze_sentiment(text)
                analysis["sentiment"] = sentiment
            
            # Emotion analysis
            if self.emotion_analyzer:
                emotions = self._analyze_emotions(text)
                analysis["emotions"] = emotions
            
            # Cultural context detection
            cultural_elements = self._detect_cultural_elements(text)
            analysis["cultural_elements"] = cultural_elements
            
            # Text quality metrics
            quality_metrics = self._calculate_quality_metrics(text)
            analysis["quality_metrics"] = quality_metrics
            
            # Generate summary if text is long enough
            if len(text.split()) > 50 and self.summarizer:
                summary = self._generate_summary(text)
                analysis["summary"] = summary
            
            # Extract key themes and topics
            themes = self._extract_themes(text)
            analysis["themes"] = themes
            
            return analysis
            
        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": text
            }
    
    def _detect_language(self, text: str) -> str:
        """Enhanced language detection"""
        if not LANGDETECT_AVAILABLE:
            return "unknown"
        
        try:
            detected = detect_langs(text)
            if detected:
                return detected[0].lang
        except:
            pass
        return "unknown"
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Advanced sentiment analysis"""
        if not self.sentiment_analyzer:
            return {"label": "NEUTRAL", "score": 0.5}
        
        try:
            results = self.sentiment_analyzer(text)
            return {
                "label": results[0]["label"],
                "score": results[0]["score"],
                "confidence": results[0]["score"]
            }
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"label": "NEUTRAL", "score": 0.5}
    
    def _analyze_emotions(self, text: str) -> Dict[str, Any]:
        """Emotion detection in text"""
        if not self.emotion_analyzer:
            return {"primary_emotion": "neutral", "confidence": 0.5}
        
        try:
            results = self.emotion_analyzer(text)
            return {
                "primary_emotion": results[0]["label"],
                "confidence": results[0]["score"],
                "all_emotions": results
            }
        except Exception as e:
            logger.error(f"Emotion analysis failed: {e}")
            return {"primary_emotion": "neutral", "confidence": 0.5}
    
    def _detect_cultural_elements(self, text: str) -> List[str]:
        """Detect cultural elements in text"""
        cultural_keywords = {
            "festivals": ["diwali", "holi", "eid", "christmas", "dussehra", "navratri", "karva chauth", "raksha bandhan"],
            "food": ["biryani", "curry", "dal", "roti", "chapati", "samosa", "dosa", "idli", "vada"],
            "music": ["raga", "tabla", "sitar", "harmonium", "classical", "folk", "bhajan", "qawwali"],
            "dance": ["bharatanatyam", "kathak", "odissi", "kuchipudi", "manipuri", "mohiniyattam", "bhangra"],
            "religion": ["temple", "mosque", "church", "gurdwara", "prayer", "worship", "ritual", "ceremony"],
            "family": ["joint family", "elder", "respect", "tradition", "custom", "heritage"],
            "clothing": ["saree", "dhoti", "kurta", "lehenga", "salwar", "turban", "traditional dress"]
        }
        
        detected_elements = []
        text_lower = text.lower()
        
        for category, keywords in cultural_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected_elements.append(f"{category}:{keyword}")
        
        return detected_elements
    
    def _calculate_quality_metrics(self, text: str) -> Dict[str, Any]:
        """Calculate text quality and readability metrics"""
        words = text.split()
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        avg_words_per_sentence = len(words) / max(len(sentences), 1)
        avg_chars_per_word = sum(len(word) for word in words) / max(len(words), 1)
        
        # Simple readability score
        readability_score = max(0, min(100, 100 - (avg_words_per_sentence * 2) - (avg_chars_per_word * 5)))
        
        return {
            "readability_score": readability_score,
            "avg_words_per_sentence": avg_words_per_sentence,
            "avg_chars_per_word": avg_chars_per_word,
            "complexity": "simple" if readability_score > 70 else "moderate" if readability_score > 40 else "complex"
        }
    
    def _generate_summary(self, text: str) -> str:
        """Generate text summary"""
        if not self.summarizer:
            return text[:200] + "..." if len(text) > 200 else text
        
        try:
            # Limit input length for summarization
            max_length = min(1024, len(text))
            summary = self.summarizer(text[:max_length], max_length=150, min_length=30, do_sample=False)
            return summary[0]["summary_text"]
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return text[:200] + "..." if len(text) > 200 else text
    
    def _extract_themes(self, text: str) -> List[str]:
        """Extract key themes from text"""
        # Simple keyword-based theme extraction
        theme_keywords = {
            "tradition": ["tradition", "custom", "heritage", "ancestral", "ancient", "old"],
            "family": ["family", "mother", "father", "grandmother", "grandfather", "children"],
            "celebration": ["festival", "celebration", "joy", "happiness", "gathering", "ceremony"],
            "spirituality": ["god", "prayer", "worship", "divine", "sacred", "holy", "spiritual"],
            "community": ["community", "village", "neighborhood", "together", "unity", "collective"],
            "nature": ["nature", "earth", "water", "fire", "air", "tree", "river", "mountain"]
        }
        
        detected_themes = []
        text_lower = text.lower()
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_themes.append(theme)
        
        return detected_themes
    
    def translate_text(self, text: str, target_language: str = "en") -> Dict[str, Any]:
        """Advanced translation with cultural context preservation"""
        if not self.translator:
            return {
                "success": False,
                "error": "Translation model not available",
                "translation": text
            }
        
        try:
            # Map language codes
            lang_map = {
                "hindi": "hin_Deva",
                "bengali": "ben_Beng", 
                "tamil": "tam_Taml",
                "telugu": "tel_Telu",
                "marathi": "mar_Deva",
                "gujarati": "guj_Gujr",
                "kannada": "kan_Knda",
                "malayalam": "mal_Mlym",
                "punjabi": "pan_Guru",
                "english": "eng_Latn"
            }
            
            target_code = lang_map.get(target_language.lower(), "eng_Latn")
            
            translation = self.translator(text, tgt_lang=target_code)
            
            return {
                "success": True,
                "translation": translation[0]["translation_text"],
                "target_language": target_language,
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "translation": text
            }


class AdvancedImageAnalyzer:
    """Advanced image analysis with cultural heritage focus"""
    
    def __init__(self):
        self.captioner = None
        self.cultural_classifier = None
        self.object_detector = None
        self._load_models()
    
    def _load_models(self):
        """Load latest vision models"""
        if not TRANSFORMERS_AVAILABLE or not PIL_AVAILABLE:
            logger.warning("Vision models not available")
            return
        
        try:
            # Latest image captioning model
            self.captioner = pipeline(
                "image-to-text",
                model="Salesforce/blip2-opt-2.7b",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Object detection
            self.object_detector = pipeline(
                "object-detection",
                model="facebook/detr-resnet-50",
                device=0 if torch.cuda.is_available() else -1
            )
            
            logger.info("Advanced vision models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load vision models: {e}")
    
    def analyze_image(self, image_data: Union[bytes, str, Image.Image]) -> Dict[str, Any]:
        """Comprehensive image analysis with cultural context"""
        try:
            # Load image
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            elif isinstance(image_data, str):
                image = Image.open(image_data)
            else:
                image = image_data
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            analysis = {
                "success": True,
                "image_size": image.size,
                "image_mode": image.mode,
                "timestamp": datetime.now().isoformat()
            }
            
            # Generate caption
            if self.captioner:
                caption = self._generate_caption(image)
                analysis["caption"] = caption
            
            # Detect objects
            if self.object_detector:
                objects = self._detect_objects(image)
                analysis["objects"] = objects
            
            # Detect cultural elements
            cultural_elements = self._detect_cultural_elements_in_image(image, analysis.get("caption", ""))
            analysis["cultural_elements"] = cultural_elements
            
            # Image quality assessment
            quality_metrics = self._assess_image_quality(image)
            analysis["quality_metrics"] = quality_metrics
            
            return analysis
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_caption(self, image: Image.Image) -> str:
        """Generate detailed image caption"""
        if not self.captioner:
            return "Image caption not available"
        
        try:
            result = self.captioner(image)
            return result[0]["generated_text"]
        except Exception as e:
            logger.error(f"Caption generation failed: {e}")
            return "Caption generation failed"
    
    def _detect_objects(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Detect objects in image"""
        if not self.object_detector:
            return []
        
        try:
            results = self.object_detector(image)
            objects = []
            for obj in results:
                objects.append({
                    "label": obj["label"],
                    "confidence": obj["score"],
                    "box": obj["box"]
                })
            return objects
        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            return []
    
    def _detect_cultural_elements_in_image(self, image: Image.Image, caption: str) -> List[str]:
        """Detect cultural elements in image based on caption and visual analysis"""
        cultural_indicators = [
            "temple", "mosque", "church", "traditional", "festival", "ceremony",
            "sari", "dhoti", "turban", "jewelry", "ornament", "decoration",
            "dance", "music", "instrument", "art", "craft", "painting",
            "food", "cooking", "kitchen", "spices", "traditional dress",
            "ritual", "worship", "prayer", "celebration", "gathering"
        ]
        
        detected_elements = []
        caption_lower = caption.lower()
        
        for indicator in cultural_indicators:
            if indicator in caption_lower:
                detected_elements.append(indicator)
        
        return detected_elements
    
    def _assess_image_quality(self, image: Image.Image) -> Dict[str, Any]:
        """Assess image quality metrics"""
        # Convert to numpy array for analysis
        img_array = np.array(image)
        
        # Calculate basic quality metrics
        brightness = np.mean(img_array)
        contrast = np.std(img_array)
        
        # Simple quality score
        quality_score = min(100, (brightness / 255 * 50) + (contrast / 128 * 50))
        
        return {
            "brightness": float(brightness),
            "contrast": float(contrast),
            "quality_score": float(quality_score),
            "resolution": f"{image.size[0]}x{image.size[1]}",
            "aspect_ratio": round(image.size[0] / image.size[1], 2)
        }


class EnhancedAIManager:
    """Enhanced AI Manager with latest models and real-time tracking"""
    
    def __init__(self):
        self.whisper_model = AdvancedWhisperTranscriber()
        self.text_processor = CulturalTextAnalyzer()
        self.image_captioner = AdvancedImageAnalyzer()
        
        # Import tracker
        try:
            from core.ai_tracker import ai_tracker
            self.tracker = ai_tracker
        except ImportError:
            self.tracker = None
            logger.warning("AI tracker not available")
        
        logger.info("Enhanced AI Manager initialized with latest models")
    
    def transcribe_audio(self, audio_path: str, language: str = None) -> Dict[str, Any]:
        """Transcribe audio with advanced features and tracking"""
        start_time = time.time()
        result = self.whisper_model.transcribe(audio_path, language)
        processing_time = time.time() - start_time
        
        # Track the operation
        if self.tracker:
            self.tracker.track_transcription(result, processing_time)
        
        return result
    
    def analyze_text(self, text: str, language: str = "auto") -> Dict[str, Any]:
        """Analyze text with cultural context and tracking"""
        start_time = time.time()
        result = self.text_processor.analyze_text(text, language)
        processing_time = time.time() - start_time
        
        # Track the operation
        if self.tracker:
            self.tracker.track_text_analysis(result, processing_time)
        
        return result
    
    def translate_text(self, text: str, target_language: str = "en") -> Dict[str, Any]:
        """Translate text preserving cultural context with tracking"""
        start_time = time.time()
        result = self.text_processor.translate_text(text, target_language)
        processing_time = time.time() - start_time
        
        # Track the operation
        if self.tracker:
            # Detect source language
            source_lang = self.text_processor._detect_language(text)
            self.tracker.track_translation(result, source_lang, target_language, processing_time)
        
        return result
    
    def caption_image(self, image_path: str) -> Dict[str, Any]:
        """Generate image caption with cultural analysis and tracking"""
        start_time = time.time()
        result = self.image_captioner.analyze_image(image_path)
        processing_time = time.time() - start_time
        
        # Track the operation
        if self.tracker:
            self.tracker.track_image_analysis(result, processing_time)
        
        return result
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        base_info = {
            "whisper_available": self.whisper_model.model is not None,
            "text_analysis_available": self.text_processor.sentiment_analyzer is not None,
            "image_analysis_available": self.image_captioner.captioner is not None,
            "models": {
                "whisper": "large-v3" if self.whisper_model.model else "not available",
                "sentiment": "twitter-xlm-roberta-base-sentiment",
                "emotion": "emotion-english-distilroberta-base", 
                "translation": "nllb-200-distilled-600M",
                "image_caption": "blip2-opt-2.7b",
                "object_detection": "detr-resnet-50"
            }
        }
        
        # Add real-time analytics if tracker is available
        if self.tracker:
            analytics = self.tracker.get_comprehensive_analytics()
            base_info.update({
                "real_time_analytics": analytics,
                "tracking_enabled": True
            })
        else:
            base_info["tracking_enabled"] = False
        
        return base_info
    
    def get_real_time_analytics(self) -> Dict[str, Any]:
        """Get real-time AI processing analytics"""
        if self.tracker:
            return self.tracker.get_comprehensive_analytics()
        else:
            return {"error": "AI tracking not available"}
    
    def get_cultural_insights(self) -> Dict[str, Any]:
        """Get cultural insights from AI processing"""
        if self.tracker:
            return self.tracker.get_cultural_insights()
        else:
            return {"error": "AI tracking not available"}
    
    def save_analytics(self):
        """Save analytics data"""
        if self.tracker:
            self.tracker.save_data()


# Global instance
ai_manager = EnhancedAIManager()