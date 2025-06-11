"""
Flask web app for newsletter subscription management.
A simple subscription system for the AI Newsletter.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import sqlite3
import csv
import os
from datetime import datetime
import re
import logging

app = Flask(__name__, template_folder='templates/subscription')

# Production-ready configuration
import os
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup - Use PostgreSQL in production, SQLite locally
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Production: Use PostgreSQL
    import psycopg2
    from urllib.parse import urlparse
    DB_PATH = DATABASE_URL
else:
    # Local development: Use SQLite
    DB_PATH = 'subscribers.db'

def init_database():
    """Initialize the SQLite database for subscribers."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            subscribed_date TEXT,
            active BOOLEAN DEFAULT 1,
            unsubscribe_token TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def is_valid_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def add_subscriber(email, name=None):
    """Add a new subscriber to the database."""
    if not is_valid_email(email):
        return False, "Invalid email format"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Generate unsubscribe token
        import secrets
        unsubscribe_token = secrets.token_urlsafe(32)
        
        cursor.execute('''
            INSERT INTO subscribers (email, name, subscribed_date, unsubscribe_token)
            VALUES (?, ?, ?, ?)
        ''', (email.lower().strip(), name, datetime.now().isoformat(), unsubscribe_token))
        
        conn.commit()
        conn.close()
        
        logger.info(f"New subscriber added: {email}")
        return True, "Successfully subscribed!"
        
    except sqlite3.IntegrityError:
        return False, "Email already subscribed"
    except Exception as e:
        logger.error(f"Error adding subscriber: {e}")
        return False, "Subscription failed. Please try again."

def get_all_subscribers():
    """Get all active subscribers."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT email, name FROM subscribers WHERE active = 1')
    subscribers = cursor.fetchall()
    
    conn.close()
    return subscribers

def unsubscribe_user(token):
    """Unsubscribe a user using their token."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE subscribers 
            SET active = 0 
            WHERE unsubscribe_token = ? AND active = 1
        ''', (token,))
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return True, "Successfully unsubscribed"
        else:
            conn.close()
            return False, "Invalid unsubscribe link"
            
    except Exception as e:
        logger.error(f"Error unsubscribing: {e}")
        return False, "Unsubscribe failed"

@app.route('/')
def index():
    """Main subscription page."""
    return render_template('subscribe.html')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    """Handle subscription form submission."""
    email = request.form.get('email', '').strip()
    name = request.form.get('name', '').strip()
    
    if not email:
        flash('Email is required', 'error')
        return redirect(url_for('index'))
    
    success, message = add_subscriber(email, name)
    
    if success:
        flash(message, 'success')
        return redirect(url_for('success'))
    else:
        flash(message, 'error')
        return redirect(url_for('index'))

@app.route('/success')
def success():
    """Success page after subscription."""
    return render_template('success.html')

@app.route('/unsubscribe/<token>')
def unsubscribe(token):
    """Handle unsubscribe requests."""
    success, message = unsubscribe_user(token)
    return render_template('unsubscribe.html', success=success, message=message)

@app.route('/admin/subscribers')
def admin_subscribers():
    """Admin page to view subscribers (password protected in production)."""
    subscribers = get_all_subscribers()
    return render_template('admin.html', subscribers=subscribers)

@app.route('/admin/export')
def export_subscribers():
    """Export subscribers to CSV."""
    subscribers = get_all_subscribers()
    
    # Create CSV content
    csv_content = "Email,Name\n"
    for email, name in subscribers:
        csv_content += f"{email},{name or ''}\n"
    
    # Save to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'subscribers_export_{timestamp}.csv'
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        f.write(csv_content)
    
    flash(f'Subscribers exported to {filename}', 'success')
    return redirect(url_for('admin_subscribers'))

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    print("Starting Newsletter Subscription App...")
    
    # Production vs Development
    if os.environ.get('FLASK_ENV') == 'production':
        print("Running in PRODUCTION mode")
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        print("Running in DEVELOPMENT mode")
        print("Visit http://localhost:5000 to see the subscription page")
        app.run(debug=True, host='0.0.0.0', port=5000)
