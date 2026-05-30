document.getElementById('add-task-btn').addEventListener('click', addTask);
document.getElementById('toggle-theme-btn').addEventListener('click', toggleTheme);

function addTask() {
    const taskInput = document.getElementById('new-task');
    const taskText = taskInput.value.trim();
    if (taskText !== '') {
        const todoList = document.getElementById('todo-list');
        const taskItem = document.createElement('li');
        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Delete';
        deleteButton.addEventListener('click', () => {
            todoList.removeChild(taskItem);
            updateTaskNumbers();
        });
        const taskNumber = todoList.children.length + 1;
        taskItem.textContent = taskNumber + '. ' + taskText;
        taskItem.appendChild(deleteButton);
        todoList.appendChild(taskItem);
        taskInput.value = '';
    }
}

function updateTaskNumbers() {
    const tasks = document.querySelectorAll('#todo-list li');
    tasks.forEach((task, index) => {
        task.firstChild.textContent = (index + 1) + '. ' + task.firstChild.textContent.slice(2);
    });
}

function toggleTheme() {
    document.body.classList.toggle('dark');
}