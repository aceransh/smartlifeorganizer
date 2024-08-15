from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Expense
from auth.routes import login_required
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import os
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for rendering without a GUI

finance_bp = Blueprint('finance', __name__)

@finance_bp.route('/expenses')
@login_required
def view_expenses():
    # Get the user_id from the session
    user_id = session.get('user_id')
    
    # Get query parameters for filtering
    filter_date = request.args.get('date')
    filter_category = request.args.get('category')
    search_term = request.args.get('search')

    # Base query, filtering by the logged-in user's expenses
    query = Expense.query.filter_by(user_id=user_id)

    # Apply filters based on the query parameters
    if filter_date:
        query = query.filter(db.func.date(Expense.date) == filter_date)
    if filter_category:
        query = query.filter(Expense.category == filter_category)
    if search_term:
        query = query.filter(Expense.name.ilike(f'%{search_term}%'))

    # Execute the query and get the filtered expenses
    expenses = query.all()

    return render_template('expenses.html', expenses=expenses)


@finance_bp.route('/add-expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        name = request.form.get('name')
        amount = request.form.get('amount')
        category = request.form.get('category')
        
        if not name or not amount or not category:
            flash('All fields are required.')
            return redirect(url_for('finance.add_expense'))
        
        # Get the user_id from the session
        user_id = session.get('user_id')
        
        # Add the new expense with the user_id
        new_expense = Expense(name=name, amount=amount, category=category, user_id=user_id)
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

@finance_bp.route('/delete-expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    flash('Expense was deleted')
    print('Expense was deleted')

    return redirect(url_for('finance.view_expenses'))

@finance_bp.route('/expenses-summary', methods=['GET'])
@login_required
def expenses_summary():
    # Get the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Get the month, year, and type of summary from the query parameters
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int, default=current_year)
    summary_type = request.args.get('summary_type')

    if summary_type == 'last_30_days':
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        title = "Expenses Summary for Last 30 Days"
        month = None  # Ensure month is None for this summary
    elif summary_type == 'last_365_days':
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now()
        title = "Expenses Summary for Last 365 Days"
        month = None  # Ensure month is None for this summary
    elif year and not month:  # Yearly summary
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)
        title = f"Expenses Summary for {year}"
        month = None  # Ensure month is None so that it won't default to a specific month
    elif month and year:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        title = f"Expenses Summary for {datetime(year, month, 1).strftime('%B')} {year}"
    else:
        return redirect(url_for('finance.view_expenses'))

    # Fetch expenses within the specified date range
    expenses = Expense.query.filter(Expense.date >= start_date, Expense.date < end_date).all()

    # Aggregate expenses by category
    categories = {}
    total_amount = 0
    for expense in expenses:
        if expense.category in categories:
            categories[expense.category] += expense.amount
        else:
            categories[expense.category] = expense.amount
        total_amount += expense.amount

    # Plotting
    fig, ax = plt.subplots()
    ax.bar(categories.keys(), categories.values(), color='skyblue')
    ax.set_xlabel('Category')
    ax.set_ylabel('Total Amount')
    ax.set_title(title)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    # Save the plot to a file
    plot_path = os.path.join('static', 'summary_plot.png')
    plt.savefig(plot_path)
    plt.close()  # Clear the plot to free up memory

    return render_template(
        'expenses_summary.html',
        expenses=expenses,
        title=title,
        chart=plot_path,
        datetime=datetime,
        selected_month=month,
        selected_year=year,
        categories=categories,
        total_amount=total_amount
    )