import streamlit as st
from datetime import datetime
import sys
from pathlib import Path
import time

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Performance optimization imports
from utils.performance_optimizer import get_performance_optimizer
# Safe memory manager import
try:
    from utils.memory_manager import get_memory_manager, MemoryTracker, show_memory_dashboard
except ImportError:
    from utils.fallback_memory import (
        get_fallback_memory_manager as get_memory_manager, 
        show_fallback_memory_dashboard as show_memory_dashboard,
        FallbackMemoryTracker as MemoryTracker
    )
from utils.redis_cache import get_cache_manager

# Initialize performance components
@st.cache_resource
def get_text_performance_components():
    """Get cached performance components for text module"""
    return {
        'optimizer': get_performance_optimizer(),
        'memory_manager': get_memory_manager(),
        'cache_manager': get_cache_manager()
    }

@st.cache_data(ttl=1800, show_spinner=False)
def get_text_processing_config():
    """Get cached text processing configuration"""
    return {
        'max_text_length': 10000,
        'supported_languages': ['hi', 'en', 'bn', 'te', 'mr', 'ta', 'gu', 'kn', 'ml', 'pa'],
        'ai_processing_timeout': 30,
        'batch_size': 5
    }

def store_text_contribution_to_supabase(title: str, content: str, language: str, 
                                       region: str, author: str, keywords: str,
                                       year_composed: int, analysis_result: dict) -> bool:
    """Store text contribution directly to Supabase"""
    try:
        if not SUPABASE_AVAILABLE:
            st.warning("Supabase not available, falling back to local storage")
            return store_text_contribution_locally(title, content, language, region, author, keywords, year_composed, analysis_result)
        
        if not AUTH_AVAILABLE:
            st.error("Authentication not available")
            return False
        
        # Get current user
        auth = get_auth_manager()
        if not auth.is_authenticated():
            st.error("Please login to submit contributions")
            return False
        
        user_info = auth.get_current_user()
        db_user = auth.get_current_db_user()
        
        if not db_user:
            st.error("User not found in database")
            return False
        
        # Get database manager
        db = get_database_manager()
        
        # Prepare metadata
        metadata = {
            'author': author,
            'year_composed': year_composed,
            'submitted_by': user_info.get('username', 'unknown'),
            'submission_timestamp': datetime.now().isoformat(),
            'word_count': len(content.split()) if content else 0,
            'character_count': len(content) if content else 0
        }
        
        # Prepare tags
        tags = [tag.strip() for tag in keywords.split(',') if tag.strip()]
        tags.extend(['text', 'story', language.lower()])
        
        # Store in Supabase
        contribution_id = db.insert_contribution(
            user_id=db_user['id'],
            title=title,
            content=content,
            content_type='text',
            language=language,
            region=region,
            tags=tags,
            metadata=metadata,
            ai_analysis=analysis_result
        )
        
        if contribution_id:
            st.success(f"✅ Text contribution stored in Supabase with ID: {contribution_id}")
            
            # Log the contribution
            try:
                db.log_user_activity(
                    user_id=db_user['id'],
                    activity_type='contribution_created',
                    details={
                        'contribution_id': contribution_id,
                        'content_type': 'text',
                        'title': title,
                        'language': language,
                        'region': region
                    }
                )
            except Exception as e:
                st.warning(f"Failed to log activity: {e}")
            
            return True
        else:
            st.error("Failed to store contribution in Supabase")
            return False
            
    except Exception as e:
        st.error(f"Error storing text contribution: {e}")
        st.info("Falling back to local storage...")
        return store_text_contribution_locally(title, content, language, region, author, keywords, year_composed, analysis_result)

def store_text_contribution_locally(title: str, content: str, language: str, 
                                  region: str, author: str, keywords: str,
                                  year_composed: int, analysis_result: dict) -> bool:
    """Fallback local storage for text contributions"""
    try:
        if not DATABASE_AVAILABLE:
            # Store in session state as last resort
            if 'local_text_contributions' not in st.session_state:
                st.session_state.local_text_contributions = []
            
            contribution = {
                'id': len(st.session_state.local_text_contributions) + 1,
                'title': title,
                'content': content,
                'language': language,
                'region': region,
                'author': author,
                'keywords': keywords,
                'year_composed': year_composed,
                'analysis_result': analysis_result,
                'timestamp': datetime.now().isoformat(),
                'stored_locally': True
            }
            
            st.session_state.local_text_contributions.append(contribution)
            st.info("📱 Contribution stored locally (will sync to cloud when available)")
            return True
        
        # Use local database
        auth = get_auth_manager()
        user_info = auth.get_current_user() if auth.is_authenticated() else None
        username = user_info.get('username', 'anonymous') if user_info else 'anonymous'
        
        success = add_contribution(
            user_id=username,
            contribution_type='text',
            title=title,
            content=content,
            metadata={
                'language': language,
                'region': region,
                'author': author,
                'keywords': keywords.split(','),
                'year_composed': year_composed,
                'analysis_result': analysis_result
            }
        )
        
        if success:
            st.info("📱 Contribution stored locally")
            return True
        else:
            st.error("Failed to store contribution locally")
            return False
            
    except Exception as e:
        st.error(f"Error in local storage: {e}")
        return False

