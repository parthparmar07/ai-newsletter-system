import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from typing import List
from datetime import datetime
from loguru import logger
import os

from models import Newsletter, Article
from config import Config

class NewsletterGenerator:
    """Generates and sends newsletters"""    
    def __init__(self):
        self.config = Config()
        self.template_env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))
        )
    
    def generate_newsletter_content(self, articles: List[Article], intro: str, outro: str) -> Newsletter:
        """Generate newsletter content"""
        today = datetime.now()
        
        # Create an engaging subject line for daily newsletter
        weekday = today.strftime('%A')
        month_day = today.strftime('%B %d')
        subject = f"🚀 Daily AI Brief - {weekday}, {month_day}: Top 5 Tech Stories"
        
        newsletter = Newsletter(
            date=today,
            articles=articles,
            intro=intro,
            outro=outro,
            subject=subject
        )
        
        return newsletter
    
    def render_html_newsletter(self, newsletter: Newsletter) -> str:
        """Render newsletter as HTML"""
        try:
            template = self.template_env.get_template('newsletter_template.html')
            html_content = template.render(
                newsletter=newsletter,
                config=self.config
            )
            return html_content
            
        except Exception as e:
            logger.error(f"Error rendering HTML newsletter: {e}")
            return self._generate_fallback_html(newsletter)
    
    def _generate_fallback_html(self, newsletter: Newsletter) -> str:
        """Generate a simple fallback HTML if template fails"""
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #007acc;">{self.config.NEWSLETTER_NAME}</h1>
            <h2>{newsletter.date.strftime('%B %d, %Y')}</h2>
            
            <p><em>{newsletter.intro}</em></p>
            
            <h3>Top Stories</h3>
        """
        
        for article in newsletter.articles:
            html += f"""
            <div style="margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #ccc;">
                <h4><a href="{article.url}" style="color: #007acc;">{article.title}</a></h4>
                <p style="font-size: 12px; color: #666;">
                    {article.source} | Score: {article.importance_score:.1f}
                </p>
                <p>{article.ai_summary}</p>
            </div>
            """
        
        html += f"""
            <p><em>{newsletter.outro}</em></p>
            <hr>
            <p style="text-align: center; color: #666; font-size: 12px;">
                {self.config.NEWSLETTER_NAME} | Curated by AI
            </p>
        </body>
        </html>
        """
        
        return html
    
    def send_newsletter(self, newsletter: Newsletter) -> bool:
        """Send newsletter via email"""
        try:
            # Render HTML content
            html_content = self.render_html_newsletter(newsletter)
            
            # Setup email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = newsletter.subject
            msg['From'] = f"{self.config.SENDER_NAME} <{self.config.EMAIL_ADDRESS}>"
            msg['To'] = ", ".join(self.config.RECIPIENT_EMAILS)
            
            # Create HTML part
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT) as server:
                server.starttls()
                server.login(self.config.EMAIL_ADDRESS, self.config.EMAIL_PASSWORD)
                
                for recipient in self.config.RECIPIENT_EMAILS:
                    if recipient.strip():
                        server.send_message(msg, to_addrs=[recipient.strip()])
                        logger.info(f"Newsletter sent to {recipient}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending newsletter: {e}")
            return False
    
    def save_newsletter_html(self, newsletter: Newsletter, filename: str = None) -> str:
        """Save newsletter as HTML file"""
        if not filename:
            filename = f"newsletter_{newsletter.date.strftime('%Y_%m_%d')}.html"
        
        filepath = os.path.join(os.path.dirname(__file__), 'output', filename)
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        try:
            html_content = self.render_html_newsletter(newsletter)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Newsletter saved to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving newsletter: {e}")
            return ""
