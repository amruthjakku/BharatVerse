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

-- Log successful initialization
INSERT INTO analytics_events (event_type, metadata) VALUES 
('database_initialized', '{"timestamp": "' || CURRENT_TIMESTAMP || '", "version": "2.0.0"}');

COMMIT;