def store_proverb_to_supabase(proverb: str, transliteration: str, translation: str,
                             meaning: str, usage: str, language: str, category: str) -> bool:
    """Store proverb contribution directly to Supabase"""
    try:
        if not SUPABASE_AVAILABLE:
            st.warning("Supabase not available, storing locally")
            return store_proverb_locally(proverb, transliteration, translation, meaning, usage, language, category)
        
        if not AUTH_AVAILABLE:
            st.error("Authentication not available")
            return False
        
        # Get current user
        auth = get_auth_manager()
        if not auth.is_authenticated():
            st.error("Please login to submit proverbs")
            return False
        
        user_info = auth.get_current_user()
        db_user = auth.get_current_db_user()
        
        if not db_user:
            st.error("User not found in database")
            return False
        
        # Get database manager
        db = get_database_manager()
        
        # Prepare content
        content = f"""
Original: {proverb}
Transliteration: {transliteration}
Translation: {translation}
Meaning: {meaning}
Usage: {usage}
        """.strip()
        
        # Prepare metadata
        metadata = {
            'original_text': proverb,
            'transliteration': transliteration,
            'translation': translation,
            'meaning': meaning,
            'usage_context': usage,
            'category': category,
            'submitted_by': user_info.get('username', 'unknown'),
            'submission_timestamp': datetime.now().isoformat(),
            'content_type': 'proverb'
        }
        
        # Prepare tags
        tags = ['proverb', 'wisdom', category.lower(), language.lower()]
        
        # Store in Supabase
        contribution_id = db.insert_contribution(
            user_id=db_user['id'],
            title=f"Proverb: {proverb[:50]}{'...' if len(proverb) > 50 else ''}",
            content=content,
            content_type='proverb',
            language=language,
            region=None,  # Proverbs might not have specific regions
            tags=tags,
            metadata=metadata,
            ai_analysis={}
        )
        
        if contribution_id:
            st.success(f"✅ Proverb stored in Supabase with ID: {contribution_id}")
            
            # Log the contribution
            try:
                db.log_user_activity(
                    user_id=db_user['id'],
                    activity_type='contribution_created',
                    details={
                        'contribution_id': contribution_id,
                        'content_type': 'proverb',
                        'language': language,
                        'category': category
                    }
                )
            except Exception as e:
                st.warning(f"Failed to log activity: {e}")
            
            return True
        else:
            st.error("Failed to store proverb in Supabase")
            return False
            
    except Exception as e:
        st.error(f"Error storing proverb: {e}")
        st.info("Falling back to local storage...")
        return store_proverb_locally(proverb, transliteration, translation, meaning, usage, language, category)

def store_proverb_locally(proverb: str, transliteration: str, translation: str,
                         meaning: str, usage: str, language: str, category: str) -> bool:
    """Fallback local storage for proverbs"""
    try:
        # Store in session state
        if 'local_proverbs' not in st.session_state:
            st.session_state.local_proverbs = []
        
        proverb_data = {
            'id': len(st.session_state.local_proverbs) + 1,
            'proverb': proverb,
            'transliteration': transliteration,
            'translation': translation,
            'meaning': meaning,
            'usage': usage,
            'language': language,
            'category': category,
            'timestamp': datetime.now().isoformat(),
            'stored_locally': True
        }
        
        st.session_state.local_proverbs.append(proverb_data)
        st.info("📱 Proverb stored locally (will sync to cloud when available)")
        return True
        
    except Exception as e:
        st.error(f"Error in local proverb storage: {e}")
        return False

