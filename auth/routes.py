from flask import Blueprint, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from functools import wraps
from dotenv import load_dotenv
import os
import secrets

# Load environment variables from the .env file
load_dotenv()

# Initialize the Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

# Initialize OAuth client for Google authentication
oauth = OAuth()
google = oauth.register(
    name='google',
    client_id=os.getenv('CLIENT_ID'),  # Load from .env
    client_secret=os.getenv('CLIENT_SECRET'),  # Load from .env
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://oauth2.googleapis.com/token',
    redirect_uri='http://localhost:5000/login/authorized',  # Redirect URI after login
    client_kwargs={'scope': 'openid profile email'},  # OAuth scopes
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'  # OpenID Connect discovery document
)

def login_required(function):
    """
    Decorator function to restrict access to certain routes.
    Checks if a user is logged in by verifying the session.
    If not logged in, it redirects to the login page.
    """
    @wraps(function)
    def dec_function(*args, **kwargs):
        if 'user' not in session:  # If user is not in session, redirect to login
            return redirect(url_for('auth.login'))
        else:
            return function(*args, **kwargs)  # If logged in, proceed to the route
    return dec_function

@auth_bp.route('/login')
def login():
    """
    Route to initiate the login process using Google OAuth.
    Generates a nonce for security and stores it in the session.
    Redirects the user to the Google login page.
    """
    nonce = secrets.token_urlsafe(16)  # Generate a secure random nonce
    session['nonce'] = nonce  # Store nonce in session
    redirect_uri = url_for('auth.authorize', _external=True)  # Generate redirect URI
    return google.authorize_redirect(redirect_uri, nonce=nonce)  # Redirect to Google OAuth with nonce

@auth_bp.route('/login/authorized')
def authorize():
    """
    Route to handle the response from Google after the user has logged in.
    Verifies the ID token and extracts user information.
    """
    token = google.authorize_access_token()  # Get OAuth token from response
    nonce = session.pop('nonce', None)  # Retrieve and remove nonce from session
    if nonce is None:
        return 'Missing nonce'  # Check if nonce is present
    user_info = google.parse_id_token(token, nonce=nonce)  # Parse ID token using nonce
    session['user'] = user_info
    return f'Logged in as {user_info["name"]} ({user_info["email"]})'  # Display user info

@auth_bp.route('/logout')
def logout():
    """
    Route to log the user out by clearing the session.
    Redirects the user to the home page after logging out.
    """
    session.clear()  # Clear the session
    return redirect(url_for('home'))  # Redirect to home page
