from django import forms
from django.contrib.auth.models import User
from .models import Perfil, Tema, Palavra


class FormularioRegistro(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'campo-input'}))
    confirmar_senha = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'campo-input'}))
    eh_professor = forms.BooleanField(label="Sou professor", required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'senha', 'confirmar_senha']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'campo-input'}),
            'email': forms.EmailInput(attrs={'class': 'campo-input'}),
        }
        labels = {
            'username': 'Nome de usuário',
            'email': 'E-mail',
        }

    def clean(self):
        dados = super().clean()
        senha = dados.get("senha")
        confirmar = dados.get("confirmar_senha")
        if senha and confirmar and senha != confirmar:
            self.add_error("confirmar_senha", "As senhas não coincidem.")

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["senha"])
        if commit:
            usuario.save()
            Perfil.objects.create(
                usuario=usuario,
                eh_professor=self.cleaned_data.get("eh_professor", False)
            )
        return usuario

class FormularioTema(forms.ModelForm):
    class Meta:
        model = Tema
        fields = ['nome']


class FormularioPalavra(forms.ModelForm):
    class Meta:
        model = Palavra
        fields = ['texto', 'dica', 'texto_auxiliar', 'tema']
