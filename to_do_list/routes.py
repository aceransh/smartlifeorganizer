from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, ToDoItem
from auth.routes import login_required
from datetime import datetime

to_do_bp = Blueprint('to_do', __name__)

@to_do_bp.route('/todos')
@login_required
def view_todos():
    user_id = session.get('user_id')

    # Sorting and filtering
    sort_by_due_date = request.args.get('sort_by_due_date')
    subject = request.args.get('subject')
    status = request.args.get('status')
    
    query = ToDoItem.query.filter_by(user_id=user_id)

    if subject:
        query = query.filter_by(subject=subject)

    if status:
        query = query.filter_by(status=status)

    if sort_by_due_date == 'asc':
        query = query.order_by(ToDoItem.due_date.asc())
    elif sort_by_due_date == 'desc':
        query = query.order_by(ToDoItem.due_date.desc())

    todos = query.all()

    return render_template('todos.html', todos=todos)

@to_do_bp.route('/add-todo', methods=['GET', 'POST'])
@login_required
def add_todo():
    if request.method == 'POST':
        subject = request.form.get('subject')
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        reminder_time = request.form.get('reminder_time')

        user_id = session.get('user_id')

        new_todo = ToDoItem(
            subject=subject,
            description=description,
            due_date=datetime.fromisoformat(due_date) if due_date else None,
            reminder_time=datetime.fromisoformat(reminder_time) if reminder_time else None,
            status='Incomplete',
            user_id=user_id
        )
        db.session.add(new_todo)
        db.session.commit()

        return redirect(url_for('to_do.view_todos'))

    return render_template('add_todo.html')

@to_do_bp.route('/edit-todo/<int:todo_id>', methods=['GET', 'POST'])
@login_required
def edit_todo(todo_id):
    todo = ToDoItem.query.get_or_404(todo_id)

    if request.method == 'POST':
        todo.subject = request.form.get('subject')
        todo.description = request.form.get('description')
        due_date = request.form.get('due_date')
        reminder_time = request.form.get('reminder_time')

        todo.due_date = datetime.fromisoformat(due_date) if due_date else None
        todo.reminder_time = datetime.fromisoformat(reminder_time) if reminder_time else None
        todo.status = request.form.get('status')

        db.session.commit()
        flash('To-Do updated successfully.')
        return redirect(url_for('to_do.view_todos'))

    return render_template('edit_todo.html', todo=todo)

@to_do_bp.route('/complete-todo/<int:todo_id>', methods=['POST'])
@login_required
def complete_todo(todo_id):
    todo = ToDoItem.query.get_or_404(todo_id)
    todo.status = 'Completed'
    db.session.commit()
    return redirect(url_for('to_do.view_todos'))

@to_do_bp.route('/delete-todo/<int:todo_id>', methods=['POST'])
@login_required
def delete_todo(todo_id):
    todo = ToDoItem.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    flash('To-Do deleted successfully.')
    return redirect(url_for('to_do.view_todos'))