#!/usr/bin/env python3
"""
Email Classification Module using GPT-4.1-mini

This module provides functionality to classify email messages using OpenAI's GPT-4.1-mini model.
It can categorize emails into different types such as work, personal, spam, newsletters, etc.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any
from openai import OpenAI, AsyncOpenAI
from dataclasses import dataclass
from .config import config


@dataclass
class EmailClassification:
    """Data class to hold email classification results."""
    category: str
    confidence: float
    reasoning: str
    tags: List[str]
    priority: str  # high, medium, low
    action_required: bool


class EmailClassifier:
    """
    Email classifier using GPT-4.1-mini model.
    
    This class provides methods to classify email messages into different categories
    and extract relevant information for automation purposes.
    """
    
    def __init__(self, api_key: Optional[str] = None, config_file: Optional[str] = None):
        """
        Initialize the email classifier.
        
        Args:
            api_key: OpenAI API key. If not provided, will use OPENAI_API_KEY from .env file.
            config_file: Path to the JSON configuration file containing categories and settings.
                        If not provided, will use CUSTOM_CATEGORIES_FILE from .env file.
        """
        # Validate required configuration
        if not config.validate_required_config():
            raise ValueError("Required configuration is missing. Please check your .env file.")
        
        # Use provided API key or get from config
        self.api_key = api_key or config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY in .env file or pass api_key parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
        
        # Use provided config file or get from environment
        self.config_file = config_file or config.CUSTOM_CATEGORIES_FILE
        
        # Load configuration from JSON file
        self.config = self._load_config(self.config_file)
        
        # Define email categories and priorities from config
        self.categories = self.config.get('categories', [])
        self.priorities = self.config.get('priorities', [])
        self.model_config = self.config.get('model_config', {})
        
        if not self.categories:
            self.logger.warning("No categories found in config file, using defaults")
            self.categories = ["work_related", "personal", "newsletter", "spam", "billing", "social_media", "shopping", "travel", "health", "education", "other"]
        
        # Define priority levels
        self.priorities = ["high", "medium", "low"]
        
        # Define model configuration using environment variables
        self.model_config = {
            "model": config.OPENAI_MODEL,
            "temperature": config.OPENAI_TEMPERATURE,
            "max_tokens": config.OPENAI_MAX_TOKENS
        }
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        Args:
            config_file: Path to the JSON configuration file
            
        Returns:
            Dictionary containing configuration data
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
        """
        try:
            if not os.path.exists(config_file):
                self.logger.warning(f"Config file not found: {config_file}, using default configuration")
                return {}
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.logger.info(f"Loaded configuration from: {config_file}")
            return config
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file {config_file}: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading config file {config_file}: {str(e)}")
            raise
    
    def classify_email(self, 
                      subject: str, 
                      sender: str, 
                      content: str, 
                      labels: Optional[List[str]] = None) -> tuple[EmailClassification, Dict[str, Any]]:
        """
        Classify an email message using GPT-4.1-mini.
        
        Args:
            subject: Email subject line
            sender: Email sender address
            content: Email body content
            labels: Gmail labels (optional)
            
        Returns:
            Tuple of (EmailClassification object, token usage dict)
            
        Raises:
            Exception: If API call fails or response is invalid
        """
        try:
            # Prepare the prompt for classification
            prompt = self._create_classification_prompt(subject, sender, content, labels)
            
            # Make API call using configuration from JSON file
            model_config = self.model_config
            response = self.client.chat.completions.create(
                model=model_config.get('model', config.OPENAI_MODEL),
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert email classifier. Analyze emails and provide structured classification results."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=model_config.get('temperature', 0.1),  # Low temperature for consistent classification
                max_tokens=model_config.get('max_tokens', 3000)
            )
            
            # Parse the response
            result = self._parse_classification_response(response.choices[0].message.content)
            
            # Extract token usage
            token_usage = {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens,
                'model': response.model
            }
            
            self.logger.info(f"Email classified as: {result.category} (confidence: {result.confidence})")
            self.logger.info(f"Token usage: {token_usage['total_tokens']} total tokens")
            return result, token_usage
            
        except Exception as e:
            self.logger.error(f"Error classifying email: {str(e)}")
            raise
    
    async def classify_email_async(self, 
                      subject: str, 
                      sender: str, 
                      content: str, 
                      labels: Optional[List[str]] = None) -> tuple[EmailClassification, Dict[str, Any]]:
        """
        Async version of classify_email method.
        
        Args:
            subject: Email subject line
            sender: Email sender address
            content: Email body content
            labels: Gmail labels (optional)
            
        Returns:
            Tuple of (EmailClassification object, token usage dict)
            
        Raises:
            Exception: If API call fails or response is invalid
        """
        try:
            # Prepare the prompt for classification
            prompt = self._create_classification_prompt(subject, sender, content, labels)
            
            # Make async API call using configuration from JSON file
            model_config = self.model_config
            response = await self.async_client.chat.completions.create(
                model=model_config.get('model', config.OPENAI_MODEL),
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert email classifier. Analyze emails and provide structured classification results."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=model_config.get('temperature', 0.1),  # Low temperature for consistent classification
                max_tokens=model_config.get('max_tokens', 3000)
            )
            
            # Parse the response
            result = self._parse_classification_response(response.choices[0].message.content)
            
            # Extract token usage
            token_usage = {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens,
                'model': response.model
            }
            
            self.logger.info(f"Email classified as: {result.category} (confidence: {result.confidence})")
            self.logger.info(f"Token usage: {token_usage['total_tokens']} total tokens")
            return result, token_usage
            
        except Exception as e:
            self.logger.error(f"Error classifying email: {str(e)}")
            raise
    
    def discover_categories(self, 
                         subject: str, 
                         sender: str, 
                         content: str, 
                         labels: Optional[List[str]] = None) -> tuple[EmailClassification, Dict[str, Any]]:
        """
        Discover email categories using AI-generated categories (not predetermined).
        
        This method allows the AI to determine the most appropriate category based on the email content,
        without being constrained to a predefined list of categories.
        
        Args:
            subject: Email subject line
            sender: Email sender address
            content: Email body content
            labels: Gmail labels (optional)
            
        Returns:
            Tuple of (EmailClassification object, token usage dict)
            
        Raises:
            Exception: If API call fails or response is invalid
        """
        try:
            # Prepare the prompt for AI classification
            prompt = self._create_ai_classification_prompt(subject, sender, content, labels)
            
            # Make API call using configuration from JSON file
            model_config = self.model_config
            response = self.client.chat.completions.create(
                model=model_config.get('model', config.OPENAI_MODEL),
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert email classifier. Analyze emails and provide structured classification results with AI-generated categories."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=model_config.get('temperature', 0.1),
                max_tokens=model_config.get('max_tokens', 3000)
            )
            
            # Parse the response
            result = self._parse_ai_classification_response(response.choices[0].message.content)
            
            # Extract token usage
            token_usage = {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens,
                'model': response.model
            }
            
            # Save the AI-generated category to JSON file
            self._save_ai_category(result.category, result.confidence, result.reasoning, result.tags, result.priority, result.action_required)
            
            self.logger.info(f"Email classified with AI category: {result.category} (confidence: {result.confidence})")
            self.logger.info(f"Token usage: {token_usage['total_tokens']} total tokens")
            return result, token_usage
            
        except Exception as e:
            self.logger.error(f"Error classifying email with AI category: {str(e)}")
            raise
    
    def _create_ai_classification_prompt(self, 
                                       subject: str, 
                                       sender: str, 
                                       content: str, 
                                       labels: Optional[List[str]] = None) -> str:
        """
        Create a structured prompt for AI email classification.
        
        Args:
            subject: Email subject
            sender: Email sender
            content: Email content
            labels: Gmail labels
            
        Returns:
            Formatted prompt string
        """
        labels_str = f", Labels: {', '.join(labels)}" if labels else ""
        
        prompt = f"""
Please analyze the following email and provide a JSON response with the following structure:
{{
    "category": "a descriptive category name that best fits this email (2-3 words maximum, e.g., 'security_alert', 'meeting_invitation', 'invoice_notification', 'social_update', 'password_reset', 'newsletter_subscription', 'shipping_confirmation', 'appointment_reminder', 'payment_receipt', 'system_maintenance')",
    "confidence": "float between 0.0 and 1.0",
    "reasoning": "brief explanation of why this category was chosen",
    "tags": ["list", "of", "relevant", "tags"],
    "priority": "one of {', '.join(self.priorities)}",
    "action_required": "boolean"
}}

Email Details:
- Subject: {subject}
- Sender: {sender}{labels_str}
- Content: {content[:1000]}...  # Truncated for brevity

Please analyze the email content, sender, subject, and context to determine the most appropriate AI-generated category. 
The category MUST be 2-3 words maximum and should be descriptive and specific to the email's purpose or content type.
Use underscores to separate words (e.g., 'security_alert', 'meeting_invitation').
"""
        return prompt
    
    def _parse_ai_classification_response(self, response_text: str) -> EmailClassification:
        """
        Parse the GPT response for AI classification into an EmailClassification object.
        
        Args:
            response_text: Raw response from GPT model
            
        Returns:
            EmailClassification object
            
        Raises:
            ValueError: If response cannot be parsed
        """
        try:
            # Extract JSON from response (handle cases where response might have extra text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['category', 'confidence', 'reasoning', 'tags', 'priority', 'action_required']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate category length (2-3 words maximum)
            category = data['category']
            word_count = len(category.split('_'))
            if word_count < 2 or word_count > 3:
                raise ValueError(f"Category must be 2-3 words, got {word_count} words: '{category}'")
            
            # Validate priority (still use predefined priorities)
            if data['priority'] not in self.priorities:
                raise ValueError(f"Invalid priority: {data['priority']}")
            
            # Validate confidence
            confidence = float(data['confidence'])
            if not 0.0 <= confidence <= 1.0:
                raise ValueError(f"Confidence must be between 0.0 and 1.0, got: {confidence}")
            
            return EmailClassification(
                category=data['category'],
                confidence=confidence,
                reasoning=data['reasoning'],
                tags=data['tags'],
                priority=data['priority'],
                action_required=bool(data['action_required'])
            )
            
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"Failed to parse AI classification response: {str(e)}")
            self.logger.error(f"Response text: {response_text}")
            raise ValueError(f"Invalid AI classification response: {str(e)}")
    
    def _create_classification_prompt(self, 
                                    subject: str, 
                                    sender: str, 
                                    content: str, 
                                    labels: Optional[List[str]] = None) -> str:
        """
        Create a structured prompt for email classification.
        
        Args:
            subject: Email subject
            sender: Email sender
            content: Email content
            labels: Gmail labels
            
        Returns:
            Formatted prompt string
        """
        labels_str = f", Labels: {', '.join(labels)}" if labels else ""
        
        prompt = f"""
Please classify the following email and provide a JSON response with the following structure:
{{
    "category": "one of {', '.join(self.categories)}",
    "confidence": "float between 0.0 and 1.0",
    "reasoning": "brief explanation of classification",
    "tags": ["list", "of", "relevant", "tags"],
    "priority": "one of {', '.join(self.priorities)}",
    "action_required": "boolean"
}}

Email Details:
- Subject: {subject}
- Sender: {sender}{labels_str}
- Content: {content[:1000]}...  # Truncated for brevity

Please analyze the email content, sender, subject, and context to determine the most appropriate classification.
"""
        return prompt
    
    def _parse_classification_response(self, response_text: str) -> EmailClassification:
        """
        Parse the GPT response into an EmailClassification object.
        
        Args:
            response_text: Raw response from GPT model
            
        Returns:
            EmailClassification object
            
        Raises:
            ValueError: If response cannot be parsed
        """
        try:
            # Extract JSON from response (handle cases where response might have extra text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['category', 'confidence', 'reasoning', 'tags', 'priority', 'action_required']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate category
            if data['category'] not in self.categories:
                raise ValueError(f"Invalid category: {data['category']}")
            
            # Validate priority
            if data['priority'] not in self.priorities:
                raise ValueError(f"Invalid priority: {data['priority']}")
            
            # Validate confidence
            confidence = float(data['confidence'])
            if not 0.0 <= confidence <= 1.0:
                raise ValueError(f"Confidence must be between 0.0 and 1.0, got: {confidence}")
            
            return EmailClassification(
                category=data['category'],
                confidence=confidence,
                reasoning=data['reasoning'],
                tags=data['tags'],
                priority=data['priority'],
                action_required=bool(data['action_required'])
            )
            
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"Failed to parse classification response: {str(e)}")
            self.logger.error(f"Response text: {response_text}")
            raise ValueError(f"Invalid classification response: {str(e)}")
    

    

    
    def get_classification_summary(self, classifications: List[EmailClassification]) -> Dict[str, Any]:
        """
        Generate a summary of email classifications.
        
        Args:
            classifications: List of EmailClassification objects
            
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'total_emails': len(classifications),
            'category_distribution': {},
            'priority_distribution': {},
            'high_priority_count': 0,
            'action_required_count': 0,
            'average_confidence': 0.0
        }
        
        if not classifications:
            return summary
        
        # Calculate distributions
        for classification in classifications:
            # Category distribution
            category = classification.category
            summary['category_distribution'][category] = summary['category_distribution'].get(category, 0) + 1
            
            # Priority distribution
            priority = classification.priority
            summary['priority_distribution'][priority] = summary['priority_distribution'].get(priority, 0) + 1
            
            # Count high priority and action required
            if classification.priority == 'high':
                summary['high_priority_count'] += 1
            if classification.action_required:
                summary['action_required_count'] += 1
        
        # Calculate average confidence
        total_confidence = sum(c.confidence for c in classifications)
        summary['average_confidence'] = total_confidence / len(classifications)
        
        return summary
    
    def get_token_usage_summary(self, token_usages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of token usage across all classifications.
        
        Args:
            token_usages: List of token usage dictionaries
            
        Returns:
            Dictionary with token usage statistics
        """
        if not token_usages:
            return {
                'total_prompt_tokens': 0,
                'total_completion_tokens': 0,
                'total_tokens': 0,
                'average_tokens_per_email': 0,
                'estimated_cost_usd': 0.0,
                'model': config.OPENAI_MODEL
            }
        
        total_prompt = sum(usage.get('prompt_tokens', 0) for usage in token_usages)
        total_completion = sum(usage.get('completion_tokens', 0) for usage in token_usages)
        total_tokens = sum(usage.get('total_tokens', 0) for usage in token_usages)
        
        # GPT-4.1-mini pricing (as of 2025): $0.00015 per 1K input tokens, $0.0006 per 1K output tokens
        # Note: This is approximate and may change
        estimated_cost = (total_prompt * 0.00015 / 1000) + (total_completion * 0.0006 / 1000)
        
        summary = {
            'total_prompt_tokens': total_prompt,
            'total_completion_tokens': total_completion,
            'total_tokens': total_tokens,
            'average_tokens_per_email': total_tokens / len(token_usages) if token_usages else 0,
            'estimated_cost_usd': estimated_cost,
            'model': token_usages[0].get('model', config.OPENAI_MODEL) if token_usages else config.OPENAI_MODEL
        }
        
        return summary
    
    def _save_ai_category(self, category: str, confidence: float, reasoning: str, tags: List[str], priority: str, action_required: bool) -> None:
        """
        Save AI-generated category to a JSON file for tracking and analysis.
        
        Args:
            category: The AI-generated category name
            confidence: Classification confidence score
            reasoning: Explanation for the classification
            tags: List of relevant tags
            priority: Priority level (high, medium, low)
            action_required: Whether action is required
        """
        try:
            # Create configs directory if it doesn't exist
            configs_dir = "configs"
            if not os.path.exists(configs_dir):
                os.makedirs(configs_dir)
                self.logger.info(f"Created directory: {configs_dir}")
            
            # Define the file path
            file_path = os.path.join(configs_dir, "ai_email_categories.json")
            
            # Load existing data if file exists
            existing_data = {"categories": [], "last_updated": ""}
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                    if not isinstance(existing_data, dict) or "categories" not in existing_data:
                        existing_data = {"categories": [], "last_updated": ""}
                except (json.JSONDecodeError, IOError) as e:
                    self.logger.warning(f"Could not load existing AI categories file: {e}")
                    existing_data = {"categories": [], "last_updated": ""}
            
            # Add category to existing categories list if not already present
            if category not in existing_data["categories"]:
                existing_data["categories"].append(category)
                # Sort categories alphabetically
                existing_data["categories"].sort()
                existing_data["last_updated"] = self._get_current_timestamp()
                
                # Save to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"Saved AI category '{category}' to {file_path}")
            else:
                self.logger.info(f"AI category '{category}' already exists in {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save AI category to file: {str(e)}")
    
    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp in ISO format.
        
        Returns:
            Current timestamp as string
        """
        from datetime import datetime
        return datetime.now().isoformat()


def create_email_classifier(api_key: Optional[str] = None, config_file: str = "configs/email_categories.json") -> EmailClassifier:
    """
    Factory function to create an EmailClassifier instance.
    
    Args:
        api_key: OpenAI API key (optional)
        config_file: Path to the JSON configuration file (optional)
        
    Returns:
        EmailClassifier instance
    """
    return EmailClassifier(api_key=api_key, config_file=config_file)
