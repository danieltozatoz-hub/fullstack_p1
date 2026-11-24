from django.db import models

from core.models import DaOrganizacao


class Usuario(DaOrganizacao):
    """Leitor da biblioteca (não confundir com o User de login do Django)."""
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=15, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['organizacao', 'email'],
                name='email_unico_por_org'),
        ]

    def __str__(self):
        return self.nome
