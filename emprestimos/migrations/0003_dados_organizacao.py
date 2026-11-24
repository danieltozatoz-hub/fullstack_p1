from django.db import migrations


def org_do_exemplar_e_do_livro(apps, schema_editor):
    """Etapa 2/3: empréstimo herda a organização do exemplar; reserva, a do livro."""
    Emprestimo = apps.get_model('emprestimos', 'Emprestimo')
    Reserva = apps.get_model('emprestimos', 'Reserva')

    for emp in Emprestimo.objects.filter(organizacao__isnull=True).select_related('exemplar'):
        emp.organizacao_id = emp.exemplar.organizacao_id
        emp.save(update_fields=['organizacao'])

    for res in Reserva.objects.filter(organizacao__isnull=True).select_related('livro'):
        res.organizacao_id = res.livro.organizacao_id
        res.save(update_fields=['organizacao'])


class Migration(migrations.Migration):

    dependencies = [
        ('emprestimos', '0002_organizacao_nullable'),
        # exemplares e livros já precisam ter organização preenchida
        ('acervo', '0004_dados_organizacao'),
    ]

    operations = [migrations.RunPython(org_do_exemplar_e_do_livro, migrations.RunPython.noop)]
