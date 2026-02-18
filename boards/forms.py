from django import forms
from .models import Task, Board
from .models import Label


class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['name', 'members']  # campos que quieres editar
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'members': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }




class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title',
            'description',
            'assigned_to',
            'priority',
            'due_date',
            'labels',
        ]






class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ["name", "color"]

        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Ej: Bug, Urgente, Frontend"}),
            "color": forms.Select(choices=[
                ("gray", "Gris"),
                ("red", "Rojo"),
                ("green", "Verde"),
                ("blue", "Azul"),
                ("yellow", "Amarillo"),
                ("purple", "Morado"),
                ("orange", "Naranja"),
            ])
        }