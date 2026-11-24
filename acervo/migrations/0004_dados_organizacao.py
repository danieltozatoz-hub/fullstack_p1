from django.db import migrations

NOME_ORG_PADRAO = 'Organização padrão'


def org_padrao(apps, schema_editor):
    """Etapa 2/3: toda linha da P1 vai para a organização padrão."""
    Org = apps.get_model('core', 'Organizacao')
    org, _ = Org.objects.get_or_create(nome=NOME_ORG_PADRAO)
    for nome_model in ('Autor', 'Livro', 'Exemplar'):
        Model = apps.get_model('acervo', nome_model)
        Model.objects.filter(organizacao__isnull=True).update(organizacao=org)


class Migration(migrations.Migration):

    dependencies = [('acervo', '0003_organizacao_nullable')]

    operations = [migrations.RunPython(org_padrao, migrations.RunPython.noop)]
