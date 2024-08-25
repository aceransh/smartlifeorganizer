import os
from flask import Flask, session, render_template
from finance_tracker.routes import finance_bp
from auth.routes import auth_bp, oauth  # Importing the OAuth instance
from to_do_list.routes import to_do_bp  # Import the to-do blueprint
from models import db, User
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from email_utils import send_email, send_daily_reminder, check_reminders  # Import the necessary functions
from datetime import datetime

# Import Flask-Migrate for handling migrations
from flask_migrate import Migrate

# Load environment variables from the .env file located in the /SmartLifeOrganizer folder
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure the SQLite database URI for SQLAlchemy
# The database file (smart_life_organizer.db) is located in the instance folder for security and separation of concerns
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_life_organizer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable SQLAlchemy event notifications to save resources
app.secret_key = os.getenv('SECRET_KEY')  # Set the secret key for session management from environment variables

# Initialize SQLAlchemy and OAuth with the app
db.init_app(app)
oauth.init_app(app)

# Initialize Flask-Migrate with the app and database
migrate = Migrate(app, db)

# Create database tables if they don't already exist
with app.app_context():
    db.create_all()

# Register the Blueprints for authentication and finance routes with the Flask app
app.register_blueprint(auth_bp)
app.register_blueprint(finance_bp)
app.register_blueprint(to_do_bp)

# Define a custom Jinja filter for formatting datetime
def datetimeformat(value, format='%Y-%m-%dT%H:%M'):
    return value.strftime(format) if value else ''

# Register the custom Jinja filter
app.jinja_env.filters['datetimeformat'] = datetimeformat

# Set up the scheduler
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(lambda: send_daily_reminder(app), 'cron', hour=20)  # Send daily emails at 8 PM
scheduler.add_job(lambda: check_reminders(app), 'interval', minutes=1)  # Check for to-do reminders every minute
scheduler.start()

@app.route('/')
def home():
    """
    Home route that checks if the user is logged in.
    If logged in, it renders the home template with user information.
    If not logged in, it provides a link to log in with Google.
    """
    return render_template('home.html')

@app.route('/trigger-email')
def trigger_email():
    if 'user' in session:
        recipient = session['user']['email']
        subject = "Test Email from Smart Life Organizer"
        body = "This is a test email to ensure that the email functionality is working correctly."

        send_email(recipient=recipient, subject=subject, body=body)
        
        return f"Test email sent to {recipient}!"
    else:
        return "You must be logged in to send a test email."

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode