"""Fábricas de dados para os testes: números pequenos, fáceis de conferir à mão."""
from datetime import date, timedelta

from django.contrib.auth.models import User

from acervo.models import Autor, Livro, Exemplar
from emprestimos.models import Emprestimo
from usuarios.models import Usuario
from .models import Organizacao, Perfil


def criar_org_com_login(nome_org, username, papel=Perfil.ADMIN):
    org = Organizacao.objects.create(nome=nome_org)
    user = User.objects.create_user(username, password='senha-teste')
    Perfil.objects.create(usuario=user, organizacao=org, papel=papel)
    return org, user


def criar_acervo(org, titulo='Dom Casmurro', codigo='P-1', autor='Machado de Assis'):
    autor = Autor.objects.create(organizacao=org, nome=autor)
    livro = Livro.objects.create(organizacao=org, titulo=titulo, autor=autor, ano=1899)
    exemplar = Exemplar.objects.create(organizacao=org, livro=livro, codigo_patrimonio=codigo)
    leitor = Usuario.objects.create(
        organizacao=org, nome=f'Leitor de {org.nome}', email=f'leitor@{org.pk}.com')
    return autor, livro, exemplar, leitor


def criar_emprestimo(org, leitor, exemplar, saida=None, devolucao=None, prazo_dias=7):
    """data_emprestimo é auto_now_add: o update força a data desejada."""
    saida = saida or date.today()
    emp = Emprestimo.objects.create(
        organizacao=org, usuario=leitor, exemplar=exemplar,
        data_prevista_devolucao=saida + timedelta(days=prazo_dias),
        data_devolucao=devolucao)
    Emprestimo.objects.filter(pk=emp.pk).update(data_emprestimo=saida)
    emp.refresh_from_db()
    return emp
