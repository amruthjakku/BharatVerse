"""
Enhanced AI Models for BharatVerse
Real implementations of Whisper, text analysis, and image processing
"""

import os
import io
import json
import logging
import tempfile
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
        MarianMTModel, 
        MarianTokenizer,
        BlipProcessor, 
        BlipForConditionalGeneration
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


class WhisperTranscriber:
    """Real Whisper-based audio transcription"""
    
    def __init__(self, model_size: str = "base"):
        self.model = None
        self.model_size = model_size
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model"""
        if not WHISPER_AVAILABLE:
            logger.warning("Whisper not available. Install with: pip install openai-whisper")
            return
        
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
    
    def transcribe(self, audio_data: Union[bytes, str, np.ndarray], language: str = None) -> Dict[str, Any]:
        """Transcribe audio to text"""
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
                # Save bytes to temporary file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    tmp_file.write(audio_data)
                    audio_path = tmp_file.name
            elif isinstance(audio_data, str):
                # File path
                audio_path = audio_data
            elif isinstance(audio_data, np.ndarray):
                # NumPy array - save to temporary file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    sf.write(tmp_file.name, audio_data, 22050)
                    audio_path = tmp_file.name
            else:
                raise ValueError("Unsupported audio data type")
            
            # Transcribe
            options = {"language": language} if language else {}
            result = self.model.transcribe(audio_path, **options)
            
            # Clean up temporary file if created
            if isinstance(audio_data, (bytes, np.ndarray)):
                os.unlink(audio_path)
            
            return {
                "success": True,
                "transcription": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", []),
                "confidence": self._calculate_confidence(result.get("segments", []))
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcription": "",
                "language": "unknown"
            }
    
    def _calculate_confidence(self, segments: List[Dict]) -> float:
        """Calculate average confidence from segments"""
        if not segments:
            return 0.0
        
        confidences = []
        for segment in segments:
            if 'avg_logprob' in segment:
                # Convert log probability to confidence (0-1)
                confidence = np.exp(segment['avg_logprob'])
                confidences.append(confidence)
        
        return float(np.mean(confidences)) if confidences else 0.0


class TextAnalyzer:
    """Advanced text analysis with sentiment, language detection, and translation"""
    
    def __init__(self):
        self.sentiment_analyzer = None
        self.translator_models = {}
        self.language_detector = None
        self._load_models()
    
    def _load_models(self):
        """Load text analysis models"""
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Transformers not available. Install with: pip install transformers torch")
            return
        
        try:
            # Sentiment analysis
            logger.info("Loading sentiment analysis model...")
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            # Language detection
            if LANGDETECT_AVAILABLE:
                logger.info("Language detection available")
            
            logger.info("Text analysis models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load text analysis models: {e}")
    
    def analyze_text(self, text: str, language: str = None) -> Dict[str, Any]:
        """Comprehensive text analysis"""
        try:
            result = {
                "success": True,
                "text": text,
                "word_count": len(text.split()),
                "character_count": len(text),
                "language": language or self._detect_language(text),
                "sentiment": self._analyze_sentiment(text),
                "readability": self._calculate_readability(text),
                "keywords": self._extract_keywords(text),
                "cultural_indicators": self._detect_cultural_indicators(text)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": text
            }
    
    def translate_text(self, text: str, source_lang: str, target_lang: str = "en") -> Dict[str, Any]:
        """Translate text between languages"""
        if not TRANSFORMERS_AVAILABLE:
            return {
                "success": False,
                "error": "Translation models not available",
                "translation": text
            }
        
        try:
            # Load translation model if not cached
            model_name = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"
            
            if model_name not in self.translator_models:
                try:
                    tokenizer = MarianTokenizer.from_pretrained(model_name)
                    model = MarianMTModel.from_pretrained(model_name)
                    self.translator_models[model_name] = (tokenizer, model)
                except Exception:
                    # Fallback to generic multilingual model
                    logger.warning(f"Specific model {model_name} not found, using generic translator")
                    translator = pipeline("translation", model="Helsinki-NLP/opus-mt-mul-en")
                    translation = translator(text)[0]['translation_text']
                    return {
                        "success": True,
                        "translation": translation,
                        "source_language": source_lang,
                        "target_language": target_lang,
                        "confidence": 0.8
                    }
            
            tokenizer, model = self.translator_models[model_name]
            
            # Translate
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            translated = model.generate(**inputs, max_length=512, num_beams=4, early_stopping=True)
            translation = tokenizer.decode(translated[0], skip_special_tokens=True)
            
            return {
                "success": True,
                "translation": translation,
                "source_language": source_lang,
                "target_language": target_lang,
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "translation": text
            }
    
    def _detect_language(self, text: str) -> str:
        """Detect text language"""
        if not LANGDETECT_AVAILABLE:
            return "unknown"
        
        try:
            return detect(text)
        except:
            return "unknown"
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze text sentiment"""
        if not self.sentiment_analyzer:
            return {"label": "NEUTRAL", "score": 0.5}
        
        try:
            results = self.sentiment_analyzer(text)
            # Get the highest scoring sentiment
            best_result = max(results[0], key=lambda x: x['score'])
            return {
                "label": best_result['label'],
                "score": best_result['score'],
                "all_scores": results[0]
            }
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"label": "NEUTRAL", "score": 0.5}
    
    def _calculate_readability(self, text: str) -> Dict[str, Any]:
        """Calculate text readability metrics"""
        words = text.split()
        sentences = text.split('.')
        
        avg_words_per_sentence = len(words) / max(len(sentences), 1)
        avg_chars_per_word = sum(len(word) for word in words) / max(len(words), 1)
        
        # Simple readability score (0-100, higher = easier)
        readability_score = max(0, min(100, 100 - (avg_words_per_sentence * 2) - (avg_chars_per_word * 5)))
        
        return {
            "score": readability_score,
            "avg_words_per_sentence": avg_words_per_sentence,
            "avg_chars_per_word": avg_chars_per_word,
            "difficulty": "Easy" if readability_score > 70 else "Medium" if readability_score > 40 else "Hard"
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction based on word frequency
        words = text.lower().split()
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Count word frequencies
        word_freq = {}
        for word in words:
            word = word.strip('.,!?";()[]{}')
            if len(word) > 2 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top keywords
        return sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True)[:10]
    
    def _detect_cultural_indicators(self, text: str) -> List[str]:
        """Detect cultural indicators in text"""
        cultural_keywords = {
            'festivals': ['diwali', 'holi', 'eid', 'christmas', 'dussehra', 'navratri', 'karva chauth', 'raksha bandhan'],
            'food': ['curry', 'dal', 'rice', 'roti', 'biryani', 'samosa', 'dosa', 'idli', 'vada', 'lassi'],
            'music': ['raga', 'tabla', 'sitar', 'harmonium', 'classical', 'folk', 'bhajan', 'qawwali'],
            'dance': ['bharatanatyam', 'kathak', 'odissi', 'kuchipudi', 'manipuri', 'mohiniyattam', 'bhangra'],
            'religion': ['temple', 'mosque', 'church', 'gurudwara', 'prayer', 'meditation', 'yoga', 'mantra'],
            'family': ['mother', 'father', 'grandmother', 'grandfather', 'uncle', 'aunt', 'cousin', 'family']
        }
        
        text_lower = text.lower()
        indicators = []
        
        for category, keywords in cultural_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    indicators.append(f"{category}:{keyword}")
        
        return indicators


