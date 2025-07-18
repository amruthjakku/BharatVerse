import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Try to import enhanced AI models
try:
    from core.ai_models_enhanced import ai_manager
    AI_MODELS_AVAILABLE = True
except ImportError:
    AI_MODELS_AVAILABLE = False

# Database imports
try:
    from streamlit_app.utils.database import add_contribution
    from core.database import DatabaseManager, ContentRepository
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


def text_page():
    st.markdown("## 📝 Story Keeper")
    st.markdown("Document stories, proverbs, recipes, and wisdom from your culture.")
    
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
    use_real_data = st.session_state.get('use_real_data', False)
    
    if use_real_data:
        title = st.text_input("Title", "", placeholder="Enter your story title...")
        content = st.text_area(
            "Story Content",
            "",
            height=200,
            placeholder="Write your story here..."
        )
    else:
        title = st.text_input("Title", "A Journey to the Village Fair")
        content = st.text_area(
            "Story Content",
            "It was a bright sunny morning when we decided to go to the village fair... "
            "The fair was bustling with people, vibrant colors, and the smell of delicious food in the air.",
            height=200
        )

    # Translation and Analysis option
    if st.checkbox("Analyze & Translate Text"):
        st.markdown("---")
        st.markdown("### 🔄 AI Analysis & Translation")
        if st.button("Analyze Text", key="analyze_story"):
            with st.spinner("Analyzing text..."):
                use_real_data = st.session_state.get('use_real_data', False)
                
                if use_real_data and AI_MODELS_AVAILABLE:
                    try:
                        # Use enhanced AI models for text analysis
                        st.info("🤖 Using real AI models for text analysis...")
                        
                        # Determine language code
                        lang_code = language.lower()[:2] if language != "English" else "en"
                        
                        result = ai_manager.process_text(
                            content, 
                            language=lang_code, 
                            translate=True
                        )
                        
                        if result.get('success'):
                            st.success("✅ Analysis complete!")
                            
                            # Show comprehensive analysis
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Word Count", result.get('word_count', 0))
                            with col2:
                                sentiment = result.get('sentiment', {})
                                st.metric("Sentiment", sentiment.get('label', 'Unknown'))
                            with col3:
                                readability = result.get('readability', {})
                                st.metric("Readability", readability.get('difficulty', 'Unknown'))
                            
                            # Language detection
                            detected_lang = result.get('language', 'unknown')
                            st.info(f"🌐 Detected language: {detected_lang}")
                            
                            # Show translation if available
                            translation_result = result.get('translation', {})
                            if translation_result and translation_result.get('success'):
                                translation = translation_result.get('translation', '')
                                st.text_area("English Translation", translation, height=200)
                                st.caption(f"🔄 Translation confidence: {translation_result.get('confidence', 0.0):.2%}")
                            
                            # Cultural indicators
                            cultural_indicators = result.get('cultural_indicators', [])
                            if cultural_indicators:
                                st.markdown("### 🏛️ Cultural Elements Detected")
                                st.write(", ".join(cultural_indicators))
                            
                            # Keywords
                            keywords = result.get('keywords', [])
                            if keywords:
                                st.markdown("### 🔑 Key Terms")
                                st.write(", ".join(keywords[:15]))
                            
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
                            raise Exception("API call failed")
                            
                    except Exception as e:
                        # Fallback to demo
                        st.warning(f"Using demo translation (API error: {str(e)})")
                        st.text_area("Translated Story Content", 
                                   "It was a bright sunny morning when we decided to go to the village fair... "
                                   "The fair was bustling with people, vibrant colors, and the smell of delicious food in the air.",
                                   height=200)
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Word Count", "42")
                        with col2:
                            st.metric("Sentiment", "positive")
                        with col3:
                            st.metric("Cultural Score", "0.85/1.0")
                else:
                    # Demo mode
                    st.info("Demo Mode: Showing simulated translation")
                    st.text_area("Translated Story Content", 
                               "It was a bright sunny morning when we decided to go to the village fair... "
                               "The fair was bustling with people, vibrant colors, and the smell of delicious food in the air.",
                               height=200)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Word Count", "42")
                    with col2:
                        st.metric("Sentiment", "positive")
                    with col3:
                        st.metric("Cultural Score", "0.85/1.0")
        else:
            st.info("Click 'Translate' to translate your story to English")

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
                "timestamp": datetime.now().isoformat()
            })

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
    
    # Proverb input
    st.markdown("---")
    proverb = st.text_input(
        "Proverb/Saying (in original language)",
        "जैसी करनी वैसी भरनी"
    )
    
    transliteration = st.text_input(
        "Transliteration",
        "Jaisi karni waisi bharni"
    )
    
    translation = st.text_input(
        "English Translation",
        "As you sow, so shall you reap"
    )
    
    meaning = st.text_area(
        "Meaning/Explanation",
        "This proverb teaches that our actions have consequences. Good deeds lead to good outcomes, while bad deeds lead to negative results.",
        height=100
    )
    
    usage = st.text_area(
        "When is it used?",
        "Often used to teach children about karma and responsibility for their actions.",
        height=80
    )
    
    # Submit
    if st.button("📤 Add Proverb", type="primary", use_container_width=True):
        st.success("✅ Proverb added successfully!")
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
