import os
from flask import Flask, session
from finance_tracker.routes import finance_bp
from auth.routes import auth_bp, oauth  # Importing the OAuth instance
from models import db, User
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from email_utils import send_email  # Assuming email_utils.py is in the same directory
from datetime import datetime

# Load environment variables from the .env file located in the /SmartLifeOrganizer folder
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure the SQLite database URI for SQLAlchemy
# The database file (expenses.db) is located in the instance folder for security and separation of concerns
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable SQLAlchemy event notifications to save resources
app.secret_key = os.getenv('SECRET_KEY')  # Set the secret key for session management from environment variables

# Initialize SQLAlchemy and OAuth with the app
db.init_app(app)
oauth.init_app(app)

# Create database tables if they don't already exist
with app.app_context():
    db.create_all()

# Register the Blueprints for authentication and finance routes with the Flask app
app.register_blueprint(auth_bp)
app.register_blueprint(finance_bp)

# Function to send daily email reminders
def send_daily_reminder():
    with app.app_context():
        # Retrieve all users who have subscribed to daily reminders
        users = User.query.filter_by(daily_reminder=True).all()
        for user in users:
            send_email(
                recipient=user.email,
                subject="Daily Expense Reminder",
                body="This is your daily reminder to log your expenses!"
            )

# Set up the scheduler
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(send_daily_reminder, 'cron', hour=20)  # Send daily emails at 8 PM
scheduler.start()

@app.route('/')
def home():
    """
    Home route that checks if the user is logged in.
    If logged in, it displays the user's name and a logout link.
    If not logged in, it provides a link to log in with Google.
    """
    if 'user' in session:
        return (f'Logged in as {session["user"]["name"]} '
                f'(email: {session["user"]["email"]}) '
                '<a href="/logout">Logout</a> ')
    else:
        return 'Welcome to the Smart Life Organizer! <a href="/login">Login with Google</a>'

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode