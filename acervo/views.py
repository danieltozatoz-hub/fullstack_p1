import csv
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from core.tenant import org_atual, obter_perfil, papel_requerido
from . import dashboard as metricas_dashboard
from .models import Livro, Autor, Exemplar
from .forms import LivroForm, AutorForm, ExemplarForm, PeriodoForm


# ---------------------------------------------------------------- Livros
@login_required
def lista_livros(request):
    org = org_atual(request)
    livros = Livro.objects.filter(organizacao=org).select_related('autor')

    termo = request.GET.get('q', '')
    if termo:
        livros = livros.filter(titulo__icontains=termo)

    status = request.GET.get('status', '')
    if status == 'disponivel':
        livros = livros.filter(exemplar__disponivel=True).distinct()
    elif status == 'indisponivel':
        livros = livros.exclude(exemplar__disponivel=True).distinct()

    return render(request, 'acervo/lista_livros.html', {
        'livros': livros,
        'termo': termo,
        'status': status,
    })


@login_required
def novo_livro(request):
    org = org_atual(request)
    if request.method == 'POST':
        form = LivroForm(request.POST, org=org)
        if form.is_valid():
            livro = form.save(commit=False)
            livro.organizacao = org      # vem do usuário logado, nunca do form
            livro.save()
            return redirect('lista_livros')
    else:
        form = LivroForm(org=org)
    return render(request, 'acervo/form_livro.html', {'form': form})


@login_required
def editar_livro(request, pk):
    org = org_atual(request)
    livro = get_object_or_404(Livro, pk=pk, organizacao=org)
    if request.method == 'POST':
        form = LivroForm(request.POST, instance=livro, org=org)
        if form.is_valid():
            form.save()
            return redirect('lista_livros')
    else:
        form = LivroForm(instance=livro, org=org)
    return render(request, 'acervo/form_livro.html', {'form': form})


@login_required
def excluir_livro(request, pk):
    livro = get_object_or_404(Livro, pk=pk, organizacao=org_atual(request))
    if request.method == 'POST':
        livro.delete()
        return redirect('lista_livros')
    return render(request, 'acervo/confirmar_exclusao.html', {'objeto': livro})


# --------------------------------------------------------------- Autores
@login_required
def lista_autores(request):
    autores = Autor.objects.filter(organizacao=org_atual(request))
    return render(request, 'acervo/lista_autores.html', {'autores': autores})


@login_required
def novo_autor(request):
    org = org_atual(request)
    if request.method == 'POST':
        form = AutorForm(request.POST, org=org)
        if form.is_valid():
            autor = form.save(commit=False)
            autor.organizacao = org
            autor.save()
            return redirect('lista_autores')
    else:
        form = AutorForm(org=org)
    return render(request, 'acervo/form_autor.html', {'form': form})


@login_required
def editar_autor(request, pk):
    org = org_atual(request)
    autor = get_object_or_404(Autor, pk=pk, organizacao=org)
    if request.method == 'POST':
        form = AutorForm(request.POST, instance=autor, org=org)
        if form.is_valid():
            form.save()
            return redirect('lista_autores')
    else:
        form = AutorForm(instance=autor, org=org)
    return render(request, 'acervo/form_autor.html', {'form': form})


@login_required
def excluir_autor(request, pk):
    autor = get_object_or_404(Autor, pk=pk, organizacao=org_atual(request))
    if request.method == 'POST':
        autor.delete()
        return redirect('lista_autores')
    return render(request, 'acervo/confirmar_exclusao.html', {'objeto': autor})


# ------------------------------------------------------------ Exemplares
@login_required
def lista_exemplares(request):
    exemplares = (Exemplar.objects
                  .filter(organizacao=org_atual(request))
                  .select_related('livro'))
    return render(request, 'acervo/lista_exemplares.html', {'exemplares': exemplares})


@login_required
def novo_exemplar(request):
    org = org_atual(request)
    if request.method == 'POST':
        form = ExemplarForm(request.POST, org=org)
        if form.is_valid():
            exemplar = form.save(commit=False)
            exemplar.organizacao = org
            exemplar.save()
            return redirect('lista_exemplares')
    else:
        form = ExemplarForm(org=org)
    return render(request, 'acervo/form_exemplar.html', {'form': form})


@login_required
def editar_exemplar(request, pk):
    org = org_atual(request)
    exemplar = get_object_or_404(Exemplar, pk=pk, organizacao=org)
    if request.method == 'POST':
        form = ExemplarForm(request.POST, instance=exemplar, org=org)
        if form.is_valid():
            form.save()
            return redirect('lista_exemplares')
    else:
        form = ExemplarForm(instance=exemplar, org=org)
    return render(request, 'acervo/form_exemplar.html', {'form': form})


@login_required
def excluir_exemplar(request, pk):
    exemplar = get_object_or_404(Exemplar, pk=pk, organizacao=org_atual(request))
    if request.method == 'POST':
        exemplar.delete()
        return redirect('lista_exemplares')
    return render(request, 'acervo/confirmar_exclusao.html', {'objeto': exemplar})

# ------------------------------------------------------------- Dashboard
@login_required
def dashboard(request):
    org = org_atual(request)
    perfil = obter_perfil(request)

    form = PeriodoForm(request.GET)
    base = metricas_dashboard.filtrar_periodo(
        request, metricas_dashboard.emprestimos_da_org(org))
    dados = metricas_dashboard.metricas(base)

    contexto = {
        'org': org,
        'form': form,
        'kpis': dados['kpis'],
        'distribuicao': dados['distribuicao'],
        'ranking': dados['ranking'],
        # Séries e exportação: só para administradores (ver tabela da Aula 17)
        'mostra_series': perfil.eh_admin,
        'por_mes': dados['por_mes'] if perfil.eh_admin else [],
        'querystring': request.GET.urlencode(),
    }
    return render(request, 'acervo/dashboard.html', contexto)


def _celula_segura(valor):
    """O Excel interpreta células iniciadas por = + - @ como fórmula."""
    texto = '' if valor is None else str(valor)
    if texto and texto[0] in ('=', '+', '-', '@'):
        return "'" + texto
    return texto


@papel_requerido('admin')
def exportar_csv(request):
    org = org_atual(request)
    qs = metricas_dashboard.filtrar_periodo(
        request,
        metricas_dashboard.emprestimos_da_org(org)
        .select_related('usuario', 'exemplar__livro')
        .order_by('-data_emprestimo', '-pk'))

    resp = HttpResponse(content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = 'attachment; filename="emprestimos.csv"'
    resp.write('\ufeff')  # BOM: o Excel reconhece os acentos
    w = csv.writer(resp, delimiter=';')  # ';' é o separador do Excel em português
    w.writerow(['Livro', 'Leitor', 'Saída', 'Prevista', 'Devolução', 'Situação'])
    for e in qs:
        if e.data_devolucao:
            situacao = 'Devolvido com atraso' if e.atrasado else 'Devolvido'
        else:
            situacao = 'Atrasado' if e.atrasado else 'Em dia'
        w.writerow([_celula_segura(c) for c in (
            e.exemplar.livro.titulo, e.usuario.nome, e.data_emprestimo,
            e.data_prevista_devolucao, e.data_devolucao or '', situacao)])
    return resp
