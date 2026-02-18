from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.http import HttpResponse
from .utils import send_task_notification

import json, csv

from .models import Board, TaskList, Task, Label
from .forms import BoardForm, TaskForm, LabelForm



import json
from .models import Board, TaskList, Task
from .utils import send_task_notification

# ==========================
# CRUD PRINCIPAL DE BOARDS
# ==========================
@login_required
def task_list(request):
    tasks = Task.objects.select_related(
        'task_list',
        'task_list__board'
    ).all()

    return render(request, 'boards/task_list.html', {
        'tasks': tasks
    })

@login_required
def board_list(request):
    """Ver todos los tableros del usuario"""
    boards = Board.objects.filter(owner=request.user)
    return render(request, 'boards/board_list.html', {'boards': boards})




@login_required
def board_create(request):
    """Crear un tablero nuevo"""
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Board.objects.create(
                name=name,
                owner=request.user
            )
        return redirect('boards:list')
    return render(request, 'boards/board_create.html')




@login_required
def board_detail(request, pk):
    """Ver un tablero y sus columnas/tareas"""

    board = get_object_or_404(Board, pk=pk)

    # Permisos
    if request.user != board.owner and request.user not in board.members.all():
        return redirect("boards:list")

    members = board.members.all()

    if request.method == "POST":

        # ==========================
        # Crear columna
        # ==========================
        if "list_title" in request.POST:
            TaskList.objects.create(
                title=request.POST.get("list_title"),
                board=board,
                order=board.lists.count()
            )
            return redirect("boards:detail", pk=board.id)

        # ==========================
        # Crear tarea + EMAIL
        # ==========================
        if "task_title" in request.POST:
            task_list = get_object_or_404(
                TaskList,
                id=request.POST.get("list_id"),
                board=board
            )

            assigned_to_id = request.POST.get("assigned_to")
            assigned_user = None

            # Solo permitir asignar a miembros del tablero
            if assigned_to_id:
                assigned_user = get_object_or_404(User, id=assigned_to_id)
                if assigned_user not in members and assigned_user != board.owner:
                    assigned_user = None

            priority = request.POST.get("priority", "medium")
            due_date = request.POST.get("due_date") or None

            task = Task.objects.create(
                title=request.POST.get("task_title"),
                task_list=task_list,
                assigned_to=assigned_user,
                priority=priority,
                due_date=due_date,
                order=task_list.tasks.count()
            )

            # 🔔 Notificación por email (solo si se asignó)
            if assigned_user and assigned_user.email:
                subject = f"📌 Nueva tarea asignada: {task.title}"

                message = (
                    f"Hola {assigned_user.username},\n\n"
                    f"Se te asignó una nueva tarea.\n\n"
                    f"📌 Tarea: {task.title}\n"
                    f"📋 Tablero: {board.name}\n"
                    f"📂 Columna: {task_list.title}\n"
                    f"⚡ Prioridad: {task.get_priority_display()}\n"
                    f"📅 Fecha límite: {task.due_date if task.due_date else 'No definida'}\n\n"
                    f"Entra al sistema para verla."
                )

                send_task_notification(task, subject, message)

            return redirect("boards:detail", pk=board.id)

    return render(request, "boards/board_detail.html", {
        "board": board,
        "members": members,
    })


# ==========================
# DRAG & DROP DE TAREAS
# ==========================

@require_POST
@csrf_exempt
def move_task(request):
    """Actualizar la columna y posición de una tarea vía JS"""
    data = json.loads(request.body)
    task_id = data.get('task_id')
    new_list_id = data.get('new_list_id')
    new_order = data.get('new_order')

    task = Task.objects.get(id=task_id)
    task.task_list_id = new_list_id
    task.order = new_order
    task.save()

    return JsonResponse({'status': 'ok'})






def board_edit(request, id):
    board = get_object_or_404(Board, id=id)

    if request.method == 'POST':
        form = BoardForm(request.POST, instance=board)
        if form.is_valid():
            form.save()
            return redirect('boards:list')
    else:
        form = BoardForm(instance=board)

    return render(request, 'boards/board_form.html', {
        'form': form,
        'title': 'Editar Tablero'
    })





def board_delete(request, id):
    board = get_object_or_404(Board, id=id)

    if request.method == 'POST':
        board.delete()
        return redirect('boards:list')

    return render(request, 'boards/board_confirm_delete.html', {
        'board': board
    })




# Creando vista ,,, para mostrar tareas asignadas al usuario logueado
@login_required
def my_tasks(request):
    """Mostrar solo las tareas asignadas al usuario logueado"""
    tasks = Task.objects.filter(assigned_to=request.user).select_related(
        'task_list',
        'task_list__board'
    ).order_by('task_list__board', 'task_list__order', 'order')

    return render(request, 'boards/my_tasks.html', {
        'tasks': tasks
    })







