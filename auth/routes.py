from flask import Blueprint, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os
import secrets

# Print the current working directory to ensure it's correct
print("Current Working Directory:", os.getcwd())

# Explicitly specify the path to the .env file
env_path = os.path.join(os.getcwd(), '.gitignore', '.env')
load_dotenv(dotenv_path=env_path)

# Initialize Blueprint
auth_bp = Blueprint('auth', __name__)

# Initialize OAuth client
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

@auth_bp.route('/login')
def login():
    nonce = secrets.token_urlsafe(16)  # Generate a secure random nonce
    session['nonce'] = nonce  # Store nonce in session
    redirect_uri = url_for('auth.authorize', _external=True)  # Generate redirect URI
    return google.authorize_redirect(redirect_uri, nonce=nonce)  # Redirect to Google OAuth with nonce

@auth_bp.route('/login/authorized')
def authorize():
    token = google.authorize_access_token()  # Get OAuth token from response
    nonce = session.pop('nonce', None)  # Retrieve and remove nonce from session
    if nonce is None:
        return 'Missing nonce'  # Check if nonce is present
    user_info = google.parse_id_token(token, nonce=nonce)  # Parse ID token using nonce
    return f'Logged in as {user_info["name"]} ({user_info["email"]})'  # Display user info