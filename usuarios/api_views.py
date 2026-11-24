from rest_framework import viewsets

from core.api import OrgViewSetMixin
from .models import Usuario
from .serializers import UsuarioSerializer


class UsuarioViewSet(OrgViewSetMixin, viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
