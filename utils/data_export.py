"""
Email Export Utilities

This module provides functionality for exporting email data to various formats.
"""

import json
import os
from datetime import datetime


def save_email_data_to_json(messages):
    """Save email data to JSON format in temp_data folder."""
    # Create temp_data directory if it doesn't exist
    temp_data_dir = "temp_data"
    if not os.path.exists(temp_data_dir):
        os.makedirs(temp_data_dir)
        print(f"📁 Created directory: {temp_data_dir}")
    
    # Prepare data for JSON output
    email_data = {
        "export_timestamp": datetime.now().isoformat(),
        "total_messages": len(messages),
        "messages": []
    }
    
    for msg in messages:
        email_data["messages"].append({
            "id": msg.get('id', ''),
            "from": msg.get('from', ''),
            "subject": msg.get('subject', ''),
            "date": msg.get('date', ''),
            "labels": msg.get('labelIds', []),
            "snippet": msg.get('snippet', ''),
            "full_content": msg.get('full_content', ''),
            "thread_id": msg.get('threadId', '')
        })
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"email_data_{timestamp}.json"
    filepath = os.path.join(temp_data_dir, filename)
    
    # Save to JSON file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(email_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Email data saved to: {filepath}")
        print(f"   Total messages exported: {len(messages)}")
    except Exception as e:
        print(f"❌ Error saving email data: {e}")
