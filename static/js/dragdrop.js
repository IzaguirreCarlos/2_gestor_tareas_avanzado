
function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    // Guardamos el ID de la tarea que se está arrastrando
    ev.dataTransfer.setData("task_id", ev.target.dataset.taskId);
}

function drop(ev) {
    ev.preventDefault();

    const taskId = ev.dataTransfer.getData("task_id");
    const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);

    // Asegurar que el drop cae sobre la columna correcta
    let column = ev.target;
    while (column && !column.classList.contains("tasks")) {
        column = column.parentElement;
    }

    if (!column) return; // Seguridad extra

    // Mover la tarjeta visualmente
    column.appendChild(taskCard);

    // Calcular nuevo orden (posición dentro de la columna)
    const newOrder = Array.from(column.children).indexOf(taskCard);

    // Enviar actualización al backend
    fetch("/boards/move-task/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({
            task_id: taskId,
            new_list_id: column.dataset.listId,
            new_order: newOrder
        })
    });
}

// Obtener CSRF token desde cookies (necesario para Django)
function getCSRFToken() {
    const name = "csrftoken=";
    const decoded = decodeURIComponent(document.cookie);
    const cookies = decoded.split(";");

    for (let c of cookies) {
        c = c.trim();
        if (c.startsWith(name)) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}



 document.addEventListener('DOMContentLoaded', () => {
  const selects = document.querySelectorAll('.reassign-select');

  selects.forEach(select => {
    select.addEventListener('change', (e) => {
      const taskId = e.target.dataset.taskId;
      const assignedTo = e.target.value;

      fetch("{% url 'boards:reassign_task' %}", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': '{{ csrf_token }}'
        },
        body: `task_id=${taskId}&assigned_to=${assignedTo}`
      })
      .then(response => response.json())
      .then(data => {
        if(data.status === 'ok'){
          console.log('Usuario reasignado:', data.assigned_to);
        } else {
          alert(data.message);
        }
      })
      .catch(err => console.error(err));
    });
  });
});

