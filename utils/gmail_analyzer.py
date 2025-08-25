#!/usr/bin/env python3
"""
Gmail Analyzer Module

This module provides utility functions for analyzing Gmail data.
It includes:
1. Email fetching and metadata extraction
2. Pattern analysis and statistics
3. Label management
4. Message categorization utilities
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.gmail_auth import GmailAuthenticator
from utils.config import config


class GmailAnalyzer:
    """Utility class for analyzing Gmail data and extracting insights."""
    
    def __init__(self):
        self.auth = GmailAuthenticator()
        self.service = None
        self.user_info = None
    
    def authenticate(self) -> bool:
        """Authenticate with Gmail and get user info."""
        print("🔐 Authenticating with Gmail...")
        
        try:
            self.service = self.auth.authenticate(use_encryption=True)
            
            if not self.service:
                print("❌ Authentication failed!")
                return False
            
            # Test connection
            if not self.auth.test_connection(self.service):
                print("❌ Connection test failed!")
                return False
            
            # Get user information
            self.user_info = self.auth.get_user_info(self.service)
            if self.user_info:
                print(f"✅ Connected to: {self.user_info['email']}")
                print(f"📊 Total messages: {self.user_info['messages_total']:,}")
                print(f"🧵 Total threads: {self.user_info['threads_total']:,}")
            
            return True
            
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def get_recent_messages(self, max_results: int = 10, skip_archived: bool = True) -> List[Dict[str, Any]]:
        """Get recent messages with full content."""
        if not self.service:
            print("❌ Not authenticated!")
            return []
        
        try:
            print(f"📨 Fetching last {max_results} messages with full content...")
            
            # Get message IDs - only from INBOX if skip_archived is True
            if skip_archived:
                print("📬 Filtering to only include non-archived emails (INBOX label)...")
                results = self.service.users().messages().list(
                    userId='me',
                    maxResults=max_results,
                    labelIds=['INBOX']  # Only get messages with INBOX label
                ).execute()
            else:
                results = self.service.users().messages().list(
                    userId='me',
                    maxResults=max_results
                ).execute()
            
            messages = results.get('messages', [])
            if not messages:
                print("📭 No messages found")
                return []
            
            # Get detailed message information with full content
            detailed_messages = []
            for message in messages:
                msg_detail = self.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()
                
                # Extract headers
                headers = msg_detail['payload']['headers']
                from_header = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                subject_header = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                date_header = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                
                # Extract full email content
                full_content = self._extract_email_content(msg_detail['payload'])
                
                detailed_messages.append({
                    'id': message['id'],
                    'threadId': message['threadId'],
                    'from': from_header,
                    'subject': subject_header,
                    'date': date_header,
                    # 'snippet': msg_detail.get('snippet', ''),
                    'full_content': full_content,
                    'labelIds': msg_detail.get('labelIds', [])
                })
            
            return detailed_messages
            
        except Exception as e:
            print(f"❌ Error fetching messages: {e}")
            return []
    
    def _extract_email_content(self, payload: Dict[str, Any]) -> str:
        """Extract the full email content from the payload."""
        try:
            # Handle multipart messages
            if 'parts' in payload:
                content = ""
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/plain':
                        # Get plain text content
                        if 'data' in part['body']:
                            import base64
                            content += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                        elif 'attachmentId' in part['body']:
                            content += f"[Attachment: {part.get('filename', 'Unknown')}]"
                    elif part.get('mimeType') == 'text/html':
                        # Get HTML content if no plain text
                        if 'data' in part['body'] and not content:
                            import base64
                            html_content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                            # Simple HTML to text conversion
                            import re
                            content = re.sub(r'<[^>]+>', '', html_content)
                            content = re.sub(r'\s+', ' ', content).strip()
                        elif 'attachmentId' in part['body']:
                            content += f"[HTML Attachment: {part.get('filename', 'Unknown')}]"
                    elif 'parts' in part:
                        # Recursively handle nested parts
                        content += self._extract_email_content(part)
                return content
            
            # Handle simple text messages
            elif payload.get('mimeType') == 'text/plain':
                if 'data' in payload['body']:
                    import base64
                    return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
                else:
                    return "[No content available]"
            
            # Handle HTML messages
            elif payload.get('mimeType') == 'text/html':
                if 'data' in payload['body']:
                    import base64
                    html_content = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
                    # Simple HTML to text conversion
                    import re
                    content = re.sub(r'<[^>]+>', '', html_content)
                    return re.sub(r'\s+', ' ', content).strip()
                else:
                    return "[No content available]"
            
            # Handle other content types
            else:
                return f"[Content type: {payload.get('mimeType', 'Unknown')}]"
                
        except Exception as e:
            return f"[Error extracting content: {str(e)}]"
    
    def analyze_message_patterns(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze basic patterns in messages."""
        if not messages:
            return {}
        
        analysis = {
            'total_messages': len(messages),
            'senders': {},
            'labels': {},
            'subjects': {},
            'date_patterns': {}
        }
        
        for msg in messages:
            # Count senders
            sender = msg['from']
            analysis['senders'][sender] = analysis['senders'].get(sender, 0) + 1
            
            # Count labels
            for label in msg['labelIds']:
                analysis['labels'][label] = analysis['labels'].get(label, 0) + 1
                    
        return analysis
    

            

    
    def add_labels_to_message(self, message_id: str, label_ids: List[str]) -> bool:
        """
        Add labels to a specific email message.
        
        Args:
            message_id (str): The ID of the email message
            label_ids (List[str]): List of label IDs to add to the message
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.service:
            print("❌ Not authenticated!")
            return False
        
        if not label_ids:
            print("❌ No label IDs provided!")
            return False
        
        try:
            print(f"🏷️  Adding labels to message {message_id}...")
            
            # Modify the message to add labels
            result = self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': label_ids}
            ).execute()
            
            print(f"✅ Successfully added labels to message {message_id}")
            print(f"📧 Message now has labels: {result.get('labelIds', [])}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding labels to message: {e}")
            return False
    

    
    def create_label(self, label_name: str, label_list_visibility: str = 'labelShow', 
                    message_list_visibility: str = 'show') -> Dict[str, Any]:
        """
        Create a new Gmail label.
        
        Args:
            label_name (str): Name of the label to create
            label_list_visibility (str): Visibility of the label in the label list
            message_list_visibility (str): Visibility of the label in the message list
            
        Returns:
            Dict[str, Any]: The created label object or empty dict if failed
        """
        if not self.service:
            print("❌ Not authenticated!")
            return {}
        
        try:
            # Check if label already exists first
            existing_label = self.find_label_by_name(label_name)
            if existing_label:
                print(f"ℹ️  Label '{label_name}' already exists (ID: {existing_label['id']})")
                return existing_label
            
            print(f"🏷️  Creating new label: {label_name}")
            
            label_object = {
                'name': label_name,
                'labelListVisibility': label_list_visibility,
                'messageListVisibility': message_list_visibility
            }
            
            result = self.service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()
            
            print(f"✅ Successfully created label: {result['name']} (ID: {result['id']})")
            return result
            
        except Exception as e:
            print(f"❌ Error creating label: {e}")
            return {}
    
    def find_label_by_name(self, label_name: str) -> Dict[str, Any]:
        """
        Find a label by its name.
        
        Args:
            label_name (str): Name of the label to find
            
        Returns:
            Dict[str, Any]: The label object if found, empty dict otherwise
        """
        if not self.service:
            print("❌ Not authenticated!")
            return {}
        
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            for label in labels:
                if label['name'].lower() == label_name.lower():
                    return label
            
            print(f"❌ Label '{label_name}' not found")
            return {}
            
        except Exception as e:
            print(f"❌ Error finding label: {e}")
            return {}
    
    def add_labels_by_name(self, message_id: str, label_names: List[str]) -> bool:
        """
        Add labels to a message by label names (not IDs).
        
        Args:
            message_id (str): The ID of the email message
            label_names (List[str]): List of label names to add to the message
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not label_names:
            print("❌ No label names provided!")
            return False
        
        label_ids = []
        for label_name in label_names:
            label = self.find_label_by_name(label_name)
            if label:
                label_ids.append(label['id'])
                print(f"✅ Found label '{label_name}' with ID: {label['id']}")
            else:
                print(f"❌ Label '{label_name}' not found, skipping...")
        
        if label_ids:
            return self.add_labels_to_message(message_id, label_ids)
        else:
            print("❌ No valid labels found to add!")
            return False
    

    
    def archive_messages_by_label(self, label_name: str, dry_run: bool = True) -> Dict[str, Any]:
        """
        Archive all messages within a specific label by removing the INBOX label.
        
        Args:
            label_name (str): Name of the label to archive messages from
            dry_run (bool): If True, only show what would be archived without actually archiving
            
        Returns:
            Dict[str, Any]: Results of the operation including count of messages found/archived
        """
        if not self.service:
            print("❌ Not authenticated!")
            return {'success': False, 'error': 'Not authenticated'}
        
        try:
            # Find the label by name
            label = self.find_label_by_name(label_name)
            if not label:
                return {'success': False, 'error': f'Label "{label_name}" not found'}
            
            label_id = label['id']
            print(f"🏷️  Found label '{label_name}' with ID: {label_id}")
            
            # Get all messages with this label
            print(f"📨 Searching for messages with label '{label_name}'...")
            results = self.service.users().messages().list(
                userId='me',
                labelIds=[label_id]
            ).execute()
            
            messages = results.get('messages', [])
            message_count = len(messages)
            
            if message_count == 0:
                print(f"📭 No messages found with label '{label_name}'")
                return {'success': True, 'messages_found': 0, 'messages_archived': 0}
            
            print(f"📊 Found {message_count} messages with label '{label_name}'")
            
            if dry_run:
                print(f"🔍 DRY RUN: Would archive {message_count} messages")
                print("   (Set dry_run=False to actually archive)")
                
                # Show first few messages for preview
                print("\n📋 Preview of messages that would be archived:")
                for i, msg in enumerate(messages[:5]):
                    try:
                        msg_detail = self.service.users().messages().get(
                            userId='me',
                            id=msg['id'],
                            format='metadata',
                            metadataHeaders=['From', 'Subject', 'Date']
                        ).execute()
                        
                        headers = msg_detail['payload']['headers']
                        from_header = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                        subject_header = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                        
                        print(f"   {i+1}. From: {from_header}")
                        print(f"      Subject: {subject_header}")
                        print(f"      ID: {msg['id']}")
                        print()
                        
                    except Exception as e:
                        print(f"   {i+1}. Error getting message details: {e}")
                
                if message_count > 5:
                    print(f"   ... and {message_count - 5} more messages")
                
                return {
                    'success': True, 
                    'messages_found': message_count, 
                    'messages_archived': 0,
                    'dry_run': True
                }
            
            else:
                # Actually archive the messages by removing INBOX label
                print(f"📦 Archiving {message_count} messages...")
                archived_count = 0
                
                for msg in messages:
                    try:
                        # Remove the INBOX label to archive the message
                        result = self.service.users().messages().modify(
                            userId='me',
                            id=msg['id'],
                            body={'removeLabelIds': ['INBOX']}
                        ).execute()
                        
                        archived_count += 1
                        
                        if archived_count % 10 == 0:  # Progress update every 10 messages
                            print(f"   Progress: {archived_count}/{message_count} messages archived")
                            
                    except Exception as e:
                        print(f"❌ Error archiving message {msg['id']}: {e}")
                
                print(f"✅ Successfully archived {archived_count}/{message_count} messages")
                
                return {
                    'success': True,
                    'messages_found': message_count,
                    'messages_archived': archived_count,
                    'dry_run': False
                }
                
        except Exception as e:
            print(f"❌ Error archiving messages by label: {e}")
            return {'success': False, 'error': str(e)}
    

    

