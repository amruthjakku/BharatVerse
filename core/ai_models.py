"""
AI Models Manager for BharatVerse
Handles Whisper (audio), Transformers (text), and BLIP (image) models
"""

import os
import logging
from typing import Optional, Dict, Any, List, Tuple
import numpy as np
from PIL import Image
import torch
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Configure logging
logger = logging.getLogger(__name__)

# Check for GPU availability
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {DEVICE}")


class WhisperModel:
    """OpenAI Whisper for audio transcription"""
    
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model"""
        try:
            import whisper
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size, device=DEVICE)
            logger.info("Whisper model loaded successfully")
        except ImportError:
            logger.error("Whisper not installed. Install with: pip install openai-whisper")
            raise
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe audio file"""
        if not self.model:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            # Transcribe audio
            result = self.model.transcribe(
                audio_path,
                language=language,
                task="transcribe",
                verbose=False
            )
            
            return {
                "text": result["text"],
                "language": result.get("language", language),
                "segments": result.get("segments", []),
                "duration": result.get("duration", 0)
            }
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    def translate(self, audio_path: str, source_language: Optional[str] = None) -> Dict[str, Any]:
        """Translate audio to English"""
        if not self.model:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            result = self.model.transcribe(
                audio_path,
                language=source_language,
                task="translate",
                verbose=False
            )
            
            return {
                "text": result["text"],
                "source_language": result.get("language", source_language),
                "segments": result.get("segments", [])
            }
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise


class TextProcessor:
    """Multilingual text processing using Transformers"""
    
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.translator = None
        self._load_models()
    
    def _load_models(self):
        """Load text processing models"""
        try:
            from transformers import (
                AutoTokenizer,
                AutoModelForSequenceClassification,
                pipeline
            )
            
            # Load multilingual BERT for text analysis
            model_name = "bert-base-multilingual-cased"
            logger.info(f"Loading text model: {model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                num_labels=2
            ).to(DEVICE)
            
            # Load translation pipeline for Indian languages
            logger.info("Loading translation pipeline")
            self.translator = pipeline(
                "translation",
                model="Helsinki-NLP/opus-mt-mul-en",
                device=0 if DEVICE == "cuda" else -1
            )
            
            logger.info("Text processing models loaded successfully")
            
        except ImportError:
            logger.error("Transformers not installed. Install with: pip install transformers")
            raise
        except Exception as e:
            logger.error(f"Failed to load text models: {e}")
            raise
    
    def analyze_text(self, text: str, language: str = "auto") -> Dict[str, Any]:
        """Analyze text for various attributes"""
        try:
            # Basic analysis
            word_count = len(text.split())
            char_count = len(text)
            
            # Language detection
            if language == "auto":
                from langdetect import detect
                try:
                    detected_lang = detect(text)
                except:
                    detected_lang = "unknown"
            else:
                detected_lang = language
            
            # Sentiment analysis (simplified)
            inputs = self.tokenizer(
                text,
                truncation=True,
                padding=True,
                max_length=512,
                return_tensors="pt"
            ).to(DEVICE)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                sentiment_score = torch.nn.functional.softmax(outputs.logits, dim=-1)
                sentiment = "positive" if sentiment_score[0][1] > 0.5 else "negative"
                confidence = float(torch.max(sentiment_score).item())
            
            return {
                "word_count": word_count,
                "char_count": char_count,
                "language": detected_lang,
                "sentiment": sentiment,
                "sentiment_confidence": confidence,
                "cultural_significance": self._estimate_cultural_significance(text, detected_lang)
            }
            
        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            return {
                "word_count": len(text.split()),
                "char_count": len(text),
                "language": "unknown",
                "error": str(e)
            }
    
    def translate_text(self, text: str, source_lang: str = "auto", target_lang: str = "en") -> str:
        """Translate text to target language"""
        try:
            if not self.translator:
                return text
            
            # Use the translation pipeline
            result = self.translator(text, max_length=512)
            return result[0]['translation_text']
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text
    
    def _estimate_cultural_significance(self, text: str, language: str) -> float:
        """Estimate cultural significance score (0-1)"""
        # Simple heuristic based on keywords
        cultural_keywords = {
            'en': ['tradition', 'culture', 'heritage', 'festival', 'ritual', 'folk', 'ancient'],
            'hi': ['परंपरा', 'संस्कृति', 'विरासत', 'त्योहार', 'रीति', 'लोक', 'प्राचीन'],
            'te': ['సంప్రదాయం', 'సంస్కృతి', 'వారసత్వం', 'పండుగ', 'ఆచారం', 'జానపద', 'ప్రాచీన'],
            'ta': ['பாரம்பரியம்', 'கலாச்சாரம்', 'பாரம்பரியம்', 'திருவிழா', 'சடங்கு', 'நாட்டுப்புற', 'பழமையான']
        }
        
        keywords = cultural_keywords.get(language[:2], cultural_keywords['en'])
        text_lower = text.lower()
        
        score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
        return min(score / len(keywords), 1.0)


