from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os
import secrets

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Initialize OAuth client
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('CLIENT_ID'),  # Google Client ID
    client_secret=os.getenv('CLIENT_SECRET'),  # Google Client Secret
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri='http://localhost:5000/login/authorized',  # Redirect URI after login
    client_kwargs={'scope': 'openid profile email'},  # OAuth scopes
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'  # OpenID Connect discovery document
)

@app.route('/')
def home():
    return 'Welcome to the Smart Life Organizer! <a href="/login">Login with Google</a>'

@app.route('/login')
def login():
    nonce = secrets.token_urlsafe(16)  # Generate a secure random nonce
    session['nonce'] = nonce  # Store nonce in session
    redirect_uri = url_for('authorize', _external=True)  # Generate redirect URI
    return google.authorize_redirect(redirect_uri, nonce=nonce)  # Redirect to Google OAuth with nonce

@app.route('/login/authorized')
def authorize():
    token = google.authorize_access_token()  # Get OAuth token from response
    nonce = session.pop('nonce', None)  # Retrieve and remove nonce from session
    if nonce is None:
        return 'Missing nonce'  # Check if nonce is present
    user_info = google.parse_id_token(token, nonce=nonce)  # Parse ID token using nonce
    return f'Logged in as {user_info["name"]} ({user_info["email"]})'  # Display user info

if __name__ == '__main__':
    app.run(debug=True)