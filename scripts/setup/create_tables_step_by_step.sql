-- 🗄️ BharatVerse Tables - Execute Each Block Separately

-- BLOCK 1: Users Table
-- Copy and run this first:
CREATE TABLE users (
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

-- BLOCK 2: Contributions Table  
-- Copy and run this second:
CREATE TABLE contributions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    content TEXT,
    content_type VARCHAR(50),
    file_url TEXT,
    file_type VARCHAR(100),
    file_size INTEGER,
    language VARCHAR(50),
    region VARCHAR(100),
    tags TEXT[],
    metadata JSONB DEFAULT '{}',
    ai_analysis JSONB DEFAULT '{}',
    is_public BOOLEAN DEFAULT true,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- BLOCK 3: Analytics Table
-- Copy and run this third:
CREATE TABLE analytics (
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

-- BLOCK 4: Community Interactions Table
-- Copy and run this fourth:
CREATE TABLE community_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    target_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    contribution_id INTEGER REFERENCES contributions(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- BLOCK 5: Create Indexes
-- Copy and run this fifth:
CREATE INDEX idx_contributions_user_id ON contributions(user_id);
CREATE INDEX idx_contributions_language ON contributions(language);
CREATE INDEX idx_contributions_region ON contributions(region);
CREATE INDEX idx_contributions_content_type ON contributions(content_type);
CREATE INDEX idx_contributions_created_at ON contributions(created_at);
CREATE INDEX idx_analytics_user_id ON analytics(user_id);
CREATE INDEX idx_analytics_event_type ON analytics(event_type);
CREATE INDEX idx_analytics_created_at ON analytics(created_at);

-- BLOCK 6: Insert Demo User
-- Copy and run this last:
INSERT INTO users (username, email, full_name, provider, role) 
VALUES ('demo_user', 'demo@bharatverse.com', 'Demo User', 'demo', 'user');

-- BLOCK 7: Verify Setup
-- Copy and run this to verify:
SELECT 'All tables created successfully!' as status;
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE' 
ORDER BY table_name;