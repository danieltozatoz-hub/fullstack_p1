from acervo.models import Exemplar
from core.forms import OrgModelForm
from .models import Emprestimo, Reserva


class EmprestimoForm(OrgModelForm):
    class Meta:
        model = Emprestimo
        fields = ['usuario', 'exemplar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Só exemplares da organização E disponíveis. select_related('livro')
        # porque o texto de cada opção (Exemplar.__str__) usa o título do livro.
        self.fields['exemplar'].queryset = (
            Exemplar.objects
            .filter(organizacao=self.org, disponivel=True)
            .select_related('livro'))


class ReservaForm(OrgModelForm):
    class Meta:
        model = Reserva
        fields = ['usuario', 'livro']
