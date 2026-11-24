from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from acervo.models import Autor, Livro, Exemplar
from core.models import Perfil
from core.testing import criar_org_com_login, criar_acervo, criar_emprestimo
from django.contrib.auth.models import User
from usuarios.models import Usuario
from .models import Emprestimo, Reserva
from .services import PRAZO_DIAS, registrar_emprestimo, registrar_devolucao


class ServicosTest(TestCase):
    def setUp(self):
        self.org, _ = criar_org_com_login('Org', 'ana')
        _, self.livro, self.ex, self.leitor = criar_acervo(self.org)

    def test_emprestimo_calcula_prazo_e_bloqueia_exemplar(self):
        emp = registrar_emprestimo(Emprestimo(
            organizacao=self.org, usuario=self.leitor, exemplar=self.ex))
        self.ex.refresh_from_db()
        self.assertEqual(emp.data_prevista_devolucao, date.today() + timedelta(days=PRAZO_DIAS))
        self.assertFalse(self.ex.disponivel)

    def test_devolucao_libera_exemplar_e_nao_repete(self):
        emp = registrar_emprestimo(Emprestimo(
            organizacao=self.org, usuario=self.leitor, exemplar=self.ex))
        registrar_devolucao(emp)
        self.ex.refresh_from_db()
        self.assertTrue(self.ex.disponivel)
        with self.assertRaises(ValueError):
            registrar_devolucao(emp)

    def test_multa_de_5_reais_por_dia_de_atraso(self):
        emp = criar_emprestimo(self.org, self.leitor, self.ex,
                               saida=date.today() - timedelta(days=10), prazo_dias=7)
        self.assertTrue(emp.atrasado)
        self.assertEqual(emp.valor_multa, 15.0)  # 3 dias de atraso


