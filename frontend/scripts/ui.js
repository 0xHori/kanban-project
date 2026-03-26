const STATUSES = ["open", "todo", "in_progress", "done"];
let draggedTask = null;
let currentDropIndicator = null;

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

function escapeHtml(text) {
    return text
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function clearColumns() {
    STATUSES.forEach((status) => {
        document.getElementById(status).innerHTML = "";
        document.getElementById(`count-${status}`).textContent = "0";
    });
}

function renderEmptyStates() {
    STATUSES.forEach((status) => {
        const container = document.getElementById(status);
        if (container.children.length === 0) {
            container.innerHTML = `<div class="empty-state">Пока нет задач</div>`;
        }
    });
}

function updateCounters(tasks) {
    const counts = {
        open: 0,
        todo: 0,
        in_progress: 0,
        done: 0,
    };

    tasks.forEach((task) => {
        counts[task.status]++;
    });

    STATUSES.forEach((status) => {
        document.getElementById(`count-${status}`).textContent = counts[status];
    });
}

function getTaskCardsInColumn(column) {
    return [...column.querySelectorAll(".task")].filter(
        (card) => !card.classList.contains("dragging")
    );
}

function calculateNewPosition(column, mouseY) {
    const cards = getTaskCardsInColumn(column);

    if (cards.length === 0) {
        return 100;
    }

    let targetCard = null;

    for (const card of cards) {
        const rect = card.getBoundingClientRect();
        const middleY = rect.top + rect.height / 2;

        if (mouseY < middleY) {
            targetCard = card;
            break;
        }
    }

    if (!targetCard) {
        const lastCard = cards[cards.length - 1];
        return Number(lastCard.dataset.position) + 100;
    }

    const targetIndex = cards.indexOf(targetCard);

    if (targetIndex === 0) {
        return Number(targetCard.dataset.position) - 100;
    }

    const prevCard = cards[targetIndex - 1];
    const prevPosition = Number(prevCard.dataset.position);
    const nextPosition = Number(targetCard.dataset.position);

    return Math.floor((prevPosition + nextPosition) / 2);
}

function getDropTargetCard(column, mouseY) {
    const cards = getTaskCardsInColumn(column);

    for (const card of cards) {
        const rect = card.getBoundingClientRect();
        const middleY = rect.top + rect.height / 2;

        if (mouseY < middleY) {
            return card;
        }
    }

    return null;
}

function removeDropIndicator() {
    if (currentDropIndicator) {
        currentDropIndicator.remove();
        currentDropIndicator = null;
    }
}

function showDropIndicator(tasksContainer, targetCard) {
    removeDropIndicator();

    const indicator = document.createElement("div");
    indicator.className = "drop-indicator active";

    if (targetCard) {
        tasksContainer.insertBefore(indicator, targetCard);
    } else {
        tasksContainer.appendChild(indicator);
    }

    currentDropIndicator = indicator;
}

function createTaskCard(task) {
    const card = document.createElement("div");
    card.className = "task";
    card.dataset.taskId = task.id;
    card.dataset.position = task.position;

    card.innerHTML = `
        <div class="drag-handle" draggable="true">⠿</div>

        <h3>${escapeHtml(task.task_name)}</h3>
        <p>${task.task_description ? escapeHtml(task.task_description) : "Без описания"}</p>
        <small>
            Создано: ${formatDate(task.created_at)}<br>
            Обновлено: ${formatDate(task.updated_at)}
        </small>

        <div class="task-actions">
            <select data-task-id="${task.id}">
                <option value="open" ${task.status === "open" ? "selected" : ""}>open</option>
                <option value="todo" ${task.status === "todo" ? "selected" : ""}>todo</option>
                <option value="in_progress" ${task.status === "in_progress" ? "selected" : ""}>in_progress</option>
                <option value="done" ${task.status === "done" ? "selected" : ""}>done</option>
            </select>

            <button class="edit-btn">Редактировать</button>
            <button class="delete-btn">Удалить</button>
        </div>
    `;

    const select = card.querySelector("select");
    select.addEventListener("change", async (event) => {
        await updateTaskStatus(task.id, event.target.value);
    });

    const editBtn = card.querySelector(".edit-btn");
    editBtn.addEventListener("click", () => {
        enableEditMode(card, task);
    });

    const deleteBtn = card.querySelector(".delete-btn");
    deleteBtn.addEventListener("click", async () => {
        await deleteTask(task.id);
    });

    const handle = card.querySelector(".drag-handle");

    handle.addEventListener("dragstart", () => {
        draggedTask = task;
        card.classList.add("dragging");
    });

    handle.addEventListener("dragend", () => {
        draggedTask = null;
        card.classList.remove("dragging");
        removeDropIndicator();
        document.querySelectorAll(".column").forEach((column) => {
            column.classList.remove("drag-over");
        });
    });

    return card;
}

function enableEditMode(card, task) {
    card.innerHTML = `
        <div class="edit-form">
            <input
                id="edit-name-${task.id}"
                type="text"
                value="${escapeHtml(task.task_name)}"
            />
            <textarea id="edit-desc-${task.id}">${task.task_description ? escapeHtml(task.task_description) : ""}</textarea>

            <div class="edit-form-actions">
                <button class="save-btn" type="button">Сохранить</button>
                <button class="cancel-btn" type="button">Отмена</button>
            </div>
        </div>
    `;

    const saveBtn = card.querySelector(".save-btn");
    saveBtn.addEventListener("click", async () => {
        await saveTask(task.id);
    });

    const cancelBtn = card.querySelector(".cancel-btn");
    cancelBtn.addEventListener("click", async () => {
        await loadTasks();
    });
}

function setupColumnDnD() {
    const columns = document.querySelectorAll(".column");

    columns.forEach((column) => {
        column.addEventListener("dragover", (event) => {
            event.preventDefault();
            column.classList.add("drag-over");

            if (!draggedTask) return;

            const tasksContainer = column.querySelector(".tasks");
            const targetCard = getDropTargetCard(tasksContainer, event.clientY);

            showDropIndicator(tasksContainer, targetCard);
        });

        column.addEventListener("dragleave", (event) => {
            if (!column.contains(event.relatedTarget)) {
                column.classList.remove("drag-over");
                removeDropIndicator();
            }
        });

        column.addEventListener("drop", async (event) => {
            event.preventDefault();
            column.classList.remove("drag-over");

            if (!draggedTask) {
                removeDropIndicator();
                return;
            }

            const tasksContainer = column.querySelector(".tasks");
            const newStatus = column.dataset.status;
            const newPosition = calculateNewPosition(tasksContainer, event.clientY);

            removeDropIndicator();
            await moveTask(draggedTask.id, newStatus, newPosition);
        });
    });
}