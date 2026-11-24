"""Regras de negócio de empréstimo.

Ficam aqui (e não nas views) para que as telas HTML e a API REST usem
exatamente o mesmo código: uma regra, um lugar.
"""
from datetime import date, timedelta

from django.db import transaction

PRAZO_DIAS = 7


@transaction.atomic
def registrar_emprestimo(emprestimo):
    """Calcula o prazo, grava o empréstimo e marca o exemplar como indisponível."""
    emprestimo.data_prevista_devolucao = date.today() + timedelta(days=PRAZO_DIAS)
    emprestimo.save()

    exemplar = emprestimo.exemplar
    exemplar.disponivel = False
    exemplar.save()
    return emprestimo


@transaction.atomic
def registrar_devolucao(emprestimo):
    """Registra a devolução e libera o exemplar."""
    if emprestimo.data_devolucao:
        raise ValueError('Este empréstimo já foi devolvido.')
    emprestimo.data_devolucao = date.today()
    emprestimo.save()

    exemplar = emprestimo.exemplar
    exemplar.disponivel = True
    exemplar.save()
    return emprestimo
