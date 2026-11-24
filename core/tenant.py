"""Helpers de multi-organização: quem é o usuário e de qual organização ele é."""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import Perfil


def obter_perfil(request):
    """Perfil do usuário logado (ou None). Fica em cache na requisição:
    uma consulta só, já com a organização (select_related)."""
    if not hasattr(request, '_perfil_cache'):
        perfil = None
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            perfil = (Perfil.objects
                      .select_related('organizacao')
                      .filter(usuario=user)
                      .first())
        request._perfil_cache = perfil
    return request._perfil_cache


def org_atual(request):
    """ÚNICO lugar que define a organização da requisição.

    Nunca confie na organização vinda da URL ou de formulário.
    Superusuário sem Perfil recebe 403 em vez de estourar
    RelatedObjectDoesNotExist.
    """
    perfil = obter_perfil(request)
    if perfil is None:
        raise PermissionDenied(
            'Seu usuário não está vinculado a nenhuma organização. '
            'Peça a um administrador para criar o seu Perfil.')
    return perfil.organizacao


def papel_requerido(*papeis):
    """Decorator: exige login e que o papel do Perfil esteja em `papeis`."""
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            perfil = obter_perfil(request)
            if perfil is None or perfil.papel not in papeis:
                raise PermissionDenied('Seu papel não permite esta ação.')
            return view(request, *args, **kwargs)
        return login_required(wrapper)
    return decorator
