document.addEventListener('DOMContentLoaded', () => {
    const tasksContainer = document.getElementById('tasks-container');
    const titleInput = document.getElementById('new-task-title');
    const descInput = document.getElementById('new-task-desc');
    const assigneeSelect = document.getElementById('new-task-assignee-select');
    const dueInput = document.getElementById('new-task-due');
    const addBtn = document.getElementById('add-task-btn');

    // Admin Panel Inputs
    const newUserNameInput = document.getElementById('new-user-name');
    const newUserEmailInput = document.getElementById('new-user-email');
    const newUserRoleInput = document.getElementById('new-user-role');
    const addUserBtn = document.getElementById('add-user-btn');

    // Available Users for dropdown
    let availableUsers = [];

    function fetchUsers() {
        if (!assigneeSelect) return; // Only if admin view
        fetch('/api/users')
            .then(res => res.json())
            .then(data => {
                availableUsers = data.users;
                // Populate Dropdown
                assigneeSelect.innerHTML = '<option value="">Unassigned</option>';
                data.users.forEach(user => {
                    if (user.role === 'Staff') {
                        const opt = document.createElement('option');
                        opt.value = user.username;
                        opt.dataset.email = user.email;
                        opt.textContent = `${user.username} (${user.email})`;
                        assigneeSelect.appendChild(opt);
                    }
                });
            });
    }

    function fetchTasks() {
        fetch('/tasks')
            .then(response => response.json())
            .then(data => {
                tasksContainer.innerHTML = '';
                const taskList = document.createElement('ul');
                taskList.className = 'task-list';

                if (data.tasks.length === 0) {
                    tasksContainer.innerHTML = '<p style="text-align:center; color:#ccc;">No tasks found.</p>';
                    return;
                }

                data.tasks.forEach(task => {
                    // Filter for Staff: Only show if unassigned (optional) or assigned to them
                    // Requirement says: "Staff View: Can only see their tasks (or all tasks?)"
                    // Let's assume Staff can see ALL tasks but only edit theirs or move status?
                    // Usually "Team Task Manager" implies visibility.
                    // But "Staff Dashboard (My Tasks)" implies filter.
                    // Let's filter VISUALITY for Staff to "My Tasks" + "Unassigned" for picking up?
                    // Re-reading: "Staff: View assigned tasks". Let's stick to that.

                    if (CURRENT_USER.role === 'Staff' && task.assignee !== CURRENT_USER.username) {
                        return;
                    }

                    const taskCard = document.createElement('li');
                    taskCard.className = 'task-card';

                    const statusClass = `status-${task.status.replace(' ', '-')}`;

                    let actionButtons = '';

                    // Logic for Buttons based on Role and Status
                    // Admin can Delete.
                    // Staff can change Status.

                    const isAssignedToMe = task.assignee === CURRENT_USER.username;
                    const isAdmin = CURRENT_USER.role === 'Admin';

                    // Status Transitions
                    if (isAdmin || isAssignedToMe) {
                         if (task.status === 'Todo') {
                            actionButtons += `<button class="action-btn btn-start" onclick="updateStatus(${task.id}, 'In Progress')">Start</button>`;
                        } else if (task.status === 'In Progress') {
                            actionButtons += `<button class="action-btn btn-review" onclick="updateStatus(${task.id}, 'Under Review')">Request Review</button>`;
                        } else if (task.status === 'Under Review') {
                             // Only Admin should approve? Or Staff? Assuming Admin usually.
                             // But previously it was open. Let's allow Admin or Assignee for now to be flexible,
                             // OR strictly Admin for "Under Review" -> "Done".
                             if (isAdmin) {
                                 actionButtons += `<button class="action-btn btn-approve" onclick="updateStatus(${task.id}, 'Done')">Approve</button>`;
                             }
                        }
                    }

                    if (isAdmin) {
                        actionButtons += `<button class="action-btn btn-delete" onclick="deleteTask(${task.id})">Delete</button>`;
                    }

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

                if (taskList.children.length === 0) {
                     tasksContainer.innerHTML = '<p style="text-align:center; color:#ccc;">No tasks assigned to you.</p>';
                } else {
                    tasksContainer.appendChild(taskList);
                }
            })
            .catch(error => console.error('Error fetching tasks:', error));
    }

    if (addBtn) {
        addBtn.addEventListener('click', () => {
            const title = titleInput.value;
            const description = descInput.value;
            const assignee = assigneeSelect.value;
            const assignee_email = assigneeSelect.selectedOptions[0]?.dataset.email || "";
            const due_date = dueInput.value;

            if (!title) return alert('Title is required');

            fetch('/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title, description, assignee, assignee_email, due_date
                })
            })
            .then(response => response.json())
            .then(() => {
                titleInput.value = '';
                descInput.value = '';
                assigneeSelect.value = '';
                dueInput.value = '';
                fetchTasks();
            });
        });
    }

    if (addUserBtn) {
        addUserBtn.addEventListener('click', () => {
            const username = newUserNameInput.value;
            const email = newUserEmailInput.value;
            const role = newUserRoleInput.value;

            if(!username) return alert('Username required');

            fetch('/api/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, role })
            })
            .then(res => {
                if(!res.ok) throw new Error('Failed');
                return res.json();
            })
            .then(() => {
                alert('User created!');
                newUserNameInput.value = '';
                newUserEmailInput.value = '';
                fetchUsers(); // Refresh dropdown
            })
            .catch(err => alert('Error creating user (might already exist)'));
        });
    }

    window.updateStatus = function(id, status) {
        fetch(`/tasks/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
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
        return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }

    fetchUsers();
    fetchTasks();
});
