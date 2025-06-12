"""
Protected Newsletter Viewer - Registration Required
Users must register/login to view newsletters
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import sqlite3
import os
from datetime import datetime
import secrets
import glob

app = Flask(__name__, template_folder='templates/newsletter_viewer')

# Production-ready configuration
import os
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Database setup - Use PostgreSQL in production, SQLite locally
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Production: Use PostgreSQL
    import psycopg2
    from urllib.parse import urlparse
    DB_PATH = DATABASE_URL
else:
    # Local development: Use SQLite
    DB_PATH = 'newsletter_users.db'

def init_database():
    """Initialize the user database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            registration_date TEXT,
            last_login TEXT,
            access_token TEXT,
            active BOOLEAN DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS newsletter_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            newsletter_date TEXT,
            viewed_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def is_valid_email(email):
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def register_user(email, name=None):
    """Register a new user or update existing user."""
    if not is_valid_email(email):
        return False, "Invalid email format"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute('SELECT id, access_token, name FROM users WHERE email = ?', (email.lower().strip(),))
        existing_user = cursor.fetchone()
        
        if existing_user:
            # User exists - update their info and return their data
            user_id, access_token, existing_name = existing_user
            
            # Update name if provided and different
            if name and name != existing_name:
                cursor.execute('UPDATE users SET name = ?, last_login = ? WHERE id = ?', 
                             (name, datetime.now().isoformat(), user_id))
            else:
                cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                             (datetime.now().isoformat(), user_id))
            
            conn.commit()
            conn.close()
            return True, {"user_id": user_id, "access_token": access_token, "returning_user": True}
        
        # New user - create account
        access_token = secrets.token_urlsafe(32)
        
        cursor.execute('''
            INSERT INTO users (email, name, registration_date, access_token)
            VALUES (?, ?, ?, ?)
        ''', (email.lower().strip(), name, datetime.now().isoformat(), access_token))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return True, {"user_id": user_id, "access_token": access_token}
        
    except sqlite3.IntegrityError:
        return False, "Email already registered"
    except Exception as e:
        return False, f"Registration failed: {e}"

def authenticate_user(email):
    """Authenticate user and return access token."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, access_token FROM users WHERE email = ? AND active = 1', (email.lower().strip(),))
        user = cursor.fetchone()
        
        if user:
            # Update last login
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now().isoformat(), user[0]))
            conn.commit()
        
        conn.close()
        
        if user:
            return True, {"user_id": user[0], "access_token": user[1]}
        else:
            return False, "Email not found or account inactive"
            
    except Exception as e:
        return False, f"Authentication failed: {e}"

def get_available_newsletters():
    """Get list of available newsletter files."""
    newsletter_files = glob.glob('output/newsletter_*.html')
    newsletters = []
    
    for file_path in sorted(newsletter_files, reverse=True):  # Most recent first
        filename = os.path.basename(file_path)
        # Extract date from filename (newsletter_2025_06_11.html)
        try:
            date_part = filename.replace('newsletter_', '').replace('.html', '')
            year, month, day = date_part.split('_')
            date_obj = datetime(int(year), int(month), int(day))
            newsletters.append({
                'filename': filename,
                'date': date_obj,
                'display_date': date_obj.strftime('%B %d, %Y'),
                'path': file_path
            })
        except:
            continue
    
    return newsletters

def log_newsletter_view(user_id, newsletter_date):
    """Log that a user viewed a newsletter."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO newsletter_views (user_id, newsletter_date, viewed_at)
            VALUES (?, ?, ?)
        ''', (user_id, newsletter_date, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    except:
        pass  # Logging is not critical

@app.route('/')
def index():
    """Main page - registration/login form."""
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    """Handle user registration and login."""
    email = request.form.get('email', '').strip()
    name = request.form.get('name', '').strip()
    
    if not email:
        flash('Email is required', 'error')
        return redirect(url_for('index'))
    
    success, result = register_user(email, name)
    
    if success:
        session['user_id'] = result['user_id']
        session['access_token'] = result['access_token']
        session['email'] = email
        
        if result.get('returning_user'):
            flash(f'Welcome back {name or email}!', 'success')
        else:
            flash(f'Welcome {name or email}! Registration successful.', 'success')
            
        return redirect(url_for('newsletter_list'))
    else:
        flash(result, 'error')
        return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    """Handle user login."""
    email = request.form.get('email', '').strip()
    
    if not email:
        flash('Email is required', 'error')
        return redirect(url_for('index'))
    
    success, result = authenticate_user(email)
    
    if success:
        session['user_id'] = result['user_id']
        session['access_token'] = result['access_token']
        session['email'] = email
        flash('Welcome back!', 'success')
        return redirect(url_for('newsletter_list'))
    else:
        flash(result, 'error')
        return redirect(url_for('index'))

@app.route('/newsletters')
def newsletter_list():
    """Show list of available newsletters (protected)."""
    if 'user_id' not in session:
        flash('Please register or login to view newsletters', 'error')
        return redirect(url_for('index'))
    
    newsletters = get_available_newsletters()
    return render_template('newsletter_list.html', newsletters=newsletters)

@app.route('/newsletter/<filename>')
def view_newsletter(filename):
    """View a specific newsletter (protected)."""
    if 'user_id' not in session:
        flash('Please register or login to view newsletters', 'error')
        return redirect(url_for('index'))
    
    # Security check - only allow viewing newsletter files
    if not filename.startswith('newsletter_') or not filename.endswith('.html'):
        flash('Invalid newsletter file', 'error')
        return redirect(url_for('newsletter_list'))
    
    file_path = os.path.join('output', filename)
    
    if not os.path.exists(file_path):
        flash('Newsletter not found', 'error')
        return redirect(url_for('newsletter_list'))
    
    # Log the view
    try:
        date_part = filename.replace('newsletter_', '').replace('.html', '')
        log_newsletter_view(session['user_id'], date_part)
    except:
        pass
    
    # Read and return the newsletter content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            newsletter_content = f.read()
        
        return newsletter_content
    except Exception as e:
        flash(f'Error loading newsletter: {e}', 'error')
        return redirect(url_for('newsletter_list'))

@app.route('/logout')
def logout():
    """Logout user."""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/admin/users')
def admin_users():
    """Admin page to view registered users."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT email, name, registration_date, last_login
            FROM users 
            WHERE active = 1 
            ORDER BY registration_date DESC
        ''')
        users = cursor.fetchall()
        
        conn.close()
        
        return render_template('admin_users.html', users=users)
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    init_database()
    print("Starting Protected Newsletter Viewer...")
    
    # Production vs Development
    if os.environ.get('FLASK_ENV') == 'production':
        print("Running in PRODUCTION mode")
        port = int(os.environ.get('PORT', 5001))
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        print("Running in DEVELOPMENT mode")
        print("Visit http://localhost:5001 to register and view newsletters")
        app.run(debug=True, host='0.0.0.0', port=5001)
