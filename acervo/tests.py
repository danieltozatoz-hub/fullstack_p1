import csv
import io
from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from core.models import Perfil
from core.testing import criar_org_com_login, criar_acervo, criar_emprestimo
from django.contrib.auth.models import User
from emprestimos.models import Emprestimo
from .models import Livro, Autor, Exemplar


class IsolamentoTest(TestCase):
    """Roteiro de isolamento da Aula 14: dois usuários, duas organizações."""

    def setUp(self):
        self.org_a, self.user_a = criar_org_com_login('Biblioteca A', 'ana')
        self.org_b, self.user_b = criar_org_com_login('Biblioteca B', 'bruno')
        self.autor_a, self.livro_a, self.ex_a, _ = criar_acervo(self.org_a, 'Livro da A', 'P-1')
        self.autor_b, self.livro_b, self.ex_b, _ = criar_acervo(self.org_b, 'Livro da B', 'P-1')
        self.client.force_login(self.user_a)

    def test_lista_mostra_so_livros_da_propria_organizacao(self):
        r = self.client.get(reverse('lista_livros'))
        self.assertContains(r, 'Livro da A')
        self.assertNotContains(r, 'Livro da B')

    def test_trocar_o_id_na_url_da_404(self):
        for nome in ('editar_livro', 'excluir_livro'):
            r = self.client.get(reverse(nome, args=[self.livro_b.pk]))
            self.assertEqual(r.status_code, 404, nome)
        r = self.client.post(reverse('excluir_livro', args=[self.livro_b.pk]))
        self.assertEqual(r.status_code, 404)
        self.assertTrue(Livro.objects.filter(pk=self.livro_b.pk).exists())

    def test_livro_criado_fica_na_organizacao_do_usuario_logado(self):
        # Mesmo que o cliente tente mandar outra organização no POST, ela é ignorada.
        self.client.post(reverse('novo_livro'), {
            'titulo': 'Novo', 'autor': self.autor_a.pk, 'ano': 2000,
            'organizacao': self.org_b.pk,
        })
        self.assertEqual(Livro.objects.get(titulo='Novo').organizacao, self.org_a)

    def test_select_de_autor_mostra_so_opcoes_da_propria_organizacao(self):
        r = self.client.get(reverse('novo_livro'))
        autores = list(r.context['form'].fields['autor'].queryset)
        self.assertEqual(autores, [self.autor_a])

    def test_nao_aceita_autor_de_outra_organizacao_no_post(self):
        r = self.client.post(reverse('novo_livro'), {
            'titulo': 'Invasor', 'autor': self.autor_b.pk, 'ano': 2000})
        self.assertEqual(r.status_code, 200)  # volta ao form com erro
        self.assertFalse(Livro.objects.filter(titulo='Invasor').exists())

    def test_mesmo_patrimonio_em_organizacoes_diferentes_e_permitido(self):
        # P-1 já existe na B; cadastrar P-1 na A (segundo livro) é permitido
        livro2 = Livro.objects.create(
            organizacao=self.org_a, titulo='Outro', autor=self.autor_a, ano=2001)
        r = self.client.post(reverse('novo_exemplar'), {
            'livro': livro2.pk, 'codigo_patrimonio': 'P-2'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Exemplar.objects.filter(codigo_patrimonio='P-2').count(), 1)
        # e o P-1 repetido NA MESMA organização é recusado (erro de form, não 500)
        r = self.client.post(reverse('novo_exemplar'), {
            'livro': livro2.pk, 'codigo_patrimonio': 'P-1'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Exemplar.objects.filter(organizacao=self.org_a, codigo_patrimonio='P-1').count(), 1)

    def test_usuario_sem_perfil_recebe_403(self):
        sem_perfil = User.objects.create_user('semperfil', password='x')
        self.client.force_login(sem_perfil)
        self.assertEqual(self.client.get(reverse('lista_livros')).status_code, 403)
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 403)

    def test_anonimo_vai_para_o_login(self):
        self.client.logout()
        r = self.client.get(reverse('lista_livros'))
        self.assertEqual(r.status_code, 302)
        self.assertIn('/login/', r['Location'])


class DashboardTest(TestCase):
    """Se o número está errado, o dashboard mente. Dados fáceis de conferir à mão."""

    def setUp(self):
        self.org_a, self.user_a = criar_org_com_login('Org A', 'ana')
        self.org_b, self.user_b = criar_org_com_login('Org B', 'bruno')
        _, self.livro_a, self.ex_a, self.leitor_a = criar_acervo(self.org_a, 'Livro A', 'A-1')
        _, self.livro_b, self.ex_b, self.leitor_b = criar_acervo(self.org_b, 'Livro B', 'B-1')
        hoje = date.today()
        # Org A: 3 empréstimos
        criar_emprestimo(self.org_a, self.leitor_a, self.ex_a, saida=date(2026, 1, 10))   # aberto e atrasado
        criar_emprestimo(self.org_a, self.leitor_a, self.ex_a, saida=date(2026, 2, 10),
                         devolucao=date(2026, 2, 12))                                     # devolvido no prazo
        criar_emprestimo(self.org_a, self.leitor_a, self.ex_a, saida=hoje)                # aberto, em dia
        # Org B: 5 empréstimos
        for _ in range(5):
            criar_emprestimo(self.org_b, self.leitor_b, self.ex_b, saida=hoje)

    def _get(self, user, **params):
        self.client.force_login(user)
        return self.client.get(reverse('dashboard'), params)

    def test_total_da_organizacao(self):
        self.assertEqual(self._get(self.user_a).context['kpis']['total'], 3)
        self.assertEqual(self._get(self.user_b).context['kpis']['total'], 5)

    def test_kpis_e_distribuicao_conferem_com_o_cenario(self):
        k = self._get(self.user_a).context['kpis']
        self.assertEqual((k['abertos'], k['atrasados'], k['leitores']), (2, 1, 1))
        dist = {d['situacao']: d['total'] for d in self._get(self.user_a).context['distribuicao']}
        self.assertEqual(dist['Atrasado (em aberto)'], 1)
        self.assertEqual(dist['Devolvido no prazo'], 1)
        self.assertEqual(dist['Em dia (em aberto)'], 1)
        self.assertEqual(sum(dist.values()), 3)  # as fatias somam o total

    def test_periodo_filtra_todas_as_metricas(self):
        r = self._get(self.user_a, inicio='2026-02-01', fim='2026-02-28')
        self.assertEqual(r.context['kpis']['total'], 1)
        self.assertEqual(r.context['por_mes'], [{'mes': '02/2026', 'total': 1}])
        self.assertEqual(r.context['ranking'], [{'titulo': 'Livro A', 'total': 1}])

    def test_serie_por_mes_vem_em_ordem(self):
        meses = [m['mes'] for m in self._get(self.user_a).context['por_mes']]
        self.assertEqual(meses[:2], ['01/2026', '02/2026'])

    def test_ranking_ordenado_e_so_da_organizacao(self):
        r = self._get(self.user_a).context['ranking']
        self.assertEqual(r, [{'titulo': 'Livro A', 'total': 3}])

    def test_data_invalida_na_url_nao_gera_erro_500(self):
        r = self._get(self.user_a, inicio='abc')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['kpis']['total'], 3)  # filtro ignorado
        self.assertTrue(r.context['form'].errors)

    def test_inicio_depois_do_fim_e_recusado(self):
        r = self._get(self.user_a, inicio='2026-03-01', fim='2026-02-01')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context['form'].errors)

    def test_dashboard_vazio_funciona(self):
        _, vazio = criar_org_com_login('Org vazia', 'vazio')
        r = self._get(vazio)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['kpis']['total'], 0)
        self.assertEqual(list(r.context['ranking']), [])
        self.assertContains(r, 'Sem dados no período')

    def test_operador_nao_ve_serie_nem_exporta(self):
        op = User.objects.create_user('op', password='x')
        Perfil.objects.create(usuario=op, organizacao=self.org_a, papel=Perfil.OPERADOR)
        r = self._get(op)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.context['mostra_series'])
        self.assertEqual(r.context['por_mes'], [])
        self.assertNotContains(r, 'Exportar CSV')
        self.assertEqual(self.client.get(reverse('exportar_csv')).status_code, 403)

    def test_exportar_csv_do_admin_respeita_organizacao_e_periodo(self):
        self.client.force_login(self.user_a)
        r = self.client.get(reverse('exportar_csv'), {'inicio': '2026-02-01', 'fim': '2026-02-28'})
        self.assertEqual(r.status_code, 200)
        self.assertIn('attachment', r['Content-Disposition'])
        linhas = list(csv.reader(io.StringIO(r.content.decode('utf-8-sig')), delimiter=';'))
        self.assertEqual(linhas[0][:3], ['Livro', 'Leitor', 'Saída'])
        self.assertEqual(len(linhas), 2)           # cabeçalho + 1 empréstimo de fevereiro
        self.assertEqual(linhas[1][0], 'Livro A')  # nunca o livro da org B

    def test_csv_neutraliza_formula_do_excel(self):
        self.leitor_a.nome = '=CMD()'
        self.leitor_a.save()
        self.client.force_login(self.user_a)
        r = self.client.get(reverse('exportar_csv'))
        self.assertIn("'=CMD()", r.content.decode('utf-8-sig'))


