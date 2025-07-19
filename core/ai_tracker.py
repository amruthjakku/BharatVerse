"""
Real-time AI Processing Tracker
Tracks and logs AI model usage and performance
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pathlib import Path
import threading
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class AIProcessingTracker:
    """Track AI model usage and performance in real-time"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.processing_history = deque(maxlen=max_history)
        self.daily_stats = defaultdict(int)
        self.model_performance = defaultdict(list)
        self.cultural_elements_found = defaultdict(int)
        self.language_distribution = defaultdict(int)
        self.lock = threading.Lock()
        
        # Load existing data if available
        self._load_data()
    
    def track_transcription(self, result: Dict[str, Any], processing_time: float = 0):
        """Track audio transcription"""
        with self.lock:
            event = {
                "type": "transcription",
                "timestamp": datetime.now().isoformat(),
                "success": result.get("success", False),
                "language": result.get("language", "unknown"),
                "duration": result.get("duration", 0),
                "word_count": result.get("word_count", 0),
                "confidence": result.get("confidence", 0),
                "processing_time": processing_time
            }
            
            self.processing_history.append(event)
            
            if event["success"]:
                self.daily_stats["transcriptions_today"] += 1
                self.language_distribution[event["language"]] += 1
                self.model_performance["whisper"].append({
                    "confidence": event["confidence"],
                    "processing_time": processing_time,
                    "timestamp": event["timestamp"]
                })
    
    def track_text_analysis(self, result: Dict[str, Any], processing_time: float = 0):
        """Track text analysis"""
        with self.lock:
            cultural_elements = result.get("cultural_elements", [])
            themes = result.get("themes", [])
            
            event = {
                "type": "text_analysis",
                "timestamp": datetime.now().isoformat(),
                "success": result.get("success", False),
                "language": result.get("language", "unknown"),
                "word_count": result.get("word_count", 0),
                "sentiment": result.get("sentiment", {}).get("label", "unknown"),
                "cultural_elements_count": len(cultural_elements),
                "themes_count": len(themes),
                "processing_time": processing_time
            }
            
            self.processing_history.append(event)
            
            if event["success"]:
                self.daily_stats["sentiment_analyses_today"] += 1
                self.language_distribution[event["language"]] += 1
                
                # Track cultural elements
                for element in cultural_elements:
                    self.cultural_elements_found[element] += 1
                    self.daily_stats["cultural_elements_detected"] += 1
    
    def track_translation(self, result: Dict[str, Any], source_lang: str, target_lang: str, processing_time: float = 0):
        """Track translation"""
        with self.lock:
            event = {
                "type": "translation",
                "timestamp": datetime.now().isoformat(),
                "success": result.get("success", False),
                "source_language": source_lang,
                "target_language": target_lang,
                "confidence": result.get("confidence", 0),
                "processing_time": processing_time
            }
            
            self.processing_history.append(event)
            
            if event["success"]:
                self.daily_stats["translations_today"] += 1
                self.model_performance["translation"].append({
                    "confidence": event["confidence"],
                    "processing_time": processing_time,
                    "timestamp": event["timestamp"]
                })
    
    def track_image_analysis(self, result: Dict[str, Any], processing_time: float = 0):
        """Track image analysis"""
        with self.lock:
            cultural_elements = result.get("cultural_elements", [])
            objects = result.get("objects", [])
            
            event = {
                "type": "image_analysis",
                "timestamp": datetime.now().isoformat(),
                "success": result.get("success", False),
                "objects_detected": len(objects),
                "cultural_elements_count": len(cultural_elements),
                "quality_score": result.get("quality_metrics", {}).get("quality_score", 0),
                "processing_time": processing_time
            }
            
            self.processing_history.append(event)
            
            if event["success"]:
                self.daily_stats["image_analyses_today"] += 1
                
                # Track cultural elements
                for element in cultural_elements:
                    self.cultural_elements_found[element] += 1
                    self.daily_stats["cultural_elements_detected"] += 1
    
    def get_daily_stats(self) -> Dict[str, Any]:
        """Get today's processing statistics"""
        with self.lock:
            return dict(self.daily_stats)
    
    def get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent AI processing activity"""
        with self.lock:
            return list(self.processing_history)[-limit:]
    
    def get_language_distribution(self) -> Dict[str, int]:
        """Get language usage distribution"""
        with self.lock:
            return dict(self.language_distribution)
    
    def get_cultural_insights(self) -> Dict[str, Any]:
        """Get cultural elements insights"""
        with self.lock:
            top_elements = sorted(
                self.cultural_elements_found.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            return {
                "top_cultural_elements": top_elements,
                "total_elements_detected": sum(self.cultural_elements_found.values()),
                "unique_elements": len(self.cultural_elements_found)
            }
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Get AI model performance metrics"""
        with self.lock:
            performance = {}
            
            for model, metrics in self.model_performance.items():
                if metrics:
                    recent_metrics = metrics[-100:]  # Last 100 operations
                    avg_confidence = sum(m["confidence"] for m in recent_metrics) / len(recent_metrics)
                    avg_processing_time = sum(m["processing_time"] for m in recent_metrics) / len(recent_metrics)
                    
                    performance[model] = {
                        "average_confidence": avg_confidence,
                        "average_processing_time": avg_processing_time,
                        "total_operations": len(metrics),
                        "recent_operations": len(recent_metrics)
                    }
            
            return performance
    
    def get_comprehensive_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics"""
        return {
            "daily_stats": self.get_daily_stats(),
            "recent_activity": self.get_recent_activity(),
            "language_distribution": self.get_language_distribution(),
            "cultural_insights": self.get_cultural_insights(),
            "model_performance": self.get_model_performance(),
            "total_operations": len(self.processing_history)
        }
    
    def reset_daily_stats(self):
        """Reset daily statistics (call at midnight)"""
        with self.lock:
            self.daily_stats.clear()
    
    def _load_data(self):
        """Load existing tracking data"""
        try:
            data_file = Path(__file__).parent.parent / "data" / "ai_tracking.json"
            if data_file.exists():
                with open(data_file, 'r') as f:
                    data = json.load(f)
                    
                # Load only today's data
                today = datetime.now().date()
                for event in data.get("processing_history", []):
                    event_date = datetime.fromisoformat(event["timestamp"]).date()
                    if event_date == today:
                        self.processing_history.append(event)
                
                # Load daily stats if from today
                stats_date = data.get("stats_date")
                if stats_date == today.isoformat():
                    self.daily_stats.update(data.get("daily_stats", {}))
                
                logger.info("AI tracking data loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load AI tracking data: {e}")
    
    def save_data(self):
        """Save tracking data"""
        try:
            data_dir = Path(__file__).parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            
            data_file = data_dir / "ai_tracking.json"
            
            with self.lock:
                data = {
                    "processing_history": list(self.processing_history),
                    "daily_stats": dict(self.daily_stats),
                    "stats_date": datetime.now().date().isoformat(),
                    "cultural_elements": dict(self.cultural_elements_found),
                    "language_distribution": dict(self.language_distribution)
                }
            
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info("AI tracking data saved successfully")
        except Exception as e:
            logger.error(f"Could not save AI tracking data: {e}")


# Global tracker instance
ai_tracker = AIProcessingTracker()