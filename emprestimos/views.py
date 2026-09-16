from django.shortcuts import render, redirect, get_object_or_404
from datetime import date, timedelta
from .models import Emprestimo, Reserva
from .forms import EmprestimoForm, ReservaForm

PRAZO_DIAS = 7

def lista_emprestimos(request):
    emprestimos = Emprestimo.objects.all()
    return render(request, 'emprestimos/lista_emprestimos.html', {'emprestimos': emprestimos})

def novo_emprestimo(request):
    if request.method == 'POST':
        form = EmprestimoForm(request.POST)
        if form.is_valid():
            emprestimo = form.save(commit=False)  # ainda não salva no banco
            emprestimo.data_prevista_devolucao = date.today() + timedelta(days=PRAZO_DIAS)
            emprestimo.save()  # agora sim salva, já com a data calculada

            exemplar = emprestimo.exemplar
            exemplar.disponivel = False
            exemplar.save()

            return redirect('lista_emprestimos')
    else:
        form = EmprestimoForm()
    return render(request, 'emprestimos/form_emprestimo.html', {'form': form})

def devolver_emprestimo(request, pk):
    emprestimo = get_object_or_404(Emprestimo, pk=pk)
    if request.method == 'POST':
        emprestimo.data_devolucao = date.today()
        emprestimo.save()

        exemplar = emprestimo.exemplar
        exemplar.disponivel = True
        exemplar.save()

        return redirect('lista_emprestimos')
    return render(request, 'emprestimos/confirmar_devolucao.html', {'emprestimo': emprestimo})

def excluir_emprestimo(request, pk):
    emprestimo = get_object_or_404(Emprestimo, pk=pk)
    if request.method == 'POST':
        emprestimo.delete()
        return redirect('lista_emprestimos')
    return render(request, 'emprestimos/confirmar_exclusao.html', {'objeto': emprestimo})


def lista_reservas(request):
    reservas = Reserva.objects.filter(ativa=True)  # já vem ordenada (Meta.ordering)
    return render(request, 'emprestimos/lista_reservas.html', {'reservas': reservas})

def nova_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_reservas')
    else:
        form = ReservaForm()
    return render(request, 'emprestimos/form_reserva.html', {'form': form})

def cancelar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        reserva.ativa = False
        reserva.save()
        return redirect('lista_reservas')
    return render(request, 'emprestimos/confirmar_cancelamento.html', {'reserva': reserva})