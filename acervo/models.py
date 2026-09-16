from django.db import models

class Autor(models.Model):
    nome = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome

class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.ForeignKey(
        Autor,
        on_delete=models.PROTECT
    )
    ano = models.IntegerField()

    def __str__(self):
        return self.titulo
    
class Exemplar(models.Model):
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    codigo_patrimonio = models.CharField(max_length=20, unique=True)
    disponivel = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.livro.titulo} - Exemplar {self.id}"