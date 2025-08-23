# Gmail API Setup Guide

This guide will walk you through setting up Gmail API access to enable email fetching and automation in this project.

## 📋 Prerequisites

- A Google account
- Python 3.7+ installed
- Basic familiarity with Google Cloud Console

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

### Step 4: Configure Gmail API Scopes

The application requires the following Gmail API scopes:

- `https://www.googleapis.com/auth/gmail.readonly` - Read emails
- `https://www.googleapis.com/auth/gmail.modify` - Modify emails (labels, etc.)
- `https://www.googleapis.com/auth/gmail.labels` - Manage labels

These scopes are automatically configured in the code.

### Step 5: Set Up Environment Variables

1. **Create a `.env` file** in your project root:
   ```bash
   # OpenAI API Configuration
   OPENAI_API_KEY=your-openai-api-key-here
   
   # Optional: Custom configuration directory
   GMAIL_AUTH_CONFIG_DIR=.gmail_auth
   
   # Optional: Custom credentials file path
   GMAIL_CREDENTIALS_FILE=credentials.json
   ```

2. **Get your OpenAI API key**:
   - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create a new API key
   - Copy it to your `.env` file

### Step 6: Test the Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the authentication test**:
   ```bash
   python main.py
   ```

3. **First-time authentication**:
   - A browser window will open
   - Sign in with your Google account
   - Grant permissions to the application
   - You'll be redirected to a localhost URL (this is normal)

## 🔐 Security Best Practices

### Credentials Management

1. **Never commit credentials**:
   - Add `credentials.json` to your `.gitignore`
   - Add `.env` to your `.gitignore`
   - Add `.gmail_auth/` to your `.gitignore`

2. **Secure storage**:
   - Store credentials in a secure location
   - Use environment variables for sensitive data
   - Consider using a secrets manager for production

### API Quotas and Limits

1. **Gmail API Limits**:
   - 1 billion queries per day per project
   - 250 queries per second per user
   - 1,000 queries per 100 seconds per user

2. **Monitor usage**:
   - Check Google Cloud Console > APIs & Services > Dashboard
   - Monitor quota usage and errors

## 🛠️ Troubleshooting

### Common Issues

1. **"Invalid credentials" error**:
   - Ensure `credentials.json` is in the project root
   - Check that the file is valid JSON
   - Verify the OAuth client ID is correct

2. **"Access denied" error**:
   - Make sure Gmail API is enabled
   - Check that your Google account has access to the project
   - Verify OAuth consent screen is configured

3. **"Quota exceeded" error**:
   - Check your API usage in Google Cloud Console
   - Consider implementing rate limiting
   - Request quota increase if needed

4. **Authentication loop**:
   - Clear browser cookies for localhost
   - Delete the `.gmail_auth` directory
   - Restart the authentication process

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Monitoring and Analytics

### Google Cloud Console

1. **API Dashboard**:
   - Monitor API usage and errors
   - View request patterns
   - Check quota utilization

2. **IAM & Admin**:
   - Manage user permissions
   - Review access logs
   - Configure service accounts

### Application Logs

The application provides detailed logging:
- Authentication events
- API request/response details
- Error messages and stack traces
- Token refresh operations

## 🔄 Token Management

### Automatic Token Refresh

The application automatically handles:
- Token expiration
- Refresh token rotation
- Secure token storage
- Multiple account support

### Manual Token Management

If needed, you can manually manage tokens:

1. **View stored tokens**:
   ```python
   from utils.gmail_auth import GmailAuthenticator
   auth = GmailAuthenticator()
   accounts = auth.get_accounts()
   print(accounts)
   ```

2. **Clear tokens**:
   ```python
   auth.clear_tokens()
   ```

3. **Force re-authentication**:
   ```python
   auth.authenticate(force_refresh=True)
   ```

## 🚀 Production Deployment

### Environment Setup

1. **Use service accounts** for production:
   - Create a service account in Google Cloud Console
   - Grant necessary permissions
   - Use service account key instead of OAuth

2. **Configure environment variables**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   export OPENAI_API_KEY=your-production-api-key
   ```

3. **Set up monitoring**:
   - Configure logging to external service
   - Set up alerts for API errors
   - Monitor token refresh failures

### Security Considerations

1. **Network security**:
   - Use HTTPS for all API calls
   - Implement proper firewall rules
   - Restrict access to credentials

2. **Access control**:
   - Use least privilege principle
   - Regularly rotate credentials
   - Monitor access patterns

## 📚 Additional Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Google Cloud Console](https://console.cloud.google.com/)
- [OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [Gmail API Quotas](https://developers.google.com/gmail/api/reference/quota)

## 🆘 Support

If you encounter issues:

1. **Check the logs** for detailed error messages
2. **Verify your setup** against this guide
3. **Check Google Cloud Console** for API errors
4. **Review the troubleshooting section** above
5. **Create an issue** in the project repository

---

**Note**: This setup guide assumes you're using the application for personal or development purposes. For production use, additional security measures and compliance considerations may be required.
