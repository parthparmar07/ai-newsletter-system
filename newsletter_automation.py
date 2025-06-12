"""
Daily Newsletter Automation
Automatically generates and sends newsletters to subscribers every day.
"""

import schedule
import time
import os
import subprocess
import logging
from datetime import datetime
from email_manager import EmailManager
import glob
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging (Windows-compatible)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('newsletter_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NewsletterAutomation:
    """Handles daily newsletter generation and sending."""
    
    def __init__(self):
        self.email_manager = EmailManager()
        
    def generate_newsletter(self):
        """Generate today's newsletter using the AI system."""
        try:
            logger.info("Starting newsletter generation...")
            
            # Run the main newsletter generation script
            result = subprocess.run(['python', 'main.py'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("Newsletter generated successfully")
                return True, result.stdout
            else:
                logger.error(f"Newsletter generation failed: {result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            logger.error("Newsletter generation timed out")
            return False, "Generation timed out"
        except Exception as e:
            logger.error(f"Error generating newsletter: {e}")
            return False, str(e)
      def get_latest_newsletter(self):
        """Get the most recently generated newsletter data."""
        try:
            # Find the most recent newsletter file
            newsletter_files = glob.glob('output/newsletter_*.html')
            if not newsletter_files:
                return None, "No newsletter files found"
            
            # Get the most recent file
            latest_file = max(newsletter_files, key=os.path.getctime)
            
            # Read the content
            with open(latest_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract date from filename for subject
            filename = os.path.basename(latest_file)
            date_str = filename.replace('newsletter_', '').replace('.html', '')
            date_obj = datetime.strptime(date_str, '%Y_%m_%d')
            formatted_date = date_obj.strftime('%B %d, %Y')
            
            # Parse the newsletter content into structured data
            # For now, create a simple structure - you can enhance this later
            newsletter_data = {
                'subject': f"AI Newsletter - {formatted_date}",
                'date': formatted_date,
                'intro': "Welcome to today's AI Newsletter! Here are the most important developments in AI and technology.",
                'articles': [
                    {
                        'title': 'Latest AI Developments',
                        'summary': 'Today\'s curated AI news and insights.',
                        'source': 'AI News',
                        'importance_score': 8.5,
                        'url': '#'
                    }
                ]
            }
            
            return newsletter_data, formatted_date
            
        except Exception as e:
            logger.error(f"Error reading newsletter: {e}")
            return None, str(e)
      def send_daily_newsletter(self):
        """Generate and send the daily newsletter."""
        logger.info("Starting daily newsletter process...")
        
        # Step 1: Generate newsletter
        success, message = self.generate_newsletter()
        if not success:
            logger.error(f"Failed to generate newsletter: {message}")
            return False
        
        # Step 2: Get the generated newsletter data
        newsletter_data, date_or_error = self.get_latest_newsletter()
        if newsletter_data is None:
            logger.error(f"Failed to read newsletter: {date_or_error}")
            return False
        
        # Step 3: Send to subscribers using new beautiful template
        subject = newsletter_data['subject']
        success, message = self.email_manager.send_newsletter(newsletter_data, subject)
        
        if success:
            logger.info(f"Newsletter sent successfully: {message}")
            return True
        else:
            logger.error(f"Failed to send newsletter: {message}")
            return False
    
    def test_email_system(self):
        """Test the email system with a simple test."""
        logger.info("Testing email system...")
        
        content, date_or_error = self.get_latest_newsletter()
        if content is None:
            logger.error("No newsletter found for testing")
            return False
        
        subject = f"Test Newsletter - {date_or_error}"
        success, message = self.email_manager.send_newsletter(content, subject)
        
        if success:
            logger.info(f"Test email sent: {message}")
        else:
            logger.error(f"Test failed: {message}")
        
        return success

def run_scheduler():
    """Run the newsletter automation scheduler."""
    automation = NewsletterAutomation()
    
    # Schedule daily newsletter at 9:00 AM
    schedule.every().day.at("09:00").do(automation.send_daily_newsletter)
    
    logger.info("Newsletter automation started!")
    logger.info("Scheduled to run daily at 9:00 AM")
    logger.info("Use Ctrl+C to stop")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Newsletter automation stopped")

def main():
    """Main function with command line options."""
    import sys
    
    automation = NewsletterAutomation()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'test':
            # Test the system
            automation.test_email_system()
        elif command == 'send':
            # Send newsletter once
            automation.send_daily_newsletter()
        elif command == 'schedule':
            # Run scheduler
            run_scheduler()
        else:
            print("Usage:")
            print("  python newsletter_automation.py test      # Test email system")
            print("  python newsletter_automation.py send      # Send newsletter once")
            print("  python newsletter_automation.py schedule  # Run daily scheduler")
    else:
        # Default: run scheduler
        run_scheduler()

if __name__ == "__main__":
    main()
