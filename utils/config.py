#!/usr/bin/env python3
"""
Configuration Module

This module handles all environment variable configuration for the email automation project.
It loads variables from .env file and provides them to other modules.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class that loads and provides access to environment variables."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4')
    OPENAI_TEMPERATURE: float = float(os.getenv('OPENAI_TEMPERATURE', '0.1'))
    OPENAI_MAX_TOKENS: int = int(os.getenv('OPENAI_MAX_TOKENS', '1000'))
    
    # Gmail Configuration
    GMAIL_AUTH_CONFIG_DIR: str = os.getenv('GMAIL_AUTH_CONFIG_DIR', './temp_data')
    GMAIL_CREDENTIALS_FILE: str = os.getenv('GMAIL_CREDENTIALS_FILE', './credentials.json')
    
    # Application Configuration
    MAX_EMAILS: int = int(os.getenv('MAX_EMAILS', '200'))
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    CUSTOM_CATEGORIES_FILE: str = os.getenv('CUSTOM_CATEGORIES_FILE', './configs/email_categories.json')
    
    @classmethod
    def validate_required_config(cls) -> bool:
        """
        Validate that all required configuration is present.
        
        Returns:
            bool: True if all required config is present, False otherwise
        """
        required_vars = [
            ('OPENAI_API_KEY', cls.OPENAI_API_KEY),
        ]
        
        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing_vars.append(var_name)
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            print("Please check your .env file and ensure all required variables are set.")
            return False
        
        return True
    
    @classmethod
    def print_config_summary(cls) -> None:
        """Print a summary of the current configuration."""
        print("📋 Configuration Summary:")
        print(f"  OpenAI Model: {cls.OPENAI_MODEL}")
        print(f"  OpenAI Temperature: {cls.OPENAI_TEMPERATURE}")
        print(f"  OpenAI Max Tokens: {cls.OPENAI_MAX_TOKENS}")
        print(f"  Max Emails: {cls.MAX_EMAILS}")
        print(f"  Debug Mode: {cls.DEBUG}")
        print(f"  Gmail Config Dir: {cls.GMAIL_AUTH_CONFIG_DIR}")
        print(f"  Gmail Credentials: {cls.GMAIL_CREDENTIALS_FILE}")
        print(f"  Categories File: {cls.CUSTOM_CATEGORIES_FILE}")
        print(f"  OpenAI API Key: {'✅ Set' if cls.OPENAI_API_KEY else '❌ Missing'}")
    
    @classmethod
    def get_openai_config(cls) -> dict:
        """Get OpenAI configuration as a dictionary."""
        return {
            'api_key': cls.OPENAI_API_KEY,
            'model': cls.OPENAI_MODEL,
            'temperature': cls.OPENAI_TEMPERATURE,
            'max_tokens': cls.OPENAI_MAX_TOKENS
        }
    
    @classmethod
    def get_gmail_config(cls) -> dict:
        """Get Gmail configuration as a dictionary."""
        return {
            'credentials_file': cls.GMAIL_CREDENTIALS_FILE,
            'config_dir': cls.GMAIL_AUTH_CONFIG_DIR
        }
    
    @classmethod
    def get_app_config(cls) -> dict:
        """Get application configuration as a dictionary."""
        return {
            'max_emails': cls.MAX_EMAILS,
            'debug': cls.DEBUG,
            'categories_file': cls.CUSTOM_CATEGORIES_FILE
        }


# Create a global config instance
config = Config()
