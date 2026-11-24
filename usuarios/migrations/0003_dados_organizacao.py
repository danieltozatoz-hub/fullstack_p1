from django.db import migrations

NOME_ORG_PADRAO = 'Organização padrão'


def org_padrao(apps, schema_editor):
    """Etapa 2/3: todo leitor da P1 vai para a organização padrão."""
    Org = apps.get_model('core', 'Organizacao')
    Usuario = apps.get_model('usuarios', 'Usuario')
    org, _ = Org.objects.get_or_create(nome=NOME_ORG_PADRAO)
    Usuario.objects.filter(organizacao__isnull=True).update(organizacao=org)


class Migration(migrations.Migration):

    dependencies = [('usuarios', '0002_organizacao_nullable')]

    operations = [migrations.RunPython(org_padrao, migrations.RunPython.noop)]
