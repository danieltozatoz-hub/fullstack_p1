from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from core.tenant import org_atual
from .models import Usuario
from .forms import UsuarioForm


@login_required
def lista_usuarios(request):
    usuarios = Usuario.objects.filter(organizacao=org_atual(request))
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})


@login_required
def novo_usuario(request):
    org = org_atual(request)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, org=org)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.organizacao = org
            usuario.save()
            return redirect('lista_usuarios')
    else:
        form = UsuarioForm(org=org)
    return render(request, 'usuarios/form_usuario.html', {'form': form})


@login_required
def editar_usuario(request, pk):
    org = org_atual(request)
    usuario = get_object_or_404(Usuario, pk=pk, organizacao=org)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario, org=org)
        if form.is_valid():
            form.save()
            return redirect('lista_usuarios')
    else:
        form = UsuarioForm(instance=usuario, org=org)
    return render(request, 'usuarios/form_usuario.html', {'form': form})


@login_required
def excluir_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk, organizacao=org_atual(request))
    if request.method == 'POST':
        usuario.delete()
        return redirect('lista_usuarios')
    return render(request, 'usuarios/confirmar_exclusao.html', {'objeto': usuario})