class ConsultasTest(TestCase):
    """Trava o desempenho: se o N+1 voltar, estes testes falham."""

    def setUp(self):
        self.org, self.user = criar_org_com_login('Org', 'ana')
        _, self.livro, self.ex, self.leitor = criar_acervo(self.org)
        self.client.force_login(self.user)

    def _queries(self, nome_url):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext
        with CaptureQueriesContext(connection) as ctx:
            self.assertEqual(self.client.get(reverse(nome_url)).status_code, 200)
        return len(ctx)

    def test_listagens_nao_crescem_com_o_numero_de_registros(self):
        for nome in ('lista_emprestimos', 'lista_exemplares', 'lista_livros', 'lista_reservas', 'dashboard'):
            criar_emprestimo(self.org, self.leitor, self.ex)
            antes = self._queries(nome)
            for _ in range(10):
                criar_emprestimo(self.org, self.leitor, self.ex)
            self.assertEqual(self._queries(nome), antes, f'{nome} tem N+1')

    def test_dashboard_faz_um_numero_fixo_de_consultas(self):
        criar_emprestimo(self.org, self.leitor, self.ex)
        # sessão + usuário + perfil/organização + KPIs/distribuição + ranking + série
        with self.assertNumQueries(6):
            self.client.get(reverse('dashboard'))
