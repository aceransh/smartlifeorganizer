import os
from flask import Flask
from finance_tracker.models import db, Expense
from auth.routes import auth_bp, oauth, login_required  # Import the Blueprint and OAuth
from dotenv import load_dotenv

# Load environment variables from the .env file in the /SmartLifeOrganizer folder
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure the SQLite database URI for SQLAlchemy
# The database file (expenses.db) is located in the instance folder for security
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable tracking modifications
app.secret_key = os.getenv('SECRET_KEY')  # Set the secret key for session management

# Initialize SQLAlchemy and OAuth with the app
db.init_app(app)
oauth.init_app(app)

# Create database tables if they don't already exist
with app.app_context():
    db.create_all()

# Register the Blueprint for authentication routes
app.register_blueprint(auth_bp)

@app.route('/')
def home():
    """Home route that provides a link to log in with Google."""
    return 'Welcome to the Smart Life Organizer! <a href="/login">Login with Google</a>'

@app.route('/test-db')
@login_required  # Protect this route, making it accessible only to authenticated users
def test():
    """Test route to add an expense to the database and verify its functionality."""
    new_expense = Expense(name="Test Expense", amount=10.99, category="Test Category")
    db.session.add(new_expense)
    db.session.commit()

    expense = Expense.query.filter_by(name="Test Expense").first()

    if expense:
        return f'Database works fine! Added {expense.name} which was {expense.amount} and was category: {expense.category}'
    else:
        return 'Database is not working properly'

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode
