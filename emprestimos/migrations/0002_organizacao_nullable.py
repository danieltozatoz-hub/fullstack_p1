import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Etapa 1/3: a FK entra permitindo nulo (as linhas da P1 ainda não têm organização)."""

    dependencies = [
        ('core', '0001_initial'),
        ('emprestimos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='emprestimo',
            name='organizacao',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.organizacao'),
        ),
        migrations.AddField(
            model_name='reserva',
            name='organizacao',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.organizacao'),
        ),
    ]
