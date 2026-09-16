from django import forms
from .models import Livro, Autor, Exemplar

class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = ['nome']

class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = ['titulo', 'autor', 'ano']
        
class ExemplarForm(forms.ModelForm):
    class Meta:
        model = Exemplar
        fields = ['livro','codigo_patrimonio']