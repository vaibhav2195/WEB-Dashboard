from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import init_db, get_db
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super secret key'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('welcome'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        roll_no = request.form['roll_no']
        department = request.form['department']
        year = request.form['year']
        birth_date = request.form['birth_date']
        course = request.form['course']

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')

        db = get_db()
        try:
            db.execute('INSERT INTO users (username, password, roll_no, department, year, birth_date, course) VALUES (?, ?, ?, ?, ?, ?, ?)',
                       (username, password, roll_no, department, year, birth_date, course))
            db.commit()
            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/welcome')
@login_required
def welcome():
    if session['role'] == 'admin':
        db = get_db()
        total_students = db.execute('SELECT COUNT(*) FROM users WHERE role = ?', ('student',)).fetchone()[0]
        department_counts = db.execute('SELECT department, COUNT(*) FROM users WHERE role = ? GROUP BY department', ('student',)).fetchall()
        department_labels = [row['department'] for row in department_counts]
        department_data = [row['COUNT(*)'] for row in department_counts]
        return render_template('admin_welcome.html', total_students=total_students, department_labels=department_labels, department_data=department_data)
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    return render_template('welcome.html', user=user)

@app.route('/dashboard')
@login_required
@admin_required
def dashboard():
    db = get_db()
    users = db.execute("SELECT * FROM users WHERE role = 'student'").fetchall()
    return render_template('dashboard.html', users=users)

@app.route('/create_user', methods=['POST'])
@login_required
@admin_required
def create_user():
    username = request.form['username']
    password = request.form['password']
    role = 'student'
    if len(password) < 6:
        flash('Password must be at least 6 characters long.', 'danger')
        db = get_db()
        users = db.execute('SELECT * FROM users').fetchall()
        return render_template('dashboard.html', users=users)
    db = get_db()
    try:
        db.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, role))
        db.commit()
        flash('User created successfully.', 'success')
    except sqlite3.IntegrityError:
        flash('Username already exists.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/delete_user/<int:id>')
@login_required
@admin_required
def delete_user(id):
    db = get_db()
    db.execute('DELETE FROM users WHERE id = ?', (id,))
    db.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        if len(new_password) < 6:
            flash('New password must be at least 6 characters long.', 'danger')
            return render_template('change_password.html')
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        if user and user['password'] == old_password:
            db.execute('UPDATE users SET password = ? WHERE id = ?', (new_password, session['user_id']))
            db.commit()
            flash('Password changed successfully.', 'success')
            return redirect(url_for('welcome'))
        else:
            flash('Invalid old password.', 'danger')
    return render_template('change_password.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)