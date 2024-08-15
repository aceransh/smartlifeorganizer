import os
from flask import Flask, session
from finance_tracker.routes import finance_bp
from auth.routes import auth_bp, oauth  # Importing the OAuth instance
from to_do_list.routes import to_do_bp  # Import the to-do blueprint
from models import db, User
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from email_utils import send_email, send_daily_reminder  # Import the send_daily_reminder function
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