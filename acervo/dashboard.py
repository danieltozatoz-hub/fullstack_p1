"""Métricas do dashboard (Aula 17).

Perguntas que o dono da biblioteca faz toda semana, uma para cada tipo de métrica:

1. KPI           -> Quantos empréstimos temos, quantos estão em aberto e quantos atrasaram?
2. Ranking       -> Quais livros mais saem?
3. Série         -> Como os empréstimos evoluem mês a mês?
4. Distribuição  -> Qual a situação dos empréstimos (em dia, atrasados, devolvidos)?

TODA métrica parte de `emprestimos_da_org(org)`: assim o isolamento entre
organizações e o filtro de período valem para todos os cartões e gráficos.
"""
from datetime import date

from django.db.models import Count, F, Q
from django.db.models.functions import TruncMonth

from emprestimos.models import Emprestimo
from .forms import PeriodoForm


def emprestimos_da_org(org):
    """Primeira linha de toda métrica: só dados da organização."""
    return Emprestimo.objects.filter(organizacao=org)


def filtrar_periodo(request, qs):
    """Aplica ?inicio=AAAA-MM-DD&fim=AAAA-MM-DD (validado) à data do empréstimo."""
    form = PeriodoForm(request.GET)
    if form.is_valid():
        if form.cleaned_data['inicio']:
            qs = qs.filter(data_emprestimo__gte=form.cleaned_data['inicio'])
        if form.cleaned_data['fim']:
            qs = qs.filter(data_emprestimo__lte=form.cleaned_data['fim'])
    return qs


def kpis_e_distribuicao(base, hoje=None):
    """KPIs (aggregate) e distribuição por situação, em UMA consulta."""
    hoje = hoje or date.today()
    aberto = Q(data_devolucao__isnull=True)
    devolvido = Q(data_devolucao__isnull=False)
    # Mesma regra de Emprestimo.atrasado: devolvido depois do prazo,
    # ou ainda aberto e já passou do prazo.
    ag = base.aggregate(
        total=Count('id'),
        leitores=Count('usuario', distinct=True),
        abertos=Count('id', filter=aberto),
        atrasados=Count('id', filter=aberto & Q(data_prevista_devolucao__lt=hoje)),
        em_dia=Count('id', filter=aberto & Q(data_prevista_devolucao__gte=hoje)),
        devolvidos_no_prazo=Count(
            'id', filter=devolvido & Q(data_devolucao__lte=F('data_prevista_devolucao'))),
        devolvidos_com_atraso=Count(
            'id', filter=devolvido & Q(data_devolucao__gt=F('data_prevista_devolucao'))),
    )
    kpis = {chave: ag[chave] for chave in ('total', 'leitores', 'abertos', 'atrasados')}
    distribuicao = [
        {'situacao': 'Em dia (em aberto)', 'total': ag['em_dia']},
        {'situacao': 'Atrasado (em aberto)', 'total': ag['atrasados']},
        {'situacao': 'Devolvido no prazo', 'total': ag['devolvidos_no_prazo']},
        {'situacao': 'Devolvido com atraso', 'total': ag['devolvidos_com_atraso']},
    ]
    return kpis, distribuicao


def ranking_livros(base, limite=5):
    """Os top-N livros mais emprestados: values() agrupa, annotate() conta."""
    qs = (
        base.values('exemplar__livro', titulo=F('exemplar__livro__titulo'))
        .annotate(total=Count('id'))
        .order_by('-total', 'titulo')[:limite]
    )
    return [{'titulo': r['titulo'], 'total': r['total']} for r in qs]


def emprestimos_por_mes(base):
    """Série no tempo. O order_by final evita meses embaralhados no gráfico."""
    qs = (
        base.annotate(mes=TruncMonth('data_emprestimo'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
    return [{'mes': r['mes'].strftime('%m/%Y'), 'total': r['total']} for r in qs]


def metricas(base):
    """Reúne tudo; usado pela tela do dashboard e pela API (sem duplicar consultas)."""
    kpis, distribuicao = kpis_e_distribuicao(base)
    return {
        'kpis': kpis,
        'distribuicao': distribuicao,
        'ranking': ranking_livros(base),
        'por_mes': emprestimos_por_mes(base),
    }
