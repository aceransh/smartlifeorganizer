from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from finance_tracker.models import db, Expense
from auth.routes import login_required
from datetime import datetime

finance_bp = Blueprint('finance', __name__)

@finance_bp.route('/expenses')
@login_required
def view_expenses():
    expenses = Expense.query.all()
    return render_template('expenses.html', expenses=expenses)

@finance_bp.route('/add-expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        name = request.form.get('name')
        amount = request.form.get('amount')
        category = request.form.get('category')
        
        # Validate that all fields are provided
        if not name or not amount or not category:
            flash('All fields are required.')
            return redirect(url_for('finance.add_expense'))
        
        # Add the new expense
        new_expense = Expense(name=name, amount=amount, category=category)
        db.session.add(new_expense)
        db.session.commit()
        return redirect('/expenses')
    return render_template('add_expense.html')

@finance_bp.route('/edit-expense/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if request.method == 'POST':
        expense.name = request.form.get('name')
        expense.amount = request.form.get('amount')
        expense.category = request.form.get('category')

        db.session.commit()
        flash('Expense updated')
        return redirect('/expenses')
    return render_template('edit_expense.html', expense=expense)

