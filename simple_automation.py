"""
Simple newsletter automation script
Generates today's newsletter and sends it with beautiful formatting
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from email_manager import EmailManager
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_newsletter_data():
    """Create sample newsletter data for today."""
    today = datetime.now()
    
    newsletter_data = {
        'subject': f"AI Newsletter - {today.strftime('%B %d, %Y')}",
        'date': today.strftime('%B %d, %Y'),
        'intro': f"Welcome to today's AI Newsletter! Here are the most important developments in AI and technology for {today.strftime('%B %d, %Y')}.",
        'articles': [
            {
                'title': 'GPT-4 Advances in Code Generation',
                'summary': 'Latest improvements in AI-powered code generation are revolutionizing software development. New models show 40% better accuracy in complex programming tasks.',
                'source': 'AI Research',
                'importance_score': 9.2,
                'url': 'https://example.com/gpt4-advances'
            },
            {
                'title': 'Breakthrough in Autonomous Vehicle Navigation',
                'summary': 'New AI algorithms enable self-driving cars to navigate complex urban environments with 99.7% accuracy, marking a significant step toward full autonomy.',
                'source': 'Tech News',
                'importance_score': 8.8,
                'url': 'https://example.com/autonomous-vehicles'
            },
            {
                'title': 'AI in Healthcare: Diagnostic Revolution',
                'summary': 'Machine learning models now outperform human doctors in early cancer detection, with 95% accuracy in identifying malignant tumors from medical imaging.',
                'source': 'Medical AI',
                'importance_score': 9.5,
                'url': 'https://example.com/ai-healthcare'
            },
            {
                'title': 'Quantum Computing Meets Machine Learning',
                'summary': 'Researchers demonstrate quantum advantage in machine learning tasks, achieving 1000x speedup in specific optimization problems.',
                'source': 'Quantum AI',
                'importance_score': 8.5,
                'url': 'https://example.com/quantum-ml'
            },
            {
                'title': 'Natural Language Processing Breakthrough',
                'summary': 'New transformer architecture enables real-time translation between 100+ languages with human-level accuracy, breaking down global communication barriers.',
                'source': 'NLP Research',
                'importance_score': 8.9,
                'url': 'https://example.com/nlp-breakthrough'
            }
        ]
    }
    
    return newsletter_data

def save_newsletter_to_output(newsletter_data):
    """Save newsletter data to output directory."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs('output', exist_ok=True)
        
        # Generate filename
        today = datetime.now()
        filename = f"output/newsletter_{today.strftime('%Y_%m_%d')}.json"
        
        # Save newsletter data
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(newsletter_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Newsletter data saved to {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving newsletter: {e}")
        return False

def send_newsletter():
    """Generate and send today's newsletter."""
    logger.info("Starting newsletter generation and sending...")
    
    try:
        # Create newsletter data
        newsletter_data = create_sample_newsletter_data()
        
        # Save to output directory
        save_newsletter_to_output(newsletter_data)
        
        # Initialize email manager
        email_manager = EmailManager()
        
        # Send newsletter
        success, message = email_manager.send_newsletter(newsletter_data, newsletter_data['subject'])
        
        if success:
            logger.info(f"✅ Newsletter sent successfully: {message}")
            return True
        else:
            logger.error(f"❌ Failed to send newsletter: {message}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in newsletter process: {e}")
        return False

def send_test_email(test_email):
    """Send a test email to verify formatting."""
    logger.info(f"Sending test email to {test_email}...")
    
    try:
        # Create newsletter data
        newsletter_data = create_sample_newsletter_data()
        
        # Initialize email manager
        email_manager = EmailManager()
        
        # Send test email
        success, message = email_manager.send_test_newsletter(
            newsletter_data, 
            newsletter_data['subject'], 
            test_email
        )
        
        if success:
            logger.info(f"✅ Test email sent successfully: {message}")
            return True
        else:
            logger.error(f"❌ Failed to send test email: {message}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error sending test email: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'test' and len(sys.argv) > 2:
            # Send test email
            test_email = sys.argv[2]
            send_test_email(test_email)
        elif command == 'send':
            # Send newsletter to all subscribers
            send_newsletter()
        else:
            print("Usage:")
            print("  python simple_automation.py test your@email.com  # Send test email")
            print("  python simple_automation.py send                 # Send to all subscribers")
    else:
        # Default: send newsletter
        send_newsletter()
