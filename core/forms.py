from django import forms

from .models import DaOrganizacao
from .validators import erros_unicidade_na_org


class OrgModelForm(forms.ModelForm):
    """ModelForm que isola os dados por organização.

    - Todo campo FK/M2M tem o queryset filtrado pela organização
      (senão o <select> mostra opções de outras organizações).
    - Unicidade "por organização" é validada no clean().
    - O campo `organizacao` NÃO fica no form: a view o preenche
      (commit=False), sempre a partir do usuário logado.
    """

    def __init__(self, *args, org=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.org = org
        for campo in self.fields.values():
            qs = getattr(campo, 'queryset', None)
            if qs is not None and issubclass(qs.model, DaOrganizacao):
                campo.queryset = qs.filter(organizacao=org)

    def clean(self):
        dados = super().clean()
        erros = erros_unicidade_na_org(
            self._meta.model, self.org, dados, self.instance)
        for campo, msg in erros.items():
            self.add_error(campo, msg)
        return dados
