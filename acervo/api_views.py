from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api import OrgViewSetMixin
from core.tenant import org_atual, obter_perfil
from . import dashboard as metricas_dashboard
from .forms import PeriodoForm
from .models import Autor, Livro, Exemplar
from .serializers import AutorSerializer, LivroSerializer, ExemplarSerializer


class AutorViewSet(OrgViewSetMixin, viewsets.ModelViewSet):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer


class LivroViewSet(OrgViewSetMixin, viewsets.ModelViewSet):
    queryset = Livro.objects.select_related('autor')
    serializer_class = LivroSerializer


class ExemplarViewSet(OrgViewSetMixin, viewsets.ModelViewSet):
    queryset = Exemplar.objects.select_related('livro')
    serializer_class = ExemplarSerializer


class DashboardApi(APIView):
    """GET /api/dashboard/?inicio=AAAA-MM-DD&fim=AAAA-MM-DD

    O mesmo dado da tela, em JSON, reaproveitando as funções de dashboard.py.
    """

    def get(self, request):
        org = org_atual(request)
        form = PeriodoForm(request.query_params)
        if not form.is_valid():
            return Response(form.errors, status=400)

        base = metricas_dashboard.filtrar_periodo(
            request, metricas_dashboard.emprestimos_da_org(org))
        dados = metricas_dashboard.metricas(base)
        if not obter_perfil(request).eh_admin:
            dados.pop('por_mes')  # operador não vê a série (igual à tela)
        return Response(dados)
