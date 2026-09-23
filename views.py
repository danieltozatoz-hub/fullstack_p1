from django.shortcuts import render, redirect, get_object_or_404
from .models import Livro, Autor, Exemplar
from .forms import LivroForm, AutorForm, ExemplarForm

def lista_livros(request):
    livros = Livro.objects.all()

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

def novo_livro(request):
    if request.method == 'POST':
        form = LivroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_livros')
    else:
        form = LivroForm()
    return render(request, 'acervo/form_livro.html', {'form': form})

def editar_livro(request, pk):
    livro = get_object_or_404(Livro, pk=pk)
    if request.method == 'POST':
        form = LivroForm(request.POST, instance=livro)
        if form.is_valid():
            form.save()
            return redirect('lista_livros')
    else:
        form = LivroForm(instance=livro)
    return render(request, 'acervo/form_livro.html', {'form': form})

def excluir_livro(request, pk):
    livro = get_object_or_404(Livro, pk=pk)
    if request.method == 'POST':
        livro.delete()
        return redirect('lista_livros')
    return render(request, 'acervo/confirmar_exclusao.html', {'objeto': livro})


def lista_autores(request):
    autores = Autor.objects.all()
    return render(request, 'acervo/lista_autores.html', {'autores': autores})

def novo_autor(request):
    if request.method == 'POST':
        form = AutorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_autores')
    else:
        form = AutorForm()
    return render(request, 'acervo/form_autor.html', {'form': form})

def editar_autor(request, pk):
    autor = get_object_or_404(Autor, pk=pk)
    if request.method == 'POST':
        form = AutorForm(request.POST, instance=autor)
        if form.is_valid():
            form.save()
            return redirect('lista_autores')
    else:
        form = AutorForm(instance=autor)
    return render(request, 'acervo/form_autor.html', {'form': form})

def excluir_autor(request, pk):
    autor = get_object_or_404(Autor, pk=pk)
    if request.method == 'POST':
        autor.delete()
        return redirect('lista_autores')
    return render(request, 'acervo/confirmar_exclusao.html', {'objeto': autor})


def lista_exemplares(request):
    exemplares = Exemplar.objects.all()
    return render(request, 'acervo/lista_exemplares.html', {'exemplares': exemplares})

def novo_exemplar(request):
    if request.method == 'POST':
        form = ExemplarForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_exemplares')
    else:
        form = ExemplarForm()
    return render(request, 'acervo/form_exemplar.html', {'form': form})

def editar_exemplar(request, pk):
    exemplar = get_object_or_404(Exemplar, pk=pk)
    if request.method == 'POST':
        form = ExemplarForm(request.POST, instance=exemplar)
        if form.is_valid():
            form.save()
            return redirect('lista_exemplares')
    else:
        form = ExemplarForm(instance=exemplar)
    return render(request, 'acervo/form_exemplar.html', {'form': form})

def excluir_exemplar(request, pk):
    exemplar = get_object_or_404(Exemplar, pk=pk)
    if request.method == 'POST':
        exemplar.delete()
        return redirect('lista_exemplares')
    return render(request, 'acervo/confirmar_exclusao.html', {'objeto': exemplar})