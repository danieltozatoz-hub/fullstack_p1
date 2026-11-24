"""Cria dados de demonstração: duas bibliotecas, cada uma com seu admin.

    python manage.py popular_demo

Logins (senha "demo1234"): ana (admin da Biblioteca Central),
bruno (admin da Biblioteca do Bairro) e carla (operadora da Central).
"""
import random
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from acervo.models import Autor, Livro, Exemplar
from core.models import Organizacao, Perfil
from emprestimos.models import Emprestimo
from usuarios.models import Usuario

OBRAS = [
    ('Dom Casmurro', 'Machado de Assis', 1899),
    ('Memórias Póstumas de Brás Cubas', 'Machado de Assis', 1881),
    ('O Guarani', 'José de Alencar', 1857),
    ('O Cortiço', 'Aluísio Azevedo', 1890),
    ('Vidas Secas', 'Graciliano Ramos', 1938),
    ('Senhora', 'José de Alencar', 1875),
]
LEITORES = ['Marina', 'Paulo', 'Joana', 'Carlos', 'Beatriz', 'Rafael', 'Lúcia', 'Tiago']


class Command(BaseCommand):
    help = 'Cria duas organizações com acervo, leitores e empréstimos de exemplo.'

    @transaction.atomic
    def handle(self, *args, **opts):
        rnd = random.Random(42)  # sempre os mesmos dados
        hoje = date.today()
        self._org('Biblioteca Central', 'ana', 'carla', rnd, hoje, volume=60)
        self._org('Biblioteca do Bairro', 'bruno', None, rnd, hoje, volume=25)
        self.stdout.write(self.style.SUCCESS(
            'Pronto! Logins (senha demo1234): ana, bruno (administradores) e carla (operadora).'))

    def _org(self, nome, admin, operador, rnd, hoje, volume):
        org, criada = Organizacao.objects.get_or_create(nome=nome)
        if not criada:
            self.stdout.write(f'{nome}: já existe, pulando.')
            return
        for username, papel in ((admin, Perfil.ADMIN), (operador, Perfil.OPERADOR)):
            if username:
                user, _ = User.objects.get_or_create(username=username)
                user.set_password('demo1234')
                user.save()
                Perfil.objects.update_or_create(
                    usuario=user, defaults={'organizacao': org, 'papel': papel})

        autores = {}
        exemplares = []
        for titulo, autor, ano in OBRAS:
            a = autores.setdefault(autor, Autor.objects.create(organizacao=org, nome=autor))
            livro = Livro.objects.create(organizacao=org, titulo=titulo, autor=a, ano=ano)
            for i in (1, 2):
                exemplares.append(Exemplar.objects.create(
                    organizacao=org, livro=livro, codigo_patrimonio=f'{livro.pk:03d}-{i}'))
        leitores = [
            Usuario.objects.create(
                organizacao=org, nome=n, email=f'{n.lower()}@{org.pk}.exemplo.com')
            for n in LEITORES]

        for _ in range(volume):
            saida = hoje - timedelta(days=rnd.randint(0, 180))
            prevista = saida + timedelta(days=7)
            ex = rnd.choice(exemplares)
            # empréstimos antigos já foram devolvidos; os recentes, metade ainda está em aberto
            devolvido = saida < hoje - timedelta(days=25) or rnd.random() < 0.5
            devolucao = min(hoje, saida + timedelta(days=rnd.randint(2, 14))) if devolvido else None
            emp = Emprestimo.objects.create(
                organizacao=org, usuario=rnd.choice(leitores), exemplar=ex,
                data_prevista_devolucao=prevista, data_devolucao=devolucao)
            Emprestimo.objects.filter(pk=emp.pk).update(data_emprestimo=saida)
        # exemplares com empréstimo em aberto ficam indisponíveis
        abertos = Emprestimo.objects.filter(organizacao=org, data_devolucao__isnull=True)
        Exemplar.objects.filter(pk__in=abertos.values('exemplar')).update(disponivel=False)
        self.stdout.write(f'{nome}: {volume} empréstimos criados.')
