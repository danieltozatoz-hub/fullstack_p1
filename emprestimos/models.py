from django.db import models
from datetime import date
from usuarios.models import Usuario
from acervo.models import Exemplar, Livro

class Emprestimo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    exemplar = models.ForeignKey(Exemplar, on_delete=models.PROTECT)
    data_emprestimo = models.DateField(auto_now_add=True)
    data_prevista_devolucao = models.DateField()
    data_devolucao = models.DateField(null=True, blank=True)
    
    @property
    def atrasado(self):
        if self.data_devolucao:
            return self.data_devolucao > self.data_prevista_devolucao
        return date.today() > self.data_prevista_devolucao
    
    @property
    def valor_multa(self):
        taxa_diaria = 5.00 
        
        if self.atrasado:
            data_base = self.data_devolucao if self.data_devolucao else date.today()
            dias_atraso = (data_base - self.data_prevista_devolucao).days
            return dias_atraso * taxa_diaria
        return 0.0
    
    def __str__(self):
        return f"Empréstimo: {self.usuario.nome} - {self.exemplar.livro.titulo}"
    
class Reserva(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    livro = models.ForeignKey(Livro, on_delete=models.PROTECT)
    data_reserva = models.DateTimeField(auto_now_add=True)
    ativa = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['data_reserva']

    def __str__(self):
        return f"Reserva: {self.usuario.nome} aguardando {self.livro.titulo}"