-- Initialize BharatVerse database schema
-- This script runs when PostgreSQL container starts for the first time

-- Create database if not exists
SELECT 'CREATE DATABASE bharatverse'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'bharatverse');

-- Connect to bharatverse database
\c bharatverse;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create content_metadata table
CREATE TABLE IF NOT EXISTS content_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    content_type VARCHAR(50) NOT NULL,
    language VARCHAR(10) NOT NULL,
    region VARCHAR(100),
    tags TEXT[],
    file_path VARCHAR(1000),
    file_extension VARCHAR(10),
    file_size BIGINT,
    transcription TEXT,
    translation TEXT,
    ai_analysis JSONB,
    user_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_content_metadata_content_type ON content_metadata(content_type);
CREATE INDEX IF NOT EXISTS idx_content_metadata_language ON content_metadata(language);
CREATE INDEX IF NOT EXISTS idx_content_metadata_region ON content_metadata(region);
CREATE INDEX IF NOT EXISTS idx_content_metadata_created_at ON content_metadata(created_at);
CREATE INDEX IF NOT EXISTS idx_content_metadata_user_id ON content_metadata(user_id);

-- Create GIN indexes for full-text search
CREATE INDEX IF NOT EXISTS idx_content_metadata_title_gin ON content_metadata USING GIN(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_content_metadata_description_gin ON content_metadata USING GIN(to_tsvector('english', description));
CREATE INDEX IF NOT EXISTS idx_content_metadata_transcription_gin ON content_metadata USING GIN(to_tsvector('english', transcription));
CREATE INDEX IF NOT EXISTS idx_content_metadata_tags_gin ON content_metadata USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_content_metadata_ai_analysis_gin ON content_metadata USING GIN(ai_analysis);

-- Create trigram indexes for fuzzy search
CREATE INDEX IF NOT EXISTS idx_content_metadata_title_trgm ON content_metadata USING GIN(title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_content_metadata_description_trgm ON content_metadata USING GIN(description gin_trgm_ops);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(200),
    region VARCHAR(100),
    preferred_language VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create analytics table
CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL,
    content_id UUID REFERENCES content_metadata(id),
    user_id VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for analytics
CREATE INDEX IF NOT EXISTS idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_events_content_id ON analytics_events(content_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_created_at ON analytics_events(created_at);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_content_metadata_updated_at 
    BEFORE UPDATE ON content_metadata 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing
INSERT INTO content_metadata (title, description, content_type, language, region, tags, transcription, translation) VALUES
('Sample Folk Song', 'A traditional Bengali folk song about harvest season', 'audio', 'bn', 'West Bengal', ARRAY['folk', 'traditional', 'harvest'], 'ধান কাটার গান, মাঠে মাঠে সোনার ধান', 'Song of rice harvest, golden rice in the fields'),
('Diwali Story', 'Traditional story about the festival of lights', 'text', 'hi', 'North India', ARRAY['festival', 'diwali', 'tradition'], 'दीवाली का त्योहार खुशियों का त्योहार है', 'Diwali is a festival of joy and happiness'),
('Rangoli Art', 'Beautiful rangoli patterns from South India', 'image', 'ta', 'Tamil Nadu', ARRAY['art', 'rangoli', 'decoration'], NULL, NULL)
ON CONFLICT DO NOTHING;

-- Create a view for content search
CREATE OR REPLACE VIEW content_search_view AS
SELECT 
    id,
    title,
    description,
    content_type,
    language,
    region,
    tags,
    transcription,
    translation,
    ai_analysis,
    created_at,
    to_tsvector('english', 
        COALESCE(title, '') || ' ' || 
        COALESCE(description, '') || ' ' || 
        COALESCE(transcription, '') || ' ' ||
        COALESCE(translation, '') || ' ' ||
        COALESCE(array_to_string(tags, ' '), '')
    ) as search_vector
FROM content_metadata;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO bharatverse_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO bharatverse_user;
GRANT USAGE ON SCHEMA public TO bharatverse_user;

-- Create function for content search
CREATE OR REPLACE FUNCTION search_content(
    search_query TEXT,
    content_type_filter TEXT DEFAULT NULL,
    language_filter TEXT DEFAULT NULL,
    region_filter TEXT DEFAULT NULL,
    limit_count INTEGER DEFAULT 20,
    offset_count INTEGER DEFAULT 0
)
RETURNS TABLE (
    id UUID,
    title VARCHAR(500),
    description TEXT,
    content_type VARCHAR(50),
    language VARCHAR(10),
    region VARCHAR(100),
    tags TEXT[],
    transcription TEXT,
    translation TEXT,
    ai_analysis JSONB,
    created_at TIMESTAMP WITH TIME ZONE,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.title,
        c.description,
        c.content_type,
        c.language,
        c.region,
        c.tags,
        c.transcription,
        c.translation,
        c.ai_analysis,
        c.created_at,
        ts_rank(c.search_vector, plainto_tsquery('english', search_query)) as rank
    FROM content_search_view c
    WHERE 
        (search_query IS NULL OR c.search_vector @@ plainto_tsquery('english', search_query))
        AND (content_type_filter IS NULL OR c.content_type = content_type_filter)
        AND (language_filter IS NULL OR c.language = language_filter)
        AND (region_filter IS NULL OR c.region = region_filter)
    ORDER BY rank DESC, c.created_at DESC
    LIMIT limit_count
    OFFSET offset_count;
END;
$$ LANGUAGE plpgsql;

-- Community Features Tables

-- Community Groups (Regional, Language, Interest-based)
CREATE TABLE IF NOT EXISTS community_groups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    group_type VARCHAR(50) NOT NULL, -- 'regional', 'language', 'interest'
    group_category VARCHAR(100), -- specific region/language/interest
    image_url VARCHAR(500),
    member_count INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Group Memberships
CREATE TABLE IF NOT EXISTS group_memberships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    group_id UUID REFERENCES community_groups(id),
    role VARCHAR(50) DEFAULT 'member', -- 'admin', 'moderator', 'member'
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, group_id)
);

-- Discussion Topics/Threads
CREATE TABLE IF NOT EXISTS discussion_topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_id UUID REFERENCES community_groups(id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(100), -- 'general', 'help', 'showcase', 'question'
    created_by UUID REFERENCES users(id),
    is_pinned BOOLEAN DEFAULT false,
    is_locked BOOLEAN DEFAULT false,
    reply_count INTEGER DEFAULT 0,
    last_reply_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Discussion Replies
CREATE TABLE IF NOT EXISTS discussion_replies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_id UUID REFERENCES discussion_topics(id),
    parent_reply_id UUID REFERENCES discussion_replies(id), -- for threaded replies
    content TEXT NOT NULL,
    created_by UUID REFERENCES users(id),
    edited_at TIMESTAMP WITH TIME ZONE,
    like_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Chat Messages
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_id UUID REFERENCES community_groups(id),
    sender_id UUID REFERENCES users(id),
    message_type VARCHAR(50) DEFAULT 'text', -- 'text', 'image', 'file', 'system'
    content TEXT NOT NULL,
    file_url VARCHAR(500),
    reply_to_id UUID REFERENCES chat_messages(id),
    edited_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Message Reactions
CREATE TABLE IF NOT EXISTS message_reactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID REFERENCES chat_messages(id),
    user_id UUID REFERENCES users(id),
    reaction VARCHAR(50) NOT NULL, -- emoji or reaction type
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(message_id, user_id, reaction)
);

-- User Profiles Extended
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    bio TEXT,
    avatar_url VARCHAR(500),
    location VARCHAR(200),
    languages_spoken TEXT[],
    cultural_interests TEXT[],
    contribution_count INTEGER DEFAULT 0,
    community_points INTEGER DEFAULT 0,
    badges TEXT[],
    is_verified BOOLEAN DEFAULT false,
    social_links JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Community Challenges
CREATE TABLE IF NOT EXISTS community_challenges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    challenge_type VARCHAR(100), -- 'preservation', 'documentation', 'creative'
    requirements JSONB,
    rewards JSONB,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    participant_count INTEGER DEFAULT 0,
    submission_count INTEGER DEFAULT 0,
    created_by UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Challenge Participations
CREATE TABLE IF NOT EXISTS challenge_participations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    challenge_id UUID REFERENCES community_challenges(id),
    user_id UUID REFERENCES users(id),
    submission_content_id UUID REFERENCES content_metadata(id),
    submission_notes TEXT,
    status VARCHAR(50) DEFAULT 'submitted', -- 'submitted', 'reviewed', 'winner'
    points_earned INTEGER DEFAULT 0,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(challenge_id, user_id)
);

-- Activity Feed
CREATE TABLE IF NOT EXISTS activity_feed (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    activity_type VARCHAR(100) NOT NULL,
    activity_data JSONB,
    target_id UUID, -- can reference various entities
    target_type VARCHAR(50), -- 'content', 'discussion', 'challenge', etc.
    is_public BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for community features
CREATE INDEX IF NOT EXISTS idx_community_groups_type ON community_groups(group_type);
CREATE INDEX IF NOT EXISTS idx_community_groups_category ON community_groups(group_category);
CREATE INDEX IF NOT EXISTS idx_group_memberships_user ON group_memberships(user_id);
CREATE INDEX IF NOT EXISTS idx_group_memberships_group ON group_memberships(group_id);
CREATE INDEX IF NOT EXISTS idx_discussion_topics_group ON discussion_topics(group_id);
CREATE INDEX IF NOT EXISTS idx_discussion_topics_created_at ON discussion_topics(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_discussion_replies_topic ON discussion_replies(topic_id);
CREATE INDEX IF NOT EXISTS idx_discussion_replies_parent ON discussion_replies(parent_reply_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_group ON chat_messages(group_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_message_reactions_message ON message_reactions(message_id);
CREATE INDEX IF NOT EXISTS idx_challenge_participations_challenge ON challenge_participations(challenge_id);
CREATE INDEX IF NOT EXISTS idx_challenge_participations_user ON challenge_participations(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_feed_user ON activity_feed(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_feed_created_at ON activity_feed(created_at DESC);

-- Create triggers for updated_at
CREATE TRIGGER update_community_groups_updated_at 
    BEFORE UPDATE ON community_groups 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_discussion_topics_updated_at 
    BEFORE UPDATE ON discussion_topics 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at 
    BEFORE UPDATE ON user_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default community groups
INSERT INTO community_groups (name, description, group_type, group_category, is_public) VALUES
-- Regional Groups
('West Bengal Heritage', 'Preserving the rich cultural heritage of West Bengal', 'regional', 'West Bengal', true),
('Tamil Nadu Traditions', 'Documenting Tamil culture and traditions', 'regional', 'Tamil Nadu', true),
('Rajasthan Folk Culture', 'Rajasthani folk music, dance, and traditions', 'regional', 'Rajasthan', true),
('Kerala Arts & Culture', 'Kerala''s unique art forms and cultural practices', 'regional', 'Kerala', true),
('Punjab Heritage', 'Punjabi culture, music, and traditions', 'regional', 'Punjab', true),

-- Language Groups
('Hindi Heritage Hub', 'Content and discussions in Hindi', 'language', 'Hindi', true),
('Bengali Cultural Circle', 'Bengali language and culture', 'language', 'Bengali', true),
('Tamil Cultural Forum', 'Tamil language heritage and traditions', 'language', 'Tamil', true),
('Telugu Traditions', 'Telugu culture and heritage', 'language', 'Telugu', true),
('Marathi Mandal', 'Marathi cultural preservation', 'language', 'Marathi', true),

-- Interest Groups
('Folk Music Preservation', 'Documenting and preserving traditional folk music', 'interest', 'Music', true),
('Festival Celebrations', 'Indian festivals and their cultural significance', 'interest', 'Festivals', true),
('Traditional Recipes', 'Preserving family recipes and cooking traditions', 'interest', 'Food', true),
('Handicrafts & Arts', 'Traditional crafts and artistic techniques', 'interest', 'Arts', true),
('Oral Storytelling', 'Preserving stories passed down through generations', 'interest', 'Stories', true),
('Classical Dance Forms', 'Indian classical and folk dance traditions', 'interest', 'Dance', true),
('Traditional Games', 'Indigenous games and sports', 'interest', 'Games', true)
ON CONFLICT DO NOTHING;

-- Insert sample challenges
INSERT INTO community_challenges (title, description, challenge_type, requirements, rewards, start_date, end_date, is_active) VALUES
('Diwali Stories Collection', 'Share your family''s unique Diwali traditions and stories', 'documentation', 
 '{"min_content": 1, "content_types": ["text", "audio"], "languages": ["any"]}',
 '{"points": 100, "badge": "Festival Storyteller", "recognition": "Featured on homepage"}',
 CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '30 days', true),

('Regional Folk Songs Archive', 'Record and preserve folk songs from your region', 'preservation',
 '{"min_content": 3, "content_types": ["audio"], "requirements": ["original_recording", "lyrics_transcription"]}',
 '{"points": 200, "badge": "Music Preserver", "recognition": "Community spotlight"}',
 CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '60 days', true),

('Traditional Recipe Documentation', 'Document family recipes with stories behind them', 'creative',
 '{"min_content": 5, "content_types": ["text", "image"], "requirements": ["recipe_details", "cultural_context"]}',
 '{"points": 150, "badge": "Recipe Keeper", "recognition": "Recipe collection feature"}',
 CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '45 days', true)
ON CONFLICT DO NOTHING;

-- Log successful initialization
INSERT INTO analytics_events (event_type, metadata) VALUES 
('database_initialized', '{"timestamp": "' || CURRENT_TIMESTAMP || '", "version": "2.0.0", "community_features": true}');

COMMIT;