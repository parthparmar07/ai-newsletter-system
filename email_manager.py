"""
Email manager for sending newsletters to subscribers.
Integrates with the subscription system to send bulk emails.
"""

import sqlite3
import yagmail
import os
from datetime import datetime
from typing import List, Tuple
import logging
from config import EMAIL_ADDRESS, EMAIL_PASSWORD

logger = logging.getLogger(__name__)

class EmailManager:
    """Manages email sending for newsletter distribution."""
    
    def __init__(self):
        self.sender_email = EMAIL_ADDRESS
        self.sender_password = EMAIL_PASSWORD
        self.db_path = 'subscribers.db'
        
    def get_active_subscribers(self) -> List[str]:
        """Get all active subscriber email addresses."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT email FROM subscribers WHERE active = 1')
            subscribers = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return subscribers
            
        except Exception as e:
            logger.error(f"Error getting subscribers: {e}")
            return []
    
    def send_newsletter(self, html_content: str, subject: str) -> Tuple[bool, str]:
        """Send newsletter to all active subscribers."""
        subscribers = self.get_active_subscribers()
        
        if not subscribers:
            return False, "No active subscribers found"
        
        if not self.sender_email or not self.sender_password:
            return False, "Email credentials not configured"
        
        try:
            # Initialize yagmail
            yag = yagmail.SMTP(self.sender_email, self.sender_password)
            
            # Send to all subscribers
            successful_sends = 0
            failed_sends = 0
            
            for email in subscribers:
                try:
                    yag.send(
                        to=email,
                        subject=subject,
                        contents=html_content
                    )
                    successful_sends += 1
                    logger.info(f"Newsletter sent to: {email}")
                    
                except Exception as e:
                    failed_sends += 1
                    logger.error(f"Failed to send to {email}: {e}")
            
            yag.close()
            
            total_subscribers = len(subscribers)
            message = f"Newsletter sent to {successful_sends}/{total_subscribers} subscribers"
            
            if failed_sends > 0:
                message += f" ({failed_sends} failed)"
            
            logger.info(message)
            return True, message
            
        except Exception as e:
            error_msg = f"Email sending failed: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def send_test_newsletter(self, html_content: str, subject: str, test_email: str) -> Tuple[bool, str]:
        """Send a test newsletter to a specific email address."""
        if not self.sender_email or not self.sender_password:
            return False, "Email credentials not configured"
        
        try:
            yag = yagmail.SMTP(self.sender_email, self.sender_password)
            
            yag.send(
                to=test_email,
                subject=f"[TEST] {subject}",
                contents=html_content
            )
            
            yag.close()
            
            message = f"Test newsletter sent to: {test_email}"
            logger.info(message)
            return True, message
            
        except Exception as e:
            error_msg = f"Test email failed: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_subscriber_count(self) -> int:
        """Get the count of active subscribers."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM subscribers WHERE active = 1')
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
            
        except Exception as e:
            logger.error(f"Error getting subscriber count: {e}")
            return 0
