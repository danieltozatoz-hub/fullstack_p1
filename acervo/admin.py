from django.contrib import admin
from .models import Autor, Livro, Exemplar


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'organizacao')
    list_filter = ('organizacao',)


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'ano', 'organizacao')
    list_filter = ('organizacao',)


@admin.register(Exemplar)
class ExemplarAdmin(admin.ModelAdmin):
    list_display = ('codigo_patrimonio', 'livro', 'disponivel', 'organizacao')
    list_filter = ('organizacao', 'disponivel')
