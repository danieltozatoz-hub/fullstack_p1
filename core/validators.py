"""Regras compartilhadas entre formulários (HTML) e serializers (API).

Um lugar principal para cada regra: assim form e API nunca divergem.
"""
from django.db.models import UniqueConstraint


def erros_unicidade_na_org(model, org, dados, instance=None):
    """Confere as UniqueConstraint que incluem `organizacao`.

    Como `organizacao` fica fora de formulários e serializers, o Django não
    valida essas restrições sozinho (daria IntegrityError no banco).
    Devolve {campo: mensagem}.
    """
    erros = {}
    if org is None:
        return erros
    for constraint in model._meta.constraints:
        if not isinstance(constraint, UniqueConstraint):
            continue
        if 'organizacao' not in constraint.fields:
            continue
        campos = [f for f in constraint.fields if f != 'organizacao']
        if not campos or not all(c in dados for c in campos):
            continue
        qs = model.objects.filter(
            organizacao=org, **{c: dados[c] for c in campos})
        if instance is not None and instance.pk:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            nome = model._meta.verbose_name
            erros[campos[0]] = f'Já existe {nome} com este valor na sua organização.'
    return erros
