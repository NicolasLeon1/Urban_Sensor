from django.db import models
from departamento.models import Departamento
# from incidencia.models import TipoIncidencia  # <-- SE ELIMINA ESTA IMPORTACIÓN

# Create your models here.
class Encuesta(models.Model):
    PRIORIDADES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja')
    ]

    id_departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    
    # --- CAMBIO AQUÍ: Se usa el string 'incidencia.TipoIncidencia' ---
    id_tipo_incidencia = models.ForeignKey("incidencia.TipoIncidencia", on_delete=models.CASCADE)
    
    titulo_encuesta = models.CharField(max_length=240, blank=False)
    descripcion_incidente = models.CharField()
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='media')
    creado = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'encuesta'
        verbose_name = 'Encuesta'
        verbose_name_plural = 'Encuestas'
    
    def __str__(self):
        return self.titulo_encuesta

class Pregunta(models.Model):
    id_encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE, related_name='pregunta_set') # related_name añadido
    texto_pregunta = models.CharField(max_length=500)

    class Meta:
        db_table = 'pregunta_encuesta'
        verbose_name = 'Pregunta de Encuesta'
        verbose_name_plural = 'Preguntas de Encuestas'
    
    def __str__(self):
        return self.texto_pregunta

# El modelo Respuesta original se eliminó en el paso anterior.