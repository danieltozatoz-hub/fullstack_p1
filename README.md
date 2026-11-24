# Biblioteca — mini-SaaS (P2)

Sistema de biblioteca em Django, evoluído da P1 com **multi-organização**, **perfis**, **API REST (DRF)** e **dashboard**.

## Como rodar

```bash
pip install -r requirements.txt
python manage.py migrate          # migra também os dados da P1 (vão para a "Organização padrão")
python manage.py popular_demo     # opcional: 2 bibliotecas com dados de exemplo
python manage.py runserver
python manage.py test             # 47 testes
```

Logins de demonstração (senha `demo1234`): `ana` e `bruno` (administradores de organizações diferentes) e `carla` (operadora da Central).
Contas já existentes viram administradoras da "Organização padrão" na migração. Novas organizações, usuários e perfis são criados em `/admin/`.

## O que foi implementado

| Aula | Entrega | Onde |
|---|---|---|
| 13 | API REST com DRF (todos os recursos), autenticação obrigatória, validação, `/api/` | `core/api.py`, `*/serializers.py`, `*/api_views.py`, `biblioteca/api_urls.py` |
| 14 | `Organizacao`, base abstrata `DaOrganizacao`, `Perfil`, migração em 3 etapas, filtro por organização em toda view/form/API, unicidade por organização | `core/`, `*/migrations/` |
| 17 | Dashboard (KPI, ranking, série, distribuição), filtro de período validado, Chart.js, CSV, API do dashboard, dashboard por papel, `select_related`, índice | `acervo/dashboard.py`, `acervo/views.py`, `static/js/` |

### Perguntas do dono da biblioteca (Tarefa 1 da Aula 17)

| Pergunta | Métrica | Tipo | Visual |
|---|---|---|---|
| Quantos empréstimos temos, quantos estão abertos e quantos atrasaram? | `aggregate` com `Count(filter=...)` | KPI | cartões |
| Quais livros mais saem? | `values` + `annotate` + `order_by` | Ranking | tabela |
| Como os empréstimos evoluem por mês? | `TruncMonth` | Série | barras |
| Qual a situação dos empréstimos? | `Count(filter=...)` | Distribuição | rosca |

### Endpoints da API (`/api/`)

`autores`, `livros`, `exemplares`, `usuarios` (CRUD) · `emprestimos` (listar, criar, detalhar, excluir, `POST /<id>/devolver/`) · `reservas` (listar, criar, detalhar, `POST /<id>/cancelar/`, `?ativa=true`) · `dashboard/?inicio=AAAA-MM-DD&fim=AAAA-MM-DD`.
Login pelo navegador em `/api-auth/login/`; no `curl`, use `-u usuario:senha`.

### Dashboard por papel

| Bloco | Administrador | Operador |
|---|---|---|
| KPIs, ranking, distribuição | sim | sim |
| Série por mês | sim | não |
| Exportar CSV | sim | não (403) |

## Roteiro de isolamento (Aula 14) — resultado

Automatizado em `acervo/tests.py::IsolamentoTest` e `emprestimos/tests.py::ApiTest`. Todos passam.

| Cenário | Esperado | Resultado |
|---|---|---|
| Usuário A abre a lista de livros | só os da A | OK |
| Usuário A abre `/livros/<id da B>/editar/` | 404 | OK |
| Usuário A cria um livro | gravado na organização A | OK |
| Selects do formulário do A | só opções da A | OK |
| A cadastra patrimônio que a B já usa | permitido; repetido na própria A é recusado | OK |
| Mesmos cenários pela API | 404 / 400 / org da sessão | OK |
