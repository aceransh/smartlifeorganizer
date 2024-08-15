from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('US/Eastern')))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Link to User model

    def __repr__(self):
        return f'<Expense {self.name}>'
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)  # Now it's non-nullable
    email = db.Column(db.String(120), unique=True, nullable=False)
    daily_reminder = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<User {self.email}>'
    
class ToDoItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50), nullable=True)  # Optional field
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)  # Optional field
    reminder_time = db.Column(db.DateTime, nullable=True)  # Optional field
    status = db.Column(db.String(20), default='Incomplete')  # New status field
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Link to User model

    def __repr__(self):
        return f'<ToDoItem {self.description}>'