from rest_framework import serializers

from core.api import OrgModelSerializer
from .models import Emprestimo, Reserva
from .services import registrar_emprestimo


class EmprestimoSerializer(OrgModelSerializer):
    usuario_nome = serializers.CharField(source='usuario.nome', read_only=True)
    livro_titulo = serializers.CharField(source='exemplar.livro.titulo', read_only=True)

    class Meta:
        model = Emprestimo
        fields = [
            'id', 'usuario', 'usuario_nome', 'exemplar', 'livro_titulo',
            'data_emprestimo', 'data_prevista_devolucao', 'data_devolucao',
            'atrasado', 'valor_multa',
        ]
        # Só usuario e exemplar vêm do cliente; prazo e devolução são regras do sistema.
        read_only_fields = [
            'data_emprestimo', 'data_prevista_devolucao', 'data_devolucao',
            'atrasado', 'valor_multa',
        ]

    def validate_exemplar(self, value):
        if not value.disponivel:
            raise serializers.ValidationError('Este exemplar não está disponível.')
        return value

    def create(self, validated_data):
        # Mesma regra das telas HTML: calcula o prazo e marca o exemplar indisponível.
        return registrar_emprestimo(Emprestimo(**validated_data))


class ReservaSerializer(OrgModelSerializer):
    usuario_nome = serializers.CharField(source='usuario.nome', read_only=True)
    livro_titulo = serializers.CharField(source='livro.titulo', read_only=True)

    class Meta:
        model = Reserva
        fields = ['id', 'usuario', 'usuario_nome', 'livro', 'livro_titulo', 'data_reserva', 'ativa']
        read_only_fields = ['data_reserva', 'ativa']