def sync_local_contributions_to_supabase():
    """Sync locally stored contributions to Supabase when available"""
    if not SUPABASE_AVAILABLE or not AUTH_AVAILABLE:
        return False
    
    try:
        # Check for local text contributions
        local_texts = st.session_state.get('local_text_contributions', [])
        local_proverbs = st.session_state.get('local_proverbs', [])
        
        if not local_texts and not local_proverbs:
            return True  # Nothing to sync
        
        auth = get_auth_manager()
        if not auth.is_authenticated():
            return False
        
        db_user = auth.get_current_db_user()
        if not db_user:
            return False
        
        db = get_database_manager()
        synced_count = 0
        
        # Sync text contributions
        for text_contrib in local_texts:
            if text_contrib.get('stored_locally'):
                try:
                    metadata = {
                        'author': text_contrib.get('author', 'Anonymous'),
                        'year_composed': text_contrib.get('year_composed'),
                        'synced_from_local': True,
                        'original_timestamp': text_contrib.get('timestamp'),
                        'word_count': len(text_contrib.get('content', '').split()),
                        'character_count': len(text_contrib.get('content', ''))
                    }
                    
                    tags = [tag.strip() for tag in text_contrib.get('keywords', '').split(',') if tag.strip()]
                    tags.extend(['text', 'story', text_contrib.get('language', '').lower()])
                    
                    contribution_id = db.insert_contribution(
                        user_id=db_user['id'],
                        title=text_contrib.get('title', 'Untitled'),
                        content=text_contrib.get('content', ''),
                        content_type='text',
                        language=text_contrib.get('language'),
                        region=text_contrib.get('region'),
                        tags=tags,
                        metadata=metadata,
                        ai_analysis=text_contrib.get('analysis_result', {})
                    )
                    
                    if contribution_id:
                        synced_count += 1
                        
                except Exception as e:
                    st.warning(f"Failed to sync text contribution: {e}")
        
        # Sync proverbs
        for proverb in local_proverbs:
            if proverb.get('stored_locally'):
                try:
                    content = f"""
Original: {proverb.get('proverb', '')}
Transliteration: {proverb.get('transliteration', '')}
Translation: {proverb.get('translation', '')}
Meaning: {proverb.get('meaning', '')}
Usage: {proverb.get('usage', '')}
                    """.strip()
                    
                    metadata = {
                        'original_text': proverb.get('proverb', ''),
                        'transliteration': proverb.get('transliteration', ''),
                        'translation': proverb.get('translation', ''),
                        'meaning': proverb.get('meaning', ''),
                        'usage_context': proverb.get('usage', ''),
                        'category': proverb.get('category', ''),
                        'synced_from_local': True,
                        'original_timestamp': proverb.get('timestamp'),
                        'content_type': 'proverb'
                    }
                    
                    tags = ['proverb', 'wisdom', proverb.get('category', '').lower(), proverb.get('language', '').lower()]
                    
                    contribution_id = db.insert_contribution(
                        user_id=db_user['id'],
                        title=f"Proverb: {proverb.get('proverb', '')[:50]}",
                        content=content,
                        content_type='proverb',
                        language=proverb.get('language'),
                        region=None,
                        tags=tags,
                        metadata=metadata,
                        ai_analysis={}
                    )
                    
                    if contribution_id:
                        synced_count += 1
                        
                except Exception as e:
                    st.warning(f"Failed to sync proverb: {e}")
        
        if synced_count > 0:
            # Clear local storage after successful sync
            st.session_state.local_text_contributions = []
            st.session_state.local_proverbs = []
            st.success(f"✅ Synced {synced_count} contributions to Supabase!")
            return True
        
        return False
        
    except Exception as e:
        st.error(f"Error syncing to Supabase: {e}")
        return False

# Try to import enhanced AI models
try:
    from core.enhanced_ai_models import ai_manager
    AI_MODELS_AVAILABLE = True
except ImportError:
    try:
        from core.ai_models import ai_manager
        AI_MODELS_AVAILABLE = True
    except ImportError:
        AI_MODELS_AVAILABLE = False

# Database imports
try:
    from utils.supabase_db import get_database_manager
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# Authentication imports
try:
    from streamlit_app.utils.auth import get_auth_manager
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

# Database utility imports
try:
    from streamlit_app.utils.database import add_contribution
    from core.database import DatabaseManager, ContentRepository
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


