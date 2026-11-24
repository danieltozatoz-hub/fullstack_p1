import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Etapa 3/3: FK obrigatória e índice em data_emprestimo (usado pelo dashboard)."""

    dependencies = [('emprestimos', '0003_dados_organizacao')]

    operations = [
        migrations.AlterField(model_name='emprestimo', name='organizacao', field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.organizacao')),
        migrations.AlterField(model_name='reserva', name='organizacao', field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.organizacao')),
        migrations.AddIndex(
            model_name='emprestimo',
            index=models.Index(fields=['data_emprestimo'], name='emprestimos_data_em_d7fa1d_idx'),
        ),
    ]
