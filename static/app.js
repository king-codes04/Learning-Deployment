
const taskList = document.getElementById("task-list");
const taskForm = document.getElementById("task-form");
const taskTitleInput = document.getElementById("task-title");
const taskFeedback = document.getElementById("task-feedback");

async function loadTasks() {
    taskFeedback.textContent = "";

    try {
        const response = await fetch("/api/tasks");

        if (!response.ok) {
            throw new Error("Failed to load tasks.");
        }

        const tasks = await response.json();

        renderTasks(tasks);
    } catch (error) {
        taskFeedback.textContent = error.message;
    }
}

function renderTasks(tasks) {
    taskList.replaceChildren();

    if (tasks.length === 0) {
        const emptyState = document.createElement("li");
        emptyState.className = "empty-state";
        emptyState.textContent =
            "Your list is clear. Add a task to get started.";

        taskList.appendChild(emptyState);
        return;
    }

    for (const task of tasks) {
        const item = document.createElement("li");
        item.className = "task-item";

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = task.completed;
        checkbox.setAttribute(
            "aria-label",
            `Mark ${task.title} as completed`
        );

        const title = document.createElement("span");
        title.className = "task-title";
        title.textContent = task.title;

        if (task.completed) {
            item.classList.add("is-completed");
        }

        checkbox.addEventListener("change", async () => {
            checkbox.disabled = true;
            taskFeedback.textContent = "";

            try {
                const response = await fetch(`/api/tasks/${task.id}`, {
                    method: "PATCH",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        completed: checkbox.checked,
                    }),
                });

                if (!response.ok) {
                    throw new Error("Failed to update task.");
                }

                const updatedTask = await response.json();

                checkbox.checked = updatedTask.completed;
                title.textContent = updatedTask.title;
                item.classList.toggle(
                    "is-completed",
                    updatedTask.completed
                );
            } catch (error) {
                checkbox.checked = task.completed;
                taskFeedback.textContent = error.message;
            } finally {
                checkbox.disabled = false;
            }
        });

        item.appendChild(checkbox);
        item.appendChild(title);
        taskList.appendChild(item);
    }
}

taskForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const title = taskTitleInput.value.trim();

    if (!title) {
        taskFeedback.textContent = "Please enter a task title.";
        return;
    }

    taskFeedback.textContent = "";

    try {
        const response = await fetch("/api/tasks", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ title }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(
                errorData.detail || "Failed to create task."
            );
        }

        taskTitleInput.value = "";
        await loadTasks();
        taskTitleInput.focus();
    } catch (error) {
        taskFeedback.textContent = error.message;
    }
});

loadTasks();
