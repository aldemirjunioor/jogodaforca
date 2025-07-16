from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from reportlab.lib.units import cm
import random
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import datetime

from .models import Tema, Palavra, Perfil, Jogo
from .forms import FormularioRegistro, FormularioTema, FormularioPalavra
from django.views.generic import TemplateView, View
from django.utils.timezone import make_aware
from datetime import datetime
from .models import Jogo, Tema
from reportlab.pdfgen import canvas

from django.views import View
from django.http import HttpResponse
from .models import Jogo
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.utils.timezone import make_aware

# HOME
class HomeView(TemplateView):
    template_name = 'jogo/home.html'


# REGISTRO
class RegistroView(CreateView):
    form_class = FormularioRegistro
    template_name = 'jogo/registro.html'

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'perfil') and user.perfil.eh_professor:
            return reverse_lazy('temas')
        else:
            return reverse_lazy('selecionar_jogo')


# LOGIN
class LoginUsuarioView(LoginView):
    template_name = 'jogo/login.html'

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'perfil') and user.perfil.eh_professor:
            return reverse_lazy('pos_login')
        else:
            return reverse_lazy('selecionar_jogo')


# LOGOUT
class LogoutUsuarioView(LogoutView):
    next_page = reverse_lazy('login')


# MIXIN: apenas professores
class SomenteProfessorMixin(UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, 'perfil') and self.request.user.perfil.eh_professor

    def handle_no_permission(self):
        return redirect('login')


# CRUD TEMA (somente professores)
class TemaListView(LoginRequiredMixin, SomenteProfessorMixin, ListView):
    model = Tema
    template_name = 'jogo/temas.html'
    context_object_name = 'temas'

    def get_queryset(self):
        return Tema.objects.filter(criado_por=self.request.user)


class TemaCreateView(LoginRequiredMixin, SomenteProfessorMixin, CreateView):
    model = Tema
    form_class = FormularioTema
    template_name = 'jogo/tema_form.html'
    success_url = reverse_lazy('temas')

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)


class TemaUpdateView(LoginRequiredMixin, SomenteProfessorMixin, UpdateView):
    model = Tema
    form_class = FormularioTema
    template_name = 'jogo/tema_form.html'
    success_url = reverse_lazy('temas')


class TemaDeleteView(LoginRequiredMixin, SomenteProfessorMixin, DeleteView):
    model = Tema
    template_name = 'jogo/tema_confirm_delete.html'
    success_url = reverse_lazy('temas')


# CRUD PALAVRA (somente professores)
class PalavraListView(LoginRequiredMixin, SomenteProfessorMixin, ListView):
    model = Palavra
    template_name = 'jogo/palavras.html'
    context_object_name = 'palavras'

    def get_queryset(self):
        return Palavra.objects.filter(tema__criado_por=self.request.user)


class PalavraCreateView(LoginRequiredMixin, SomenteProfessorMixin, CreateView):
    model = Palavra
    form_class = FormularioPalavra
    template_name = 'jogo/palavra_form.html'
    success_url = reverse_lazy('palavras')


class PalavraUpdateView(LoginRequiredMixin, SomenteProfessorMixin, UpdateView):
    model = Palavra
    form_class = FormularioPalavra
    template_name = 'jogo/palavra_form.html'
    success_url = reverse_lazy('palavras')


class PalavraDeleteView(LoginRequiredMixin, SomenteProfessorMixin, DeleteView):
    model = Palavra
    template_name = 'jogo/palavra_confirm_delete.html'
    success_url = reverse_lazy('palavras')


class SelecaoJogoView(TemplateView):
    template_name = 'jogo/selecao_jogo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['temas'] = Tema.objects.filter(palavras__isnull=False).distinct()
        return context


class JogoDaForcaView(View):
    template_name = 'jogo/jogo_forca.html'

    def get(self, request, tema_id):
        tema = get_object_or_404(Tema, pk=tema_id)

        if 'jogo' in request.session:
            del request.session['jogo']

        palavra = random.choice(Palavra.objects.filter(tema=tema))
        request.session['jogo'] = {
            'palavra': palavra.texto.lower(),
            'dica': palavra.dica,
            'acertos': [],
            'erros': [],
            'max_erros': 6,
            'status': 'jogando',
            'tema': tema.nome,
            'tema_id': tema.id,
        }

        contexto = self._criar_contexto(request)
        contexto['tema'] = tema.nome
        contexto['dica'] = palavra.dica
        return render(request, self.template_name, contexto)

    def post(self, request, tema_id):
        letra = request.POST.get('letra', '').lower()
        jogo = request.session.get('jogo')

        if not jogo or jogo['status'] != 'jogando':
            return redirect('jogo_forca', tema_id=tema_id)

        if letra.isalpha() and len(letra) == 1:
            if letra in jogo['palavra']:
                if letra not in jogo['acertos']:
                    jogo['acertos'].append(letra)
            else:
                if letra not in jogo['erros']:
                    jogo['erros'].append(letra)

        # Verifica vitória ou derrota
        if all(c in jogo['acertos'] for c in jogo['palavra'] if c.isalpha()):
            jogo['status'] = 'ganhou'
        elif len(jogo['erros']) >= jogo['max_erros']:
            jogo['status'] = 'perdeu'

        # Atualiza a sessão
        request.session['jogo'] = jogo

        # Salva no banco se finalizou
        if jogo['status'] in ['ganhou', 'perdeu']:
            palavra_obj = Palavra.objects.filter(texto__iexact=jogo['palavra'], tema_id=tema_id).first()
            if palavra_obj:
                Jogo.objects.create(
                    palavra=palavra_obj,
                    jogador=request.user if request.user.is_authenticated else None,
                    acertos=len(jogo['acertos']),
                    erros=len(jogo['erros']),
                    status=jogo['status']
                )

        contexto = self._criar_contexto(request)
        contexto['tema'] = jogo['tema']
        contexto['dica'] = jogo['dica']
        return render(request, self.template_name, contexto)

    def _criar_contexto(self, request):
        jogo = request.session['jogo']
        palavra = jogo['palavra']
        acertos = jogo['acertos']
        erros = jogo['erros']
        status = jogo['status']
        max_erros = jogo['max_erros']
        tema_id = jogo['tema_id']

        palavra_mostrada = ' '.join([l if l in acertos else '_' for l in palavra])

        return {
            'palavra_mostrada': palavra_mostrada,
            'palavra_original': palavra,
            'status': status,
            'jogo': {
                'acertos': acertos,
                'erros': erros,
            },
            'max_erros': max_erros,
            'tema_id': tema_id,
            'letras_usadas': acertos + erros,
        }

