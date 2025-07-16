from django.db import models
from django.contrib.auth.models import User


class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuário")
    eh_professor = models.BooleanField(default=False, verbose_name="É professor")

    def __str__(self):
        return f"{self.usuario.username} ({'Professor' if self.eh_professor else 'Aluno'})"

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"


class Tema(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do tema")
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='temas_criados', verbose_name="Criado por")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Tema"
        verbose_name_plural = "Temas"


class Palavra(models.Model):
    texto = models.CharField(max_length=50, verbose_name="Texto da palavra")
    dica = models.CharField(max_length=100, blank=True, null=True, verbose_name="Dica")
    texto_auxiliar = models.TextField(blank=True, null=True, verbose_name="Texto auxiliar")
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, related_name='palavras', verbose_name="Tema")

    def __str__(self):
        return self.texto

    class Meta:
        verbose_name = "Palavra"
        verbose_name_plural = "Palavras"


class Jogo(models.Model):
    palavra = models.ForeignKey(Palavra, on_delete=models.CASCADE, verbose_name="Palavra")
    jogador = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Jogador")
    acertos = models.IntegerField(default=0, verbose_name="Acertos")
    erros = models.IntegerField(default=0, verbose_name="Erros")
    status = models.CharField(
        max_length=20,
        choices=[('em_andamento', 'Em andamento'), ('ganhou', 'Ganhou'), ('perdeu', 'Perdeu')],
        default='em_andamento',
        verbose_name="Status"
    )
    data = models.DateTimeField(auto_now_add=True, verbose_name="Data")

    def __str__(self):
        return f"{self.jogador.username if self.jogador else 'Anônimo'} - {self.palavra.texto} ({self.status})"

    class Meta:
        verbose_name = "Jogo"
        verbose_name_plural = "Jogos"
