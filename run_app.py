#!/usr/bin/env python3
"""
Launcher script for the Email Automation Streamlit App
"""

import subprocess
import sys
import os

# Import config to validate environment variables
from utils.config import config

def main():
    """Launch the Streamlit app."""
    print("🚀 Starting Email Automation Dashboard...")
    
    # Validate configuration before starting
    if not config.validate_required_config():
        print("❌ Configuration Error: Missing required environment variables.")
        print("Please check your .env file and ensure all required variables are set.")
        sys.exit(1)
    
    # Print configuration summary
    config.print_config_summary()
    
    print("📧 Streamlit app will open in your browser")
    print("🌐 URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the app")
    print("-" * 50)
    
    try:
        # Run the Streamlit app
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running app: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install it with: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main()
