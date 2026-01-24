from flask import Flask, render_template, jsonify, request
import datetime

app = Flask(__name__)

# In-memory database
tasks = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        return jsonify({'error': 'Not Found'}), 404
    return jsonify({'task': task})

@app.route('/tasks', methods=['POST'])
def add_task():
    if not request.json or not 'title' in request.json:
        return jsonify({'error': 'Bad Request'}), 400

    task = {
        'id': tasks[-1]['id'] + 1 if tasks else 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'assignee': request.json.get('assignee', "Unassigned"),
        'assignee_email': request.json.get('assignee_email', ""),
        'due_date': request.json.get('due_date', ""),
        'status': 'Todo'  # Todo, In Progress, Under Review, Done
    }
    tasks.append(task)
    return jsonify({'task': task}), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        return jsonify({'error': 'Not Found'}), 404
    if not request.json:
         return jsonify({'error': 'Bad Request'}), 400

    task['title'] = request.json.get('title', task['title'])
    task['description'] = request.json.get('description', task['description'])
    task['assignee'] = request.json.get('assignee', task.get('assignee'))
    task['assignee_email'] = request.json.get('assignee_email', task.get('assignee_email'))
    task['due_date'] = request.json.get('due_date', task.get('due_date'))

    if 'status' in request.json:
        task['status'] = request.json['status']

    return jsonify({'task': task})

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        return jsonify({'error': 'Not Found'}), 404
    tasks.remove(task)
    return jsonify({'result': True})

@app.route('/api/cron/reminders', methods=['POST', 'GET'])
def send_reminders():
    # Simulate sending emails
    count = 0
    logs = []
    for task in tasks:
        if task['status'] != 'Done' and task.get('assignee_email'):
            # In a real app, integrate with SendGrid/SMTP here
            msg = f"Sending reminder to {task['assignee_email']} for task '{task['title']}' (Status: {task['status']})"
            print(msg) # Log to stdout
            logs.append(msg)
            count += 1

    return jsonify({'sent': count, 'logs': logs}), 200

if __name__ == '__main__':
    app.run(debug=True)
