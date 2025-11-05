"""
Email Export Utilities

This module provides functionality for exporting email data to various formats.
"""

import json
import os
import glob
import shutil
from datetime import datetime


def clean_email_data_folder():
    """Delete all existing email data files in temp_data/email_data folder."""
    temp_data_dir = "temp_data/email_data"
    
    if not os.path.exists(temp_data_dir):
        print(f"📁 Email data directory doesn't exist: {temp_data_dir}")
        return True, 0, []
    
    try:
        # Find all JSON files in the email_data directory
        json_files = glob.glob(os.path.join(temp_data_dir, "*.json"))
        
        if not json_files:
            print("📭 No existing email data files found to delete")
            return True, 0, []
        
        # Delete each file
        deleted_count = 0
        deleted_files = []
        for filepath in json_files:
            try:
                filename = os.path.basename(filepath)
                os.remove(filepath)
                deleted_count += 1
                deleted_files.append(filename)
                print(f"🗑️  Deleted: {filename}")
            except Exception as e:
                print(f"❌ Error deleting {filepath}: {e}")
        
        print(f"✅ Successfully deleted {deleted_count} email data files")
        return True, deleted_count, deleted_files
        
    except Exception as e:
        print(f"❌ Error cleaning email data folder: {e}")
        return False, 0, []


def save_email_data_to_json(messages):
    """Save email data to JSON format in temp_data folder."""
    # Create temp_data directory if it doesn't exist
    temp_data_dir = "temp_data/email_data"
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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"email_data_{timestamp}.json"
    filepath = os.path.join(temp_data_dir, filename)
    
    # Save to JSON file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(email_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Email data saved to: {filepath}")
        print(f"   Total messages exported: {len(messages)}")
        return filepath
    except Exception as e:
        print(f"❌ Error saving email data: {e}")
        return None


def load_classification_data(filename):
    """Load classification data from JSON file in configs folder."""
    filepath = os.path.join("configs", filename)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"📂 Classification data loaded from: {filepath}")
        return data
    except Exception as e:
        print(f"❌ Error loading classification data: {e}")
        return None








def list_category_files():
    """List all category JSON files in configs folder, sorted by modification time."""
    configs_dir = "configs"
    if not os.path.exists(configs_dir):
        return []
    
    # Find all JSON files in configs directory
    json_files = glob.glob(os.path.join(configs_dir, "*.json"))
    
    # Get file information and filter for category files
    file_list = []
    for filepath in json_files:
        try:
            # Check if this is a category file by reading its content
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Only include files that have category data
            if 'categories' in data and 'total_classifications' not in data:
                stat = os.stat(filepath)
                filename = os.path.basename(filepath)
                modified_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                
                file_list.append({
                    "filename": filename,
                    "filepath": filepath,
                    "modified": modified_time,
                    "size": stat.st_size,
                    "category_count": len(data.get('categories', []))
                })
        except Exception as e:
            print(f"❌ Error reading file {filepath}: {e}")
    
    # Sort by modification time (newest first)
    file_list.sort(key=lambda x: x["modified"], reverse=True)
    
    return file_list
