from django.contrib import admin
from .models import Emprestimo, Reserva


@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'exemplar', 'data_emprestimo', 'data_prevista_devolucao', 'data_devolucao', 'organizacao')
    list_filter = ('organizacao',)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'livro', 'data_reserva', 'ativa', 'organizacao')
    list_filter = ('organizacao', 'ativa')
