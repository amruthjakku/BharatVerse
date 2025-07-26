-- 🗄️ BharatVerse Supabase Database Schema
-- Copy and paste this SQL into your Supabase SQL Editor

-- 1. Users table - Store user accounts and profiles
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    avatar_url TEXT,
    provider VARCHAR(50) DEFAULT 'email',
    provider_id VARCHAR(255),
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Contributions table - Store all user contributions (text, proverbs, etc.)
CREATE TABLE IF NOT EXISTS contributions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    content TEXT,
    content_type VARCHAR(50), -- 'text', 'proverb', 'audio', 'image', etc.
    file_url TEXT,
    file_type VARCHAR(100),
    file_size INTEGER,
    language VARCHAR(50),
    region VARCHAR(100),
    tags TEXT[], -- Array of tags
    metadata JSONB DEFAULT '{}', -- Flexible metadata storage
    ai_analysis JSONB DEFAULT '{}', -- AI analysis results
    is_public BOOLEAN DEFAULT true,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Analytics table - Track user activity and system events
CREATE TABLE IF NOT EXISTS analytics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}',
    session_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    processing_time_ms INTEGER,
    status VARCHAR(20),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Community interactions table - Likes, comments, shares, follows
CREATE TABLE IF NOT EXISTS community_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    target_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    contribution_id INTEGER REFERENCES contributions(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50), -- 'like', 'comment', 'share', 'follow'
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_contributions_user_id ON contributions(user_id);
CREATE INDEX IF NOT EXISTS idx_contributions_language ON contributions(language);
CREATE INDEX IF NOT EXISTS idx_contributions_region ON contributions(region);
CREATE INDEX IF NOT EXISTS idx_contributions_content_type ON contributions(content_type);
CREATE INDEX IF NOT EXISTS idx_contributions_created_at ON contributions(created_at);
CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_event_type ON analytics(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_created_at ON analytics(created_at);
CREATE INDEX IF NOT EXISTS idx_community_interactions_user_id ON community_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_community_interactions_contribution_id ON community_interactions(contribution_id);

-- 6. Insert sample data for testing
INSERT INTO users (username, email, full_name, provider, role) 
VALUES ('demo_user', 'demo@bharatverse.com', 'Demo User', 'demo', 'user')
ON CONFLICT (username) DO NOTHING;

-- Get the demo user ID for sample contributions
DO $$
DECLARE
    demo_user_id INTEGER;
BEGIN
    SELECT id INTO demo_user_id FROM users WHERE username = 'demo_user';
    
    -- Insert sample text contribution
    INSERT INTO contributions (
        user_id, title, content, content_type, language, region, tags, metadata, ai_analysis
    ) VALUES (
        demo_user_id,
        'Sample Bengali Folk Tale',
        'এক সময় এক ছোট গ্রামে একটি সুন্দর গল্প ছিল... (Once upon a time in a small village, there was a beautiful story...)',
        'text',
        'Bengali',
        'West Bengal',
        ARRAY['folk', 'story', 'bengali', 'traditional'],
        '{"author": "Traditional", "word_count": 25, "sample_data": true}',
        '{"sentiment": "positive", "themes": ["tradition", "culture", "storytelling"], "cultural_significance": 0.85}'
    ) ON CONFLICT DO NOTHING;
    
    -- Insert sample proverb
    INSERT INTO contributions (
        user_id, title, content, content_type, language, region, tags, metadata
    ) VALUES (
        demo_user_id,
        'Sample Hindi Proverb',
        'जैसी करनी वैसी भरनी - As you sow, so shall you reap',
        'proverb',
        'Hindi',
        'North India',
        ARRAY['proverb', 'wisdom', 'hindi', 'karma'],
        '{"original_text": "जैसी करनी वैसी भरनी", "translation": "As you sow, so shall you reap", "meaning": "Your actions determine your consequences", "category": "wisdom", "sample_data": true}'
    ) ON CONFLICT DO NOTHING;
    
    -- Insert sample Tamil story
    INSERT INTO contributions (
        user_id, title, content, content_type, language, region, tags, metadata
    ) VALUES (
        demo_user_id,
        'Sample Tamil Cultural Story',
        'ஒரு காலத்தில் ஒரு சிறிய கிராமத்தில் ஒரு பழைய கதை இருந்தது... (Once upon a time in a small village, there was an old story...)',
        'text',
        'Tamil',
        'Tamil Nadu',
        ARRAY['story', 'culture', 'village', 'tamil'],
        '{"author": "Village Elder", "word_count": 30, "sample_data": true}'
    ) ON CONFLICT DO NOTHING;
END $$;

-- 7. Verify the setup
SELECT 'Tables created successfully!' as status;
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name;
SELECT 'Sample data inserted!' as status;
SELECT COUNT(*) as user_count FROM users;
SELECT COUNT(*) as contribution_count FROM contributions;