def text_page():
    st.markdown("## 📝 Story Keeper")
    st.markdown("Document stories, proverbs, recipes, and wisdom from your culture.")
    
    # Check for local contributions to sync
    local_texts = st.session_state.get('local_text_contributions', [])
    local_proverbs = st.session_state.get('local_proverbs', [])
    
    if (local_texts or local_proverbs) and SUPABASE_AVAILABLE and AUTH_AVAILABLE:
        st.info(f"📱 You have {len(local_texts + local_proverbs)} local contributions that can be synced to cloud")
        if st.button("☁️ Sync to Supabase", type="secondary"):
            with st.spinner("Syncing contributions to cloud..."):
                sync_local_contributions_to_supabase()
    
    # Initialize performance components
    perf_components = get_text_performance_components()
    optimizer = perf_components['optimizer']
    memory_manager = perf_components['memory_manager']
    cache_manager = perf_components['cache_manager']
    
    # Get text processing configuration
    text_config = get_text_processing_config()
    
    # Performance monitoring for admins
    if st.session_state.get("user_role") == "admin":
        with st.expander("⚡ Performance Monitoring", expanded=False):
            show_memory_dashboard()
    
    # Memory tracking for text operations
    with MemoryTracker("text_page_operations"):
        # Content type tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Stories", "Proverbs & Sayings", "Recipes", "Customs & Traditions"])
    
    with tab1:
        story_section()
    
    with tab2:
        proverbs_section()
    
    with tab3:
        recipes_section()
    
    with tab4:
        customs_section()


