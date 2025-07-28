"""
Supabase Database Manager for BharatVerse Cloud Deployment
Manages PostgreSQL operations via Supabase for user data and analytics

Module: supabase_db.py  
Purpose: Database operations and data persistence
- User account management and authentication
- Content storage (stories, contributions, metadata)
- Analytics tracking and usage statistics
- AI processing logs and performance metrics
"""
import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlalchemy as sa
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import Optional, Dict, List, Any
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages PostgreSQL database connections and operations"""
    
    def __init__(self):
        """Initialize database connection using Streamlit secrets"""
        try:
            # Get database configuration from secrets
            db_config = st.secrets.get("postgres", {})
            
            self.connection_params = {
                'host': db_config.get('host', 'localhost'),
                'port': db_config.get('port', 5432),
                'database': db_config.get('database', 'bharatverse'),
                'user': db_config.get('user', 'postgres'),
                'password': db_config.get('password', '')
            }
            
            # Create SQLAlchemy engine
            connection_string = (
                f"postgresql://{self.connection_params['user']}:"
                f"{self.connection_params['password']}@"
                f"{self.connection_params['host']}:"
                f"{self.connection_params['port']}/"
                f"{self.connection_params['database']}"
            )
            
            self.engine = create_engine(
                connection_string,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(bind=self.engine)
            
            # Initialize database schema
            self._init_schema()
            
            logger.info("Database Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            self.engine = None
            self.SessionLocal = None
    
    def _init_schema(self):
        """Initialize database schema with required tables"""
        try:
            with self.engine.connect() as conn:
                # Users table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        hashed_password TEXT NOT NULL,
                        full_name VARCHAR(100),
                        is_active BOOLEAN DEFAULT true,
                        is_admin BOOLEAN DEFAULT false,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Contributions table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS contributions (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        title VARCHAR(200) NOT NULL,
                        content TEXT,
                        content_type VARCHAR(50),
                        file_url TEXT,
                        file_type VARCHAR(50),
                        file_size INTEGER,
                        language VARCHAR(10),
                        region VARCHAR(100),
                        tags TEXT[],
                        metadata JSONB DEFAULT '{}',
                        ai_analysis JSONB DEFAULT '{}',
                        is_public BOOLEAN DEFAULT true,
                        views INTEGER DEFAULT 0,
                        likes INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Analytics table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS analytics (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                        action VARCHAR(100) NOT NULL,
                        resource_type VARCHAR(50),
                        resource_id INTEGER,
                        metadata JSONB DEFAULT '{}',
                        ip_address INET,
                        user_agent TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # AI Processing logs
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS ai_processing_logs (
                        id SERIAL PRIMARY KEY,
                        contribution_id INTEGER REFERENCES contributions(id) ON DELETE CASCADE,
                        model_name VARCHAR(100),
                        processing_type VARCHAR(50),
                        input_data JSONB,
                        output_data JSONB,
                        processing_time_ms INTEGER,
                        status VARCHAR(20),
                        error_message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Community interactions
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS community_interactions (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        target_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        contribution_id INTEGER REFERENCES contributions(id) ON DELETE CASCADE,
                        interaction_type VARCHAR(50), -- 'like', 'comment', 'share', 'follow'
                        content TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create indexes
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_contributions_user_id ON contributions(user_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_contributions_language ON contributions(language)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_contributions_region ON contributions(region)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_contributions_created_at ON contributions(created_at)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics(user_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_analytics_created_at ON analytics(created_at)"))
                
                conn.commit()
                logger.info("Database schema initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
    
    @contextmanager
    def get_connection(self):
        """Get database connection context manager"""
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            conn.autocommit = False
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def get_session(self):
        """Get SQLAlchemy session context manager"""
        if not self.SessionLocal:
            raise Exception("Database not initialized")
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def execute_query(self, query: str, params: Dict = None) -> List[Dict]:
        """Execute a query and return results"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, params or {})
                    if cursor.description:
                        return [dict(row) for row in cursor.fetchall()]
                    return []
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return []
    
    def execute_query_async(self, query: str, params: Dict = None):
        """Execute a query asynchronously"""
        from utils.threading_manager import get_threading_manager
        manager = get_threading_manager()
        return manager.submit_task(self.execute_query, query, params, task_name="db_query")
    
    def batch_insert(self, table: str, records: List[Dict], batch_size: int = 100):
        """Insert multiple records in batches with multithreading"""
        from utils.threading_manager import batch_process_files
        
        def insert_batch(batch_records):
            """Insert a batch of records"""
            if not batch_records:
                return 0
                
            # Build insert query
            if not batch_records:
                return 0
                
            columns = list(batch_records[0].keys())
            placeholders = ', '.join([f'%({col})s' for col in columns])
            query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            
            try:
                with self.get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.executemany(query, batch_records)
                        conn.commit()
                        return len(batch_records)
            except Exception as e:
                logger.error(f"Batch insert error: {e}")
                return 0
        
        # Split records into batches and process in parallel
        batches = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]
        results = batch_process_files(insert_batch, batches, batch_size=5)
        
        return sum(results)
    
    def parallel_query_execution(self, queries: List[tuple], max_workers: int = 5):
        """Execute multiple queries in parallel"""
        from utils.threading_manager import parallel_map
        
        def execute_single_query(query_data):
            query, params = query_data
            return self.execute_query(query, params)
        
        return parallel_map(execute_single_query, queries, max_workers=max_workers)
    
    def insert_user(self, username: str, email: str, hashed_password: str, 
                   full_name: str = None, is_admin: bool = False) -> Optional[int]:
        """Insert a new user"""
        query = """
            INSERT INTO users (username, email, hashed_password, full_name, is_admin)
            VALUES (%(username)s, %(email)s, %(hashed_password)s, %(full_name)s, %(is_admin)s)
            RETURNING id
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, {
                        'username': username,
                        'email': email,
                        'hashed_password': hashed_password,
                        'full_name': full_name,
                        'is_admin': is_admin
                    })
                    user_id = cursor.fetchone()[0]
                    conn.commit()
                    logger.info(f"User created successfully: {username}")
                    return user_id
        except Exception as e:
            logger.error(f"Failed to create user {username}: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        query = "SELECT * FROM users WHERE username = %(username)s AND is_active = true"
        users = self.execute_query(query, {'username': username})
        return users[0] if users else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        query = "SELECT * FROM users WHERE email = %(email)s AND is_active = true"
        users = self.execute_query(query, {'email': email})
        return users[0] if users else None
    
    def insert_contribution(self, user_id: int, title: str, content: str = None,
                          content_type: str = None, file_url: str = None,
                          file_type: str = None, file_size: int = None,
                          language: str = None, region: str = None,
                          tags: List[str] = None, metadata: Dict = None,
                          ai_analysis: Dict = None) -> Optional[int]:
        """Insert a new contribution"""
        query = """
            INSERT INTO contributions (
                user_id, title, content, content_type, file_url, file_type,
                file_size, language, region, tags, metadata, ai_analysis
            ) VALUES (
                %(user_id)s, %(title)s, %(content)s, %(content_type)s,
                %(file_url)s, %(file_type)s, %(file_size)s, %(language)s,
                %(region)s, %(tags)s, %(metadata)s, %(ai_analysis)s
            ) RETURNING id
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, {
                        'user_id': user_id,
                        'title': title,
                        'content': content,
                        'content_type': content_type,
                        'file_url': file_url,
                        'file_type': file_type,
                        'file_size': file_size,
                        'language': language,
                        'region': region,
                        'tags': tags or [],
                        'metadata': json.dumps(metadata or {}),
                        'ai_analysis': json.dumps(ai_analysis or {})
                    })
                    contribution_id = cursor.fetchone()[0]
                    conn.commit()
                    logger.info(f"Contribution created successfully: {title}")
                    return contribution_id
        except Exception as e:
            logger.error(f"Failed to create contribution {title}: {e}")
            return None
    
    def get_contributions(self, user_id: int = None, limit: int = 50, 
                         offset: int = 0) -> List[Dict]:
        """Get contributions with optional user filter"""
        base_query = """
            SELECT c.*, u.username, u.full_name
            FROM contributions c
            JOIN users u ON c.user_id = u.id
            WHERE c.is_public = true
        """
        
        if user_id:
            base_query += " AND c.user_id = %(user_id)s"
        
        base_query += " ORDER BY c.created_at DESC LIMIT %(limit)s OFFSET %(offset)s"
        
        params = {'limit': limit, 'offset': offset}
        if user_id:
            params['user_id'] = user_id
        
        return self.execute_query(base_query, params)
    
    def log_analytics(self, action: str, user_id: int = None,
                     resource_type: str = None, resource_id: int = None,
                     metadata: Dict = None, ip_address: str = None,
                     user_agent: str = None):
        """Log analytics event"""
        query = """
            INSERT INTO analytics (
                user_id, action, resource_type, resource_id,
                metadata, ip_address, user_agent
            ) VALUES (
                %(user_id)s, %(action)s, %(resource_type)s, %(resource_id)s,
                %(metadata)s, %(ip_address)s, %(user_agent)s
            )
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, {
                        'user_id': user_id,
                        'action': action,
                        'resource_type': resource_type,
                        'resource_id': resource_id,
                        'metadata': json.dumps(metadata or {}),
                        'ip_address': ip_address,
                        'user_agent': user_agent
                    })
                    conn.commit()
        except Exception as e:
            logger.error(f"Failed to log analytics: {e}")
    
    def get_analytics_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics statistics for the last N days"""
        query = """
            SELECT 
                action,
                COUNT(*) as count,
                COUNT(DISTINCT user_id) as unique_users
            FROM analytics
            WHERE created_at >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY action
            ORDER BY count DESC
        """
        
        try:
            stats = self.execute_query(query % days)
            return {
                'total_actions': sum(stat['count'] for stat in stats),
                'unique_users': len(set(stat['unique_users'] for stat in stats if stat['unique_users'])),
                'action_breakdown': stats
            }
        except Exception as e:
            logger.error(f"Failed to get analytics stats: {e}")
            return {}

