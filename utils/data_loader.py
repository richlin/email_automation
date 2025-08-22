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
        Load email data from JSON files in the temp_data folder.
        
        Args:
            folder_path: Path to the folder containing email data files
            
        Returns:
            List of email dictionaries formatted for classification
        """
        if not os.path.exists(folder_path):
            self.logger.error(f"temp_data folder not found: {folder_path}")
            return []
        
        # Find all JSON files in the folder
        json_files = glob.glob(os.path.join(folder_path, "*.json"))
        
        if not json_files:
            self.logger.error(f"No JSON files found in {folder_path}")
            return []
        
        all_emails = []
        
        for json_file in json_files:
            try:
                self.logger.info(f"Loading email data from: {json_file}")
                
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract messages from the JSON structure
                messages = data.get('messages', [])
                
                if not messages:
                    self.logger.warning(f"No messages found in {json_file}")
                    continue
                
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
                
                self.logger.info(f"Loaded {len(messages)} emails from {json_file}")
                
            except Exception as e:
                self.logger.error(f"Error loading {json_file}: {str(e)}")
                continue
        
        self.logger.info(f"Total emails loaded: {len(all_emails)}")
        return all_emails
    
    def load_from_gmail_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert Gmail API message format to classification format.
        
        Args:
            messages: List of messages from Gmail API
            
        Returns:
            List of email dictionaries formatted for classification
        """
        formatted_emails = []
        
        for message in messages:
            # Extract headers
            headers = message.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
            
            # Extract content
            content = self._extract_message_content(message)
            
            email_data = {
                'subject': subject,
                'sender': sender,
                'content': content,
                'labels': message.get('labelIds', []),
                'date': date,
                'id': message.get('id', ''),
                'thread_id': message.get('threadId', '')
            }
            formatted_emails.append(email_data)
        
        return formatted_emails
    
    def _extract_message_content(self, message: Dict[str, Any]) -> str:
        """
        Extract text content from Gmail message structure.
        
        Args:
            message: Gmail API message object
            
        Returns:
            Extracted text content
        """
        def extract_from_part(part):
            if part.get('mimeType') == 'text/plain':
                return part.get('body', {}).get('data', '')
            elif part.get('mimeType') == 'text/html':
                return part.get('body', {}).get('data', '')
            elif 'parts' in part:
                for subpart in part['parts']:
                    content = extract_from_part(subpart)
                    if content:
                        return content
            return ''
        
        payload = message.get('payload', {})
        
        # Try to extract from payload
        if payload.get('mimeType') == 'text/plain':
            return payload.get('body', {}).get('data', '')
        elif payload.get('mimeType') == 'text/html':
            return payload.get('body', {}).get('data', '')
        elif 'parts' in payload:
            for part in payload['parts']:
                content = extract_from_part(part)
                if content:
                    return content
        
        # Fallback to snippet
        return message.get('snippet', '')
    
    def save_email_data(self, emails: List[Dict[str, Any]], 
                       output_path: Optional[str] = None) -> str:
        """
        Save email data to a JSON file.
        
        Args:
            emails: List of email dictionaries
            output_path: Optional output path, defaults to temp_data folder
            
        Returns:
            Path to the saved file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"temp_data/email_data_{timestamp}.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_messages': len(emails),
            'messages': emails
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Saved {len(emails)} emails to {output_path}")
        return output_path


def load_email_data_from_temp_data(folder_path: str = "temp_data") -> List[Dict[str, Any]]:
    """
    Convenience function to load email data from temp_data folder.
    
    Args:
        folder_path: Path to the folder containing email data files
        
    Returns:
        List of email dictionaries formatted for classification
    """
    loader = EmailDataLoader()
    return loader.load_from_temp_data(folder_path)


def convert_gmail_messages_to_classification_format(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convenience function to convert Gmail API messages to classification format.
    
    Args:
        messages: List of messages from Gmail API
        
    Returns:
        List of email dictionaries formatted for classification
    """
    loader = EmailDataLoader()
    return loader.load_from_gmail_messages(messages)