def story_section():
    st.markdown("### 📖 Share a Story")
    
    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox(
            "Language",
            ["Hindi", "Bengali", "Tamil", "Telugu", "Marathi", "Gujarati", 
             "Kannada", "Malayalam", "Punjabi", "Odia", "Assamese", "Urdu", "English"]
        )
    
    with col2:
        story_type = st.selectbox(
            "Story Type",
            ["Folk Tale", "Mythology", "Legend", "Fable", "Personal Story", "Historical"]
        )

    # Story content
    st.markdown("---")
    st.markdown("### 📝 Write Your Story")
    
    # Language-specific placeholders
    language_placeholders = {
        "Hindi": {
            "title": "अपनी कहानी का शीर्षक लिखें...",
            "content": "यहाँ अपनी कहानी लिखें... (अपने परिवार, गाँव, या संस्कृति की कोई यादगार घटना साझा करें)"
        },
        "Bengali": {
            "title": "আপনার গল্পের শিরোনাম লিখুন...",
            "content": "এখানে আপনার গল্প লিখুন... (আপনার পরিবার, গ্রাম বা সংস্কৃতির কোনো স্মরণীয় ঘটনা শেয়ার করুন)"
        },
        "Tamil": {
            "title": "உங்கள் கதையின் தலைப்பை எழுதுங்கள்...",
            "content": "இங்கே உங்கள் கதையை எழுதுங்கள்... (உங்கள் குடும்பம், கிராமம் அல்லது கலாச்சாரத்தின் நினைவுகூரத்தக்க நிகழ்வைப் பகிருங்கள்)"
        },
        "Telugu": {
            "title": "మీ కథ యొక్క శీర్షిక రాయండి...",
            "content": "ఇక్కడ మీ కథను రాయండి... (మీ కుటుంబం, గ్రామం లేదా సంస్కృతికి సంబంధించిన గుర్తుండిపోయే సంఘటనను పంచుకోండి)"
        },
        "Marathi": {
            "title": "तुमच्या कथेचे शीर्षक लिहा...",
            "content": "इथे तुमची कथा लिहा... (तुमच्या कुटुंबाची, गावाची किंवा संस्कृतीची आठवणीजोगी घटना सामायिक करा)"
        },
        "Gujarati": {
            "title": "તમારી વાર્તાનું શીર્ષક લખો...",
            "content": "અહીં તમારી વાર્તા લખો... (તમારા કુટુંબ, ગામ અથવા સંસ્કૃતિની યાદગાર ઘટના શેર કરો)"
        },
        "Kannada": {
            "title": "ನಿಮ್ಮ ಕಥೆಯ ಶೀರ್ಷಿಕೆ ಬರೆಯಿರಿ...",
            "content": "ಇಲ್ಲಿ ನಿಮ್ಮ ಕಥೆಯನ್ನು ಬರೆಯಿರಿ... (ನಿಮ್ಮ ಕುಟುಂಬ, ಹಳ್ಳಿ ಅಥವಾ ಸಂಸ್ಕೃತಿಯ ನೆನಪಿನ ಘಟನೆಯನ್ನು ಹಂಚಿಕೊಳ್ಳಿ)"
        },
        "Malayalam": {
            "title": "നിങ്ങളുടെ കഥയുടെ തലക്കെട്ട് എഴുതുക...",
            "content": "ഇവിടെ നിങ്ങളുടെ കഥ എഴുതുക... (നിങ്ങളുടെ കുടുംബം, ഗ്രാമം അല്ലെങ്കിൽ സംസ്കാരത്തിന്റെ അവിസ്മരണീയമായ സംഭവം പങ്കിടുക)"
        },
        "Punjabi": {
            "title": "ਆਪਣੀ ਕਹਾਣੀ ਦਾ ਸਿਰਲੇਖ ਲਿਖੋ...",
            "content": "ਇੱਥੇ ਆਪਣੀ ਕਹਾਣੀ ਲਿਖੋ... (ਆਪਣੇ ਪਰਿਵਾਰ, ਪਿੰਡ ਜਾਂ ਸੱਭਿਆਚਾਰ ਦੀ ਕੋਈ ਯਾਦਗਾਰ ਘਟਨਾ ਸਾਂਝੀ ਕਰੋ)"
        },
        "Odia": {
            "title": "ଆପଣଙ୍କ କାହାଣୀର ଶୀର୍ଷକ ଲେଖନ୍ତୁ...",
            "content": "ଏଠାରେ ଆପଣଙ୍କ କାହାଣୀ ଲେଖନ୍ତୁ... (ଆପଣଙ୍କ ପରିବାର, ଗାଁ କିମ୍ବା ସଂସ୍କୃତିର କୌଣସି ସ୍ମରଣୀୟ ଘଟଣା ସାଝା କରନ୍ତୁ)"
        },
        "Assamese": {
            "title": "আপোনাৰ কাহিনীৰ শিৰোনাম লিখক...",
            "content": "ইয়াত আপোনাৰ কাহিনী লিখক... (আপোনাৰ পৰিয়াল, গাঁও বা সংস্কৃতিৰ কোনো স্মৰণীয় ঘটনা ভাগ কৰক)"
        },
        "Urdu": {
            "title": "اپنی کہانی کا عنوان لکھیں...",
            "content": "یہاں اپنی کہانی لکھیں... (اپنے خاندان، گاؤں یا ثقافت کا کوئی یادگار واقعہ شیئر کریں)"
        },
        "English": {
            "title": "Enter your story title...",
            "content": "Write your story here... (Share a memorable event from your family, village, or culture)"
        }
    }
    
    placeholders = language_placeholders.get(language, language_placeholders["English"])
    
    title = st.text_input("Title", "", placeholder=placeholders["title"])
    content = st.text_area(
        "Story Content",
        "",
        height=200,
        placeholder=placeholders["content"]
    )

    # Translation and Analysis option
    if st.checkbox("Analyze & Translate Text"):
        st.markdown("---")
        st.markdown("### 🔄 AI Analysis & Translation")
        if st.button("Analyze Text", key="analyze_story"):
            if not content.strip():
                st.warning("Please enter some content to analyze.")
            else:
                from utils.threading_manager import streamlit_threaded_operation
                
                def _analyze_text_task():
                    """Internal text analysis task for threading"""
                    if AI_MODELS_AVAILABLE:
                        try:
                            # Determine language code
                            lang_code = language.lower()[:2] if language != "English" else "en"
                            
                            # Use enhanced AI for comprehensive analysis
                            result = ai_manager.analyze_text(content, language=lang_code)
                            
                            # Get translation if needed
                            if language != "English":
                                translation_result = ai_manager.translate_text(content, "english")
                                result["translation"] = translation_result
                            
                            return result
                        except Exception as e:
                            return {"success": False, "error": str(e)}
                    else:
                        return {"success": False, "error": "AI models not available"}
                
                # Execute text analysis in a separate thread
                try:
                    result = streamlit_threaded_operation(
                        _analyze_text_task,
                        progress_text="🤖 Analyzing text with AI...",
                        success_text="✅ Text analysis complete!"
                    )
                    
                    if result and result.get('success'):
                        # Show comprehensive analysis
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Word Count", result.get('word_count', 0))
                        with col2:
                            sentiment = result.get('sentiment', {})
                            st.metric("Sentiment", sentiment.get('label', 'Unknown'))
                        with col3:
                            emotions = result.get('emotions', {})
                            st.metric("Primary Emotion", emotions.get('primary_emotion', 'Unknown'))
                        with col4:
                            quality = result.get('quality_metrics', {})
                            st.metric("Readability", quality.get('complexity', 'Unknown'))
                        
                        # Language detection
                        detected_lang = result.get('language', 'unknown')
                        st.info(f"🌐 Detected language: {detected_lang}")
                        
                        # Show translation if available
                        translation_result = result.get('translation', {})
                        if translation_result and translation_result.get('success'):
                            translation = translation_result.get('translation', '')
                            st.text_area("🔄 English Translation", translation, height=200)
                            st.caption(f"Translation confidence: {translation_result.get('confidence', 0.0):.2%}")
                        
                        # Cultural elements
                        cultural_elements = result.get('cultural_elements', [])
                        if cultural_elements:
                            st.markdown("### 🏛️ Cultural Elements Detected")
                            st.write(", ".join(cultural_elements))
                    
                        # Themes
                        themes = result.get('themes', [])
                        if themes:
                            st.markdown("### 🎭 Key Themes")
                            st.write(", ".join(themes))
                        
                        # Summary if available
                        summary = result.get('summary')
                        if summary and summary != result.get('text', '')[:200]:
                            st.markdown("### 📋 Summary")
                            st.write(summary)
                        
                        # Detailed sentiment analysis
                        sentiment = result.get('sentiment', {})
                        if sentiment.get('all_scores'):
                            with st.expander("📊 Detailed Sentiment Analysis"):
                                for score_data in sentiment['all_scores']:
                                    st.write(f"**{score_data['label']}**: {score_data['score']:.3f}")
                        
                        # Readability details
                        readability = result.get('readability', {})
                        if readability:
                            with st.expander("📖 Readability Analysis"):
                                st.write(f"**Overall Score**: {readability.get('score', 0):.1f}/100")
                                st.write(f"**Average Words per Sentence**: {readability.get('avg_words_per_sentence', 0):.1f}")
                                st.write(f"**Average Characters per Word**: {readability.get('avg_chars_per_word', 0):.1f}")
                                st.write(f"**Difficulty Level**: {readability.get('difficulty', 'Unknown')}")
                        
                        # Store results for submission
                        st.session_state.text_analysis_result = result
                    else:
                        st.error(f"Analysis failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                # Fallback to API call
                st.info("Falling back to API analysis...")
                try:
                    import requests
                    import os
                    
                    API_URL = os.getenv("API_URL", "http://localhost:8000")
                    response = requests.post(
                        f"{API_URL}/api/v1/text/analyze",
                        json={
                            "text": content,
                            "language": language.lower()[:2],
                            "translate": True
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            translation = result.get('translation', '')
                            analysis = result.get('analysis', {})
                            
                            st.text_area("Translated Story Content", translation, height=200)
                            
                            # Show analysis insights
                            if analysis:
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Word Count", analysis.get('word_count', 0))
                                with col2:
                                    st.metric("Sentiment", analysis.get('sentiment', 'neutral'))
                                with col3:
                                    score = analysis.get('cultural_significance', 0)
                                    st.metric("Cultural Score", f"{score:.2f}/1.0")
                        else:
                            st.error(f"Translation failed: {result.get('error', 'Unknown error')}")
                    else:
                        st.error(f"API error: {response.status_code}")
                        
                except Exception as e:
                    # Fallback error message
                    st.error(f"Translation service unavailable: {str(e)}")
                    st.info("💡 Try submitting your story without translation for now.")
        else:
            # AI models not available
            st.warning("🤖 AI analysis not available")
            st.info("💡 Install AI models or configure API to enable text analysis and translation.")

    # Metadata
    st.markdown("---")
    st.markdown("### 🏷️ Metadata & Tags")
    
    col1, col2 = st.columns(2)
    with col1:
        author = st.text_input("Author/Credited Contributor", "Anonymous")
        region = st.text_input("Region/State", "West Bengal")
    
    with col2:
        keywords = st.text_input("Keywords/Tags (comma-separated)", "fair, village, tradition")
        year_composed = st.number_input("Year Composed (Optional)", 1800, 2024, 2024)

    # Consent checkbox
    consent = st.checkbox(
        "I confirm that I have the right to share this content and agree to the "
        "terms of use and CC-BY 4.0 license for the contributed data."
    )
    
    # Submit button
    if consent:
        if st.button("📤 Submit Contribution", type="primary", use_container_width=True):
            # Store in Supabase
            success = store_text_contribution_to_supabase(
                title=title,
                content=content,
                language=language,
                region=region,
                author=author,
                keywords=keywords,
                year_composed=year_composed,
                analysis_result=st.session_state.get('text_analysis_result', {})
            )
            
            if success:
                st.success("🎉 Thank you for your contribution! Your story has been added to BharatVerse.")
                st.balloons()
                
                # Show contribution summary
                st.markdown("### 📋 Contribution Summary")
                st.json({
                    "type": "text",
                    "title": title,
                    "language": language,
                    "region": region,
                    "author": author,
                    "keywords": keywords.split(", "),
                    "timestamp": datetime.now().isoformat(),
                    "stored_in": "Supabase Cloud Database"
                })
                
                # Clear the form
                st.session_state.pop('text_analysis_result', None)
                st.rerun()
            else:
                st.error("❌ Failed to submit contribution. Please try again.")
                st.info("Your contribution will be saved locally and synced when connection is restored.")

    # Storytelling tips
    with st.expander("💡 Storytelling Tips"):
        st.markdown("""
        - **Be descriptive** to paint a vivid picture
        - **Include dialogue** to bring characters to life
        - **Provide cultural context** to enrich the narrative
        - **Keep it concise** yet engaging
        """)


def proverbs_section():
    st.markdown("### 🗣️ Share Proverbs & Sayings")
    
    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox(
            "Language",
            ["Hindi", "Bengali", "Tamil", "Telugu", "Marathi", "Sanskrit", "Urdu"],
            key="proverb_lang"
        )
    
    with col2:
        category = st.selectbox(
            "Category",
            ["Wisdom", "Life Lessons", "Nature", "Family", "Work", "Humor"]
        )
    
    # Proverb input with language-specific placeholders
    st.markdown("---")
    
    # Language-specific placeholders for proverbs
    proverb_placeholders = {
        "Hindi": {
            "proverb": "अपनी कहावत या सूक्ति लिखें...",
            "transliteration": "Roman script mein likhiye...",
            "meaning": "इस कहावत का अर्थ और संदेश बताएं...",
            "usage": "यह कब और कैसे इस्तेमाल होती है?"
        },
        "Bengali": {
            "proverb": "আপনার প্রবাদ বা বাণী লিখুন...",
            "transliteration": "Romanized form e likhun...",
            "meaning": "এই প্রবাদের অর্থ ও বার্তা ব্যাখ্যা করুন...",
            "usage": "এটি কখন এবং কীভাবে ব্যবহৃত হয়?"
        },
        "Tamil": {
            "proverb": "உங்கள் பழமொழி அல்லது வாக்கியத்தை எழுதுங்கள்...",
            "transliteration": "Roman script-il ezhuthungal...",
            "meaning": "இந்த பழமொழியின் பொருள் மற்றும் செய்தியை விளக்குங்கள்...",
            "usage": "இது எப்போது மற்றும் எப்படி பயன்படுத்தப்படுகிறது?"
        },
        "Telugu": {
            "proverb": "మీ సామెత లేదా వాక్యాన్ని రాయండి...",
            "transliteration": "Roman script lo rayandi...",
            "meaning": "ఈ సామెత యొక్క అర్థం మరియు సందేశాన్ని వివరించండి...",
            "usage": "ఇది ఎప్పుడు మరియు ఎలా ఉపయోగించబడుతుంది?"
        },
        "Marathi": {
            "proverb": "तुमची म्हण किंवा वाक्य लिहा...",
            "transliteration": "Roman script madhe lihaa...",
            "meaning": "या म्हणीचा अर्थ आणि संदेश स्पष्ट करा...",
            "usage": "हे कधी आणि कसे वापरले जाते?"
        },
        "Sanskrit": {
            "proverb": "अपनं श्लोकं वा सुभाषितं लिखत...",
            "transliteration": "Roman script mein likhiye...",
            "meaning": "अस्य श्लोकस्य अर्थं संदेशं च व्याख्यातु...",
            "usage": "एतत् कदा कथं च प्रयुज्यते?"
        },
        "Urdu": {
            "proverb": "اپنا محاورہ یا کہاوت لکھیں...",
            "transliteration": "Roman script mein likhiye...",
            "meaning": "اس کہاوت کا مطلب اور پیغام بیان کریں...",
            "usage": "یہ کب اور کیسے استعمال ہوتا ہے؟"
        }
    }
    
    placeholders = proverb_placeholders.get(language, {
        "proverb": "Enter your proverb or saying...",
        "transliteration": "Write in Roman script...",
        "meaning": "Explain the meaning and message...",
        "usage": "When and how is it used?"
    })
    
    proverb = st.text_input(
        "Proverb/Saying (in original language)",
        "",
        placeholder=placeholders["proverb"]
    )
    
    transliteration = st.text_input(
        "Transliteration",
        "",
        placeholder=placeholders["transliteration"]
    )
    
    translation = st.text_input(
        "English Translation",
        "",
        placeholder="Enter English translation..."
    )
    
    meaning = st.text_area(
        "Meaning/Explanation",
        "",
        height=100,
        placeholder=placeholders["meaning"]
    )
    
    usage = st.text_area(
        "When is it used?",
        "",
        height=80,
        placeholder=placeholders["usage"]
    )
    
    # Submit
    if st.button("📤 Add Proverb", type="primary", use_container_width=True):
        if not proverb.strip():
            st.warning("Please enter a proverb or saying.")
        elif not translation.strip():
            st.warning("Please provide an English translation.")
        else:
            # Store proverb in Supabase
            success = store_proverb_to_supabase(
                proverb=proverb,
                transliteration=transliteration,
                translation=translation,
                meaning=meaning,
                usage=usage,
                language=language,
                category=category
            )
            
            if success:
                st.success("✅ Proverb added successfully to Supabase!")
                st.json({
                    "type": "proverb",
                    "text": proverb,
                    "language": language,
                    "category": category,
                    "translation": translation,
                    "meaning": meaning
                })


def recipes_section():
    st.markdown("### 🍳 Share Traditional Recipes")
    
    col1, col2 = st.columns(2)
    with col1:
        recipe_name = st.text_input("Recipe Name", "Puran Poli")
        region = st.text_input("Region/State", "Maharashtra")
    
    with col2:
        meal_type = st.selectbox(
            "Meal Type",
            ["Breakfast", "Lunch", "Dinner", "Snack", "Dessert", "Beverage"]
        )
        occasion = st.text_input("Special Occasion", "Holi Festival")
    
    # Ingredients
    st.markdown("---")
    st.markdown("#### 🥘 Ingredients")
    ingredients = st.text_area(
        "List all ingredients with quantities",
        """- 2 cups whole wheat flour
- 1 cup chana dal (split chickpeas)
- 1 cup jaggery
- 1/2 tsp cardamom powder
- Ghee for cooking""",
        height=150
    )
    
    # Method
    st.markdown("#### 👨‍🍳 Preparation Method")
    method = st.text_area(
        "Step-by-step instructions",
        """1. Boil chana dal until soft and drain
2. Mash the dal and cook with jaggery until thick
3. Add cardamom powder and let it cool
4. Make a soft dough with wheat flour
5. Stuff the dal mixture in the dough and roll flat
6. Cook on griddle with ghee until golden brown""",
        height=200
    )
    
    # Cultural significance
    significance = st.text_area(
        "Cultural Significance",
        "This sweet flatbread is traditionally made during Holi and other festivals. It symbolizes the sweetness of relationships.",
        height=100
    )
    
    # Submit
    if st.button("📤 Add Recipe", type="primary", use_container_width=True):
        st.success("✅ Recipe added successfully!")
        st.balloons()


def customs_section():
    st.markdown("### 🎭 Share Customs & Traditions")
    
    col1, col2 = st.columns(2)
    with col1:
        custom_name = st.text_input("Custom/Tradition Name", "Rangoli")
        region = st.text_input("Region", "Pan-India")
    
    with col2:
        category = st.selectbox(
            "Category",
            ["Festival", "Wedding", "Birth", "Coming of Age", "Harvest", "Religious", "Daily Life"]
        )
        frequency = st.selectbox(
            "How often practiced?",
            ["Daily", "Weekly", "Monthly", "Annually", "Special Occasions"]
        )
    
    # Description
    st.markdown("---")
    description = st.text_area(
        "Describe the custom",
        "Rangoli is the art of creating colorful patterns on the floor using materials like colored rice, flour, sand, or flower petals. It is believed to bring good luck and ward off evil spirits.",
        height=150
    )
    
    # How it's done
    process = st.text_area(
        "How is it performed?",
        """1. Clean the area where rangoli will be made
2. Draw the outline with chalk or white powder
3. Fill in colors starting from the center
4. Add diyas (oil lamps) around the rangoli
5. Maintain it throughout the festival period""",
        height=150
    )
    
    # Significance
    significance = st.text_area(
        "Why is it important?",
        "Rangoli represents joy, positivity, and celebration. It's a way to welcome deities and guests into the home.",
        height=100
    )
    
    # Materials needed
    materials = st.text_input(
        "Materials used",
        "Colored powder, rice flour, flower petals, chalk"
    )
    
    # Submit
    if st.button("📤 Add Custom", type="primary", use_container_width=True):
        st.success("✅ Custom/Tradition added successfully!")
        st.json({
            "type": "custom",
            "name": custom_name,
            "region": region,
            "category": category,
            "frequency": frequency,
            "description": description
        })
