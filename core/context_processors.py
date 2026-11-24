from .tenant import obter_perfil


def perfil(request):
    """Disponibiliza `perfil` (organização e papel) em todos os templates."""
    return {'perfil': obter_perfil(request)}
