from flask import Blueprint, redirect, url_for, session, render_template, flash, request
from authlib.integrations.flask_client import OAuth
from models import db, User
from email_utils import send_email
from functools import wraps
from dotenv import load_dotenv
import os
import secrets

# Load environment variables from the .env file
load_dotenv()

# Initialize the Blueprint for authentication-related routes
auth_bp = Blueprint('auth', __name__)

# Initialize OAuth client for Google authentication
oauth = OAuth()
google = oauth.register(
    name='google',
    client_id=os.getenv('CLIENT_ID'),  # Load the CLIENT_ID from .env
    client_secret=os.getenv('CLIENT_SECRET'),  # Load the CLIENT_SECRET from .env
    authorize_url='https://accounts.google.com/o/oauth2/auth',  # Google OAuth authorization URL
    access_token_url='https://oauth2.googleapis.com/token',  # URL to obtain access tokens
    redirect_uri='http://localhost:5000/login/authorized',  # Redirect URI after Google login
    client_kwargs={'scope': 'openid profile email'},  # OAuth scopes for requested user data
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'  # OpenID configuration
)

def login_required(function):
    """
    Custom decorator function to restrict access to routes.
    This decorator checks if a user is authenticated by verifying the session.
    If the user is not logged in, they are redirected to the login page.
    """
    @wraps(function)
    def dec_function(*args, **kwargs):
        if 'user' not in session:  # If the user is not in session, redirect to the login page
            return redirect(url_for('home'))
        else:
            return function(*args, **kwargs)  # If the user is authenticated, proceed to the route
    return dec_function

@auth_bp.route('/login')
def login():
    """
    Route to initiate the login process using Google OAuth.
    A secure random nonce is generated and stored in the session for security.
    The user is then redirected to the Google login page.
    """
    nonce = secrets.token_urlsafe(16)  # Generate a secure random nonce
    session['nonce'] = nonce  # Store the nonce in the session for later verification
    redirect_uri = url_for('auth.authorize', _external=True)  # Generate the redirect URI to Google's OAuth flow
    return google.authorize_redirect(redirect_uri, nonce=nonce)  # Redirect the user to Google's OAuth with nonce

@auth_bp.route('/login/authorized')
def authorize():
    try:
        token = google.authorize_access_token()
        nonce = session.pop('nonce', None)
        if nonce is None:
            return 'Missing nonce'
        user_info = google.parse_id_token(token, nonce=nonce)
        session['user'] = user_info

        # Check if the user already exists in the database
        user = User.query.filter_by(email=user_info['email']).first()
        if not user:
            # If the user does not exist, create a new User record
            user = User(email=user_info['email'], name=user_info.get('name'), daily_reminder=False)
            db.session.add(user)
            db.session.commit()

        # Store the user's ID in the session
        session['user_id'] = user.id

    except Exception as e:
        flash(f"An error occurred during authorization: {str(e)}")
        return redirect(url_for('auth.login'))
    
    return redirect(url_for('home'))

@auth_bp.route('/logout')
def logout():
    """
    Route to log the user out by clearing the session.
    After logging out, the user is redirected to the home page.
    """
    session.clear()  # Clear the session to log the user out
    return redirect(url_for('home'))  # Redirect the user to the home page after logout

@auth_bp.route('/trigger-email', methods=['GET'])
@login_required
def trigger_email():
    user_email = session.get('user')['email']  # Retrieve email from session
    if user_email:
        send_email(
            recipient=user_email,
            subject="Daily Expense Reminder",
            body="This is a reminder to log your expenses for today!"
        )
    return redirect(url_for('finance.view_expenses'))  # Redirect to the main expenses page

@auth_bp.route('/profile-settings', methods=['GET', 'POST'])
@login_required
def profile_settings():
    user = User.query.filter_by(email=session.get('user')['email']).first()

    if request.method == 'POST':
        user.daily_reminder = request.form.get('daily_reminder') == 'on'
        db.session.commit()
        flash('Settings updated successfully.')
        return redirect(url_for('auth.profile_settings'))

    return render_template('profile_settings.html', user=user)
