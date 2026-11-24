"""Regras de negócio do acervo, reaproveitadas pelo formulário e pela API."""
from datetime import date

from django.core.exceptions import ValidationError


def validar_ano_publicacao(ano):
    if ano and ano > date.today().year:
        raise ValidationError('O ano de publicação não pode ser um ano futuro.')
    return ano
