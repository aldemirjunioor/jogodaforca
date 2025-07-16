from django.contrib import admin
from .models import Perfil, Tema, Palavra, Jogo

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'eh_professor']

@admin.register(Tema)
class TemaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'criado_por']

@admin.register(Palavra)
class PalavraAdmin(admin.ModelAdmin):
    list_display = ['texto', 'tema']

@admin.register(Jogo)
class JogoAdmin(admin.ModelAdmin):
    list_display = ['palavra', 'jogador', 'status', 'data']
