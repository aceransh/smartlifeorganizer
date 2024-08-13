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

    def __repr__(self):
        return f'<Expense {self.name}>'
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    daily_reminder = db.Column(db.Boolean, default=True)  # Field to track whether the user has subscribed to daily reminders

    def __repr__(self):
        return f'<User {self.email}>'