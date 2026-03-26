async function checkHealth() {
    const badge = document.getElementById("api-status");

    try {
        const data = await apiCheckHealth();
        badge.textContent = `API: ${data.status}`;
    } catch (error) {
        badge.textContent = "API: offline";
    }
}

async function loadTasks() {
    try {
        const tasks = await apiGetTasks();

        tasks.sort((a, b) => {
            if (a.status === b.status) {
                return a.position - b.position;
            }
            return 0;
        });

        clearColumns();
        updateCounters(tasks);

        tasks.forEach((task) => {
            const column = document.getElementById(task.status);
            column.appendChild(createTaskCard(task));
        });

        renderEmptyStates();
    } catch (error) {
        clearColumns();
        STATUSES.forEach((status) => {
            document.getElementById(status).innerHTML =
                `<div class="empty-state">Ошибка загрузки</div>`;
        });
    }
}

async function createTask(event) {
    event.preventDefault();

    const taskNameInput = document.getElementById("task-name");
    const taskDescriptionInput = document.getElementById("task-description");

    const task_name = taskNameInput.value.trim();
    const task_description = taskDescriptionInput.value.trim();

    if (!task_name) return;

    try {
        await apiCreateTask(task_name, task_description);
        document.getElementById("task-form").reset();
        await loadTasks();
    } catch (error) {
        alert("Ошибка при создании задачи");
    }
}

async function saveTask(taskId) {
    const nameInput = document.getElementById(`edit-name-${taskId}`);
    const descInput = document.getElementById(`edit-desc-${taskId}`);

    const task_name = nameInput.value.trim();
    const task_description = descInput.value.trim();

    if (!task_name) {
        alert("Название задачи не может быть пустым");
        return;
    }

    try {
        await apiSaveTask(taskId, task_name, task_description);
        await loadTasks();
    } catch (error) {
        alert("Ошибка при сохранении задачи");
    }
}

async function updateTaskStatus(taskId, newStatus) {
    try {
        await apiUpdateTaskStatus(taskId, newStatus);
        await loadTasks();
    } catch (error) {
        alert("Ошибка при обновлении задачи");
    }
}

async function moveTask(taskId, newStatus, newPosition) {
    try {
        await apiMoveTask(taskId, newStatus, newPosition);
        await loadTasks();
    } catch (error) {
        alert("Ошибка при перемещении задачи");
    }
}

async function deleteTask(taskId) {
    const confirmed = confirm("Удалить задачу?");
    if (!confirmed) return;

    try {
        await apiDeleteTask(taskId);
        await loadTasks();
    } catch (error) {
        alert("Ошибка при удалении задачи");
    }
}

document
    .getElementById("task-form")
    .addEventListener("submit", createTask);

setupColumnDnD();
checkHealth();
loadTasks();