class ImageAnalyzer:
    """Image analysis and captioning"""
    
    def __init__(self):
        self.captioning_model = None
        self.processor = None
        self._load_models()
    
    def _load_models(self):
        """Load image analysis models"""
        if not TRANSFORMERS_AVAILABLE or not PIL_AVAILABLE:
            logger.warning("Image analysis dependencies not available")
            return
        
        try:
            logger.info("Loading image captioning model...")
            self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.captioning_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            logger.info("Image analysis models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load image analysis models: {e}")
    
    def analyze_image(self, image_data: Union[bytes, str, Image.Image]) -> Dict[str, Any]:
        """Analyze image and generate caption"""
        if not self.captioning_model:
            return {
                "success": False,
                "error": "Image analysis models not available",
                "caption": "Image analysis not available"
            }
        
        try:
            # Handle different input types
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            elif isinstance(image_data, str):
                image = Image.open(image_data)
            elif isinstance(image_data, Image.Image):
                image = image_data
            else:
                raise ValueError("Unsupported image data type")
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Generate caption
            inputs = self.processor(image, return_tensors="pt")
            out = self.captioning_model.generate(**inputs, max_length=50, num_beams=5)
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            
            # Analyze image properties
            width, height = image.size
            aspect_ratio = width / height
            
            # Detect cultural elements in the image (basic keyword matching)
            cultural_elements = self._detect_cultural_elements(caption)
            
            return {
                "success": True,
                "caption": caption,
                "dimensions": {"width": width, "height": height},
                "aspect_ratio": aspect_ratio,
                "cultural_elements": cultural_elements,
                "analysis": {
                    "dominant_colors": self._get_dominant_colors(image),
                    "brightness": self._calculate_brightness(image),
                    "complexity": self._calculate_complexity(image)
                }
            }
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "caption": "Failed to analyze image"
            }
    
    def _detect_cultural_elements(self, caption: str) -> List[str]:
        """Detect cultural elements from image caption"""
        cultural_keywords = [
            'temple', 'mosque', 'church', 'festival', 'traditional', 'cultural',
            'dance', 'music', 'art', 'sculpture', 'painting', 'architecture',
            'food', 'cooking', 'ceremony', 'ritual', 'celebration', 'costume',
            'jewelry', 'decoration', 'pattern', 'design', 'craft', 'handmade'
        ]
        
        caption_lower = caption.lower()
        detected = []
        
        for keyword in cultural_keywords:
            if keyword in caption_lower:
                detected.append(keyword)
        
        return detected
    
    def _get_dominant_colors(self, image: Image.Image) -> List[str]:
        """Get dominant colors from image"""
        # Resize image for faster processing
        image_small = image.resize((50, 50))
        
        # Get color histogram
        colors = image_small.getcolors(maxcolors=256*256*256)
        if not colors:
            return ["unknown"]
        
        # Sort by frequency and get top colors
        colors.sort(key=lambda x: x[0], reverse=True)
        
        # Convert RGB to color names (simplified)
        color_names = []
        for count, rgb in colors[:3]:
            r, g, b = rgb
            if r > 200 and g > 200 and b > 200:
                color_names.append("white")
            elif r < 50 and g < 50 and b < 50:
                color_names.append("black")
            elif r > g and r > b:
                color_names.append("red")
            elif g > r and g > b:
                color_names.append("green")
            elif b > r and b > g:
                color_names.append("blue")
            elif r > 150 and g > 150:
                color_names.append("yellow")
            else:
                color_names.append("mixed")
        
        return list(set(color_names))
    
    def _calculate_brightness(self, image: Image.Image) -> float:
        """Calculate average brightness of image"""
        grayscale = image.convert('L')
        pixels = list(grayscale.getdata())
        return sum(pixels) / len(pixels) / 255.0
    
    def _calculate_complexity(self, image: Image.Image) -> float:
        """Calculate image complexity (0-1, higher = more complex)"""
        # Convert to grayscale and calculate edge density
        grayscale = image.convert('L')
        pixels = np.array(grayscale)
        
        # Simple edge detection using gradient
        grad_x = np.abs(np.diff(pixels, axis=1))
        grad_y = np.abs(np.diff(pixels, axis=0))
        
        edge_density = (np.sum(grad_x) + np.sum(grad_y)) / (pixels.shape[0] * pixels.shape[1])
        
        # Normalize to 0-1 range
        return min(1.0, edge_density / 50.0)


