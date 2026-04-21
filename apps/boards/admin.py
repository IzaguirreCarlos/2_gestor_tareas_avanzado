from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Board, TaskList, Task


class TaskInline(admin.TabularInline):
    model = Task
    extra = 1


class TaskListInline(admin.TabularInline):
    model = TaskList
    extra = 1


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    inlines = [TaskListInline]


@admin.register(TaskList)
class TaskListAdmin(admin.ModelAdmin):
    list_display = ('title', 'board', 'order')
    inlines = [TaskInline]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'task_list', 'priority', 'assigned_to')
    list_filter = ('priority',)