# PDF do Relatório
class RelatorioPDFView(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="relatorio_jogos.pdf"'

        tema_id = request.GET.get('tema')
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')

        jogos = Jogo.objects.all()

        if tema_id:
            jogos = jogos.filter(palavra__tema_id=tema_id)

        if data_inicio:
            data_i = make_aware(datetime.strptime(data_inicio, '%Y-%m-%d'))
            jogos = jogos.filter(data__gte=data_i)

        if data_fim:
            data_f = make_aware(datetime.strptime(data_fim, '%Y-%m-%d'))
            jogos = jogos.filter(data__lte=data_f)

        doc = SimpleDocTemplate(response, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Título
        elements.append(Paragraph("Relatório de Jogos", styles['Title']))
        elements.append(Spacer(1, 12))

        # Cabeçalho + Dados
        data = [["Jogador", "Tema", "Palavra", "Status", "Data"]]
        total_ganhou = total_perdeu = total_acertos = total_erros = 0

        for jogo in jogos:
            jogador = jogo.jogador.username if jogo.jogador else "Anônimo"
            data.append([
                jogador,
                jogo.palavra.tema.nome,
                jogo.palavra.dica,
                jogo.palavra.texto,
                jogo.status,
                jogo.data.strftime('%d/%m/%Y %H:%M')
            ])
            if jogo.status == 'ganhou':
                total_ganhou += 1
            elif jogo.status == 'perdeu':
                total_perdeu += 1
            total_acertos += jogo.acertos
            total_erros += jogo.erros

        # Tabela com bordas verticais e horizontais
        table = Table(data, colWidths=[100, 100, 100, 80, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # <-- adiciona bordas em todas as células
        ]))
        elements.append(table)
        elements.append(Spacer(1, 24))

        # Totais
        elementos_totais = [
            f"Total de Vitórias: {total_ganhou}",
            f"Total de Derrotas: {total_perdeu}",
            f"Total de Acertos: {total_acertos}",
            f"Total de Erros: {total_erros}"
        ]
        bold_style = ParagraphStyle(
            name="BoldStyle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            spaceAfter=6,
        )

        for item in elementos_totais:
            elements.append(Paragraph(item, bold_style))

        doc.build(elements)
        return response

class RelatorioView(TemplateView):
    template_name = 'jogo/relatorio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        jogos = Jogo.objects.all()
        temas = Tema.objects.all()

        tema_id = self.request.GET.get('tema')
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')

        if tema_id:
            jogos = jogos.filter(palavra__tema_id=tema_id)

        if data_inicio:
            try:
                data_i = make_aware(datetime.strptime(data_inicio, '%Y-%m-%d'))
                jogos = jogos.filter(data__gte=data_i)
            except:
                pass

        if data_fim:
            try:
                data_f = make_aware(datetime.strptime(data_fim, '%Y-%m-%d'))
                jogos = jogos.filter(data__lte=data_f)
            except:
                pass

        context['temas'] = temas
        context['jogos'] = jogos
        return context

class ProximaPalavraView(View):
    def post(self, request, tema_id):
        tema = get_object_or_404(Tema, pk=tema_id)

        # Escolhe uma nova palavra aleatória do mesmo tema
        nova_palavra = Palavra.objects.filter(tema=tema).order_by('?').first()
        if not nova_palavra:
            return redirect('selecionar_tema')

        # Reinicia a sessão do jogo
        request.session['jogo'] = {
            'palavra': nova_palavra.texto.lower(),
            'dica': nova_palavra.dica,
            'acertos': [],
            'erros': [],
            'max_erros': 6,
            'status': 'jogando',
            'tema': tema.nome,
        }

        return redirect('jogo_forca', tema_id=tema.id)

@login_required
def home_professor(request):
    perfil = request.user.perfil
    if perfil.eh_professor:
        return render(request, 'home_professor.html')
    else:
        return redirect('home')

@login_required
def redirecionar_pos_login(request):
    perfil = request.user.perfil
    if perfil.eh_professor:
        return redirect('home_professor')
    else:
        return redirect('selecionar_jogo')