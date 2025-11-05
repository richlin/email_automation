#!/usr/bin/env python3
"""
Data Loading Utilities

This module provides functions to load email data from various sources
including JSON files, Gmail API, and other formats.
"""

import os
import json
import glob
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime


class EmailDataLoader:
    """
    Utility class for loading email data from different sources.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def load_from_temp_data(self, folder_path: str = "temp_data") -> List[Dict[str, Any]]:
        """
        Load email data from the latest JSON file in the email_data subfolder.
        
        Args:
            folder_path: Path to the temp_data folder
            
        Returns:
            List of email dictionaries formatted for classification
        """
        # Look specifically in the email_data subfolder
        email_data_path = os.path.join(folder_path, "email_data")
        
        if not os.path.exists(email_data_path):
            self.logger.error(f"email_data folder not found: {email_data_path}")
            return []
        
        # Find all JSON files in the email_data folder
        json_files = glob.glob(os.path.join(email_data_path, "*.json"))
        
        if not json_files:
            self.logger.error(f"No JSON files found in {email_data_path}")
            return []
        
        # Sort files by modification time to get the latest one
        latest_file = max(json_files, key=os.path.getmtime)
        self.logger.info(f"Loading from latest file: {latest_file}")
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract messages from the JSON structure
            messages = data.get('messages', [])
            
            if not messages:
                self.logger.warning(f"No messages found in {latest_file}")
                return []
            
            all_emails = []
            
            # Convert to the format expected by the classifier
            for message in messages:
                email_data = {
                    'subject': message.get('subject', ''),
                    'sender': message.get('from', ''),
                    'content': message.get('full_content', message.get('snippet', '')),
                    'full_content': message.get('full_content', message.get('snippet', '')),
                    'labels': message.get('labels', []),
                    'date': message.get('date', ''),
                    'id': message.get('id', ''),
                    'thread_id': message.get('thread_id', '')
                }
                all_emails.append(email_data)
            
            self.logger.info(f"Loaded {len(messages)} emails from {latest_file}")
            return all_emails
            
        except Exception as e:
            self.logger.error(f"Error loading {latest_file}: {str(e)}")
            return []
    

    



def load_email_data_from_temp_data(folder_path: str = "temp_data") -> List[Dict[str, Any]]:
    """
    Convenience function to load email data from the latest JSON file in email_data subfolder.
    
    Args:
        folder_path: Path to the temp_data folder
        
    Returns:
        List of email dictionaries formatted for classification
    """
    loader = EmailDataLoader()
    return loader.load_from_temp_data(folder_path)



