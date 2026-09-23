from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Livro, Autor, Exemplar

class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = ['nome']

class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = ['titulo', 'autor', 'ano']

    def clean_ano(self):
        ano = self.cleaned_data.get('ano')
        ano_atual = date.today().year
        if ano and ano > ano_atual:
            raise ValidationError('O ano de publicação não pode ser um ano futuro.')
        return ano
        
class ExemplarForm(forms.ModelForm):
    class Meta:
        model = Exemplar
        fields = ['livro','codigo_patrimonio']
