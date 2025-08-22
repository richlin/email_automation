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
    
    def get_recent_messages(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages with full content."""
        if not self.service:
            print("❌ Not authenticated!")
            return []
        
        try:
            print(f"📨 Fetching last {max_results} messages with full content...")
            
            # Get message IDs
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
            
            # Analyze subjects (simple keyword extraction)
            subject = msg['subject'].lower()
            words = subject.split()
            for word in words[:5]:  # First 5 words
                if len(word) > 3:  # Skip short words
                    analysis['subjects'][word] = analysis['subjects'].get(word, 0) + 1
        
        return analysis
    
    def display_analysis(self, analysis: Dict[str, Any]):
        """Display the analysis results."""
        print("\n📊 Message Analysis Results")
        print("=" * 50)
        
        print(f"📨 Total messages analyzed: {analysis['total_messages']}")
        
        # Top senders
        print(f"\n👥 Top senders:")
        top_senders = sorted(analysis['senders'].items(), key=lambda x: x[1], reverse=True)[:5]
        for sender, count in top_senders:
            print(f"   {sender}: {count} messages")
        
        # Top labels
        print(f"\n🏷️  Most common labels:")
        top_labels = sorted(analysis['labels'].items(), key=lambda x: x[1], reverse=True)[:5]
        for label, count in top_labels:
            print(f"   {label}: {count} messages")
        
        # Top subject words
        print(f"\n📝 Most common subject words:")
        top_words = sorted(analysis['subjects'].items(), key=lambda x: x[1], reverse=True)[:10]
        for word, count in top_words:
            print(f"   '{word}': {count} occurrences")
    
    def get_labels(self) -> List[Dict[str, Any]]:
        """Get all Gmail labels."""
        if not self.service:
            return []
        
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            print(f"\n🏷️  Found {len(labels)} labels:")
            for label in labels[:10]:  # Show first 10
                print(f"   - {label['name']} (ID: {label['id']})")
            
            if len(labels) > 10:
                print(f"   ... and {len(labels) - 10} more")
            
            return labels
            
        except Exception as e:
            print(f"❌ Error fetching labels: {e}")
            return []
    

