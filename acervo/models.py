from django.db import models

from core.models import DaOrganizacao


class Autor(DaOrganizacao):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Livro(DaOrganizacao):
    titulo = models.CharField(max_length=200)
    autor = models.ForeignKey(
        Autor,
        on_delete=models.PROTECT
    )
    ano = models.IntegerField()

    def __str__(self):
        return self.titulo


class Exemplar(DaOrganizacao):
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    # A unicidade é POR ORGANIZAÇÃO (ver constraint), não global.
    codigo_patrimonio = models.CharField(max_length=20)
    disponivel = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['organizacao', 'codigo_patrimonio'],
                name='patrimonio_unico_por_org'),
        ]

    def __str__(self):
        return f"{self.livro.titulo} - Exemplar {self.id}"
