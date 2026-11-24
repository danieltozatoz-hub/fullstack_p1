from django.contrib.auth.models import User
from django.db import models


class Organizacao(models.Model):
    """O "inquilino" do sistema: dono de todos os dados de negócio."""
    nome = models.CharField(max_length=120)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'organização'
        verbose_name_plural = 'organizações'

    def __str__(self):
        return self.nome


class DaOrganizacao(models.Model):
    """Base abstrata: todo model com dados de negócio herda daqui.

    O Django não cria tabela para ela; o campo é copiado para cada filho.
    """
    organizacao = models.ForeignKey(
        'core.Organizacao',
        on_delete=models.PROTECT,
    )

    class Meta:
        abstract = True


class Perfil(models.Model):
    """Liga o User do Django a UMA organização e a UM papel."""
    ADMIN = 'admin'
    OPERADOR = 'operador'
    PAPEIS = [
        (ADMIN, 'Administrador'),
        (OPERADOR, 'Operador'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    organizacao = models.ForeignKey(Organizacao, on_delete=models.PROTECT)
    papel = models.CharField(max_length=20, choices=PAPEIS, default=OPERADOR)

    @property
    def eh_admin(self):
        return self.papel == self.ADMIN

    def __str__(self):
        return f'{self.usuario.username} ({self.organizacao} / {self.get_papel_display()})'
