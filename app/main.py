from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

tasks = [
    {'id': 1, 'title': 'Task 1', 'description': 'This is the first task.', 'done': False},
    {'id': 2, 'title': 'Task 2', 'description': 'This is the second task.', 'done': False}
]

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
        'done': False
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
    task['done'] = request.json.get('done', task['done'])
    return jsonify({'task': task})

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        return jsonify({'error': 'Not Found'}), 404
    tasks.remove(task)
    return jsonify({'result': True})

if __name__ == '__main__':
    app.run(debug=True)