# Global database manager instance
@st.cache_resource
def get_database_manager() -> DatabaseManager:
    """Get cached database manager instance"""
    return DatabaseManager()

# Convenience functions
def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user by username using global database manager"""
    db = get_database_manager()
    return db.get_user_by_username(username)

def insert_contribution(**kwargs) -> Optional[int]:
    """Insert contribution using global database manager"""
    db = get_database_manager()
    return db.insert_contribution(**kwargs)

def get_contributions(**kwargs) -> List[Dict]:
    """Get contributions using global database manager"""
    db = get_database_manager()
    return db.get_contributions(**kwargs)

def log_analytics(**kwargs):
    """Log analytics using global database manager"""
    db = get_database_manager()
    db.log_analytics(**kwargs)

# Enhanced cached database operations
@st.cache_data(ttl=1800, show_spinner=False)
def get_cached_contributions(user_id: int = None, limit: int = 50, offset: int = 0):
    """Get contributions with Streamlit caching"""
    db_manager = get_database_manager()
    if db_manager:
        return db_manager.get_contributions(user_id=user_id, limit=limit, offset=offset)
    return []

@st.cache_data(ttl=3600, show_spinner=False)
def get_cached_user_analytics(user_id: int):
    """Get user analytics with caching"""
    db_manager = get_database_manager()
    if db_manager:
        return db_manager.get_user_analytics(user_id)
    return {}

@st.cache_data(ttl=7200, show_spinner=False)
def get_cached_platform_stats():
    """Get platform-wide statistics with caching"""
    db_manager = get_database_manager()
    if not db_manager:
        return {}
    
    try:
        stats = {}
        
        # Total users
        result = db_manager.execute_query("SELECT COUNT(*) as count FROM users WHERE is_active = true")
        stats['total_users'] = result[0]['count'] if result else 0
        
        # Total contributions
        result = db_manager.execute_query("SELECT COUNT(*) as count FROM contributions WHERE is_public = true")
        stats['total_contributions'] = result[0]['count'] if result else 0
        
        # Languages represented
        result = db_manager.execute_query("SELECT COUNT(DISTINCT language) as count FROM contributions WHERE language IS NOT NULL")
        stats['languages_count'] = result[0]['count'] if result else 0
        
        # Regions covered
        result = db_manager.execute_query("SELECT COUNT(DISTINCT region) as count FROM contributions WHERE region IS NOT NULL")
        stats['regions_count'] = result[0]['count'] if result else 0
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get platform stats: {e}")
        return {}

# Analytics logging with batching
def log_analytics_batched(action: str, user_id: int = None, resource_type: str = None, 
                         resource_id: int = None, metadata: Dict = None):
    """Log analytics event with batching for better performance"""
    db_manager = get_database_manager()
    if not db_manager:
        return
    
    # Store in session state for batching
    if "analytics_batch" not in st.session_state:
        st.session_state.analytics_batch = []
    
    analytics_event = {
        "action": action,
        "user_id": user_id,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "metadata": metadata or {},
        "timestamp": datetime.now().isoformat()
    }
    
    st.session_state.analytics_batch.append(analytics_event)
    
    # Flush batch if it gets too large
    if len(st.session_state.analytics_batch) >= 10:
        flush_analytics_batch()

def flush_analytics_batch():
    """Flush analytics batch to database"""
    if "analytics_batch" not in st.session_state or not st.session_state.analytics_batch:
        return
    
    db_manager = get_database_manager()
    if not db_manager:
        return
    
    try:
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                for event in st.session_state.analytics_batch:
                    query = """
                        INSERT INTO analytics (action, user_id, resource_type, resource_id, metadata)
                        VALUES (%(action)s, %(user_id)s, %(resource_type)s, %(resource_id)s, %(metadata)s)
                    """
                    cursor.execute(query, {
                        'action': event['action'],
                        'user_id': event['user_id'],
                        'resource_type': event['resource_type'],
                        'resource_id': event['resource_id'],
                        'metadata': json.dumps(event['metadata'])
                    })
                
                conn.commit()
                logger.info(f"Flushed {len(st.session_state.analytics_batch)} analytics events")
                
        # Clear the batch
        st.session_state.analytics_batch = []
        
    except Exception as e:
        logger.error(f"Failed to flush analytics batch: {e}")

# Cleanup function to be called on app shutdown
def cleanup_database_connections():
    """Clean up database connections and flush pending analytics"""
    flush_analytics_batch()