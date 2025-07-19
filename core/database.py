"""
Database connection and management for BharatVerse
Handles PostgreSQL (metadata), MinIO (files), and Redis (cache)
"""

import os
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

# Database imports
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.pool import SimpleConnectionPool
import redis
from minio import Minio
from minio.error import S3Error

# Configuration
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration"""
    # PostgreSQL
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "bharatverse")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secure_password")
    
    # MinIO
    MINIO_HOST = os.getenv("MINIO_HOST", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"
    
    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
    
    # Buckets
    AUDIO_BUCKET = "bharatverse-audio"
    VIDEO_BUCKET = "bharatverse-video"
    IMAGE_BUCKET = "bharatverse-images"
    DOCUMENT_BUCKET = "bharatverse-documents"


class DatabaseManager:
    """Manages all database connections"""
    
    def __init__(self):
        self.config = DatabaseConfig()
        self._postgres_pool = None
        self._minio_client = None
        self._redis_client = None
        self._disabled = os.getenv('DISABLE_DATABASE', 'false').lower() == 'true'
        
        if not self._disabled:
            self._initialize_connections()
        else:
            logger.info("Database connections disabled (running in UI-only mode)")
    
    def _initialize_connections(self):
        """Initialize all database connections"""
        try:
            # PostgreSQL connection pool
            self._postgres_pool = SimpleConnectionPool(
                1, 20,  # min and max connections
                host=self.config.POSTGRES_HOST,
                port=self.config.POSTGRES_PORT,
                database=self.config.POSTGRES_DB,
                user=self.config.POSTGRES_USER,
                password=self.config.POSTGRES_PASSWORD
            )
            
            # MinIO client
            self._minio_client = Minio(
                self.config.MINIO_HOST,
                access_key=self.config.MINIO_ACCESS_KEY,
                secret_key=self.config.MINIO_SECRET_KEY,
                secure=self.config.MINIO_SECURE
            )
            
            # Redis client
            self._redis_client = redis.Redis(
                host=self.config.REDIS_HOST,
                port=self.config.REDIS_PORT,
                db=self.config.REDIS_DB,
                password=self.config.REDIS_PASSWORD,
                decode_responses=True
            )
            
            # Initialize MinIO buckets
            self._initialize_buckets()
            
            # Initialize PostgreSQL schema
            self._initialize_schema()
            
            logger.info("All database connections initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connections: {e}")
            print(f"\nFailed to initialize database connections: {e}")
            if self._disabled:
                logger.info("Running in UI-only mode without database")
            else:
                raise
    
    def _initialize_buckets(self):
        """Create MinIO buckets if they don't exist"""
        buckets = [
            self.config.AUDIO_BUCKET,
            self.config.VIDEO_BUCKET,
            self.config.IMAGE_BUCKET,
            self.config.DOCUMENT_BUCKET
        ]
        
        for bucket in buckets:
            try:
                if not self._minio_client.bucket_exists(bucket):
                    self._minio_client.make_bucket(bucket)
                    logger.info(f"Created bucket: {bucket}")
            except S3Error as e:
                logger.error(f"Failed to create bucket {bucket}: {e}")
    
    def _initialize_schema(self):
        """Initialize PostgreSQL schema"""
        schema_sql = """
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            full_name VARCHAR(200),
            region VARCHAR(100),
            preferred_language VARCHAR(10),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Content metadata table
        CREATE TABLE IF NOT EXISTS content_metadata (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id VARCHAR(100),
            content_type VARCHAR(50) NOT NULL, -- audio, video, image, text
            title VARCHAR(500) NOT NULL,
            description TEXT,
            language VARCHAR(50),
            region VARCHAR(100),
            tags TEXT[],
            file_url TEXT,
            file_size BIGINT,
            duration_seconds INTEGER, -- for audio/video
            transcription TEXT,
            translation TEXT,
            ai_analysis JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_content_type ON content_metadata(content_type);
        CREATE INDEX IF NOT EXISTS idx_language ON content_metadata(language);
        CREATE INDEX IF NOT EXISTS idx_region ON content_metadata(region);
        CREATE INDEX IF NOT EXISTS idx_tags ON content_metadata USING gin(tags);
        CREATE INDEX IF NOT EXISTS idx_created_at ON content_metadata(created_at DESC);
        
        -- Full text search
        CREATE INDEX IF NOT EXISTS idx_content_search ON content_metadata 
        USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '') || ' ' || COALESCE(transcription, '')));
        
        -- Activity log
        CREATE TABLE IF NOT EXISTS activity_log (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id VARCHAR(100),
            action VARCHAR(100) NOT NULL,
            content_id UUID REFERENCES content_metadata(id),
            details JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Community Groups (Regional, Language, Interest-based)
        CREATE TABLE IF NOT EXISTS community_groups (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id),
            group_id UUID REFERENCES community_groups(id),
            role VARCHAR(50) DEFAULT 'member', -- 'admin', 'moderator', 'member'
            joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, group_id)
        );

        -- Discussion Topics/Threads
        CREATE TABLE IF NOT EXISTS discussion_topics (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
        """
        
        conn = self.get_postgres_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(schema_sql)
                conn.commit()
            logger.info("PostgreSQL schema initialized")
        finally:
            self.release_postgres_connection(conn)
    
    def get_postgres_connection(self):
        """Get a connection from the pool"""
        if self._disabled:
            raise RuntimeError("Database is disabled in UI-only mode")
        return self._postgres_pool.getconn()
    
    def release_postgres_connection(self, conn):
        """Release connection back to pool"""
        if not self._disabled and conn:
            self._postgres_pool.putconn(conn)
    
    @property
    def minio(self):
        """Get MinIO client"""
        if self._disabled:
            return None
        return self._minio_client
    
    @property
    def redis(self):
        """Get Redis client"""
        if self._disabled:
            return None
        return self._redis_client
    
    def close_all(self):
        """Close all connections"""
        if self._postgres_pool:
            self._postgres_pool.closeall()
        logger.info("All database connections closed")


