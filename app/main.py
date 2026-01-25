import os
import smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# In-Memory Storage
TASKS = {}
NEXT_ID = 1

# Email Configuration
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'

# Task Model (Simple Python Object)
class Task:
    def __init__(self, id, title, description="", assignee="Unassigned", assignee_email="", due_date="", status="Todo"):
        self.id = id
        self.title = title
        self.description = description
        self.assignee = assignee
        self.assignee_email = assignee_email
        self.due_date = due_date
        self.status = status

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasks', methods=['GET'])
def get_tasks():
    # Return list of all tasks
    return jsonify({'tasks': [t.to_dict() for t in TASKS.values()]})

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    # O(1) Access
    task = TASKS.get(task_id)
    if not task:
        return jsonify({'error': 'Not Found'}), 404
    return jsonify({'task': task.to_dict()})

@app.route('/tasks', methods=['POST'])
def add_task():
    global NEXT_ID
    if not request.json or not 'title' in request.json:
        return jsonify({'error': 'Bad Request'}), 400

    new_task = Task(
        id=NEXT_ID,
        title=request.json['title'],
        description=request.json.get('description', ""),
        assignee=request.json.get('assignee', "Unassigned"),
        assignee_email=request.json.get('assignee_email', ""),
        due_date=request.json.get('due_date', ""),
        status='Todo'
    )
    TASKS[NEXT_ID] = new_task
    NEXT_ID += 1

    return jsonify({'task': new_task.to_dict()}), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = TASKS.get(task_id)
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

    return jsonify({'task': task.to_dict()})

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    if task_id not in TASKS:
        return jsonify({'error': 'Not Found'}), 404
    del TASKS[task_id]
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
    tasks = [t for t in TASKS.values() if t.status != 'Done' and t.assignee_email != ""]

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
