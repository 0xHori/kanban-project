const API_URL = "http://127.0.0.1:8000";

async function apiCheckHealth() {
    const response = await fetch(`${API_URL}/health`);
    if (!response.ok) throw new Error("Health check failed");
    return await response.json();
}

async function apiGetTasks() {
    const response = await fetch(`${API_URL}/tasks`);
    if (!response.ok) throw new Error("Не удалось загрузить задачи");
    return await response.json();
}

async function apiCreateTask(task_name, task_description) {
    const response = await fetch(`${API_URL}/tasks`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            task_name,
            task_description: task_description || null,
        }),
    });

    if (!response.ok) throw new Error("Не удалось создать задачу");
    return await response.json();
}

async function apiSaveTask(taskId, task_name, task_description) {
    const response = await fetch(`${API_URL}/tasks/${taskId}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            task_name,
            task_description: task_description || null,
        }),
    });

    if (!response.ok) throw new Error("Не удалось сохранить задачу");
    return await response.json();
}

async function apiUpdateTaskStatus(taskId, newStatus) {
    const response = await fetch(`${API_URL}/tasks/${taskId}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            status: newStatus,
        }),
    });

    if (!response.ok) throw new Error("Не удалось обновить задачу");
    return await response.json();
}

async function apiMoveTask(taskId, newStatus, newPosition) {
    const response = await fetch(`${API_URL}/tasks/${taskId}/move`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            status: newStatus,
            position: newPosition,
        }),
    });

    if (!response.ok) throw new Error("Не удалось переместить задачу");
    return await response.json();
}

async function apiDeleteTask(taskId) {
    const response = await fetch(`${API_URL}/tasks/${taskId}`, {
        method: "DELETE",
    });

    if (!response.ok) throw new Error("Не удалось удалить задачу");
}