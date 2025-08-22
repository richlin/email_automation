#!/usr/bin/env python3
"""
Email Classification Module using GPT-4o-mini

This module provides functionality to classify email messages using OpenAI's GPT-4o-mini model.
It can categorize emails into different types such as work, personal, spam, newsletters, etc.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from openai import OpenAI
from dataclasses import dataclass
from dotenv import load_dotenv


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
    Email classifier using GPT-4o-mini model.
    
    This class provides methods to classify email messages into different categories
    and extract relevant information for automation purposes.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the email classifier.
        
        Args:
            api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY env var.
        """
        # Load environment variables from .env file
        load_dotenv()
        
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY in .env file or pass api_key parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
        
        # Define email categories
        self.categories = [
            "work_related",
            "personal",
            "newsletter",
            "spam",
            "billing",
            "social_media",
            "shopping",
            "travel",
            "health",
            "education",
            "other"
        ]
        
        # Define priority levels
        self.priorities = ["high", "medium", "low"]
    
    def classify_email(self, 
                      subject: str, 
                      sender: str, 
                      content: str, 
                      labels: Optional[List[str]] = None) -> tuple[EmailClassification, Dict[str, Any]]:
        """
        Classify an email message using GPT-4o-mini.
        
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
            
            # Make API call to GPT-4o-mini
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
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
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=3000
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
    
    def batch_classify(self, emails: List[Dict[str, Any]]) -> tuple[List[EmailClassification], List[Dict[str, Any]]]:
        """
        Classify multiple emails in batch.
        
        Args:
            emails: List of email dictionaries with 'subject', 'sender', 'content' keys
            
        Returns:
            Tuple of (List of EmailClassification objects, List of token usage dicts)
        """
        results = []
        token_usages = []
        
        for i, email in enumerate(emails):
            try:
                self.logger.info(f"Classifying email {i+1}/{len(emails)}")
                classification, token_usage = self.classify_email(
                    subject=email.get('subject', ''),
                    sender=email.get('sender', ''),
                    content=email.get('content', ''),
                    labels=email.get('labels')
                )
                results.append(classification)
                token_usages.append(token_usage)
                
            except Exception as e:
                self.logger.error(f"Failed to classify email {i+1}: {str(e)}")
                # Add a default classification for failed emails
                results.append(EmailClassification(
                    category="other",
                    confidence=0.0,
                    reasoning=f"Classification failed: {str(e)}",
                    tags=[],
                    priority="low",
                    action_required=False
                ))
                # Add empty token usage for failed emails
                token_usages.append({
                    'prompt_tokens': 0,
                    'completion_tokens': 0,
                    'total_tokens': 0,
                    'model': 'gpt-4.1-mini'
                })
        
        return results, token_usages
    
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
                'model': 'gpt-4.1-mini'
            }
        
        total_prompt = sum(usage.get('prompt_tokens', 0) for usage in token_usages)
        total_completion = sum(usage.get('completion_tokens', 0) for usage in token_usages)
        total_tokens = sum(usage.get('total_tokens', 0) for usage in token_usages)
        
        # GPT-4o-mini pricing (as of 2024): $0.00015 per 1K input tokens, $0.0006 per 1K output tokens
        # Note: This is approximate and may change
        estimated_cost = (total_prompt * 0.00015 / 1000) + (total_completion * 0.0006 / 1000)
        
        summary = {
            'total_prompt_tokens': total_prompt,
            'total_completion_tokens': total_completion,
            'total_tokens': total_tokens,
            'average_tokens_per_email': total_tokens / len(token_usages) if token_usages else 0,
            'estimated_cost_usd': estimated_cost,
            'model': token_usages[0].get('model', 'gpt-4.1-mini') if token_usages else 'gpt-4.1-mini'
        }
        
        return summary


def create_email_classifier(api_key: Optional[str] = None) -> EmailClassifier:
    """
    Factory function to create an EmailClassifier instance.
    
    Args:
        api_key: OpenAI API key (optional)
        
    Returns:
        EmailClassifier instance
    """
    return EmailClassifier(api_key=api_key)
