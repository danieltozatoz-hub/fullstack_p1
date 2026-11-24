"""Base da API REST (DRF) com isolamento por organização.

Mesmas regras da parte HTML (Aula 14), agora no JSON:
- todo queryset parte de filter(organizacao=org);
- a organização vem do usuário logado, nunca do corpo da requisição;
- campos FK só aceitam ids de registros da própria organização.
"""
from django.db.models import ProtectedError
from rest_framework import serializers
from rest_framework.exceptions import APIException

from .models import DaOrganizacao
from .tenant import org_atual
from .validators import erros_unicidade_na_org


class OrgModelSerializer(serializers.ModelSerializer):
    """ModelSerializer que não deixa vincular dados de outra organização."""

    def _org(self):
        request = self.context.get('request')
        return org_atual(request) if request is not None else None

    def get_fields(self):
        fields = super().get_fields()
        org = self._org()
        if org is None:
            return fields
        for campo in fields.values():
            if isinstance(campo, serializers.PrimaryKeyRelatedField) and not campo.read_only:
                qs = campo.queryset
                if qs is not None and issubclass(qs.model, DaOrganizacao):
                    campo.queryset = qs.filter(organizacao=org)
        return fields

    def validate(self, attrs):
        attrs = super().validate(attrs)
        erros = erros_unicidade_na_org(
            self.Meta.model, self._org(), attrs, self.instance)
        if erros:
            raise serializers.ValidationError(erros)
        return attrs


class ExclusaoProtegida(APIException):
    status_code = 409
    default_detail = 'Este registro está em uso por outros dados e não pode ser excluído.'
    default_code = 'protegido'


class OrgViewSetMixin:
    """Mixin para ViewSets: filtra pela organização e grava na organização certa."""

    def get_queryset(self):
        return super().get_queryset().filter(organizacao=org_atual(self.request))

    def perform_create(self, serializer):
        serializer.save(organizacao=org_atual(self.request))

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise ExclusaoProtegida()
