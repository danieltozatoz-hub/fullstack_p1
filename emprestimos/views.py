from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from core.tenant import org_atual
from .models import Emprestimo, Reserva
from .forms import EmprestimoForm, ReservaForm
from .services import registrar_emprestimo, registrar_devolucao


# ----------------------------------------------------------- Empréstimos
@login_required
def lista_emprestimos(request):
    # select_related: a tela mostra usuário, exemplar e o título do livro de
    # cada linha. Sem ele seriam 1 + 2N consultas (problema N+1).
    emprestimos = (Emprestimo.objects
                   .filter(organizacao=org_atual(request))
                   .select_related('usuario', 'exemplar__livro')
                   .order_by('-data_emprestimo', '-pk'))
    return render(request, 'emprestimos/lista_emprestimos.html', {'emprestimos': emprestimos})


@login_required
def novo_emprestimo(request):
    org = org_atual(request)
    if request.method == 'POST':
        form = EmprestimoForm(request.POST, org=org)
        if form.is_valid():
            emprestimo = form.save(commit=False)  # ainda não salva no banco
            emprestimo.organizacao = org
            registrar_emprestimo(emprestimo)      # prazo + exemplar indisponível
            return redirect('lista_emprestimos')
    else:
        form = EmprestimoForm(org=org)
    return render(request, 'emprestimos/form_emprestimo.html', {'form': form})


@login_required
def devolver_emprestimo(request, pk):
    emprestimo = get_object_or_404(
        Emprestimo.objects.select_related('usuario', 'exemplar__livro'),
        pk=pk, organizacao=org_atual(request))
    if emprestimo.data_devolucao:
        return redirect('lista_emprestimos')  # já devolvido
    if request.method == 'POST':
        registrar_devolucao(emprestimo)
        return redirect('lista_emprestimos')
    return render(request, 'emprestimos/confirmar_devolucao.html', {'emprestimo': emprestimo})


@login_required
def excluir_emprestimo(request, pk):
    emprestimo = get_object_or_404(
        Emprestimo.objects.select_related('usuario', 'exemplar__livro'),
        pk=pk, organizacao=org_atual(request))
    if request.method == 'POST':
        emprestimo.delete()
        return redirect('lista_emprestimos')
    return render(request, 'emprestimos/confirmar_exclusao.html', {'objeto': emprestimo})


# -------------------------------------------------------------- Reservas
@login_required
def lista_reservas(request):
    reservas = (Reserva.objects
                .filter(organizacao=org_atual(request), ativa=True)  # já vem ordenada (Meta.ordering)
                .select_related('usuario', 'livro'))
    return render(request, 'emprestimos/lista_reservas.html', {'reservas': reservas})


@login_required
def nova_reserva(request):
    org = org_atual(request)
    if request.method == 'POST':
        form = ReservaForm(request.POST, org=org)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.organizacao = org
            reserva.save()
            return redirect('lista_reservas')
    else:
        form = ReservaForm(org=org)
    return render(request, 'emprestimos/form_reserva.html', {'form': form})


@login_required
def cancelar_reserva(request, pk):
    reserva = get_object_or_404(
        Reserva.objects.select_related('usuario', 'livro'),
        pk=pk, organizacao=org_atual(request))
    if request.method == 'POST':
        reserva.ativa = False
        reserva.save()
        return redirect('lista_reservas')
    return render(request, 'emprestimos/confirmar_cancelamento.html', {'reserva': reserva})
