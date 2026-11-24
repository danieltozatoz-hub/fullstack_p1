from core.forms import OrgModelForm
from .models import Usuario


class UsuarioForm(OrgModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'telefone']
