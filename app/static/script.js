document.addEventListener('DOMContentLoaded', () => {
    const tasksContainer = document.getElementById('tasks-container');
    const titleInput = document.getElementById('new-task-title');
    const descInput = document.getElementById('new-task-desc');
    const addBtn = document.getElementById('add-task-btn');

    function fetchTasks() {
        fetch('/tasks')
            .then(response => response.json())
            .then(data => {
                tasksContainer.innerHTML = '';
                const taskList = document.createElement('ul');
                data.tasks.forEach(task => {
                    const taskItem = document.createElement('li');

                    const span = document.createElement('span');
                    span.textContent = `${task.title} - ${task.description}`;
                    if (task.done) {
                        span.classList.add('done');
                    }

                    const doneBtn = document.createElement('button');
                    doneBtn.textContent = task.done ? 'Undo' : 'Done';
                    doneBtn.onclick = () => toggleTask(task.id, !task.done);

                    const deleteBtn = document.createElement('button');
                    deleteBtn.textContent = 'Delete';
                    deleteBtn.onclick = () => deleteTask(task.id);

                    taskItem.appendChild(span);
                    taskItem.appendChild(doneBtn);
                    taskItem.appendChild(deleteBtn);
                    taskList.appendChild(taskItem);
                });
                tasksContainer.appendChild(taskList);
            })
            .catch(error => console.error('Error fetching tasks:', error));
    }

    addBtn.addEventListener('click', () => {
        const title = titleInput.value;
        const description = descInput.value;
        if (!title) return alert('Title is required');

        fetch('/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title, description })
        })
        .then(response => response.json())
        .then(() => {
            titleInput.value = '';
            descInput.value = '';
            fetchTasks();
        });
    });

    function toggleTask(id, done) {
        fetch(`/tasks/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ done })
        })
        .then(() => fetchTasks());
    };

    function deleteTask(id) {
        if (!confirm('Are you sure?')) return;
        fetch(`/tasks/${id}`, {
            method: 'DELETE'
        })
        .then(() => fetchTasks());
    };

    fetchTasks();
});
