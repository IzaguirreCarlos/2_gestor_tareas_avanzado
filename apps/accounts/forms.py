from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

_INPUT_CLASS = 'auth-input'


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': _INPUT_CLASS,
            'placeholder': 'tu@email.com',
            'autocomplete': 'email',
        }),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': _INPUT_CLASS,
                'placeholder': 'Elige un nombre de usuario',
                'autocomplete': 'username',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': _INPUT_CLASS,
            'placeholder': 'Mínimo 8 caracteres',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': _INPUT_CLASS,
            'placeholder': 'Repite tu contraseña',
            'autocomplete': 'new-password',
        })
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': _INPUT_CLASS,
            'placeholder': 'Tu nombre de usuario',
            'autocomplete': 'username',
        })
        self.fields['password'].widget.attrs.update({
            'class': _INPUT_CLASS,
            'placeholder': 'Tu contraseña',
            'autocomplete': 'current-password',
        })
