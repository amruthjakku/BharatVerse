"""
Community Service for BharatVerse
Handles all community-related database operations including groups, discussions, chat, and challenges
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
import logging

import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.pool import SimpleConnectionPool

logger = logging.getLogger(__name__)


class CommunityService:
    """Service for community operations"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    # Group Management
    def get_all_groups(self, group_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all community groups, optionally filtered by type"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if group_type:
                    cursor.execute("""
                        SELECT g.*, COUNT(gm.user_id) as actual_member_count
                        FROM community_groups g
                        LEFT JOIN group_memberships gm ON g.id = gm.group_id
                        WHERE g.group_type = %s AND g.is_public = true
                        GROUP BY g.id
                        ORDER BY actual_member_count DESC, g.created_at DESC
                    """, (group_type,))
                else:
                    cursor.execute("""
                        SELECT g.*, COUNT(gm.user_id) as actual_member_count
                        FROM community_groups g
                        LEFT JOIN group_memberships gm ON g.id = gm.group_id
                        WHERE g.is_public = true
                        GROUP BY g.id
                        ORDER BY g.group_type, actual_member_count DESC
                    """)
                return [dict(row) for row in cursor.fetchall()]
        finally:
            self.db.release_postgres_connection(conn)
    
    def get_user_groups(self, user_id: str) -> List[Dict[str, Any]]:
        """Get groups that a user is a member of"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Convert user_id to string to handle both UUID and integer IDs
                user_id_str = str(user_id)
                cursor.execute("""
                    SELECT g.*, gm.role, gm.joined_at,
                           COUNT(gm2.user_id) as actual_member_count
                    FROM community_groups g
                    JOIN group_memberships gm ON g.id = gm.group_id
                    LEFT JOIN group_memberships gm2 ON g.id = gm2.group_id
                    WHERE gm.user_id::text = %s
                    GROUP BY g.id, gm.role, gm.joined_at
                    ORDER BY gm.joined_at DESC
                """, (user_id_str,))
                return [dict(row) for row in cursor.fetchall()]
        finally:
            self.db.release_postgres_connection(conn)
    
    def join_group(self, user_id: str, group_id: str) -> bool:
        """Join a community group"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor() as cursor:
                # Convert user_id to string to handle both UUID and integer IDs
                user_id_str = str(user_id)
                cursor.execute("""
                    INSERT INTO group_memberships (user_id, group_id)
                    VALUES (%s::uuid, %s)
                    ON CONFLICT (user_id, group_id) DO NOTHING
                """, (user_id_str, group_id))
                
                # Update member count
                cursor.execute("""
                    UPDATE community_groups 
                    SET member_count = (
                        SELECT COUNT(*) FROM group_memberships WHERE group_id = %s
                    )
                    WHERE id = %s
                """, (group_id, group_id))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to join group: {e}")
            return False
        finally:
            self.db.release_postgres_connection(conn)
    
    def leave_group(self, user_id: str, group_id: str) -> bool:
        """Leave a community group"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor() as cursor:
                # Convert user_id to string to handle both UUID and integer IDs
                user_id_str = str(user_id)
                cursor.execute("""
                    DELETE FROM group_memberships 
                    WHERE user_id::text = %s AND group_id = %s
                """, (user_id_str, group_id))
                
                # Update member count
                cursor.execute("""
                    UPDATE community_groups 
                    SET member_count = (
                        SELECT COUNT(*) FROM group_memberships WHERE group_id = %s
                    )
                    WHERE id = %s
                """, (group_id, group_id))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to leave group: {e}")
            return False
        finally:
            self.db.release_postgres_connection(conn)
    
    # Discussion Management
    def get_discussion_topics(self, group_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get discussion topics for a group"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT dt.*, u.username as creator_name,
                           COUNT(dr.id) as actual_reply_count
                    FROM discussion_topics dt
                    LEFT JOIN users u ON dt.created_by = u.id
                    LEFT JOIN discussion_replies dr ON dt.id = dr.topic_id
                    WHERE dt.group_id = %s
                    GROUP BY dt.id, u.username
                    ORDER BY dt.is_pinned DESC, dt.last_reply_at DESC
                    LIMIT %s
                """, (group_id, limit))
                return [dict(row) for row in cursor.fetchall()]
        finally:
            self.db.release_postgres_connection(conn)
    
    def create_discussion_topic(self, group_id: str, user_id: str, title: str, 
                              description: str, category: str = 'general') -> Dict[str, Any]:
        """Create a new discussion topic"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO discussion_topics (group_id, title, description, category, created_by)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING *
                """, (group_id, title, description, category, user_id))
                result = dict(cursor.fetchone())
                conn.commit()
                
                # Log activity
                self._log_activity(user_id, 'discussion_created', {
                    'topic_id': result['id'],
                    'group_id': group_id,
                    'title': title
                }, result['id'], 'discussion')
                
                return result
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to create discussion topic: {e}")
            raise
        finally:
            self.db.release_postgres_connection(conn)
    
    def get_discussion_replies(self, topic_id: str) -> List[Dict[str, Any]]:
        """Get replies for a discussion topic"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT dr.*, u.username as author_name,
                           up.avatar_url as author_avatar
                    FROM discussion_replies dr
                    LEFT JOIN users u ON dr.created_by = u.id
                    LEFT JOIN user_profiles up ON dr.created_by = up.user_id
                    WHERE dr.topic_id = %s
                    ORDER BY dr.created_at ASC
                """, (topic_id,))
                return [dict(row) for row in cursor.fetchall()]
        finally:
            self.db.release_postgres_connection(conn)
    
    def add_discussion_reply(self, topic_id: str, user_id: str, content: str, 
                           parent_reply_id: Optional[str] = None) -> Dict[str, Any]:
        """Add a reply to a discussion topic"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO discussion_replies (topic_id, content, created_by, parent_reply_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING *
                """, (topic_id, content, user_id, parent_reply_id))
                result = dict(cursor.fetchone())
                
                # Update topic reply count and last reply time
                cursor.execute("""
                    UPDATE discussion_topics 
                    SET reply_count = reply_count + 1, last_reply_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (topic_id,))
                
                conn.commit()
                return result
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to add discussion reply: {e}")
            raise
        finally:
            self.db.release_postgres_connection(conn)
    
    # Chat Management
    def get_chat_messages(self, group_id: str, limit: int = 50, before_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get chat messages for a group"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if before_id:
                    cursor.execute("""
                        SELECT cm.*, u.username as sender_name,
                               up.avatar_url as sender_avatar,
                               COUNT(mr.id) as reaction_count
                        FROM chat_messages cm
                        LEFT JOIN users u ON cm.sender_id = u.id
                        LEFT JOIN user_profiles up ON cm.sender_id = up.user_id
                        LEFT JOIN message_reactions mr ON cm.id = mr.message_id
                        WHERE cm.group_id = %s AND cm.created_at < (
                            SELECT created_at FROM chat_messages WHERE id = %s
                        )
                        GROUP BY cm.id, u.username, up.avatar_url
                        ORDER BY cm.created_at DESC
                        LIMIT %s
                    """, (group_id, before_id, limit))
                else:
                    cursor.execute("""
                        SELECT cm.*, u.username as sender_name,
                               up.avatar_url as sender_avatar,
                               COUNT(mr.id) as reaction_count
                        FROM chat_messages cm
                        LEFT JOIN users u ON cm.sender_id = u.id
                        LEFT JOIN user_profiles up ON cm.sender_id = up.user_id
                        LEFT JOIN message_reactions mr ON cm.id = mr.message_id
                        WHERE cm.group_id = %s
                        GROUP BY cm.id, u.username, up.avatar_url
                        ORDER BY cm.created_at DESC
                        LIMIT %s
                    """, (group_id, limit))
                
                messages = [dict(row) for row in cursor.fetchall()]
                messages.reverse()  # Return in chronological order
                return messages
        finally:
            self.db.release_postgres_connection(conn)
    
    def send_chat_message(self, group_id: str, sender_id: str, content: str, 
                         message_type: str = 'text', file_url: Optional[str] = None,
                         reply_to_id: Optional[str] = None) -> Dict[str, Any]:
        """Send a chat message"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO chat_messages (group_id, sender_id, content, message_type, file_url, reply_to_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING *
                """, (group_id, sender_id, content, message_type, file_url, reply_to_id))
                result = dict(cursor.fetchone())
                conn.commit()
                return result
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to send chat message: {e}")
            raise
        finally:
            self.db.release_postgres_connection(conn)
    
    def add_message_reaction(self, message_id: str, user_id: str, reaction: str) -> bool:
        """Add a reaction to a message"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO message_reactions (message_id, user_id, reaction)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (message_id, user_id, reaction) DO NOTHING
                """, (message_id, user_id, reaction))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to add message reaction: {e}")
            return False
        finally:
            self.db.release_postgres_connection(conn)
    
    def remove_message_reaction(self, message_id: str, user_id: str, reaction: str) -> bool:
        """Remove a reaction from a message"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM message_reactions 
                    WHERE message_id = %s AND user_id = %s AND reaction = %s
                """, (message_id, user_id, reaction))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to remove message reaction: {e}")
            return False
        finally:
            self.db.release_postgres_connection(conn)
    
    # Challenge Management
    def get_active_challenges(self) -> List[Dict[str, Any]]:
        """Get all active community challenges"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT cc.*, u.username as creator_name,
                           COUNT(cp.user_id) as actual_participant_count
                    FROM community_challenges cc
                    LEFT JOIN users u ON cc.created_by = u.id
                    LEFT JOIN challenge_participations cp ON cc.id = cp.challenge_id
                    WHERE cc.is_active = true AND cc.end_date > CURRENT_TIMESTAMP
                    GROUP BY cc.id, u.username
                    ORDER BY cc.end_date ASC
                """)
                return [dict(row) for row in cursor.fetchall()]
        finally:
            self.db.release_postgres_connection(conn)
    
    def get_challenge_leaderboard(self, challenge_id: str) -> List[Dict[str, Any]]:
        """Get leaderboard for a specific challenge"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT cp.*, u.username, up.avatar_url,
                           cm.title as submission_title
                    FROM challenge_participations cp
                    LEFT JOIN users u ON cp.user_id = u.id
                    LEFT JOIN user_profiles up ON cp.user_id = up.user_id
                    LEFT JOIN content_metadata cm ON cp.submission_content_id = cm.id
                    WHERE cp.challenge_id = %s
                    ORDER BY cp.points_earned DESC, cp.submitted_at ASC
                """, (challenge_id,))
                return [dict(row) for row in cursor.fetchall()]
        finally:
            self.db.release_postgres_connection(conn)
    
    def participate_in_challenge(self, challenge_id: str, user_id: str, 
                               submission_content_id: str, submission_notes: str = '') -> Dict[str, Any]:
        """Participate in a challenge"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO challenge_participations 
                    (challenge_id, user_id, submission_content_id, submission_notes)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (challenge_id, user_id) 
                    DO UPDATE SET 
                        submission_content_id = EXCLUDED.submission_content_id,
                        submission_notes = EXCLUDED.submission_notes,
                        submitted_at = CURRENT_TIMESTAMP
                    RETURNING *
                """, (challenge_id, user_id, submission_content_id, submission_notes))
                result = dict(cursor.fetchone())
                
                # Update challenge participant count
                cursor.execute("""
                    UPDATE community_challenges 
                    SET participant_count = (
                        SELECT COUNT(DISTINCT user_id) 
                        FROM challenge_participations 
                        WHERE challenge_id = %s
                    )
                    WHERE id = %s
                """, (challenge_id, challenge_id))
                
                conn.commit()
                return result
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to participate in challenge: {e}")
            raise
        finally:
            self.db.release_postgres_connection(conn)
    
    # User Profile Management
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile with community stats"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT u.*, up.*,
                           COUNT(DISTINCT gm.group_id) as groups_joined,
                           COUNT(DISTINCT cm.id) as content_contributed,
                           COUNT(DISTINCT cp.challenge_id) as challenges_participated
                    FROM users u
                    LEFT JOIN user_profiles up ON u.id = up.user_id
                    LEFT JOIN group_memberships gm ON u.id = gm.user_id
                    LEFT JOIN content_metadata cm ON u.id = cm.user_id
                    LEFT JOIN challenge_participations cp ON u.id = cp.user_id
                    WHERE u.id = %s
                    GROUP BY u.id, up.user_id
                """, (user_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
        finally:
            self.db.release_postgres_connection(conn)
    
    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO user_profiles (
                        user_id, bio, avatar_url, location, languages_spoken, 
                        cultural_interests, social_links
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) 
                    DO UPDATE SET 
                        bio = EXCLUDED.bio,
                        avatar_url = EXCLUDED.avatar_url,
                        location = EXCLUDED.location,
                        languages_spoken = EXCLUDED.languages_spoken,
                        cultural_interests = EXCLUDED.cultural_interests,
                        social_links = EXCLUDED.social_links,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING *
                """, (
                    user_id,
                    profile_data.get('bio'),
                    profile_data.get('avatar_url'),
                    profile_data.get('location'),
                    profile_data.get('languages_spoken', []),
                    profile_data.get('cultural_interests', []),
                    Json(profile_data.get('social_links', {}))
                ))
                result = dict(cursor.fetchone())
                conn.commit()
                return result
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to update user profile: {e}")
            raise
        finally:
            self.db.release_postgres_connection(conn)
    
    def get_community_leaderboard(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get community leaderboard"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT u.username, up.avatar_url, up.location,
                           up.community_points, up.badges, up.contribution_count,
                           COUNT(DISTINCT gm.group_id) as groups_joined,
                           COUNT(DISTINCT cp.challenge_id) as challenges_won
                    FROM users u
                    LEFT JOIN user_profiles up ON u.id = up.user_id
                    LEFT JOIN group_memberships gm ON u.id = gm.user_id
                    LEFT JOIN challenge_participations cp ON u.id = cp.user_id AND cp.status = 'winner'
                    GROUP BY u.id, u.username, up.avatar_url, up.location, up.community_points, up.badges, up.contribution_count
                    ORDER BY up.community_points DESC, up.contribution_count DESC
                    LIMIT %s
                """, (limit,))
                return [dict(row) for row in cursor.fetchall()]
        finally:
            self.db.release_postgres_connection(conn)
    
    def get_user_activity_feed(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's activity feed"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT af.*, u.username
                    FROM activity_feed af
                    LEFT JOIN users u ON af.user_id = u.id
                    WHERE af.user_id = %s AND af.is_public = true
                    ORDER BY af.created_at DESC
                    LIMIT %s
                """, (user_id, limit))
                return [dict(row) for row in cursor.fetchall()]
        finally:
            self.db.release_postgres_connection(conn)
    
    def _log_activity(self, user_id: str, activity_type: str, activity_data: Dict[str, Any],
                     target_id: Optional[str] = None, target_type: Optional[str] = None):
        """Log user activity"""
        conn = self.db.get_postgres_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO activity_feed (user_id, activity_type, activity_data, target_id, target_type)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, activity_type, Json(activity_data), target_id, target_type))
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to log activity: {e}")
        finally:
            self.db.release_postgres_connection(conn)