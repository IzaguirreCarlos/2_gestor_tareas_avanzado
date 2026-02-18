from django.urls import path
from . import views
from .views import export_tasks_csv


app_name = 'boards'

urlpatterns = [
    path('tasks/', views.task_list, name='task_list'),
    path('', views.board_list, name='list'),           # Lista de tableros
    path('create/', views.board_create, name='create'), # Crear tablero
    path('<int:pk>/', views.board_detail, name='detail'), # Ver tablero específico
    path('task/move/', views.move_task, name='move_task'), # Drag & drop de tareas
    path('edit/<int:id>/', views.board_edit, name='board_edit'),# Editar tablero
    path('delete/<int:id>/', views.board_delete, name='board_delete'),# Eliminar tablero
    path('my-tasks/', views.my_tasks, name='my_tasks'), # Ver mis tareas
    path('reassign-task/', views.reassign_task, name='reassign_task'),
    path("labels/create/<int:tasklist_id>/", views.label_create, name="label_create"),
    path("labels/delete/<int:label_id>/", views.label_delete, name="label_delete"),
    path("board/<int:board_id>/export/csv/", export_tasks_csv, name="export_tasks_csv"),
    path("my-tasks/export/csv/", views.export_my_tasks_csv, name="export_my_tasks_csv"),

]