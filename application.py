from flask import Flask, Response, render_template, request, redirect, url_for, flash, session, abort
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

application = app = Flask(__name__)
app.config['SECRET_KEY'] = '1234'
BASE_DIR = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
DATABASE = os.path.join(BASE_DIR,'site.db')
print('database:----', DATABASE)

def connect_db():
    return sqlite3.connect(DATABASE)

def init_db():
    with connect_db() as db:
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS material (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                content BLOB NOT NULL,
                uploader_id INTEGER NOT NULL,
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (uploader_id) REFERENCES user (id)
            )
        ''')
        db.commit()



def login_required(role):
    if 'user_id' not in session or session['role'] != role:
        abort(403)  # Forbidden

@app.route('/')
def index():
    init_db()
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        hashed_password = generate_password_hash(password)

        with connect_db() as db:
            cursor = db.cursor()
            cursor.execute('INSERT INTO user (username, password, role) VALUES (?, ?, ?)',
                           (username, hashed_password, role))
            db.commit()

        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with connect_db() as db:
            cursor = db.cursor()
            cursor.execute('SELECT * FROM user WHERE username = ?', (username,))
            user = cursor.fetchone()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            flash('Login successful!', 'success')
            # Redirect to the respective homepage based on the user's role
            if user[3] == 'teacher':
                return redirect(url_for('teacher_homepage'))
            elif user[3] == 'student':
                return redirect(url_for('student_homepage'))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/student-homepage')
def student_homepage():
    login_required('student')
    return render_template('student-homepage.html')

@app.route('/upload-assignments', methods=['GET', 'POST'])
def upload_assignments():
    return render_template('upload-assignments.html')

@app.route('/download-materials')
def download_materials():
    return render_template('download-materials.html')

@app.route('/teacher-homepage')
def teacher_homepage():
    login_required('teacher')
    return render_template('teacher-homepage.html')

# Route for uploading material
@app.route('/upload-material', methods=['GET', 'POST'])
def upload_material():
    return render_template('upload-material.html')

# Route for viewing student uploads
@app.route('/view-student-uploads')
def view_student_uploads():
    return render_template('view-student-uploads.html')



if __name__ == '__main__':
    app.run(debug=True)
