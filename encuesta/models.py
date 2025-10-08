from django.db import models

# Create your models here.

##############################################

#Temporal, en espera al modulo Departamento
class Departamento(models.Model):
    nombre_departamento = models.CharField(max_length=200, blank=False)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'departamento'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'

##############################################

class TipoIncidencia(models.Model):
    nombre_incidencia = models.CharField(max_length=240)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'tipo_incidencia'
        verbose_name = 'Tipo de incidencia'
        verbose_name_plural = 'Tipo de incidencias'
    
    def __str__(self):
        return self.nombre_incidencia

class Encuesta(models.Model):
    PRIORIDADES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja')
    ]

    id_departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    id_tipo_incidencia = models.ForeignKey(TipoIncidencia, on_delete=models.CASCADE)
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
    id_encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE)
    texto_pregunta = models.CharField(max_length=500)

    class Meta:
        db_table = 'pregunta_encuesta'
        verbose_name = 'Pregunta de Encuesta'
        verbose_name_plural = 'Preguntas de Encuestas'
    
    def __str__(self):
        return self.texto_pregunta

class Respuesta(models.Model):
    id_pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    respuesta = models.CharField(max_length=1000)

    class Meta:
        db_table = 'respuesta_pregunta'
        verbose_name = 'Respuesta de pregunta'
        verbose_name_plural = 'Respuestas de preguntas'
    
    def __str__(self):
        return self.respuesta
