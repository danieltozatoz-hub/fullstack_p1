from django.contrib import admin

from .models import Organizacao, Perfil


@admin.register(Organizacao)
class OrganizacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'criada_em')


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'organizacao', 'papel')
    list_filter = ('organizacao', 'papel')