class AIManager:
    """Main AI manager that coordinates all AI models"""
    
    def __init__(self):
        self.whisper = WhisperTranscriber()
        self.text_analyzer = TextAnalyzer()
        self.image_analyzer = ImageAnalyzer()
        
        logger.info("AI Manager initialized")
    
    def get_model_status(self) -> Dict[str, bool]:
        """Get status of all AI models"""
        return {
            "whisper": self.whisper.model is not None,
            "text_analyzer": self.text_analyzer.sentiment_analyzer is not None,
            "image_analyzer": self.image_analyzer.captioning_model is not None,
            "dependencies": {
                "whisper": WHISPER_AVAILABLE,
                "transformers": TRANSFORMERS_AVAILABLE,
                "langdetect": LANGDETECT_AVAILABLE,
                "audio_processing": AUDIO_PROCESSING_AVAILABLE,
                "pil": PIL_AVAILABLE
            }
        }
    
    def process_audio(self, audio_data: Union[bytes, str, np.ndarray], language: str = None, translate: bool = False) -> Dict[str, Any]:
        """Process audio with transcription and optional translation"""
        # Transcribe
        transcription_result = self.whisper.transcribe(audio_data, language)
        
        if not transcription_result["success"]:
            return transcription_result
        
        result = transcription_result.copy()
        
        # Analyze transcribed text
        if transcription_result["transcription"]:
            text_analysis = self.text_analyzer.analyze_text(
                transcription_result["transcription"],
                transcription_result["language"]
            )
            result["text_analysis"] = text_analysis
            
            # Translate if requested
            if translate and transcription_result["language"] != "en":
                translation_result = self.text_analyzer.translate_text(
                    transcription_result["transcription"],
                    transcription_result["language"],
                    "en"
                )
                result["translation"] = translation_result
        
        return result
    
    def process_text(self, text: str, language: str = None, translate: bool = False) -> Dict[str, Any]:
        """Process text with analysis and optional translation"""
        # Analyze text
        analysis_result = self.text_analyzer.analyze_text(text, language)
        
        if not analysis_result["success"]:
            return analysis_result
        
        result = analysis_result.copy()
        
        # Translate if requested
        if translate and analysis_result["language"] != "en":
            translation_result = self.text_analyzer.translate_text(
                text,
                analysis_result["language"],
                "en"
            )
            result["translation"] = translation_result
        
        return result
    
    def process_image(self, image_data: Union[bytes, str, Image.Image]) -> Dict[str, Any]:
        """Process image with analysis and captioning"""
        return self.image_analyzer.analyze_image(image_data)


# Global AI manager instance
ai_manager = AIManager()