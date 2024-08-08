from flask import Flask
from finance_tracker.models import db, Expense
from auth.routes import auth_bp, oauth  # Import the Blueprint and OAuth
from dotenv import load_dotenv
import os

# Load environment variables from the .env file in the /SmartLifeOrganizer folder
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY')

# Initialize SQLAlchemy and OAuth with the app
db.init_app(app)
oauth.init_app(app)

with app.app_context():
    db.create_all()

# Register the Blueprint
app.register_blueprint(auth_bp)

@app.route('/')
def home():
    return 'Welcome to the Smart Life Organizer! <a href="/login">Login with Google</a>'

if __name__ == '__main__':
    app.run(debug=True)