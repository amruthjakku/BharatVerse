import streamlit as st
from datetime import datetime


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
    title = st.text_input("Title", "A Journey to the Village Fair")
    content = st.text_area(
        "Story Content",
        "It was a bright sunny morning when we decided to go to the village fair... "
        "The fair was bustling with people, vibrant colors, and the smell of delicious food in the air.",
        height=200)

    # Translation option
    if st.checkbox("Translate to English"):
        st.markdown("---")
        st.markdown("### 🔄 Translation")
        st.text_area("Translated Story Content", "This is the translated version of the story...")

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
