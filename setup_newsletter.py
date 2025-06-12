"""
Quick Setup Script for AI Newsletter System
Sets up daily automation and tests the system.
"""

import os
import subprocess
import sys
from dotenv import load_dotenv
from newsletter_automation import NewsletterAutomation

# Load environment variables from .env file
load_dotenv()

def check_environment():
    """Check if required environment variables are set."""
    required_vars = ['OPENAI_API_KEY', 'EMAIL_USER', 'EMAIL_PASS']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please set these in your .env file:")
        print("   OPENAI_API_KEY=your_openai_key")
        print("   EMAIL_USER=your_email@gmail.com") 
        print("   EMAIL_PASS=your_gmail_app_password")
        return False
    
    print("✅ All required environment variables are set!")
    return True

def test_newsletter_generation():
    """Test newsletter generation."""
    print("\n🤖 Testing newsletter generation...")
    try:
        result = subprocess.run(['python', 'main.py'], 
                              capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✅ Newsletter generation successful!")
            return True
        else:
            print(f"❌ Newsletter generation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error testing generation: {e}")
        return False

def test_email_system():
    """Test email sending."""
    print("\n📧 Testing email system...")
    automation = NewsletterAutomation()
    success = automation.test_email_system()
    
    if success:
        print("✅ Email system working!")
        return True
    else:
        print("❌ Email system failed!")
        return False

def main():
    """Main setup function."""
    print("🚀 AI Newsletter Setup & Testing")
    print("=" * 40)
    
    # Check environment
    if not check_environment():
        return
    
    # Test generation
    if not test_newsletter_generation():
        print("\n⚠️  Newsletter generation failed. Check your OPENAI_API_KEY.")
        return
    
    # Test email
    if not test_email_system():
        print("\n⚠️  Email system failed. Check your EMAIL_USER and EMAIL_PASS.")
        return
    
    print("\n🎉 Setup Complete! Your newsletter system is ready!")
    print("\n📅 To start daily automation:")
    print("   python newsletter_automation.py schedule")
    print("\n📧 To send a newsletter now:")
    print("   python newsletter_automation.py send")
    print("\n🧪 To test again:")
    print("   python newsletter_automation.py test")

if __name__ == "__main__":
    main()
