# 🤖 AI Newsletter System

A modern, production-ready AI newsletter platform with registration-required viewing and email subscription management.

## 🌟 Features

### 📰 Newsletter System
- **AI-Powered Content Generation** - Automated newsletter creation using OpenAI
- **Registration-Required Viewing** - Users must register to access newsletters
- **Email Subscription System** - Collect and manage email subscribers
- **Beautiful Responsive Design** - Modern UI that works on all devices
- **Admin Panels** - Manage users and subscribers with built-in dashboards

### 🔐 Security & Management
- **User Registration & Login** - Secure authentication system
- **Session Management** - Protected access to newsletters
- **SQLite/PostgreSQL Support** - Local development and production databases
- **Environment-Based Configuration** - Secure credential management

### 📱 Modern UI/UX
- **Responsive Design** - Perfect on desktop, laptop, and mobile
- **Animated Interactions** - Smooth transitions and modern effects
- **Gradient Backgrounds** - Vibrant, professional color schemes
- **Mobile-First Approach** - Optimized for all screen sizes

## 🚀 Quick Start

### 1. Clone and Install
```bash
git clone <your-repo-url>
cd newsletter
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
SECRET_KEY=your_secret_key
```

### 3. Run Locally
```bash
# Start Newsletter Viewer (Registration System)
python newsletter_viewer.py
# Visit: http://localhost:5001

# Start Subscription System (Email Collection)
python subscription_app.py  
# Visit: http://localhost:5000
```

## 🌐 Production Deployment

### Deploy to Render (Recommended)
Follow the complete guide in **`RENDER_DEPLOYMENT.md`** for:
- Automatic HTTPS/SSL certificates
- Custom domain configuration
- PostgreSQL database setup
- Environment variable management
- Professional email configuration

### Quick Deploy Steps:
1. Push code to GitHub
2. Connect to Render
3. Configure environment variables
4. Deploy both services
5. Set up custom domain

## 📁 Project Structure
```
newsletter/
├── 📱 Core Applications
│   ├── newsletter_viewer.py      # Registration-required newsletter viewer
│   ├── subscription_app.py       # Email subscription system
│   └── email_manager.py         # Email sending and management
│
├── 🤖 AI Generation
│   ├── ai_curator.py            # AI content curation
│   ├── newsletter_generator.py  # Newsletter generation
│   ├── content_collector.py     # Content collection
│   └── main.py                  # Main generation script
│
├── 🎨 Templates
│   ├── templates/newsletter_viewer/  # Registration system templates
│   ├── templates/subscription/       # Subscription system templates
│   └── templates/newsletter_template.html  # Main newsletter template
│
├── 🚀 Deployment
│   ├── render.yaml              # Render deployment config
│   ├── Procfile                 # Process definition
│   ├── runtime.txt             # Python version
│   └── requirements.txt        # Dependencies
│
├── 📊 Data
│   ├── newsletter_users.db      # User registration database
│   ├── subscribers.db          # Email subscribers database
│   └── output/                 # Generated newsletters
│
└── 📚 Documentation
    ├── README.md               # This file
    ├── RENDER_DEPLOYMENT.md    # Complete deployment guide
    └── SUBSCRIPTION_SETUP.md   # Marketing and setup guide
```

## 🎯 Usage

### For Users
1. **Register** at your newsletter viewer URL
2. **Login** to access all newsletters
3. **Subscribe** via the subscription page for email delivery
4. **View newsletters** in responsive, mobile-friendly design

### For Administrators
1. **Generate newsletters** using `python main.py`
2. **Manage users** at `/admin/users`
3. **Manage subscribers** at `/admin/subscribers`
4. **Send newsletters** via email to all subscribers

## 🔧 Configuration

### Environment Variables
```env
# Required for AI Generation
OPENAI_API_KEY=your_openai_api_key

# Required for Email Sending
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password

# Required for Security
SECRET_KEY=your_secret_key

# Optional for Production
FLASK_ENV=production
DATABASE_URL=postgresql://...
```

## 📈 Marketing & Growth

