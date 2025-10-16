from django.db import models

class Departamento(models.Model):
    nombre = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre


class Cuadrilla(models.Model):
    nombre = models.CharField(max_length=150)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} ({self.departamento})"


class TipoIncidencia(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class Incidencia(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.ForeignKey(TipoIncidencia, on_delete=models.SET_NULL, null=True)
    cuadrilla = models.ForeignKey(Cuadrilla, on_delete=models.SET_NULL, null=True)
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=30,
        choices=[
            ('abierta', 'Abierta'),
            ('en_proceso', 'En proceso'),
            ('finalizada', 'Finalizada'),
        ],
        default='abierta'
    )

    def __str__(self):
        return self.titulo
