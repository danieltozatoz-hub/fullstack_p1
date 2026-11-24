from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.api import OrgViewSetMixin
from .models import Emprestimo, Reserva
from .serializers import EmprestimoSerializer, ReservaSerializer
from .services import registrar_devolucao


class EmprestimoViewSet(OrgViewSetMixin,
                        mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    """Sem PUT/PATCH: prazo e devolução são regras do sistema, não campos livres."""
    queryset = (Emprestimo.objects
                .select_related('usuario', 'exemplar__livro')
                .order_by('-data_emprestimo', '-pk'))
    serializer_class = EmprestimoSerializer

    @action(detail=True, methods=['post'])
    def devolver(self, request, pk=None):
        """POST /api/emprestimos/<id>/devolver/"""
        emprestimo = self.get_object()
        try:
            registrar_devolucao(emprestimo)
        except ValueError as erro:
            raise ValidationError({'detail': str(erro)})
        return Response(self.get_serializer(emprestimo).data)


class ReservaViewSet(OrgViewSetMixin,
                     mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    queryset = Reserva.objects.select_related('usuario', 'livro')
    serializer_class = ReservaSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('ativa') in ('1', 'true'):
            qs = qs.filter(ativa=True)
        return qs

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """POST /api/reservas/<id>/cancelar/"""
        reserva = self.get_object()
        reserva.ativa = False
        reserva.save()
        return Response(self.get_serializer(reserva).data)
