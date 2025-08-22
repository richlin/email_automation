#!/usr/bin/env python3
"""
Example usage of the Email Classification Module

This script demonstrates how to use the EmailClassifier to classify email messages.
Make sure to set your OPENAI_API_KEY environment variable before running.
"""

import os
from dotenv import load_dotenv
from utils.email_classifier import create_email_classifier
from utils.data_loader import load_email_data_from_temp_data


def run_classification_demo():
    """Run the email classification demonstration."""
    print("🤖 Email Classification Demo using GPT-4.1-mini")
    print("=" * 60)
    
    try:
        # Create classifier instance
        classifier = create_email_classifier()
        print("✅ Email classifier initialized successfully")
        
        # Load real email data from temp_data folder
        sample_emails = load_email_data_from_temp_data()
        
        if not sample_emails:
            print("❌ No email data found in temp_data folder")
            print("Please ensure you have email data files in the temp_data directory")
            return
        
        print(f"\n📧 Classifying {len(sample_emails)} sample emails...")
        print("-" * 60)
        
        # Classify each email
        classifications = []
        token_usages = []
        for i, email in enumerate(sample_emails, 1):
            print(f"\n{i}. Subject: {email['subject']}")
            print(f"   From: {email['sender']}")
            print(f"   Date: {email['date']}")
            print(f"   Labels: {', '.join(email['labels'])}")
            
            try:
                classification, token_usage = classifier.classify_email(
                    subject=email['subject'],
                    sender=email['sender'],
                    content=email['full_content'],
                    labels=email['labels']
                )
                
                print(f"   📊 Category: {classification.category}")
                print(f"   🎯 Priority: {classification.priority}")
                print(f"   📈 Confidence: {classification.confidence:.2f}")
                print(f"   🏷️  Tags: {', '.join(classification.tags)}")
                print(f"   ⚡ Action Required: {classification.action_required}")
                print(f"   💭 Reasoning: {classification.reasoning}")
                print(f"   🔢 Tokens: {token_usage['total_tokens']} (prompt: {token_usage['prompt_tokens']}, completion: {token_usage['completion_tokens']})")
                
                classifications.append(classification)
                token_usages.append(token_usage)
                
            except Exception as e:
                print(f"   ❌ Classification failed: {str(e)}")
        
        # Generate summary
        if classifications:
            print(f"\n📊 Classification Summary")
            print("-" * 60)
            summary = classifier.get_classification_summary(classifications)
            
            print(f"Total emails: {summary['total_emails']}")
            print(f"High priority emails: {summary['high_priority_count']}")
            print(f"Emails requiring action: {summary['action_required_count']}")
            print(f"Average confidence: {summary['average_confidence']:.2f}")
            
            print(f"\nCategory distribution:")
            for category, count in summary['category_distribution'].items():
                print(f"  {category}: {count}")
            
            print(f"\nPriority distribution:")
            for priority, count in summary['priority_distribution'].items():
                print(f"  {priority}: {count}")
            
            # Token usage summary
            if token_usages:
                print(f"\n🔢 Token Usage Summary")
                print("-" * 60)
                token_summary = classifier.get_token_usage_summary(token_usages)
                
                print(f"Model: {token_summary['model']}")
                print(f"Total tokens: {token_summary['total_tokens']:,}")
                print(f"  - Prompt tokens: {token_summary['total_prompt_tokens']:,}")
                print(f"  - Completion tokens: {token_summary['total_completion_tokens']:,}")
                print(f"Average tokens per email: {token_summary['average_tokens_per_email']:.1f}")
                print(f"Estimated cost: ${token_summary['estimated_cost_usd']:.4f}")
        
        print(f"\n✅ Classification demo completed successfully!")
        print(f"💡 This demonstrates how to integrate AI-powered email classification into your automation workflow.")
        
    except Exception as e:
        print(f"❌ Error during classification demo: {str(e)}")


if __name__ == '__main__':
    run_classification_demo()