class ImageCaptioner:
    """Image captioning using BLIP model"""
    
    def __init__(self):
        self.processor = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load BLIP model for image captioning"""
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            
            model_name = "Salesforce/blip-image-captioning-base"
            logger.info(f"Loading image captioning model: {model_name}")
            
            self.processor = BlipProcessor.from_pretrained(model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(model_name).to(DEVICE)
            
            logger.info("Image captioning model loaded successfully")
            
        except ImportError:
            logger.error("Transformers not installed. Install with: pip install transformers")
            raise
        except Exception as e:
            logger.error(f"Failed to load image captioning model: {e}")
            raise
    
    def generate_caption(self, image_path: str, max_length: int = 50) -> Dict[str, Any]:
        """Generate caption for image"""
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            
            # Generate caption
            inputs = self.processor(image, return_tensors="pt").to(DEVICE)
            
            with torch.no_grad():
                out = self.model.generate(**inputs, max_length=max_length)
                caption = self.processor.decode(out[0], skip_special_tokens=True)
            
            # Analyze image content
            analysis = self._analyze_image(image)
            
            return {
                "caption": caption,
                "image_analysis": analysis,
                "cultural_elements": self._detect_cultural_elements(caption)
            }
            
        except Exception as e:
            logger.error(f"Image captioning failed: {e}")
            raise
    
    def _analyze_image(self, image: Image.Image) -> Dict[str, Any]:
        """Basic image analysis"""
        # Convert to numpy array
        img_array = np.array(image)
        
        return {
            "width": image.width,
            "height": image.height,
            "aspect_ratio": round(image.width / image.height, 2),
            "dominant_colors": self._get_dominant_colors(img_array),
            "brightness": np.mean(img_array) / 255.0
        }
    
    def _get_dominant_colors(self, img_array: np.ndarray, n_colors: int = 3) -> List[Tuple[int, int, int]]:
        """Get dominant colors from image"""
        # Reshape image to list of pixels
        pixels = img_array.reshape(-1, 3)
        
        # Simple k-means clustering for dominant colors
        from sklearn.cluster import KMeans
        
        try:
            kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
            kmeans.fit(pixels)
            colors = kmeans.cluster_centers_.astype(int)
            return [tuple(color) for color in colors]
        except:
            # Fallback to average color
            avg_color = np.mean(pixels, axis=0).astype(int)
            return [tuple(avg_color)]
    
    def _detect_cultural_elements(self, caption: str) -> List[str]:
        """Detect cultural elements in caption"""
        cultural_items = [
            'temple', 'festival', 'traditional', 'costume', 'ritual',
            'ceremony', 'dance', 'music', 'art', 'craft', 'food',
            'sari', 'turban', 'jewelry', 'henna', 'rangoli'
        ]
        
        caption_lower = caption.lower()
        detected = [item for item in cultural_items if item in caption_lower]
        
        return detected


class AIModelManager:
    """Manages all AI models"""
    
    def __init__(self):
        self.whisper_model = None
        self.text_processor = None
        self.image_captioner = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize AI models based on configuration"""
        # Load models based on feature flags from environment
        from dotenv import load_dotenv
        load_dotenv()
        
        if os.getenv("ENABLE_AI_TRANSCRIPTION", "True") == "True":
            try:
                whisper_size = os.getenv("WHISPER_MODEL", "base")
                self.whisper_model = WhisperModel(model_size=whisper_size)
            except Exception as e:
                logger.warning(f"Failed to load Whisper model: {e}")
        
        if os.getenv("ENABLE_AI_TRANSLATION", "True") == "True":
            try:
                self.text_processor = TextProcessor()
            except Exception as e:
                logger.warning(f"Failed to load text processor: {e}")
        
        if os.getenv("ENABLE_IMAGE_CAPTIONING", "True") == "True":
            try:
                self.image_captioner = ImageCaptioner()
            except Exception as e:
                logger.warning(f"Failed to load image captioner: {e}")
    
    def transcribe_audio(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe audio file"""
        if not self.whisper_model:
            return {"error": "Whisper model not available"}
        
        return self.whisper_model.transcribe(audio_path, language)
    
    def translate_audio(self, audio_path: str, source_language: Optional[str] = None) -> Dict[str, Any]:
        """Translate audio to English"""
        if not self.whisper_model:
            return {"error": "Whisper model not available"}
        
        return self.whisper_model.translate(audio_path, source_language)
    
    def analyze_text(self, text: str, language: str = "auto") -> Dict[str, Any]:
        """Analyze text content"""
        if not self.text_processor:
            return {"error": "Text processor not available"}
        
        return self.text_processor.analyze_text(text, language)
    
    def translate_text(self, text: str, source_lang: str = "auto", target_lang: str = "en") -> str:
        """Translate text"""
        if not self.text_processor:
            return text
        
        return self.text_processor.translate_text(text, source_lang, target_lang)
    
    def caption_image(self, image_path: str) -> Dict[str, Any]:
        """Generate image caption"""
        if not self.image_captioner:
            return {"error": "Image captioner not available"}
        
        return self.image_captioner.generate_caption(image_path)


# Singleton instance
ai_manager = AIModelManager()
