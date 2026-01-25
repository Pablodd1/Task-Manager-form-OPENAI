document.addEventListener('DOMContentLoaded', () => {
    const tasksContainer = document.getElementById('tasks-container');
    const titleInput = document.getElementById('new-task-title');
    const descInput = document.getElementById('new-task-desc');
    const assigneeInput = document.getElementById('new-task-assignee');
    const emailInput = document.getElementById('new-task-email');
    const dueInput = document.getElementById('new-task-due');
    const addBtn = document.getElementById('add-task-btn');

    function fetchTasks() {
        fetch('/tasks')
            .then(response => response.json())
            .then(data => {
                tasksContainer.innerHTML = '';
                const taskList = document.createElement('ul');
                taskList.className = 'task-list';

                if (data.tasks.length === 0) {
                    tasksContainer.innerHTML = '<p style="text-align:center; color:#ccc;">No tasks found. Add one above!</p>';
                    return;
                }

                data.tasks.forEach(task => {
                    const taskCard = document.createElement('li');
                    taskCard.className = 'task-card';

                    // Determine badge class
                    const statusClass = `status-${task.status.replace(' ', '-')}`;

                    let actionButtons = '';
                    if (task.status === 'Todo') {
                        actionButtons += `<button class="action-btn btn-start" onclick="updateStatus(${task.id}, 'In Progress')">Start</button>`;
                    } else if (task.status === 'In Progress') {
                        actionButtons += `<button class="action-btn btn-review" onclick="updateStatus(${task.id}, 'Under Review')">Request Review</button>`;
                    } else if (task.status === 'Under Review') {
                        actionButtons += `<button class="action-btn btn-approve" onclick="updateStatus(${task.id}, 'Done')">Approve</button>`;
                    }
                    actionButtons += `<button class="action-btn btn-delete" onclick="deleteTask(${task.id})">Delete</button>`;

                    taskCard.innerHTML = `
                        <div class="task-header">
                            <h3 class="task-title">${escapeHtml(task.title)}</h3>
                            <span class="status-badge ${statusClass}">${task.status}</span>
                        </div>
                        <p>${escapeHtml(task.description)}</p>
                        <div class="task-meta">
                            <span>👤 ${escapeHtml(task.assignee)}</span>
                            <span>📧 ${escapeHtml(task.assignee_email || 'No Email')}</span>
                            <span>📅 ${escapeHtml(task.due_date || 'No Date')}</span>
                        </div>
                        <div class="task-actions">
                            ${actionButtons}
                        </div>
                    `;
                    taskList.appendChild(taskCard);
                });
                tasksContainer.appendChild(taskList);
            })
            .catch(error => console.error('Error fetching tasks:', error));
    }

    addBtn.addEventListener('click', () => {
        const title = titleInput.value;
        const description = descInput.value;
        const assignee = assigneeInput.value;
        const assignee_email = emailInput.value;
        const due_date = dueInput.value;

        if (!title) return alert('Title is required');

        fetch('/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title,
                description,
                assignee,
                assignee_email,
                due_date
            })
        })
        .then(response => response.json())
        .then(() => {
            titleInput.value = '';
            descInput.value = '';
            assigneeInput.value = '';
            emailInput.value = '';
            dueInput.value = '';
            fetchTasks();
        });
    });

    window.updateStatus = function(id, status) {
        fetch(`/tasks/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status })
        })
        .then(() => fetchTasks());
    };

    window.deleteTask = function(id) {
        if (!confirm('Are you sure you want to delete this task?')) return;
        fetch(`/tasks/${id}`, {
            method: 'DELETE'
        })
        .then(() => fetchTasks());
    };

    function escapeHtml(text) {
        if (!text) return '';
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    fetchTasks();
});
