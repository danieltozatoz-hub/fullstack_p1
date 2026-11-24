from django.db import migrations

NOME_ORG_PADRAO = 'Organização padrão'


def perfis_para_usuarios_existentes(apps, schema_editor):
    """Antes da P2 ninguém precisava de organização. Quem já tem conta passa
    a ser administrador da organização padrão, senão perderia o acesso."""
    User = apps.get_model('auth', 'User')
    Org = apps.get_model('core', 'Organizacao')
    Perfil = apps.get_model('core', 'Perfil')

    sem_perfil = User.objects.filter(perfil__isnull=True)
    if not sem_perfil.exists():
        return
    org, _ = Org.objects.get_or_create(nome=NOME_ORG_PADRAO)
    for user in sem_perfil:
        Perfil.objects.create(usuario=user, organizacao=org, papel='admin')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(perfis_para_usuarios_existentes, migrations.RunPython.noop),
    ]