@login_required
@require_POST
def reassign_task(request):
    """Cambiar el usuario asignado de una tarea vía AJAX"""
    task_id = request.POST.get('task_id')
    assigned_to_id = request.POST.get('assigned_to')

    try:
        task = Task.objects.get(id=task_id)
        if assigned_to_id:
            task.assigned_to = User.objects.get(id=assigned_to_id)
        else:
            task.assigned_to = None
        task.save()
        return JsonResponse({'status': 'ok', 'assigned_to': task.assigned_to.username if task.assigned_to else ''})
    except Task.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Tarea no encontrada'})
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Usuario no encontrado'})




@login_required
def label_create(request, tasklist_id):
    task_list = get_object_or_404(TaskList, id=tasklist_id)
    board = task_list.board

    # seguridad
    if request.user != board.owner and request.user not in board.members.all():
        return redirect("boards:list")

    if request.method == "POST":
        form = LabelForm(request.POST)
        if form.is_valid():
            label = form.save(commit=False)
            label.task_list = task_list
            label.save()

    return redirect("boards:detail", pk=board.id)


@login_required
def label_delete(request, label_id):
    label = get_object_or_404(Label, id=label_id)
    task_list = label.task_list
    board = task_list.board

    # seguridad
    if request.user != board.owner and request.user not in board.members.all():
        return redirect("boards:list")

    if request.method == "POST":
        label.delete()

    return redirect("boards:detail", pk=board.id)






@login_required
def export_tasks_csv(request, board_id):
    board = get_object_or_404(Board, id=board_id)

    # Seguridad: solo owner o miembros
    if request.user != board.owner and request.user not in board.members.all():
        return HttpResponse("No autorizado", status=403)

    tasks = (
        Task.objects
        .filter(task_list__board=board)
        .select_related("task_list", "assigned_to", "task_list__board")
        .prefetch_related("labels")
        .order_by("task_list__order", "order")
    )

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="tablero_{board.id}_{board.name}.csv"'

    # Esto ayuda a Excel con acentos (UTF-8 BOM)
    response.write("\ufeff")

    writer = csv.writer(response)

    # =========================
    # CABECERA GENERAL (BONITA)
    # =========================
    writer.writerow(["TABLERO", board.name])
    writer.writerow(["DUEÑO", board.owner.username])
    writer.writerow(["EXPORTADO POR", request.user.username])
    writer.writerow([])  # línea vacía

    # =========================
    # CABECERA DE COLUMNAS
    # =========================
    writer.writerow([
        "ID",
        "Tarea",
        "Descripcion",
        "Columna",
        "Orden",
        "Prioridad",
        "Etiquetas",
        "Asignado a",
        "Fecha limite",
        "Creado",
    ])

    # =========================
    # FILAS
    # =========================
    for task in tasks:
        labels = " | ".join([label.name for label in task.labels.all()])
        assigned = task.assigned_to.username if task.assigned_to else "Sin asignar"

        # Prioridad bonita
        if task.priority == "high":
            priority = "Alta"
        elif task.priority == "medium":
            priority = "Media"
        else:
            priority = "Baja"

        due_date = task.due_date.strftime("%d/%m/%Y") if task.due_date else ""
        created_at = task.created_at.strftime("%d/%m/%Y %H:%M") if task.created_at else ""

        writer.writerow([
            task.id,
            task.title,
            task.description,
            task.task_list.title if task.task_list else "",
            task.order,
            priority,
            labels,
            assigned,
            due_date,
            created_at,
        ])

    return response






@login_required
def export_my_tasks_csv(request):
    tasks = (
        Task.objects
        .filter(assigned_to=request.user)
        .select_related("task_list", "task_list__board", "assigned_to")
        .prefetch_related("labels")
        .order_by("task_list__board__name", "task_list__order", "order")
    )

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="mis_tareas_{request.user.username}.csv"'

    # Para que Excel abra acentos bien
    response.write("\ufeff")

    writer = csv.writer(response)

    # Cabecera bonita
    writer.writerow(["EXPORTACION DE TAREAS"])
    writer.writerow(["Usuario", request.user.username])
    writer.writerow([])

    # Columnas
    writer.writerow([
        "ID",
        "Tablero",
        "Columna",
        "Orden",
        "Tarea",
        "Descripcion",
        "Prioridad",
        "Etiquetas",
        "Fecha limite",
        "Creado",
    ])

    for task in tasks:
        labels = " | ".join([label.name for label in task.labels.all()])

        # Prioridad bonita
        if task.priority == "high":
            priority = "Alta"
        elif task.priority == "medium":
            priority = "Media"
        else:
            priority = "Baja"

        due_date = task.due_date.strftime("%d/%m/%Y") if task.due_date else ""
        created_at = task.created_at.strftime("%d/%m/%Y %H:%M") if task.created_at else ""

        writer.writerow([
            task.id,
            task.task_list.board.name if task.task_list and task.task_list.board else "",
            task.task_list.title if task.task_list else "",
            task.order,
            task.title,
            task.description,
            priority,
            labels,
            due_date,
            created_at,
        ])

    return response
