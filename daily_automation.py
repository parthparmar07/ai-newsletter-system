"""
Daily Newsletter Automation for Render Deployment
Runs automatically and generates/sends newsletters daily
"""

import os
import schedule
import time
import logging
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_daily_newsletter():
    """Run the daily newsletter generation and sending."""
    logger.info("🚀 Starting daily newsletter automation...")
    
    try:
        # Run the simple automation script
        result = subprocess.run(
            ['python', 'simple_automation.py', 'send'], 
            capture_output=True, 
            text=True, 
            timeout=120
        )
        
        if result.returncode == 0:
            logger.info("✅ Daily newsletter completed successfully")
            logger.info(f"Output: {result.stdout}")
        else:
            logger.error(f"❌ Daily newsletter failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Daily newsletter timed out")
    except Exception as e:
        logger.error(f"❌ Error in daily newsletter: {e}")

def start_scheduler():
    """Start the daily newsletter scheduler."""
    # Schedule newsletter for 9:00 AM every day
    schedule.every().day.at("09:00").do(run_daily_newsletter)
    
    logger.info("📅 Daily newsletter scheduler started!")
    logger.info("📧 Newsletter will be sent daily at 9:00 AM")
    logger.info("🔄 Use Ctrl+C to stop")
    
    # Also run once immediately for testing
    logger.info("🧪 Running initial newsletter...")
    run_daily_newsletter()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("🛑 Newsletter automation stopped")

if __name__ == "__main__":
    start_scheduler()
