from django import forms
<<<<<<< HEAD
=======
from django.core.exceptions import ValidationError
from datetime import date
from .models import Livro, Autor, Exemplar
>>>>>>> 30da19d2bc8a0a562a7a78d2681f04e392423f67

from core.forms import OrgModelForm
from .models import Livro, Autor, Exemplar
from .validators import validar_ano_publicacao


class AutorForm(OrgModelForm):
    class Meta:
        model = Autor
        fields = ['nome']


class LivroForm(OrgModelForm):
    class Meta:
        model = Livro
        fields = ['titulo', 'autor', 'ano']

    def clean_ano(self):
<<<<<<< HEAD
        return validar_ano_publicacao(self.cleaned_data.get('ano'))


class ExemplarForm(OrgModelForm):
    class Meta:
        model = Exemplar
        fields = ['livro', 'codigo_patrimonio']


class PeriodoForm(forms.Form):
    """Filtro de período do dashboard.

    Nunca confie na data digitada na URL: o DateField valida e converte,
    e uma string como "abc" vira erro de formulário (e não erro 500).
    """
    inicio = forms.DateField(
        required=False, label='Início',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'))
    fim = forms.DateField(
        required=False, label='Fim',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'))

    def clean(self):
        dados = super().clean()
        inicio, fim = dados.get('inicio'), dados.get('fim')
        if inicio and fim and inicio > fim:
            raise forms.ValidationError('A data inicial não pode ser depois da data final.')
        return dados
=======
        ano = self.cleaned_data.get('ano')
        ano_atual = date.today().year
        if ano and ano > ano_atual:
            raise ValidationError('O ano de publicação não pode ser um ano futuro.')
        return ano
        
class ExemplarForm(forms.ModelForm):
    class Meta:
        model = Exemplar
        fields = ['livro','codigo_patrimonio']
>>>>>>> 30da19d2bc8a0a562a7a78d2681f04e392423f67
