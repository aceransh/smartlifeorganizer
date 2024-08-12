import os
from flask import Flask, session
from finance_tracker.models import db, Expense
from finance_tracker.routes import finance_bp
from auth.routes import auth_bp, oauth, login_required  # Import the Blueprint and OAuth
from dotenv import load_dotenv

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

# Register the Blueprint for authentication routes with the Flask app
app.register_blueprint(auth_bp)
app.register_blueprint(finance_bp)

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
