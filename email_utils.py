import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from models import User
from email import encoders
import os


def send_email(recipient, subject, body):
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")

    unsubscribe_link = f"http://127.0.0.1:5000//profile-settings"  # Adjust as needed

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject

    body_with_unsubscribe = f"{body}\n\nIf you wish to unsubscribe, click here: {unsubscribe_link}"
    msg.attach(MIMEText(body_with_unsubscribe, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")

def send_daily_reminder(app):
    with app.app_context():
        # Retrieve all users who have subscribed to daily reminders
        users = User.query.filter_by(daily_reminder=True).all()
        for user in users:
            send_email(
                recipient=user.email,
                subject="Daily Expense Reminder",
                body="This is your daily reminder to log your expenses!"
            )