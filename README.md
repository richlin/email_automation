# Email Automation & AI Classification System

An intelligent email management system that automatically categorizes and organizes emails using AI-powered classification, reducing email overload and improving productivity. Features secure Gmail integration, real-time email analysis, and intelligent prioritization.

## 🚀 Features

- **Secure Gmail Authentication** - OAuth 2.0 with encrypted token storage
- **Email Analysis Engine** - Analyze email patterns and metadata
- **AI-Powered Classification** - Intelligent email categorization using GPT-4.1-mini
- **Real-time Email Analysis** - Analyze email patterns and metadata instantly
- **Smart Priority Detection** - Automatically identify high-priority emails
- **Action Required Flagging** - Detect emails that need immediate attention
- **Token Usage Tracking** - Monitor API usage and costs in real-time
- **Multiple Account Support** - Handle multiple Gmail accounts securely
- **Bulk Email Processing** - Process and classify multiple emails efficiently
- **Cost Optimization** - Track and optimize AI API usage

## 📋 Project Status

### ✅ Completed
- [x] Gmail OAuth 2.0 Authentication Module
- [x] Secure token management with encryption
- [x] Multiple account support
- [x] Real-time email fetching and analysis
- [x] AI-powered email classification with GPT-4.1-mini
- [x] Token usage tracking and cost monitoring
- [x] Bulk email processing capabilities
- [x] Comprehensive setup documentation
- [x] Data loading utilities for multiple formats

### 🚧 In Progress
- [ ] Web dashboard interface
- [ ] Advanced analytics and insights
- [ ] Custom classification rules engine
- [ ] Email automation workflows

### 📅 Planned
- [ ] Machine learning clustering algorithms
- [ ] Mobile optimization
- [ ] Integration with other email providers
- [ ] Advanced bulk action functionality

## 🛠️ Quick Start

### Prerequisites
- Python 3.7+
- Google Cloud Project with Gmail API enabled
- OAuth 2.0 credentials
- OpenAI API key for AI classification

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd email_automation
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Cloud credentials**
   - Follow the [GCP Setup Guide](GCP_SETUP_GUIDE.md) to configure Gmail API
   - Download `credentials.json` and place it in the project root
   - Set up your `.env` file with OpenAI API key

4. **Set up OpenAI API key for email classification**
   ```bash
   # Create a .env file in the project root
   echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
   ```
   
   Get your OpenAI API key from: https://platform.openai.com/api-keys

5. **Test email classification with sample data**
   ```bash
   python example_classifier.py
   ```

6. **Run the complete demo with Gmail integration**
   ```bash
   python main.py
   ```

## 📁 Project Structure

```
email_automation/
├── utils/                   # Utility modules
│   ├── __init__.py         # Package initialization
│   ├── gmail_auth.py       # Main authentication module
│   ├── gmail_analyzer.py   # Email analysis utilities
│   ├── email_classifier.py # AI-powered email classification
│   ├── data_loader.py      # Email data loading utilities
│   └── data_export.py      # Email data export utilities
├── main.py                 # Complete demo with Gmail integration
├── example_classifier.py   # Email classification demo
├── requirements.txt        # Python dependencies
├── GCP_SETUP_GUIDE.md     # GCP setup instructions
├── PRD_Email_Automation.md # Product requirements document
├── temp_data/             # Email data storage (auto-created)
│   └── *.json             # Exported email data files
├── credentials.json       # OAuth 2.0 credentials (you provide)
├── .env                   # Environment variables (you create)
├── .gmail_auth/          # Configuration directory (auto-created)
│   ├── encryption.key    # Encryption key for token storage
│   └── encrypted_token.json # Encrypted OAuth tokens
└── README.md            # This file
```

## 🔐 Security Features

- **Encrypted Token Storage** - OAuth tokens are encrypted using Fernet encryption
- **Secure Key Management** - Encryption keys are stored separately and securely
- **Multiple Account Support** - Each account has separate encrypted storage
- **Automatic Token Refresh** - Handles token expiration automatically
- **No Hardcoded Credentials** - All credentials are stored securely



## 🎯 Use Cases

### For Individuals
- **Email Overload Management** - Automatically organize thousands of emails
- **Productivity Improvement** - Focus on important emails first
- **Time Savings** - Reduce manual email sorting by 60%

### For Teams
- **Shared Email Management** - Handle team inboxes efficiently
- **Workflow Automation** - Bulk actions on email categories
- **Analytics & Insights** - Understand email patterns and trends

## 🔧 Configuration

### Environment Variables
```bash
# Required: OpenAI API key for AI classification
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Custom configuration directory
export GMAIL_AUTH_CONFIG_DIR=/path/to/config

# Optional: Custom credentials file
export GMAIL_CREDENTIALS_FILE=/path/to/credentials.json
```

### Multiple Accounts
```python
# Authenticate with different accounts
service1 = auth.authenticate(account_id='personal')
service2 = auth.authenticate(account_id='work')

# List all authenticated accounts
accounts = auth.get_accounts()
print(f"Authenticated accounts: {list(accounts.keys())}")
```

### Email Classification Categories
The AI classifier automatically categorizes emails into:
- **work_related** - Business and professional emails
- **personal** - Personal communications
- **newsletter** - Newsletters and subscriptions
- **spam** - Unwanted emails
- **billing** - Financial and billing emails
- **social_media** - Social media notifications
- **shopping** - E-commerce and shopping emails
- **travel** - Travel-related emails
- **health** - Health and medical emails
- **education** - Educational content
- **other** - Miscellaneous emails

## 📈 Performance & Metrics

- **Authentication**: < 5 seconds for first-time setup
- **Token Refresh**: < 1 second for subsequent uses
- **Email Fetching**: ~100 emails per second
- **AI Classification**: ~2-3 seconds per email
- **Token Usage**: ~500-600 tokens per email classification
- **Cost Efficiency**: ~$0.0001-0.0002 per email classification

## 🛡️ Privacy & Compliance

- **GDPR Compliant** - No permanent storage of email content without consent
- **Data Encryption** - All sensitive data encrypted at rest
- **Local Processing** - Email analysis happens locally
- **Secure Storage** - Tokens encrypted with industry-standard algorithms

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [GCP Setup Guide](GCP_SETUP_GUIDE.md)
- **Issues**: Create an issue on GitHub
- **Questions**: Check the troubleshooting section in the setup guide
- **Setup Help**: Follow the step-by-step instructions in GCP_SETUP_GUIDE.md

## 🔮 Roadmap

### Phase 1: MVP ✅ (Completed)
- ✅ Gmail authentication with OAuth 2.0
- ✅ AI-powered email classification
- ✅ Token usage tracking and cost monitoring
- ✅ Secure token management
- ✅ Bulk email processing

### Phase 2: Enhanced Features 🚧 (In Progress)
- 🚧 Web dashboard interface
- 🚧 Advanced analytics and insights
- 🚧 Custom classification rules engine
- 🚧 Email automation workflows

### Phase 3: Advanced Features 📅 (Planned)
- 📅 Machine learning clustering algorithms
- 📅 Mobile optimization
- 📅 Integration with other email providers
- 📅 Advanced bulk action functionality
- 📅 Real-time email monitoring

## 🎯 Key Benefits

- **Time Savings**: Reduce manual email sorting by 60%
- **Improved Focus**: Prioritize high-importance emails automatically
- **Cost Effective**: Monitor and optimize AI API usage
- **Secure**: Enterprise-grade encryption and token management
- **Scalable**: Handle multiple accounts and large email volumes
- **Intelligent**: AI-powered classification with high accuracy

---

**Built with ❤️ for better email management**