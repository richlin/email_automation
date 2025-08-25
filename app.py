#!/usr/bin/env python3
"""
Streamlit Inbox Triage Assistant

A web-based interface for Gmail automation including:
- Fetching sample emails
- Classifying emails with AI
- Adding labels to emails
- Archiving emails by label
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json
import asyncio

# Import our utility modules
from utils.gmail_analyzer import GmailAnalyzer
from utils.email_classifier import create_email_classifier
from utils.data_export import save_email_data_to_json
from utils.data_loader import load_email_data_from_temp_data
from utils.config import config

# Page configuration
st.set_page_config(
    page_title="Inbox Triage Assistant",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# Validate configuration on startup
if not config.validate_required_config():
    st.error("❌ Configuration Error: Missing required environment variables. Please check your .env file.")
    st.stop()

# Initialize session state
if 'gmail_analyzer' not in st.session_state:
    st.session_state.gmail_analyzer = None
if 'email_classifier' not in st.session_state:
    st.session_state.email_classifier = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'emails_data' not in st.session_state:
    st.session_state.emails_data = []

def authenticate_gmail():
    """Authenticate with Gmail and store in session state."""
    if st.session_state.gmail_analyzer is None:
        st.session_state.gmail_analyzer = GmailAnalyzer()
    
    if st.session_state.gmail_analyzer.authenticate():
        st.session_state.authenticated = True
        return True
    return False

def initialize_classifier():
    """Initialize the email classifier."""
    if st.session_state.email_classifier is None:
        try:
            st.session_state.email_classifier = create_email_classifier()
            return True
        except Exception as e:
            st.error(f"Failed to initialize classifier: {str(e)}")
            return False
    return True

# Main header
st.markdown('<h1 class="main-header">📧 Inbox Triage Assistant</h1>', unsafe_allow_html=True)

# Sidebar for authentication and configuration
with st.sidebar:
    st.header("🔐 Authentication")
    
    if not st.session_state.authenticated:
        if st.button("🔑 Authenticate with Gmail"):
            with st.spinner("Authenticating with Gmail..."):
                if authenticate_gmail():
                    st.success("✅ Authentication successful!")
                    st.rerun()
                else:
                    st.error("❌ Authentication failed!")
    else:
        st.success("✅ Authenticated")
        if st.button("🔄 Re-authenticate"):
            st.session_state.authenticated = False
            st.session_state.gmail_analyzer = None
            st.rerun()
    
    # Configuration section
    st.header("⚙️ Configuration")
    
    with st.expander("📋 Current Settings"):
        st.write("**OpenAI Configuration:**")
        st.write(f"• Model: {config.OPENAI_MODEL}")
        st.write(f"• Temperature: {config.OPENAI_TEMPERATURE}")
        st.write(f"• Max Tokens: {config.OPENAI_MAX_TOKENS}")
        
        st.write("**Gmail Configuration:**")
        st.write(f"• Config Dir: {config.GMAIL_AUTH_CONFIG_DIR}")
        st.write(f"• Credentials: {config.GMAIL_CREDENTIALS_FILE}")
        
        st.write("**Application Settings:**")
        st.write(f"• Max Emails: {config.MAX_EMAILS}")
        st.write(f"• Debug Mode: {config.DEBUG}")
        st.write(f"• Categories File: {config.CUSTOM_CATEGORIES_FILE}")
        
        st.write("**API Key Status:**")
        if config.OPENAI_API_KEY:
            st.success("✅ OpenAI API Key: Set")
        else:
            st.error("❌ OpenAI API Key: Missing")

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📥 Fetch Emails", "🔍 Category Discovery", "📋 Apply Classifications", "📦 Archive Labels"])

# Tab 1: Fetch Emails
with tab1:
    st.header("📥 Fetch Sample Emails")
    
    if not st.session_state.authenticated:
        st.warning("Please authenticate with Gmail first using the sidebar.")
    else:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📊 Email Count Options")
            email_count = st.selectbox(
                "Number of emails to fetch:",
                [20, 50, 100, 200,"All"],
                index=0
            )
            
            if st.button("📥 Fetch Emails", type="primary"):
                with st.spinner("Fetching emails..."):
                    try:
                        # Step 1: Clean existing email data
                        from utils.data_export import clean_email_data_folder
                        success, deleted_count, deleted_files = clean_email_data_folder()
                        if not success:
                            st.error("❌ Failed to clean existing email data")
                            st.stop()
                                                
                        # Convert "All" to a large number
                        max_results = 1000 if email_count == "All" else email_count
                        
                        # Step 2: Fetch emails (following test_fetch_email.py logic)
                        st.info("📥 Fetching new emails...")
                        emails = st.session_state.gmail_analyzer.get_recent_messages(
                            max_results=max_results,
                            skip_archived=True
                        )
                        
                        if emails:
                            st.session_state.emails_data = emails
                            
                            # Step 3: Save email data to JSON in temp_data folder (like test_fetch_email.py)
                            save_email_data_to_json(emails)
                                                        
                            # Step 4: Analyze patterns (like test_fetch_email.py)
                            analysis = st.session_state.gmail_analyzer.analyze_message_patterns(emails)
                            st.session_state.analysis_data = analysis
                            
                            # Step 5: Also store emails in sample_emails for classification
                            # Convert emails to the format expected by the classifier
                            sample_emails = []
                            for email in emails:
                                sample_email = {
                                    'subject': email.get('subject', ''),
                                    'sender': email.get('from', ''),
                                    'content': email.get('full_content', ''),
                                    'full_content': email.get('full_content', ''),
                                    'labels': email.get('labelIds', []),  # Convert labelIds to labels
                                    'labelIds': email.get('labelIds', []),  # Keep original for compatibility
                                    'date': email.get('date', ''),
                                    'id': email.get('id', ''),
                                    'thread_id': email.get('threadId', '')
                                }
                                sample_emails.append(sample_email)
                            
                            st.session_state.sample_emails = sample_emails
                            
                            st.success(f"✅ Successfully fetched {len(emails)} emails!")
                        else:
                            st.warning("No emails found.")
                            
                    except Exception as e:
                        st.error(f"Error fetching emails: {str(e)}")
        
        with col2:
            st.subheader("📊 Analysis Results")
            if hasattr(st.session_state, 'analysis_data') and st.session_state.analysis_data:
                analysis = st.session_state.analysis_data
                
                # Display total messages
                st.metric("📨 Total Messages", analysis['total_messages'])
                
                # Additional metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("👥 Unique Senders", len(analysis['senders']))
                with col2:
                    st.metric("🏷️ Unique Labels", len(analysis['labels']))
                
                # Top senders
                st.subheader("👥 Top Senders")
                top_senders = sorted(analysis['senders'].items(), key=lambda x: x[1], reverse=True)[:5]
                for sender, count in top_senders:
                    st.write(f"• **{sender}**: {count} messages")
                
                # Top labels
                st.subheader("🏷️ Most Common Labels")
                top_labels = sorted(analysis['labels'].items(), key=lambda x: x[1], reverse=True)[:5]
                for label, count in top_labels:
                    st.write(f"• **{label}**: {count} messages")
                
                # Email preview in expander
                with st.expander("📋 Email Preview", expanded=False):
                    if st.session_state.emails_data:
                        # Create a DataFrame for display
                        email_df = pd.DataFrame([
                            {
                                'Subject': email.get('subject', 'No Subject'),
                                'From': email.get('from', 'Unknown'),
                                'Date': email.get('date', 'Unknown'),
                                'Labels': ', '.join(email.get('labelIds', [])),
                                'ID': email.get('id', 'Unknown')
                            }
                            for email in st.session_state.emails_data
                        ])
                        
                        st.dataframe(email_df, use_container_width=True)
            else:
                st.info("No analysis data available. Click 'Fetch Emails' to get started.")

# Tab 2: Category Discovery
with tab2:
    st.header("🔍 Category Discovery with AI")
    
    if not st.session_state.authenticated:
        st.warning("Please authenticate with Gmail first.")
    else:
        if not initialize_classifier():
            st.error("Failed to initialize email classifier. Please check your OpenAI API key.")
        else:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("🔧 Discovery Options")
                
                if st.button("🔍 Discover Categories", type="primary"):
                    # Load email data from temp_data folder (following test_classify_email.py logic)
                    from utils.data_loader import load_email_data_from_temp_data
                    
                    sample_emails = load_email_data_from_temp_data()
                    
                    if not sample_emails:
                        st.info("Please ensure you have fetched emails first.")
                    else:
                        with st.spinner(f"Classifying {len(sample_emails)} emails..."):
                            try:
                                classifications = []
                                token_usages = []
                                progress_bar = st.progress(0)
                                
                                # Display classification progress
                                progress_text = st.empty()
                                
                                for i, email in enumerate(sample_emails, 1):
                                    # Update progress
                                    progress_bar.progress(i / len(sample_emails))
                                    progress_text.text(f"Classifying email {i} of {len(sample_emails)}: {email.get('subject', 'No Subject')}")
                                    
                                    try:
                                        # Use AI classification for category discovery
                                        classification, token_usage = st.session_state.email_classifier.discover_categories(
                                            subject=email.get('subject', ''),
                                            sender=email.get('sender', ''),
                                            content=email.get('full_content', ''),
                                            labels=email.get('labels', [])
                                        )
                                        
                                        classifications.append(classification)
                                        token_usages.append(token_usage)
                                        
                                    except Exception as e:
                                        st.error(f"❌ Classification failed for email {i}: {str(e)}")
                                
                                # Store results in session state
                                st.session_state.classifications = classifications
                                st.session_state.token_usages = token_usages
                                st.session_state.sample_emails = sample_emails
                                
                                # Generate summary
                                if classifications:
                                    summary = st.session_state.email_classifier.get_classification_summary(classifications)
                                    st.session_state.classification_summary = summary
                                    
                                    # Token usage summary
                                    if token_usages:
                                        token_summary = st.session_state.email_classifier.get_token_usage_summary(token_usages)
                                        st.session_state.token_summary = token_summary
                                    
                                    st.success(f"✅ Successfully discovered categories for {len(classifications)} emails!")
                                
                            except Exception as e:
                                st.error(f"Error during classification: {str(e)}")
            
            with col2:
                st.subheader("📊 Discovery Results")
                if hasattr(st.session_state, 'classifications') and st.session_state.classifications:
                    # Display summary metrics (like test_classify_email.py)
                    if hasattr(st.session_state, 'classification_summary'):
                        summary = st.session_state.classification_summary
                        
                        st.subheader("📈 Discovery Summary")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Emails", summary['total_emails'])
                        with col2:
                            st.metric("High Priority", summary['high_priority_count'])
                        with col3:
                            st.metric("Action Required", summary['action_required_count'])
                        with col4:
                            st.metric("Avg Confidence", f"{summary['average_confidence']:.2f}")
                        
                        # Category distribution
                        st.subheader("📊 Category Distribution")
                        for category, count in summary['category_distribution'].items():
                            st.write(f"• **{category}**: {count}")
                        
                        # Priority distribution
                        st.subheader("🎯 Priority Distribution")
                        for priority, count in summary['priority_distribution'].items():
                            st.write(f"• **{priority}**: {count}")
                    
                    # Enhanced token usage summary
                    if hasattr(st.session_state, 'token_summary'):
                        token_summary = st.session_state.token_summary
                        
                        st.subheader("🔢 AI Token Usage & Cost")
                        
                        # Main metrics in a more compact layout
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Tokens", f"{token_summary['total_tokens']:,}")
                        with col2:
                            st.metric("Avg/Email", f"{token_summary['average_tokens_per_email']:.0f}")
                        with col3:
                            st.metric("Estimated Cost", f"${token_summary['estimated_cost_usd']:.4f}")
                        with col4:
                            st.metric("Model", token_summary['model'])
                                            
                    # Save AI Categories button
                    st.subheader("💾 Save AI Categories")
                    st.write("Save the discovered AI categories for later use in the Apply Classifications tab.")
                    
                    if st.button("💾 Save AI Categories", type="primary"):
                        if hasattr(st.session_state, 'classifications'):
                            # Extract unique categories from classifications
                            categories = list(set(classification.category for classification in st.session_state.classifications))
                            categories.sort()  # Sort alphabetically
                            
                            # Create the same format as email_categories.json
                            from datetime import datetime
                            category_data = {
                                "categories": categories,
                                "last_updated": datetime.now().isoformat()
                            }
                            
                            # Save to configs/ai_email_categories.json
                            import os
                            import json
                            configs_dir = "configs"
                            if not os.path.exists(configs_dir):
                                os.makedirs(configs_dir)
                            
                            file_path = os.path.join(configs_dir, "ai_email_categories.json")
                            with open(file_path, 'w', encoding='utf-8') as f:
                                json.dump(category_data, f, indent=2, ensure_ascii=False)
                            
                            saved_file = file_path
                            if saved_file:
                                st.success(f"✅ AI categories saved to: {saved_file}")
                                st.info("💡 You can now load these categories in the 'Apply Classifications' tab")
                            else:
                                st.error("❌ Failed to save AI categories")
                        else:
                            st.error("❌ No AI categories available to save")
                else:
                    st.info("No discoveries available. Click 'Discover Categories' to start.")
                    st.info("💡 Make sure you have email data in the temp_data folder first.")

# Tab 3: Apply Classifications
with tab3:
    st.header("📋 Apply Classifications")
    
    if not st.session_state.authenticated:
        st.warning("Please authenticate with Gmail first.")
    else:
        col1, col2 = st.columns([1, 2])
        
        with col1:            
            # Category File Selection Section
            st.subheader("📂 Select Category File")
            from utils.data_export import list_category_files
            category_files = list_category_files()
            
            if category_files:                
                # File selection dropdown
                file_options = [f"{f['filename']} ({f['category_count']} categories)" for f in category_files]
                selected_category_file_idx = st.selectbox(
                    "Choose a category file to edit:",
                    range(len(file_options)), 
                    format_func=lambda x: file_options[x],
                    help="Select a category file to load and edit"
                )
                
                # Load button
                if st.button("📂 Load Selected Category File", type="primary"):
                    selected_file = category_files[selected_category_file_idx]['filename']
                    from utils.data_export import load_classification_data
                    loaded_data = load_classification_data(selected_file)
                    
                    if loaded_data and 'categories' in loaded_data:
                        st.session_state.selected_category_file = selected_file
                        st.session_state.loaded_categories = loaded_data['categories']
                        
                        # Update the email classifier with the loaded categories
                        if hasattr(st.session_state, 'email_classifier') and st.session_state.email_classifier:
                            st.session_state.email_classifier.categories = loaded_data['categories']
                        
                        st.success(f"✅ Successfully loaded: {selected_file}")
                        st.success(f"📊 {len(loaded_data['categories'])} categories loaded")
                    else:
                        st.error("❌ Failed to load category file")
            else:
                st.warning("📭 No category files found")
                st.info("💡 Create category files in the 'Apply Classifications' tab")
            
            # Edit Categories Section (moved from col2)
            st.subheader("📋 Edit Categories")
            
            # Show loaded categories for editing
            if hasattr(st.session_state, 'loaded_categories') and st.session_state.loaded_categories:
                
                # Text area for editing categories (one per line)
                categories_text = "\n".join(st.session_state.loaded_categories)
                edited_categories_text = st.text_area(
                    "Edit categories (one per line):",
                    value=categories_text,
                    height=200,
                    help="Enter each category on a separate line. Empty lines will be ignored."
                )
                
                # Parse the edited text into a list
                edited_categories = [line.strip() for line in edited_categories_text.split('\n') if line.strip()]
                
                # Store the edited categories in session state for immediate use
                st.session_state.edited_categories = edited_categories
                
                # Show if categories have been edited
                if hasattr(st.session_state, 'edited_categories') and st.session_state.edited_categories != st.session_state.loaded_categories:
                    st.info("📝 Categories have been edited. Click 'Apply Categories to Emails' to use the edited version, or 'Save Edited Categories' to save to file.")
                                
                # Save categories button
                if st.button("💾 Save Edited Categories", type="primary"):
                    if edited_categories:
                        # Filter out empty categories
                        filtered_categories = [cat.strip() for cat in edited_categories if cat.strip()]
                        
                        # Remove duplicates while preserving order
                        unique_categories = []
                        for cat in filtered_categories:
                            if cat not in unique_categories:
                                unique_categories.append(cat)
                        
                        # Save back to the original file
                        try:
                            updated_categories_data = {
                                "categories": unique_categories,
                                "last_updated": datetime.now().isoformat()
                            }
                            
                            filepath = os.path.join("configs", st.session_state.selected_category_file)
                            with open(filepath, "w") as f:
                                json.dump(updated_categories_data, f, indent=2)
                            
                            st.success(f"✅ Saved {len(unique_categories)} categories to {st.session_state.selected_category_file}")
                            
                            # Update the loaded categories
                            st.session_state.loaded_categories = unique_categories
                            
                        except Exception as e:
                            st.error(f"❌ Error saving categories: {str(e)}")
                    else:
                        st.warning("⚠️ No categories to save")
        
        with col2:
            st.subheader("🎯 Apply Categories")
            
            # Check if we have loaded categories and email data
            if hasattr(st.session_state, 'loaded_categories') and st.session_state.loaded_categories:
                # Show current categories being used (edited or loaded)
                current_categories = st.session_state.get('edited_categories', st.session_state.loaded_categories)
                st.success(f"✅ {len(current_categories)} categories loaded")
                
                # Show if using edited categories
                if hasattr(st.session_state, 'edited_categories') and st.session_state.edited_categories != st.session_state.loaded_categories:
                    st.info("📝 Using edited categories (not yet saved)")
                
                # Check if we have email data
                if hasattr(st.session_state, 'sample_emails') and st.session_state.sample_emails:
                    st.success(f"✅ {len(st.session_state.sample_emails)} emails available")
                                        
                    # Apply categories button
                    if st.button("🎯 Apply Categories to Emails", type="primary", key="apply_categories_button"):
                        with st.spinner("Applying categories to emails..."):
                            try:
                                # Initialize classifier if not already done
                                if not hasattr(st.session_state, 'email_classifier') or st.session_state.email_classifier is None:
                                    st.session_state.email_classifier = create_email_classifier()
                                else:
                                    # Ensure the classifier has the async method (recreate if needed)
                                    if not hasattr(st.session_state.email_classifier, 'classify_email_async'):
                                        st.session_state.email_classifier = create_email_classifier()
                                
                                # Update the classifier with the current categories (including any edits)
                                # Use edited categories if available, otherwise use loaded categories
                                current_categories = st.session_state.get('edited_categories', st.session_state.get('loaded_categories', []))
                                if current_categories:
                                    st.session_state.email_classifier.categories = current_categories
                                
                                # Async function for parallel email classification
                                async def classify_emails_parallel(emails, progress_bar, progress_text):
                                    """Classify emails in parallel using async/await."""
                                    classifications = []
                                    token_usages = []
                                    errors = []
                                    
                                    # Use semaphore to limit concurrent requests (max 5 at a time)
                                    semaphore = asyncio.Semaphore(5)
                                    
                                    async def classify_single_email(i, email):
                                        async with semaphore:
                                            return await st.session_state.email_classifier.classify_email_async(
                                                subject=email.get('subject', ''),
                                                sender=email.get('sender', ''),
                                                content=email.get('full_content', ''),
                                                labels=email.get('labelIds', [])
                                            )
                                    
                                    # Create tasks for all emails
                                    tasks = []
                                    for i, email in enumerate(emails):
                                        task = asyncio.create_task(classify_single_email(i, email))
                                        tasks.append((i, email, task))
                                    
                                    # Process completed tasks as they finish
                                    completed = 0
                                    for i, email, task in tasks:
                                        try:
                                            classification, token_usage = await task
                                            classifications.append(classification)
                                            if token_usage:
                                                token_usages.append(token_usage)
                                            
                                            # Update progress
                                            completed += 1
                                            progress_bar.progress(completed / len(emails))
                                            progress_text.text(f"Classified {completed} of {len(emails)} emails: {email.get('subject', 'No Subject')}")
                                            
                                        except Exception as e:
                                            errors.append((i, email, str(e)))
                                            completed += 1
                                            progress_bar.progress(completed / len(emails))
                                            progress_text.text(f"Failed to classify email {i+1}: {email.get('subject', 'No Subject')}")
                                    
                                    return classifications, token_usages, errors
                                
                                # Classify emails using the current categories
                                classifications = []
                                token_usages = []
                                progress_bar = st.progress(0)
                                progress_text = st.empty()
                                
                                # Debug: Check if async method exists
                                if not hasattr(st.session_state.email_classifier, 'classify_email_async'):
                                    st.error("❌ Async method not found on classifier. Available methods:")
                                    st.write([m for m in dir(st.session_state.email_classifier) if 'classify' in m])
                                    st.stop()
                                
                                # Run async classification
                                with st.spinner("Classifying emails in parallel..."):
                                    try:
                                        classifications, token_usages, errors = asyncio.run(
                                            classify_emails_parallel(st.session_state.sample_emails, progress_bar, progress_text)
                                        )
                                    except RuntimeError as e:
                                        if "asyncio.run() cannot be called from a running event loop" in str(e):
                                            # If we're already in an event loop, use asyncio.create_task
                                            loop = asyncio.get_event_loop()
                                            task = loop.create_task(
                                                classify_emails_parallel(st.session_state.sample_emails, progress_bar, progress_text)
                                            )
                                            classifications, token_usages, errors = loop.run_until_complete(task)
                                        else:
                                            raise
                                    except Exception as e:
                                        st.warning(f"⚠️ Async classification failed, falling back to sequential: {str(e)}")
                                        # Fallback to sequential classification
                                        classifications = []
                                        token_usages = []
                                        errors = []
                                        for i, email in enumerate(st.session_state.sample_emails):
                                            progress_bar.progress(i / len(st.session_state.sample_emails))
                                            progress_text.text(f"Classifying email {i+1} of {len(st.session_state.sample_emails)}: {email.get('subject', 'No Subject')}")
                                            
                                            try:
                                                classification, token_usage = st.session_state.email_classifier.classify_email(
                                                    subject=email.get('subject', ''),
                                                    sender=email.get('sender', ''),
                                                    content=email.get('full_content', ''),
                                                    labels=email.get('labelIds', [])
                                                )
                                                classifications.append(classification)
                                                if token_usage:
                                                    token_usages.append(token_usage)
                                            except Exception as e:
                                                errors.append((i, email, str(e)))
                                                st.error(f"❌ Classification failed for email {i+1}: {str(e)}")
                                
                                # Show any errors that occurred
                                for i, email, error in errors:
                                    st.error(f"❌ Classification failed for email {i+1}: {error}")
                                
                                # Create labels and apply to Gmail
                                if classifications:
                                    st.success(f"✅ Successfully classified {len(classifications)} emails")
                                    
                                    # Create labels for each category (only if they don't exist)
                                    created_labels = []
                                    existing_labels = []
                                    for classification in classifications:
                                        category = classification.category
                                        if category not in created_labels and category not in existing_labels:
                                            try:
                                                # Check if label already exists
                                                existing_label = st.session_state.gmail_analyzer.find_label_by_name(category)
                                                if existing_label:
                                                    existing_labels.append(category)
                                                else:
                                                    # Create label in Gmail only if it doesn't exist
                                                    label_result = st.session_state.gmail_analyzer.create_label(category)
                                                    if label_result:
                                                        created_labels.append(category)
                                            except Exception as e:
                                                st.warning(f"⚠️ Could not create label '{category}': {str(e)}")
                                    
                                    # Apply labels to emails
                                    labeled_count = 0
                                    for i, (email, classification) in enumerate(zip(st.session_state.sample_emails, classifications)):
                                        try:
                                            # Add label to email
                                            success = st.session_state.gmail_analyzer.add_labels_by_name(
                                                email.get('id', ''),
                                                [classification.category]
                                            )
                                            if success:
                                                labeled_count += 1
                                        except Exception as e:
                                            st.warning(f"⚠️ Could not label email {i+1}: {str(e)}")
                                    
                                    st.success(f"✅ Successfully labeled {labeled_count} emails")
                                    
                                    # Show summary
                                    st.subheader("📊 Application Summary")
                                    st.metric("Emails Classified", len(classifications))
                                    st.metric("Labels Created", len(created_labels))
                                    st.metric("Labels Already Existed", len(existing_labels))
                                    st.metric("Emails Labeled", labeled_count)
                                    
                                    # Show comprehensive token usage summary
                                    if 'token_usages' in locals() and token_usages:
                                        # Use the get_token_usage_summary function
                                        token_summary = st.session_state.email_classifier.get_token_usage_summary(token_usages)
                                        
                                        st.subheader("🔢 AI Token Usage & Cost")
                                        
                                        # Main metrics
                                        col1, col2, col3, col4 = st.columns(4)
                                        with col1:
                                            st.metric("Total Tokens", f"{token_summary['total_tokens']:,}")
                                        with col2:
                                            st.metric("Prompt Tokens", f"{token_summary['total_prompt_tokens']:,}")
                                        with col3:
                                            st.metric("Completion Tokens", f"{token_summary['total_completion_tokens']:,}")
                                        with col4:
                                            st.metric("Avg/Email", f"{token_summary['average_tokens_per_email']:.0f}")
                                        
                                        # Cost and efficiency metrics
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric("Estimated Cost", f"${token_summary['estimated_cost_usd']:.4f}")
                                        with col2:
                                            st.metric("Emails Processed", len(token_usages))
                                        with col3:
                                            st.metric("Model Used", token_summary['model'])
                                        
                                    
                                    # Show category distribution
                                    st.subheader("📈 Category Distribution")
                                    category_counts = {}
                                    for classification in classifications:
                                        category = classification.category
                                        category_counts[category] = category_counts.get(category, 0) + 1
                                    
                                    for category, count in category_counts.items():
                                        st.write(f"• **{category}**: {count} emails")
                                
                                else:
                                    st.error("❌ No classifications generated")
                                    
                            except Exception as e:
                                st.error(f"❌ Error applying categories: {str(e)}")
                else:
                    st.warning("⚠️ No email data available")
                    st.info("💡 Fetch emails first in the 'Fetch Emails' tab")
                    
                    # Show what's available in session state for debugging
                    with st.expander("🔍 Session State Debug"):
                        st.write(f"**Available session keys:** {list(st.session_state.keys())}")
                        if hasattr(st.session_state, 'emails_data'):
                            st.write(f"**emails_data:** {len(st.session_state.emails_data)} emails")
                        if hasattr(st.session_state, 'sample_emails'):
                            st.write(f"**sample_emails:** {len(st.session_state.sample_emails) if st.session_state.sample_emails else 0} emails")
            else:
                st.warning("⚠️ No categories loaded")
                st.info("💡 Load a category file in the left column first")

# Tab 4: Archive Labels
with tab4:    
    if not st.session_state.authenticated:
        st.warning("Please authenticate with Gmail first.")
    else:
        st.subheader("🎯 Archive Selection")
        
        # Add a refresh button to ensure we have the latest categories
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Refresh Categories", help="Refresh to see the latest category updates"):
                st.rerun()
        
        # Check if we have categories (either loaded or edited)
        current_categories = []
        if hasattr(st.session_state, 'edited_categories') and st.session_state.edited_categories:
            current_categories = st.session_state.edited_categories
        elif hasattr(st.session_state, 'loaded_categories') and st.session_state.loaded_categories:
            current_categories = st.session_state.loaded_categories
        
        if current_categories:
            # Show current category count and status
            st.success(f"✅ {len(current_categories)} categories available for archiving")
            
            # Show if using edited categories
            if hasattr(st.session_state, 'edited_categories') and st.session_state.edited_categories != st.session_state.get('loaded_categories', []):
                st.info("📝 Using edited categories (not yet saved)")
            
            # Create a drag-and-drop interface using multiselect
            st.write("**Select categories to archive emails:**")
            
            selected_categories = st.multiselect(
                "Drag categories here to archive:",
                options=current_categories,
                default=[],
                help="Select one or more categories. Emails with these labels will be archived."
            )
            
            if selected_categories:
                st.success(f"✅ Selected {len(selected_categories)} categories for archiving")
                
                # Archive button
                if st.button("📦 Archive Emails by Categories", type="primary", key="archive_categories_button"):
                    with st.spinner("Archiving emails by categories..."):
                        try:
                            total_messages_found = 0
                            total_messages_archived = 0
                            archive_results = []
                            
                            # Archive emails for each selected category
                            for category in selected_categories:
                                try:
                                    result = st.session_state.gmail_analyzer.archive_messages_by_label(
                                        category, 
                                        dry_run=False
                                    )
                                    
                                    if result['success']:
                                        total_messages_found += result['messages_found']
                                        total_messages_archived += result['messages_archived']
                                        archive_results.append({
                                            'category': category,
                                            'found': result['messages_found'],
                                            'archived': result['messages_archived']
                                        })
                                    else:
                                        st.warning(f"⚠️ Failed to archive category '{category}': {result.get('error', 'Unknown error')}")
                                        
                                except Exception as e:
                                    st.error(f"❌ Error archiving category '{category}': {str(e)}")
                            
                            # Show results
                            if archive_results:
                                st.success(f"✅ Archive operation completed!")
                                st.success(f"✅ Archived {total_messages_archived} messages across {len(selected_categories)} categories")
                                
                                # Display detailed results
                                st.subheader("📊 Archive Results")
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("Total Messages Found", total_messages_found)
                                with col2:
                                    st.metric("Total Messages Archived", total_messages_archived)
                                
                                # Show results by category
                                st.subheader("📈 Results by Category")
                                for result in archive_results:
                                    st.write(f"• **{result['category']}**: {result['archived']} messages archived")
                            
                        except Exception as e:
                            st.error(f"❌ Error during archiving: {str(e)}")
            else:
                st.info("💡 Select categories from the list above to archive emails")
                
            # Archive information
            st.subheader("📋 Archive Information")
            st.info("""
            **About Archiving:**
            - Archived messages are removed from your inbox
            - They can still be found in 'All Mail' or by searching
            - This action cannot be undone automatically
            - Emails with the selected category labels will be archived
            """)
        else:
            st.warning("⚠️ No categories available")
            st.info("💡 Load categories in the 'Apply Classifications' tab first")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>📧 Inbox Triage Assistant | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