class ContentRepository:
    """Repository for content operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def save_content(self, content_type: str, file_data: bytes, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Save content with metadata"""
        content_id = str(uuid.uuid4())
        
        # Determine bucket based on content type
        bucket_map = {
            'audio': self.db.config.AUDIO_BUCKET,
            'video': self.db.config.VIDEO_BUCKET,
            'image': self.db.config.IMAGE_BUCKET,
            'text': self.db.config.DOCUMENT_BUCKET
        }
        bucket = bucket_map.get(content_type, self.db.config.DOCUMENT_BUCKET)
        
        # Generate file name
        file_extension = metadata.get('file_extension', 'bin')
        file_name = f"{content_id}.{file_extension}"
        
        try:
            # Upload to MinIO
            if file_data:
                self.db.minio.put_object(
                    bucket,
                    file_name,
                    file_data,
                    len(file_data),
                    metadata={'content_id': content_id}
                )
                file_url = f"/{bucket}/{file_name}"
            else:
                file_url = None
            
            # Save metadata to PostgreSQL
            conn = self.db.get_postgres_connection()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        INSERT INTO content_metadata (
                            id, user_id, content_type, title, description,
                            language, region, tags, file_url, file_size,
                            duration_seconds, transcription, translation, ai_analysis
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        ) RETURNING *
                    """, (
                        content_id,
                        metadata.get('user_id'),
                        content_type,
                        metadata.get('title', 'Untitled'),
                        metadata.get('description'),
                        metadata.get('language'),
                        metadata.get('region'),
                        metadata.get('tags', []),
                        file_url,
                        len(file_data) if file_data else None,
                        metadata.get('duration_seconds'),
                        metadata.get('transcription'),
                        metadata.get('translation'),
                        Json(metadata.get('ai_analysis', {}))
                    ))
                    result = cursor.fetchone()
                    conn.commit()
                    
                    # Cache in Redis
                    self._cache_content(result)
                    
                    return dict(result)
                    
            finally:
                self.db.release_postgres_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to save content: {e}")
            raise
    
    def get_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID"""
        # Check Redis cache first
        cached = self.db.redis.get(f"content:{content_id}")
        if cached:
            return json.loads(cached)
        
        # Get from PostgreSQL
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM content_metadata WHERE id = %s",
                    (content_id,)
                )
                result = cursor.fetchone()
                if result:
                    result = dict(result)
                    self._cache_content(result)
                return result
        finally:
            self.db.release_postgres_connection(conn)
    
    def search_content(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search content with filters"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Build query
                base_query = """
                    SELECT * FROM content_metadata
                    WHERE to_tsvector('english', title || ' ' || COALESCE(description, '') || ' ' || COALESCE(transcription, ''))
                    @@ plainto_tsquery('english', %s)
                """
                params = [query]
                
                # Add filters
                if filters:
                    if filters.get('content_type'):
                        base_query += " AND content_type = %s"
                        params.append(filters['content_type'])
                    if filters.get('language'):
                        base_query += " AND language = %s"
                        params.append(filters['language'])
                    if filters.get('region'):
                        base_query += " AND region = %s"
                        params.append(filters['region'])
                
                base_query += " ORDER BY created_at DESC LIMIT 50"
                
                cursor.execute(base_query, params)
                results = cursor.fetchall()
                return [dict(r) for r in results]
                
        finally:
            self.db.release_postgres_connection(conn)
    
    def _cache_content(self, content: Dict[str, Any]):
        """Cache content in Redis"""
        if content and content.get('id'):
            # Convert datetime objects to strings
            for key in ['created_at', 'updated_at']:
                if key in content and isinstance(content[key], datetime):
                    content[key] = content[key].isoformat()
            
            self.db.redis.setex(
                f"content:{content['id']}",
                3600,  # 1 hour TTL
                json.dumps(content)
            )


# Singleton instance
db_manager = DatabaseManager()
content_repo = ContentRepository(db_manager)
