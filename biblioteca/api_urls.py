from django.urls import path
from rest_framework.routers import DefaultRouter

from acervo.api_views import (
    AutorViewSet, LivroViewSet, ExemplarViewSet, DashboardApi)
from emprestimos.api_views import EmprestimoViewSet, ReservaViewSet
from usuarios.api_views import UsuarioViewSet

router = DefaultRouter()
router.register('autores', AutorViewSet)
router.register('livros', LivroViewSet)
router.register('exemplares', ExemplarViewSet)
router.register('usuarios', UsuarioViewSet)
router.register('emprestimos', EmprestimoViewSet)
router.register('reservas', ReservaViewSet)

urlpatterns = [
    path('dashboard/', DashboardApi.as_view(), name='api_dashboard'),
] + router.urls