class TelasEmprestimoTest(TestCase):
    def setUp(self):
        self.org_a, self.user_a = criar_org_com_login('A', 'ana')
        self.org_b, _ = criar_org_com_login('B', 'bruno')
        _, _, self.ex_a, self.leitor_a = criar_acervo(self.org_a, codigo='A-1')
        _, _, self.ex_b, self.leitor_b = criar_acervo(self.org_b, codigo='B-1')
        self.client.force_login(self.user_a)

    def test_fluxo_emprestar_e_devolver(self):
        r = self.client.post(reverse('novo_emprestimo'), {
            'usuario': self.leitor_a.pk, 'exemplar': self.ex_a.pk})
        self.assertEqual(r.status_code, 302)
        emp = Emprestimo.objects.get()
        self.assertEqual(emp.organizacao, self.org_a)
        self.ex_a.refresh_from_db()
        self.assertFalse(self.ex_a.disponivel)

        self.client.post(reverse('devolver_emprestimo', args=[emp.pk]))
        emp.refresh_from_db(); self.ex_a.refresh_from_db()
        self.assertEqual(emp.data_devolucao, date.today())
        self.assertTrue(self.ex_a.disponivel)

    def test_nao_empresta_exemplar_nem_leitor_de_outra_organizacao(self):
        r = self.client.post(reverse('novo_emprestimo'), {
            'usuario': self.leitor_a.pk, 'exemplar': self.ex_b.pk})
        self.assertEqual(r.status_code, 200)
        r = self.client.post(reverse('novo_emprestimo'), {
            'usuario': self.leitor_b.pk, 'exemplar': self.ex_a.pk})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Emprestimo.objects.count(), 0)

    def test_exemplar_indisponivel_nao_aparece_para_emprestar(self):
        registrar_emprestimo(Emprestimo(organizacao=self.org_a, usuario=self.leitor_a, exemplar=self.ex_a))
        r = self.client.get(reverse('novo_emprestimo'))
        self.assertEqual(list(r.context['form'].fields['exemplar'].queryset), [])

    def test_devolver_ou_excluir_emprestimo_de_outra_org_da_404(self):
        emp_b = criar_emprestimo(self.org_b, self.leitor_b, self.ex_b)
        self.assertEqual(self.client.get(reverse('devolver_emprestimo', args=[emp_b.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('excluir_emprestimo', args=[emp_b.pk])).status_code, 404)

    def test_cancelar_reserva_de_outra_org_da_404(self):
        livro_b = self.ex_b.livro
        res_b = Reserva.objects.create(organizacao=self.org_b, usuario=self.leitor_b, livro=livro_b)
        self.assertEqual(self.client.post(reverse('cancelar_reserva', args=[res_b.pk])).status_code, 404)
        res_b.refresh_from_db()
        self.assertTrue(res_b.ativa)


class ApiTest(APITestCase):
    """API REST (Aula 13) com isolamento (Aula 14)."""

    def setUp(self):
        self.org_a, self.user_a = criar_org_com_login('A', 'ana')
        self.org_b, self.user_b = criar_org_com_login('B', 'bruno')
        self.autor_a, self.livro_a, self.ex_a, self.leitor_a = criar_acervo(self.org_a, 'Livro A', 'A-1')
        self.autor_b, self.livro_b, self.ex_b, self.leitor_b = criar_acervo(self.org_b, 'Livro B', 'A-1')
        self.client.force_authenticate(self.user_a)

    # --- autenticação
    def test_api_exige_login(self):
        self.client.force_authenticate(None)
        for rota in ('/api/livros/', '/api/emprestimos/', '/api/dashboard/'):
            self.assertIn(self.client.get(rota).status_code, (401, 403), rota)
        self.assertIn(self.client.post('/api/livros/', {}).status_code, (401, 403))

    def test_usuario_sem_perfil_recebe_403(self):
        self.client.force_authenticate(User.objects.create_user('semperfil', password='x'))
        self.assertEqual(self.client.get('/api/livros/').status_code, 403)

    # --- isolamento
    def test_lista_so_da_propria_organizacao(self):
        r = self.client.get('/api/livros/')
        self.assertEqual([l['titulo'] for l in r.data], ['Livro A'])

    def test_registro_de_outra_org_da_404_em_todos_os_verbos(self):
        url = f'/api/livros/{self.livro_b.pk}/'
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.patch(url, {'titulo': 'x'}).status_code, 404)
        self.assertEqual(self.client.delete(url).status_code, 404)
        self.livro_b.refresh_from_db()
        self.assertEqual(self.livro_b.titulo, 'Livro B')

    def test_nao_vincula_registro_de_outra_organizacao(self):
        r = self.client.post('/api/livros/', {'titulo': 'X', 'autor': self.autor_b.pk, 'ano': 2000})
        self.assertEqual(r.status_code, 400)
        self.assertIn('autor', r.data)
        r = self.client.post('/api/emprestimos/', {'usuario': self.leitor_b.pk, 'exemplar': self.ex_a.pk})
        self.assertEqual(r.status_code, 400)

    def test_criar_grava_na_organizacao_do_usuario_e_ignora_organizacao_do_corpo(self):
        r = self.client.post('/api/livros/', {
            'titulo': 'Novo', 'autor': self.autor_a.pk, 'ano': 2001, 'organizacao': self.org_b.pk},
            format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Livro.objects.get(pk=r.data['id']).organizacao, self.org_a)
        self.assertNotIn('organizacao', r.data)

    # --- validação (400 em JSON)
    def test_ano_futuro_e_recusado(self):
        r = self.client.post('/api/livros/', {
            'titulo': 'Futuro', 'autor': self.autor_a.pk, 'ano': date.today().year + 1})
        self.assertEqual(r.status_code, 400)
        self.assertIn('ano', r.data)

    def test_unicidade_e_por_organizacao(self):
        # 'A-1' já existe na org B e na A (setUp): na A, repetir é 400
        r = self.client.post('/api/exemplares/', {'livro': self.livro_a.pk, 'codigo_patrimonio': 'A-1'})
        self.assertEqual(r.status_code, 400)
        r = self.client.post('/api/exemplares/', {'livro': self.livro_a.pk, 'codigo_patrimonio': 'A-2'})
        self.assertEqual(r.status_code, 201)

    def test_email_de_leitor_unico_por_organizacao(self):
        r = self.client.post('/api/usuarios/', {'nome': 'Dup', 'email': self.leitor_a.email})
        self.assertEqual(r.status_code, 400)
        r = self.client.post('/api/usuarios/', {'nome': 'Outro', 'email': self.leitor_b.email})
        self.assertEqual(r.status_code, 201)  # o mesmo e-mail na outra org é permitido

    # --- CRUD
    def test_crud_completo_de_autor(self):
        r = self.client.post('/api/autores/', {'nome': 'Clarice'})
        self.assertEqual(r.status_code, 201)
        pk = r.data['id']
        self.assertEqual(self.client.patch(f'/api/autores/{pk}/', {'nome': 'Clarice L.'}).data['nome'], 'Clarice L.')
        self.assertEqual(self.client.delete(f'/api/autores/{pk}/').status_code, 204)
        self.assertEqual(self.client.get(f'/api/autores/{pk}/').status_code, 404)

    def test_excluir_autor_com_livros_da_409_e_nao_500(self):
        r = self.client.delete(f'/api/autores/{self.autor_a.pk}/')
        self.assertEqual(r.status_code, 409)

    # --- empréstimos
    def test_emprestimo_pela_api_aplica_as_mesmas_regras_das_telas(self):
        r = self.client.post('/api/emprestimos/', {'usuario': self.leitor_a.pk, 'exemplar': self.ex_a.pk})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['data_prevista_devolucao'],
                         str(date.today() + timedelta(days=PRAZO_DIAS)))
        self.ex_a.refresh_from_db()
        self.assertFalse(self.ex_a.disponivel)
        # o mesmo exemplar não pode ser emprestado de novo
        r2 = self.client.post('/api/emprestimos/', {'usuario': self.leitor_a.pk, 'exemplar': self.ex_a.pk})
        self.assertEqual(r2.status_code, 400)

    def test_cliente_nao_consegue_forcar_prazo_ou_devolucao(self):
        r = self.client.post('/api/emprestimos/', {
            'usuario': self.leitor_a.pk, 'exemplar': self.ex_a.pk,
            'data_prevista_devolucao': '2099-01-01', 'data_devolucao': '2026-01-01'}, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertIsNone(r.data['data_devolucao'])
        self.assertNotEqual(r.data['data_prevista_devolucao'], '2099-01-01')

    def test_devolver_pela_api(self):
        pk = self.client.post('/api/emprestimos/', {
            'usuario': self.leitor_a.pk, 'exemplar': self.ex_a.pk}).data['id']
        r = self.client.post(f'/api/emprestimos/{pk}/devolver/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['data_devolucao'], str(date.today()))
        self.ex_a.refresh_from_db()
        self.assertTrue(self.ex_a.disponivel)
        self.assertEqual(self.client.post(f'/api/emprestimos/{pk}/devolver/').status_code, 400)

    def test_nao_ha_put_em_emprestimo(self):
        emp = criar_emprestimo(self.org_a, self.leitor_a, self.ex_a)
        self.assertEqual(self.client.put(f'/api/emprestimos/{emp.pk}/', {}).status_code, 405)

    def test_cancelar_reserva_pela_api(self):
        pk = self.client.post('/api/reservas/', {'usuario': self.leitor_a.pk, 'livro': self.livro_a.pk}).data['id']
        self.assertEqual(len(self.client.get('/api/reservas/?ativa=true').data), 1)
        self.client.post(f'/api/reservas/{pk}/cancelar/')
        self.assertEqual(len(self.client.get('/api/reservas/?ativa=true').data), 0)

    # --- dashboard
    def test_api_do_dashboard_tem_os_mesmos_numeros_da_tela(self):
        criar_emprestimo(self.org_a, self.leitor_a, self.ex_a)
        criar_emprestimo(self.org_b, self.leitor_b, self.ex_b)
        criar_emprestimo(self.org_b, self.leitor_b, self.ex_b)
        r = self.client.get('/api/dashboard/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['kpis']['total'], 1)
        self.assertEqual(r.data['ranking'], [{'titulo': 'Livro A', 'total': 1}])
        self.assertIn('por_mes', r.data)

    def test_api_do_dashboard_esconde_serie_do_operador_e_valida_periodo(self):
        op = User.objects.create_user('op', password='x')
        Perfil.objects.create(usuario=op, organizacao=self.org_a, papel=Perfil.OPERADOR)
        self.client.force_authenticate(op)
        self.assertNotIn('por_mes', self.client.get('/api/dashboard/').data)
        self.assertEqual(self.client.get('/api/dashboard/?inicio=abc').status_code, 400)
