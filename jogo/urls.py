from django.urls import path

from . import views
from .views import (
    HomeView,
    RegistroView,
    LoginUsuarioView,
    LogoutUsuarioView,
    TemaListView,
    TemaCreateView,
    TemaUpdateView,
    TemaDeleteView,
    PalavraListView,
    PalavraCreateView,
    PalavraUpdateView,
    PalavraDeleteView,
    SelecaoJogoView,
    JogoDaForcaView,
    RelatorioView,
    RelatorioPDFView,
    ProximaPalavraView
)

urlpatterns = [
    # Página inicial
    path('', HomeView.as_view(), name='home'),

    # Autenticação
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginUsuarioView.as_view(), name='login'),
    path('logout/', LogoutUsuarioView.as_view(), name='logout'),


    # Temas (somente professores)
    path('professor/', views.home_professor, name='home_professor'),
    path('temas/', TemaListView.as_view(), name='temas'),
    path('temas/novo/', TemaCreateView.as_view(), name='novo_tema'),
    path('temas/<int:pk>/editar/', TemaUpdateView.as_view(), name='editar_tema'),
    path('temas/<int:pk>/excluir/', TemaDeleteView.as_view(), name='excluir_tema'),

    # Palavras (somente professores)
    path('palavras/', PalavraListView.as_view(), name='palavras'),
    path('palavras/nova/', PalavraCreateView.as_view(), name='nova_palavra'),
    path('palavras/<int:pk>/editar/', PalavraUpdateView.as_view(), name='editar_palavra'),
    path('palavras/<int:pk>/excluir/', PalavraDeleteView.as_view(), name='excluir_palavra'),

    # Jogo
    path('selecionar_jogo/', SelecaoJogoView.as_view(), name='selecionar_jogo'),
    path('jogo/<int:tema_id>/', JogoDaForcaView.as_view(), name='jogo_forca'),
    path('jogo/<int:tema_id>/proxima/', ProximaPalavraView.as_view(), name='proxima_palavra'),
    # PDF do Relatório
    path('relatorio/pdf/', RelatorioPDFView.as_view(), name='relatorio_pdf'),
    path('relatorio/', RelatorioView.as_view(), name='relatorio'),
    # Redirecionamento pós Login
    path('pos_login/', views.redirecionar_pos_login, name='pos_login'),
    ]
