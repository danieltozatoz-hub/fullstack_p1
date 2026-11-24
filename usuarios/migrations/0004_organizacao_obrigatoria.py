import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Etapa 3/3: FK obrigatória; o e-mail passa a ser único por organização."""

    dependencies = [('usuarios', '0003_dados_organizacao')]

    operations = [
        migrations.AlterField(model_name='usuario', name='organizacao', field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.organizacao')),
        migrations.AlterField(model_name='usuario', name='email', field=models.EmailField(max_length=254)),
        migrations.AddConstraint(
            model_name='usuario',
            constraint=models.UniqueConstraint(fields=('organizacao', 'email'), name='email_unico_por_org'),
        ),
    ]
