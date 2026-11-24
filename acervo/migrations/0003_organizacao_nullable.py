import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Etapa 1/3: a FK entra permitindo nulo (as linhas da P1 ainda não têm organização)."""

    dependencies = [
        ('core', '0001_initial'),
        ('acervo', '0002_autor_remove_livro_disponivel_alter_livro_autor_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='autor',
            name='organizacao',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.organizacao'),
        ),
        migrations.AddField(
            model_name='livro',
            name='organizacao',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.organizacao'),
        ),
        migrations.AddField(
            model_name='exemplar',
            name='organizacao',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.organizacao'),
        ),
    ]