See **`SUBSCRIPTION_SETUP.md`** for comprehensive strategies on:
- Building your subscriber list
- Social media promotion
- Content marketing
- SEO optimization
- Email automation
- Analytics and tracking

## 🆘 Support

### Common Issues
- **Email not sending**: Check Gmail app password setup
- **Registration not working**: Verify SECRET_KEY is set
- **Database errors**: Ensure proper permissions and paths
- **Mobile display issues**: Clear browser cache and test

### Getting Help
- Check the deployment guide: `RENDER_DEPLOYMENT.md`
- Review setup instructions: `SUBSCRIPTION_SETUP.md`
- Verify environment variables are correctly set
- Test locally before deploying to production

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🎉 Success!

You now have a complete, production-ready AI newsletter system with:
- ✅ User registration and authentication
- ✅ Email subscription management  
- ✅ Responsive, modern design
- ✅ AI-powered content generation
- ✅ Admin panels for management
- ✅ Production deployment ready

**Start building your audience and sharing amazing AI content! 🚀**
```bash
python main.py
```

## Project Structure

```
newsletter/
├── main.py                    # Main application entry point
├── config.py                  # Configuration management
├── models.py                  # Data models
├── content_collector.py       # RSS and Twitter content collection
├── ai_curator.py             # AI curation and summarization
├── newsletter_generator.py   # HTML generation and email sending
├── templates/
│   └── newsletter_template.html  # Newsletter HTML template
├── output/                   # Generated newsletters (auto-created)
├── requirements.txt          # Python dependencies
├── .env                      # Environment configuration
└── README.md                 # This file
```

## How It Works

1. **Content Collection**: The system fetches articles from configured RSS feeds and relevant tweets from Twitter
2. **AI Curation**: Each article is scored for importance (1-10) using OpenAI's GPT model
3. **Summarization**: AI generates concise, engaging summaries of each article
4. **Newsletter Generation**: Creates a beautiful HTML newsletter using Jinja2 templates
5. **Email Delivery**: Sends the newsletter to configured recipients via SMTP
6. **Scheduling**: Runs automatically on your specified schedule

## Customization

### Adding RSS Feeds
Add comma-separated RSS feed URLs to the `RSS_FEEDS` environment variable.

### Modifying Templates
Edit `templates/newsletter_template.html` to customize the newsletter design.

### Changing AI Behavior
Modify prompts in `ai_curator.py` to adjust how articles are scored and summarized.

### Scheduling
Modify `NEWSLETTER_SCHEDULE_DAY` and `NEWSLETTER_SCHEDULE_TIME` in `.env`:
- Days: monday, tuesday, wednesday, thursday, friday, saturday, sunday
- Time: 24-hour format (e.g., "09:00", "14:30")

## Monitoring

- Logs are saved to `newsletter.log`
- Generated newsletters are saved in the `output/` directory
- Check the terminal output for real-time status

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`

2. **Email Sending Fails**: 
   - Verify Gmail app password is correct
   - Check if 2-factor authentication is enabled
   - Ensure SMTP settings are correct

3. **No Articles Collected**: 
   - Check if RSS feeds are accessible
   - Verify Twitter Bearer Token if using Twitter
   - Check internet connection

4. **AI API Errors**: 
   - Verify OpenAI API key is valid and has credits
   - Check API rate limits

### Getting Help

Check the `newsletter.log` file for detailed error messages and troubleshooting information.

## Security Notes

- Never commit your `.env` file to version control
- Use environment variables for all sensitive information
- Regularly rotate API keys
- Use Gmail app passwords instead of your main password

## Advanced Features

### Running on a Server
To run continuously on a server:

```bash
# Using nohup
nohup python main.py &

# Using screen
screen -S newsletter
python main.py
# Press Ctrl+A, then D to detach
```

### Docker Deployment
Create a `Dockerfile` for containerized deployment:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Integration with Cloud Services
- Deploy on AWS Lambda with CloudWatch Events for scheduling
- Use SendGrid or AWS SES for email delivery
- Store configuration in AWS Parameter Store or Azure Key Vault
