import smtplib
from models import ToDoItem, db
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
from models import User, ToDoItem
import os
from datetime import datetime

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

def check_reminders(app):
    with app.app_context():
        now = datetime.now()
        print(f"Checking reminders at {now}")  # Debugging: Print the current time

        # Find all to-do items with a reminder_time that matches or is before the current time and where the reminder hasn't been sent
        todos = ToDoItem.query.filter(
            ToDoItem.reminder_time <= now,
            ToDoItem.status == 'Incomplete',
            ToDoItem.reminder_sent == False  # Check if the reminder has not been sent
        ).all()

        print(f"Found {len(todos)} todo items needing reminders")  # Debugging: Print the number of matching todos

        for todo in todos:
            user = User.query.get(todo.user_id)
            if user:
                # Add a final check before sending to ensure it hasn't just been sent
                if not todo.reminder_sent:
                    print(f"Sending reminder for To-Do item: {todo.description} to {user.email}")  # Debugging: Print which reminder is being sent
                    send_email(
                        recipient=user.email,
                        subject=f"Reminder: {todo.description}",
                        body=f"This is a reminder to complete the following task: {todo.description} by {todo.due_date.strftime('%Y-%m-%d %H:%M')}.\n"
                             f"You can view your To-Do list here: http://127.0.0.1:5000/todos"
                    )
                    todo.reminder_sent = True  # Mark the reminder as sent
                    db.session.commit()  # Commit the changes to the database
