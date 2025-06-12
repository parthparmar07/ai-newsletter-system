"""
Simplified email manager for sending beautiful newsletters
"""

import sqlite3
import yagmail
import os
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class EmailManager:
    def __init__(self):
        self.sender_email = os.getenv('EMAIL_USER') or os.getenv('EMAIL_ADDRESS')
        self.sender_password = os.getenv('EMAIL_PASS') or os.getenv('EMAIL_PASSWORD')
        self.db_path = 'subscribers.db'
        
    def render_beautiful_email(self, newsletter_data: dict) -> str:
        """Create beautiful HTML email from newsletter data."""
        
        articles_html = ""
        for article in newsletter_data.get('articles', []):
            articles_html += f"""
            <div style="background: #ffffff; border-radius: 12px; padding: 25px; margin-bottom: 20px; border: 1px solid #e1e8ed; border-top: 4px solid #667eea;">
                <div style="margin-bottom: 15px;">
                    <span style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; margin-right: 10px;">{article.get('source', 'News')}</span>
                    <span style="background: #f39c12; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: 600;">★ {article.get('importance_score', 8.0)}</span>
                </div>
                <h3 style="font-size: 1.4rem; font-weight: 700; color: #2c3e50; margin-bottom: 12px; line-height: 1.4;">
                    <a href="{article.get('url', '#')}" style="color: inherit; text-decoration: none;" target="_blank">{article.get('title', 'Untitled')}</a>
                </h3>
                <p style="color: #666; line-height: 1.6; margin-bottom: 15px;">{article.get('summary', '')}</p>
                <a href="{article.get('url', '#')}" style="display: inline-block; background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 10px 20px; border-radius: 25px; text-decoration: none; font-weight: 600; font-size: 0.9rem;" target="_blank">Read Full Article →</a>
            </div>
            """
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{newsletter_data.get('subject', 'AI Newsletter')}</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #2c3e50; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px;">
            <div style="max-width: 650px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.1);">
                
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center;">
                    <h1 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 10px; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">🤖 AI Newsletter</h1>
                    <p style="font-size: 1.1rem; opacity: 0.9; margin: 0;">{newsletter_data.get('date', '')} • Curated by AI</p>
                </div>
                
                <!-- Content -->
                <div style="padding: 40px 30px;">
                    <div style="font-size: 1.1rem; color: #555; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #f8f9ff 0%, #e3f2fd 100%); border-radius: 12px; border-left: 4px solid #667eea;">
                        <p style="margin: 0;">{newsletter_data.get('intro', 'Welcome to today\'s AI Newsletter!')}</p>
                    </div>
                    
                    <div>
                        {articles_html}
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e1e8ed;">
                    <div style="color: #666; font-size: 0.9rem; line-height: 1.5;">
                        <p style="margin: 0 0 10px 0;"><strong>Thanks for reading the AI Newsletter!</strong></p>
                        <p style="margin: 0;">Powered by AI • Delivered with ❤️</p>
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <a href="#" style="color: #667eea; text-decoration: none; font-weight: 600; padding: 8px 16px; border-radius: 20px; border: 2px solid #667eea; margin: 0 10px;">View Online</a>
                        <a href="#" style="color: #667eea; text-decoration: none; font-weight: 600; padding: 8px 16px; border-radius: 20px; border: 2px solid #667eea; margin: 0 10px;">Manage Subscription</a>
                    </div>
                    
                    <div style="margin-top: 20px; font-size: 0.8rem; color: #999;">
                        <p style="margin: 0;">Don't want to receive these emails? <a href="#" style="color: #667eea; text-decoration: none;">Unsubscribe here</a></p>
                    </div>
                </div>
                
            </div>
        </body>
        </html>
        """
        
        return html_content
        
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
    
    def send_newsletter(self, newsletter_data: dict, subject: str) -> Tuple[bool, str]:
        """Send newsletter to all active subscribers."""
        subscribers = self.get_active_subscribers()
        
        if not subscribers:
            return False, "No active subscribers found"
        
        if not self.sender_email or not self.sender_password:
            return False, "Email credentials not configured"
        
        try:
            html_content = self.render_beautiful_email(newsletter_data)
            yag = yagmail.SMTP(self.sender_email, self.sender_password)
            
            successful_sends = 0
            failed_sends = 0
            
            for email in subscribers:
                try:
                    yag.send(to=email, subject=subject, contents=html_content)
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
    
    def send_test_newsletter(self, newsletter_data: dict, subject: str, test_email: str) -> Tuple[bool, str]:
        """Send a test newsletter to a specific email address."""
        if not self.sender_email or not self.sender_password:
            return False, "Email credentials not configured"
        
        try:
            html_content = self.render_beautiful_email(newsletter_data)
            yag = yagmail.SMTP(self.sender_email, self.sender_password)
            yag.send(to=test_email, subject=f"[TEST] {subject}", contents=html_content)
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
