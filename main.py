import schedule
import time
from datetime import datetime
from loguru import logger
import sys
import os

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from content_collector import ContentCollector
from ai_curator import AIContentCurator
from newsletter_generator import NewsletterGenerator

class NewsletterScheduler:
    """Schedules and manages newsletter generation"""
    
    def __init__(self):
        self.config = Config()
        self.content_collector = ContentCollector()
        self.ai_curator = AIContentCurator()
        self.newsletter_generator = NewsletterGenerator()
        
        # Setup logging
        logger.add("newsletter.log", rotation="1 week", retention="4 weeks")
        
    def generate_and_send_newsletter(self):
        """Main function to generate and send newsletter"""
        try:
            logger.info("Starting newsletter generation process...")
            
            # Validate configuration
            self.config.validate_config()
            
            # Step 1: Collect content from all sources
            logger.info("Collecting content...")
            articles = self.content_collector.collect_all_content()
            
            if not articles:
                logger.warning("No articles collected. Skipping newsletter generation.")
                return
            
            # Step 2: Use AI to curate and enhance content
            logger.info("Curating content with AI...")
            curated_articles = self.ai_curator.curate_articles(articles)
            
            # Step 3: Generate newsletter intro and outro
            intro = self.ai_curator.generate_newsletter_intro(curated_articles)
            outro = self.ai_curator.generate_newsletter_outro()
            
            # Step 4: Generate newsletter
            newsletter = self.newsletter_generator.generate_newsletter_content(
                articles=curated_articles,
                intro=intro,
                outro=outro
            )
            
            # Step 5: Save newsletter locally
            saved_file = self.newsletter_generator.save_newsletter_html(newsletter)
            logger.info(f"Newsletter saved locally: {saved_file}")
            
            # Step 6: Send newsletter
            if self.newsletter_generator.send_newsletter(newsletter):                logger.info("Newsletter sent successfully!")
            else:
                logger.error("Failed to send newsletter")
            
        except Exception as e:
            logger.error(f"Error in newsletter generation process: {e}")
    
    def run_once(self):
        """Run newsletter generation once (for testing)"""
        logger.info("Running newsletter generation once...")
        self.generate_and_send_newsletter()
    
    def start_scheduler(self):
        """Start the scheduled newsletter generation"""
        logger.info(f"Starting newsletter scheduler...")
        
        schedule_day = self.config.NEWSLETTER_SCHEDULE_DAY.lower()
        schedule_time = self.config.NEWSLETTER_SCHEDULE_TIME
        
        if schedule_day == "daily":
            logger.info(f"Daily newsletter scheduled for {schedule_time}")
            schedule.every().day.at(schedule_time).do(self.generate_and_send_newsletter)
        else:
            logger.info(f"Weekly newsletter scheduled for {schedule_day} at {schedule_time}")
            schedule_func = getattr(schedule.every(), schedule_day)
            schedule_func.at(schedule_time).do(self.generate_and_send_newsletter)
        
        logger.info("Scheduler started. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")

def main():
    """Main entry point"""
    scheduler = NewsletterScheduler()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--run-once":
        # Run once for testing
        scheduler.run_once()
    else:
        # Start scheduler
        scheduler.start_scheduler()

if __name__ == "__main__":
    main()
