window.addEventListener('load', () => {
    console.log('Fetching tasks...');
    fetch('/tasks')
        .then(response => {
            console.log('Received response:', response);
            return response.json();
        })
        .then(data => {
            console.log('Received data:', data);
            const taskList = document.createElement('ul');
            data.tasks.forEach(task => {
                const taskItem = document.createElement('li');
                taskItem.textContent = task.title;
                taskList.appendChild(taskItem);
            });
            document.body.appendChild(taskList);
        })
        .catch(error => {
            console.error('Error fetching tasks:', error);
        });
});
