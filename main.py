#!/usr/bin/env python3
"""
Example usage of the Gmail Authentication Module

This script demonstrates how to run the Gmail authentication and analysis demo.
Run this script after setting up credentials.json
"""

from utils.gmail_analyzer import GmailAnalyzer
from utils.data_export import save_email_data_to_json
from utils.email_classifier import create_email_classifier
from utils.data_loader import convert_gmail_messages_to_classification_format


def run_demo():
    """Run the complete demonstration."""
    print("🚀 Gmail Authentication & Analysis Demo")
    print("=" * 50)
    
    # Initialize the Gmail analyzer
    analyzer = GmailAnalyzer()
    
    # Step 1: Authenticate
    if not analyzer.authenticate():
        return
    
    # Step 2: Get recent messages
    messages = analyzer.get_recent_messages(max_results=20)
    if not messages:
        return
    
    # Step 3: Display sample messages
    print(f"\n📧 Sample messages:")
    for i, msg in enumerate(messages[:5], 1):
        print(f"\n{i}. From: {msg['from']}")
        print(f"   Subject: {msg['subject']}")
        print(f"   Date: {msg['date']}")
        print(f"   Labels: {', '.join(msg['labelIds'])}")
        print(f"   Full Content:")
        print(f"   {msg.get('full_content', 'No content available')[:100]}...")
    
    # Step 4: Save email data to JSON in temp_data folder
    save_email_data_to_json(messages)
    
    # Step 5: Analyze patterns@
    analysis = analyzer.analyze_message_patterns(messages)
    analyzer.display_analysis(analysis)
    
    # Step 6: Get labels
    analyzer.get_labels()
    
    # Step 7: Classify emails using AI
    print(f"\n🤖 AI Email Classification Demo")
    print("=" * 50)
    
    try:
        # Create email classifier
        classifier = create_email_classifier()
        print("✅ Email classifier initialized successfully")
        
        # Convert Gmail messages to classification format
        emails_for_classification = convert_gmail_messages_to_classification_format(messages)
        
        if emails_for_classification:
            print(f"📧 Classifying {len(emails_for_classification)} emails...")
            
            # Classify each email
            classifications = []
            token_usages = []
            for i, email in enumerate(emails_for_classification, 1):
                print(f"\n{i}. Subject: {email['subject']}")
                print(f"   From: {email['sender']}")
                
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
                    print(f"   ⚡ Action Required: {classification.action_required}")
                    print(f"   🔢 Tokens: {token_usage['total_tokens']}")
                    
                    classifications.append(classification)
                    token_usages.append(token_usage)
                    
                except Exception as e:
                    print(f"   ❌ Classification failed: {str(e)}")
            
            # Generate summary
            if classifications:
                print(f"\n📊 Classification Summary")
                print("-" * 50)
                summary = classifier.get_classification_summary(classifications)
                
                print(f"Total emails: {summary['total_emails']}")
                print(f"High priority emails: {summary['high_priority_count']}")
                print(f"Emails requiring action: {summary['action_required_count']}")
                print(f"Average confidence: {summary['average_confidence']:.2f}")
                
                print(f"\nCategory distribution:")
                for category, count in summary['category_distribution'].items():
                    print(f"  {category}: {count}")
                
                # Token usage summary
                if token_usages:
                    print(f"\n🔢 Token Usage Summary")
                    print("-" * 50)
                    token_summary = classifier.get_token_usage_summary(token_usages)
                    
                    print(f"Model: {token_summary['model']}")
                    print(f"Total tokens: {token_summary['total_tokens']:,}")
                    print(f"  - Prompt tokens: {token_summary['total_prompt_tokens']:,}")
                    print(f"  - Completion tokens: {token_summary['total_completion_tokens']:,}")
                    print(f"Average tokens per email: {token_summary['average_tokens_per_email']:.1f}")
                    print(f"Estimated cost: ${token_summary['estimated_cost_usd']:.4f}")
        
    except Exception as e:
        print(f"❌ Error during email classification: {str(e)}")
        print("💡 Make sure you have set up your OpenAI API key in the .env file")
    
    print(f"\n✅ Demo completed successfully!")
    print(f"💡 This demonstrates the foundation for email clustering and automation.")


if __name__ == '__main__':
    run_demo()
