from core.api import OrgModelSerializer
from .models import Usuario


class UsuarioSerializer(OrgModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nome', 'email', 'telefone']
