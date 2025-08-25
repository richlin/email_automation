"""
Gmail Authentication Module

This module provides secure authentication to Gmail using OAuth 2.0.
It handles token management, refresh, and secure storage of credentials.

Requirements:
- google-auth-oauthlib
- google-auth-httplib2
- google-api-python-client
- cryptography (for secure token storage)

Usage:
    auth = GmailAuthenticator()
    service = auth.authenticate()
"""

import os
import json
import pickle
import base64
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from .config import config


class GmailAuthenticator:
    """
    Handles Gmail OAuth 2.0 authentication with secure token storage.
    
    Features:
    - OAuth 2.0 authentication flow
    - Automatic token refresh
    - Encrypted token storage
    - Support for multiple accounts
    - Secure credential management
    """
    
    # Gmail API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.labels'
    ]
    
    def __init__(self, 
                 credentials_file: Optional[str] = None,
                 token_file: str = 'token.pickle',
                 encrypted_token_file: str = 'encrypted_token.json',
                 config_dir: Optional[str] = None):
        """
        Initialize the Gmail authenticator.
        
        Args:
            credentials_file: Path to OAuth 2.0 credentials JSON file. If not provided, uses GMAIL_CREDENTIALS_FILE from .env
            token_file: Path to store unencrypted tokens (for development)
            encrypted_token_file: Path to store encrypted tokens (production)
            config_dir: Directory to store configuration files. If not provided, uses GMAIL_AUTH_CONFIG_DIR from .env
        """
        # Use environment variables if not provided
        self.credentials_file = config.GMAIL_CREDENTIALS_FILE
        self.token_file = token_file
        self.encrypted_token_file = encrypted_token_file
        self.config_dir = Path(config_dir or config.GMAIL_AUTH_CONFIG_DIR)
        self.config_dir.mkdir(exist_ok=True)
        
        # Encryption key for secure token storage
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Multiple account support
        self.accounts: Dict[str, Credentials] = {}
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for secure token storage."""
        key_file = self.config_dir / 'encryption.key'
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate a new encryption key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def _encrypt_token(self, token_data: Dict[str, Any]) -> str:
        """Encrypt token data for secure storage."""
        token_json = json.dumps(token_data)
        encrypted_data = self.cipher_suite.encrypt(token_json.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def _decrypt_token(self, encrypted_token: str) -> Dict[str, Any]:
        """Decrypt token data from secure storage."""
        encrypted_data = base64.b64decode(encrypted_token.encode())
        decrypted_data = self.cipher_suite.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())
    
    def _save_encrypted_token(self, account_id: str, credentials: Credentials):
        """Save encrypted token to secure storage."""
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'expiry': credentials.expiry.isoformat() if credentials.expiry else None
        }
        
        encrypted_token = self._encrypt_token(token_data)
        
        # Load existing tokens
        tokens_file = self.config_dir / self.encrypted_token_file
        if tokens_file.exists():
            with open(tokens_file, 'r') as f:
                all_tokens = json.load(f)
        else:
            all_tokens = {}
        
        # Update tokens
        all_tokens[account_id] = encrypted_token
        
        # Save back to file
        with open(tokens_file, 'w') as f:
            json.dump(all_tokens, f, indent=2)
    
    def _load_encrypted_token(self, account_id: str) -> Optional[Credentials]:
        """Load encrypted token from secure storage."""
        tokens_file = self.config_dir / self.encrypted_token_file
        
        if not tokens_file.exists():
            return None
        
        try:
            with open(tokens_file, 'r') as f:
                all_tokens = json.load(f)
            
            if account_id not in all_tokens:
                return None
            
            encrypted_token = all_tokens[account_id]
            token_data = self._decrypt_token(encrypted_token)
            
            # Convert expiry string back to datetime
            if token_data.get('expiry'):
                token_data['expiry'] = datetime.fromisoformat(token_data['expiry'])
            
            return Credentials(**token_data)
            
        except Exception as e:
            print(f"Error loading encrypted token: {e}")
            return None
    
    def _save_token(self, account_id: str, credentials: Credentials):
        """Save token to file (for development/testing)."""
        token_file = self.config_dir / f"{account_id}_{self.token_file}"
        with open(token_file, 'wb') as token:
            pickle.dump(credentials, token)
    
    def _load_token(self, account_id: str) -> Optional[Credentials]:
        """Load token from file (for development/testing)."""
        token_file = self.config_dir / f"{account_id}_{self.token_file}"
        
        if not token_file.exists():
            return None
        
        try:
            with open(token_file, 'rb') as token:
                return pickle.load(token)
        except Exception as e:
            print(f"Error loading token: {e}")
            return None
    
    def authenticate(self, 
                    account_id: str = 'default',
                    force_reauth: bool = False,
                    use_encryption: bool = True) -> Optional[Any]:
        """
        Authenticate with Gmail API.
        
        Args:
            account_id: Unique identifier for the account
            force_reauth: Force re-authentication even if token exists
            use_encryption: Use encrypted token storage (recommended for production)
            
        Returns:
            Gmail API service object or None if authentication fails
        """
        credentials = None
        
        # Try to load existing credentials
        if not force_reauth:
            if use_encryption:
                credentials = self._load_encrypted_token(account_id)
            else:
                credentials = self._load_token(account_id)
        
        # If no valid credentials available, let the user log in
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    credentials = None
            
            if not credentials:
                credentials = self._authenticate_user(account_id)
                if not credentials:
                    return None
        
        # Save credentials for future use
        if use_encryption:
            self._save_encrypted_token(account_id, credentials)
        else:
            self._save_token(account_id, credentials)
        
        # Store in memory for quick access
        self.accounts[account_id] = credentials
        
        try:
            # Build the Gmail service
            service = build('gmail', 'v1', credentials=credentials)
            return service
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
    
    def _authenticate_user(self, account_id: str) -> Optional[Credentials]:
        """Perform OAuth 2.0 authentication flow."""
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"Credentials file '{self.credentials_file}' not found. "
                "Please download it from Google Cloud Console."
            )
        
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_file, self.SCOPES
        )
        
        try:
            credentials = flow.run_local_server(port=0)
            return credentials
        except Exception as e:
            print(f"Authentication failed: {e}")
            return None
    

    
    def test_connection(self, service) -> bool:
        """Test the Gmail API connection."""
        try:
            # Try to get user profile
            profile = service.users().getProfile(userId='me').execute()
            print(f"Successfully connected to Gmail account: {profile.get('emailAddress')}")
            return True
        except HttpError as error:
            print(f'Connection test failed: {error}')
            return False
    
    def get_user_info(self, service) -> Optional[Dict[str, Any]]:
        """Get user profile information."""
        try:
            profile = service.users().getProfile(userId='me').execute()
            return {
                'email': profile.get('emailAddress'),
                'name': profile.get('name'),
                'messages_total': profile.get('messagesTotal'),
                'threads_total': profile.get('threadsTotal'),
                'history_id': profile.get('historyId')
            }
        except HttpError as error:
            print(f'Error getting user info: {error}')
            return None



