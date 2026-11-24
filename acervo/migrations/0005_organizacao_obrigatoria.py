import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Etapa 3/3: a FK vira obrigatória e a unicidade do patrimônio passa a ser por organização."""

    dependencies = [('acervo', '0004_dados_organizacao')]

    operations = [
        migrations.AlterField(model_name='autor', name='organizacao', field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.organizacao')),
        migrations.AlterField(model_name='livro', name='organizacao', field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.organizacao')),
        migrations.AlterField(model_name='exemplar', name='organizacao', field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.organizacao')),
        migrations.AlterField(
            model_name='exemplar',
            name='codigo_patrimonio',
            field=models.CharField(max_length=20),
        ),
        migrations.AddConstraint(
            model_name='exemplar',
            constraint=models.UniqueConstraint(fields=('organizacao', 'codigo_patrimonio'), name='patrimonio_unico_por_org'),
        ),
    ]
