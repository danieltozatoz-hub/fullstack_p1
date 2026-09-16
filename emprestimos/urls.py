from django.urls import path
from . import views

urlpatterns = [
    # Empréstimo
    path('emprestimos/', views.lista_emprestimos, name='lista_emprestimos'),
    path('emprestimos/novo/', views.novo_emprestimo, name='novo_emprestimo'),
    path('emprestimos/<int:pk>/devolver/', views.devolver_emprestimo, name='devolver_emprestimo'),
    path('emprestimos/<int:pk>/excluir/', views.excluir_emprestimo, name='excluir_emprestimo'),

    # Reserva
    path('reservas/', views.lista_reservas, name='lista_reservas'),
    path('reservas/nova/', views.nova_reserva, name='nova_reserva'),
    path('reservas/<int:pk>/cancelar/', views.cancelar_reserva, name='cancelar_reserva'),
]