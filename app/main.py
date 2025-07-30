from flask import Flask, render_template, jsonify

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

if __name__ == '__main__':
    app.run(debug=True)
