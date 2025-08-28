"""
User Manager Module for BharatVerse
Handles user data management and operations
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class UserManager:
    """Manages user data and operations"""
    
    def __init__(self):
        """Initialize user manager"""
        self.contributions_cache = {}
        self.users_cache = {}
    
    def get_user_contributions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all contributions for a specific user
        
        Args:
            user_id: The user ID to get contributions for
            
        Returns:
            List of contribution dictionaries
        """
        try:
            # Check cache first
            if user_id in self.contributions_cache:
                return self.contributions_cache[user_id]
            
            # Mock data for now - in production this would query the database
            mock_contributions = [
                {
                    'id': f'contrib_1_{user_id}',
                    'user_id': user_id,
                    'type': 'text',
                    'title': 'Traditional Bengali Wedding Rituals',
                    'description': 'A detailed account of wedding ceremonies in Bengal',
                    'created_at': '2024-01-15T10:30:00Z',
                    'status': 'published',
                    'tags': ['wedding', 'bengali', 'tradition']
                },
                {
                    'id': f'contrib_2_{user_id}',
                    'user_id': user_id,
                    'type': 'audio',
                    'title': 'Folk Songs of Punjab',
                    'description': 'Collection of traditional Punjabi folk songs',
                    'created_at': '2024-01-20T14:45:00Z',
                    'status': 'published',
                    'tags': ['music', 'punjabi', 'folk']
                },
                {
                    'id': f'contrib_3_{user_id}',
                    'user_id': user_id,
                    'type': 'visual',
                    'title': 'Rangoli Patterns from Gujarat',
                    'description': 'Traditional rangoli designs for festivals',
                    'created_at': '2024-02-01T09:15:00Z',
                    'status': 'published',
                    'tags': ['art', 'gujarati', 'festival']
                }
            ]
            
            # Cache the results
            self.contributions_cache[user_id] = mock_contributions
            return mock_contributions
            
        except Exception as e:
            logger.error(f"Error getting user contributions: {e}")
            return []
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get statistics for a user
        
        Args:
            user_id: The user ID
            
        Returns:
            Dictionary with user statistics
        """
        try:
            contributions = self.get_user_contributions(user_id)
            
            # Calculate statistics
            stats = {
                'total_contributions': len(contributions),
                'contributions_by_type': {},
                'recent_activity': [],
                'popular_tags': []
            }
            
            # Count by type
            for contrib in contributions:
                contrib_type = contrib.get('type', 'other')
                if contrib_type not in stats['contributions_by_type']:
                    stats['contributions_by_type'][contrib_type] = 0
                stats['contributions_by_type'][contrib_type] += 1
            
            # Get recent activity (last 5)
            stats['recent_activity'] = contributions[:5] if contributions else []
            
            # Extract popular tags
            all_tags = []
            for contrib in contributions:
                all_tags.extend(contrib.get('tags', []))
            
            # Count tag frequency
            tag_counts = {}
            for tag in all_tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # Get top 5 tags
            stats['popular_tags'] = sorted(tag_counts.items(), 
                                         key=lambda x: x[1], 
                                         reverse=True)[:5]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            return {
                'total_contributions': 0,
                'contributions_by_type': {},
                'recent_activity': [],
                'popular_tags': []
            }
    
    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """
        Update user profile information
        
        Args:
            user_id: The user ID
            profile_data: Dictionary with profile updates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # In production, this would update the database
            # For now, just cache the update
            if user_id not in self.users_cache:
                self.users_cache[user_id] = {}
            
            self.users_cache[user_id].update(profile_data)
            self.users_cache[user_id]['updated_at'] = datetime.now().isoformat()
            
            logger.info(f"Updated profile for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return False
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user preferences
        
        Args:
            user_id: The user ID
            
        Returns:
            Dictionary with user preferences
        """
        try:
            # Default preferences
            default_prefs = {
                'email_notifications': True,
                'public_profile': True,
                'show_contributions': True,
                'language': 'en',
                'theme': 'light',
                'default_content_type': ['audio', 'text', 'visual'],
                'preferred_regions': []
            }
            
            # Check if user has custom preferences
            if user_id in self.users_cache and 'preferences' in self.users_cache[user_id]:
                default_prefs.update(self.users_cache[user_id]['preferences'])
            
            return default_prefs
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {}
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences
        
        Args:
            user_id: The user ID
            preferences: Dictionary with preference updates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if user_id not in self.users_cache:
                self.users_cache[user_id] = {}
            
            if 'preferences' not in self.users_cache[user_id]:
                self.users_cache[user_id]['preferences'] = {}
            
            self.users_cache[user_id]['preferences'].update(preferences)
            
            logger.info(f"Updated preferences for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return False
    
    def delete_contribution(self, user_id: str, contribution_id: str) -> bool:
        """
        Delete a user contribution
        
        Args:
            user_id: The user ID
            contribution_id: The contribution ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if user_id in self.contributions_cache:
                self.contributions_cache[user_id] = [
                    c for c in self.contributions_cache[user_id]
                    if c.get('id') != contribution_id
                ]
            
            logger.info(f"Deleted contribution {contribution_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting contribution: {e}")
            return False
    
    def get_user_by_gitlab_id(self, gitlab_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by GitLab ID
        
        Args:
            gitlab_id: The GitLab user ID
            
        Returns:
            User dictionary or None if not found
        """
        try:
            # In production, this would query the database
            # For now, return mock data
            mock_user = {
                'id': f'user_{gitlab_id}',
                'gitlab_id': gitlab_id,
                'created_at': datetime.now().isoformat(),
                'role': 'contributor'
            }
            
            return mock_user
            
        except Exception as e:
            logger.error(f"Error getting user by GitLab ID: {e}")
            return None

# Create a global instance
user_manager = UserManager()
