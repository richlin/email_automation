# GCP Setup Guide

Quick setup guide for configuring Google Cloud Platform and Gmail API access.

## 📋 Prerequisites

- A Google account
- Python 3.7+ installed

## 🚀 Step-by-Step Setup

### Step 1: Create a Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Sign in with your Google account

2. **Create a new project**
   - Click on the project dropdown at the top
   - Click "New Project"
   - Enter a project name (e.g., "Email Automation")
   - Click "Create"

3. **Select your project**
   - Make sure your new project is selected in the dropdown

### Step 2: Enable Gmail API

1. **Navigate to APIs & Services**
   - In the left sidebar, click "APIs & Services" > "Library"

2. **Search for Gmail API**
   - In the search bar, type "Gmail API"
   - Click on "Gmail API" from the results

3. **Enable the API**
   - Click "Enable" button
   - Wait for the API to be enabled

### Step 3: Create OAuth 2.0 Credentials

1. **Go to Credentials**
   - In the left sidebar, click "APIs & Services" > "Credentials"

2. **Create credentials**
   - Click "Create Credentials" button
   - Select "OAuth client ID"

3. **Configure OAuth consent screen**
   - If prompted, click "Configure Consent Screen"
   - Choose "External" user type
   - Fill in the required information:
     - **App name**: Email Automation
     - **User support email**: Your email address
     - **Developer contact information**: Your email address
   - Click "Save and Continue"
   - Skip adding scopes (click "Save and Continue")
   - Add test users if needed (click "Save and Continue")
   - Click "Back to Dashboard"

4. **Create OAuth client ID**
   - Application type: "Desktop application"
   - Name: "Email Automation Desktop Client"
   - Click "Create"

5. **Download credentials**
   - Click "Download JSON"
   - Save the file as `credentials.json` in your project root directory
   - **Important**: Keep this file secure and never commit it to version control

### Step 4: Test the Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the authentication test**
   ```bash
   python main.py
   ```

3. **First-time authentication**
   - A browser window will open
   - Sign in with your Google account
   - Grant permissions to the application
   - You'll be redirected to a localhost URL (this is normal)

## 🔐 Security Notes

- Add `credentials.json` to your `.gitignore`
- Add `.env` to your `.gitignore`
- Add `.gmail_auth/` to your `.gitignore`

## 🛠️ Troubleshooting

### Common Issues

1. **"Invalid credentials" error**
   - Ensure `credentials.json` is in the project root
   - Check that the file is valid JSON

2. **"Access denied" error**
   - Make sure Gmail API is enabled
   - Check that your Google account has access to the project

3. **"Quota exceeded" error**
   - Check your API usage in Google Cloud Console
   - Request quota increase if needed

## 📚 Additional Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Google Cloud Console](https://console.cloud.google.com/)
- [OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
