#!/usr/bin/env python3
"""
Setup script for BharatVerse Community Features
Initializes database tables and creates sample data
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from core.database import DatabaseManager
from core.community_service import CommunityService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_community_database():
    """Setup community database tables and sample data"""
    try:
        logger.info("Initializing database manager...")
        db_manager = DatabaseManager()
        
        logger.info("Creating community service...")
        community_service = CommunityService(db_manager)
        
        logger.info("Community database setup completed successfully!")
        logger.info("You can now use the community features in BharatVerse")
        
        # Display some stats
        try:
            groups = community_service.get_all_groups()
            challenges = community_service.get_active_challenges()
            
            logger.info(f"Found {len(groups)} community groups")
            logger.info(f"Found {len(challenges)} active challenges")
            
            # Display groups by type
            group_types = {}
            for group in groups:
                group_type = group['group_type']
                if group_type not in group_types:
                    group_types[group_type] = []
                group_types[group_type].append(group['name'])
            
            for group_type, group_names in group_types.items():
                logger.info(f"{group_type.title()} groups: {', '.join(group_names)}")
                
        except Exception as e:
            logger.warning(f"Could not fetch community stats: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup community database: {e}")
        return False

def main():
    """Main setup function"""
    print("🤝 BharatVerse Community Setup")
    print("=" * 40)
    
    if setup_community_database():
        print("✅ Community features setup completed successfully!")
        print("\nYou can now:")
        print("- Join regional, language, and interest-based groups")
        print("- Participate in real-time chat")
        print("- Start and join discussions")
        print("- Take part in community challenges")
        print("- View leaderboards and profiles")
        print("\nStart the application and navigate to the Community page to begin!")
    else:
        print("❌ Community setup failed. Please check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()