import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # AI API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
    
    # Email Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    
    # Newsletter Configuration
    NEWSLETTER_NAME = os.getenv('NEWSLETTER_NAME', 'AI Weekly Digest')
    SENDER_NAME = os.getenv('SENDER_NAME', 'AI Newsletter Bot')
    RECIPIENT_EMAILS = os.getenv('RECIPIENT_EMAILS', '').split(',')
    
    # Schedule Configuration
    NEWSLETTER_SCHEDULE_DAY = os.getenv('NEWSLETTER_SCHEDULE_DAY', 'monday')
    NEWSLETTER_SCHEDULE_TIME = os.getenv('NEWSLETTER_SCHEDULE_TIME', '09:00')
    
    # Content Sources
    RSS_FEEDS = os.getenv('RSS_FEEDS', '').split(',')
    TWITTER_KEYWORDS = os.getenv('TWITTER_KEYWORDS', '').split(',')
    MAX_ARTICLES_PER_SOURCE = int(os.getenv('MAX_ARTICLES_PER_SOURCE', 5))
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        required_fields = [
            'OPENAI_API_KEY', 'EMAIL_ADDRESS', 'EMAIL_PASSWORD'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(cls, field):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required configuration: {', '.join(missing_fields)}")
        
        return True
