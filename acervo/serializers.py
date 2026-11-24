from rest_framework import serializers

from core.api import OrgModelSerializer
from .models import Autor, Livro, Exemplar
from .validators import validar_ano_publicacao


class AutorSerializer(OrgModelSerializer):
    class Meta:
        model = Autor
        fields = ['id', 'nome']


class LivroSerializer(OrgModelSerializer):
    autor_nome = serializers.CharField(source='autor.nome', read_only=True)

    class Meta:
        model = Livro
        fields = ['id', 'titulo', 'autor', 'autor_nome', 'ano']

    def validate_ano(self, value):
        return validar_ano_publicacao(value)  # mesma regra do formulário


class ExemplarSerializer(OrgModelSerializer):
    livro_titulo = serializers.CharField(source='livro.titulo', read_only=True)

    class Meta:
        model = Exemplar
        fields = ['id', 'livro', 'livro_titulo', 'codigo_patrimonio', 'disponivel']
        # A disponibilidade é controlada pelos empréstimos/devoluções.
        read_only_fields = ['disponivel']
