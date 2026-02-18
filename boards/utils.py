from django.core.mail import send_mail
from django.conf import settings

def send_task_notification(task, subject, message):
    if not task.assigned_to:
        return
# envio de email a la persona asignada a la tarea
    if not task.assigned_to.email:
        return

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [task.assigned_to.email],
        fail_silently=False
    )
