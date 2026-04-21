from django.contrib.auth.models import User
from django.db import models


class Board(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_boards"
    )
    members = models.ManyToManyField(
        User,
        related_name="boards",
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ✅ 
class TaskList(models.Model):
    title = models.CharField(max_length=100)
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="lists"
    )
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
    ]

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    task_list = models.ForeignKey(
        "TaskList",   # ← referencia en string para evitar errores
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    due_date = models.DateField(null=True, blank=True)

    labels = models.ManyToManyField(
        "Label",
        blank=True,
        related_name="tasks"
    )

    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Label(models.Model):
    task_list = models.ForeignKey(
        "TaskList",   # ← igual aquí
        on_delete=models.CASCADE,
        related_name="labels"
    )

    name = models.CharField(max_length=30)

    color = models.CharField(
        max_length=20,
        default="gray"
    )

    def __str__(self):
        return self.name