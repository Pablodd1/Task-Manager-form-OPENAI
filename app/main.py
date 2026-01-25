import os
import smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Configuration
# Use SQLite for local development, or DATABASE_URL if provided (e.g. Postgres on Vercel)
# On Vercel, if DATABASE_URL is not set, fallback to in-memory SQLite to prevent read-only filesystem errors.
if os.environ.get('VERCEL'):
    default_db = 'sqlite:///:memory:'
else:
    default_db = 'sqlite:///tasks.db'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', default_db)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key') # Required for session
db = SQLAlchemy(app)

# Email Configuration
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default='Staff') # 'Admin' or 'Staff'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role
        }

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), default="")
    assignee = db.Column(db.String(100), default="Unassigned")
    assignee_email = db.Column(db.String(100), default="")
    due_date = db.Column(db.String(20), default="")
    status = db.Column(db.String(20), default="Todo")

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'assignee': self.assignee,
            'assignee_email': self.assignee_email,
            'due_date': self.due_date,
            'status': self.status
        }

# Initialize DB
with app.app_context():
    try:
        db.create_all()
        # Create default Admin if not exists
        if not User.query.filter_by(role='Admin').first():
            admin = User(username='admin', email='admin@example.com', role='Admin')
            db.session.add(admin)
            db.session.commit()
            print("Default Admin created: admin / admin@example.com")
    except Exception as e:
        print(f"Error initializing database: {e}")

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = db.session.get(User, session['user_id'])
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="User not found")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify({'users': [u.to_dict() for u in users]})

@app.route('/api/users', methods=['POST'])
def add_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    current_user = db.session.get(User, session['user_id'])
    if current_user.role != 'Admin':
         return jsonify({'error': 'Forbidden'}), 403

    if not request.json or 'username' not in request.json:
        return jsonify({'error': 'Bad Request'}), 400

    username = request.json['username']
    email = request.json.get('email', f"{username}@example.com")
    role = request.json.get('role', 'Staff')

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 400

    new_user = User(username=username, email=email, role=role)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'user': new_user.to_dict()}), 201

@app.route('/api/current_user', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    user = db.session.get(User, session['user_id'])
    return jsonify({'user': user.to_dict()})

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify({'tasks': [t.to_dict() for t in tasks]})

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Not Found'}), 404
    return jsonify({'task': task.to_dict()})

@app.route('/tasks', methods=['POST'])
def add_task():
    if not request.json or not 'title' in request.json:
        return jsonify({'error': 'Bad Request'}), 400

    new_task = Task(
        title=request.json['title'],
        description=request.json.get('description', ""),
        assignee=request.json.get('assignee', "Unassigned"),
        assignee_email=request.json.get('assignee_email', ""),
        due_date=request.json.get('due_date', ""),
        status='Todo'
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'task': new_task.to_dict()}), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Not Found'}), 404
    if not request.json:
         return jsonify({'error': 'Bad Request'}), 400

    task.title = request.json.get('title', task.title)
    task.description = request.json.get('description', task.description)
    task.assignee = request.json.get('assignee', task.assignee)
    task.assignee_email = request.json.get('assignee_email', task.assignee_email)
    task.due_date = request.json.get('due_date', task.due_date)

    if 'status' in request.json:
        task.status = request.json['status']

    db.session.commit()
    return jsonify({'task': task.to_dict()})

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Not Found'}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({'result': True})

def send_email(to_email, subject, body):
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        print(f"Skipping email to {to_email} (Credentials not set)")
        return False

    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = MAIL_USERNAME
        msg['To'] = to_email

        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            if MAIL_USE_TLS:
                server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

@app.route('/api/cron/reminders', methods=['POST', 'GET'])
def send_reminders():
    # Fetch pending tasks with emails
    tasks = Task.query.filter(Task.status != 'Done', Task.assignee_email != "").all()

    count = 0
    logs = []

    for task in tasks:
        subject = f"Reminder: Task '{task.title}' is {task.status}"
        body = f"Hi {task.assignee},\n\nThis is a friendly reminder that the task '{task.title}' is currently marked as '{task.status}'.\n\nDescription: {task.description}\nDue Date: {task.due_date}\n\nPlease update the status when you can!"

        # Try to send real email
        success = send_email(task.assignee_email, subject, body)

        log_msg = f"Email to {task.assignee_email} for task '{task.title}': {'Sent' if success else 'Skipped (No Config)'}"
        print(log_msg)
        logs.append(log_msg)
        count += 1

    return jsonify({'processed': count, 'logs': logs}), 200

if __name__ == '__main__':
    app.run(debug=True)
