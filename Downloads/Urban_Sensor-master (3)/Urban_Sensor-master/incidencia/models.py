from django.db import models
from direccion.models import Direccion
from departamento.models import Departamento
from register.models import User, Perfiles

class TipoIncidencia(models.Model):
    nombre_incidencia = models.CharField(max_length=240, blank=False, unique=True)
    id_direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE, related_name='incidencias')
    id_departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='incidencias')
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'tipo_incidencia'
        verbose_name = 'Tipo de Incidencia'
        verbose_name_plural = 'Tipos de Incidencia'
    
    def __str__(self):
        return self.nombre_incidencia

class SolicitudIncidencia(models.Model):
    ESTADOS_SOLICITUD = [
        ('abierta', 'Abierta'),
        ('derivada', 'Derivada'),
        ('rechazada', 'Rechazada'),
        ('finalizada', 'Finalizada'),
    ]

    encuesta_base = models.ForeignKey("encuesta.Encuesta", on_delete=models.CASCADE, related_name='solicitudes')
    
    ubicacion = models.CharField()

    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitudes_creadas')
    
    estado = models.CharField(max_length=20, choices=ESTADOS_SOLICITUD, default='abierta')
    
    direccion_asignada = models.ForeignKey(Direccion, on_delete=models.CASCADE, related_name='solicitudes_asignadas')
    departamento_asignado = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='solicitudes_asignadas')

    cuadrilla_asignada = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='tareas_asignadas', 
        limit_choices_to={'perfil__id': Perfiles.CUADRILLA.value}
    )

    descripcion_resolucion = models.TextField(null=True, blank=True)
    descripcion_rechazo = models.TextField(null=True, blank=True)
    descripcion_reabrir = models.TextField(null=True, blank=True)
    
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'solicitud_incidencia'
        verbose_name = 'Solicitud de Incidencia'
        verbose_name_plural = 'Solicitudes de Incidencia'
        ordering = ['-creado']

    def __str__(self):
        return f"Solicitud {self.id} - {self.encuesta_base.titulo_encuesta} ({self.get_estado_display()})"


class RespuestaSolicitud(models.Model):
    solicitud = models.ForeignKey(SolicitudIncidencia, on_delete=models.CASCADE, related_name='respuestas')
    pregunta = models.ForeignKey("encuesta.Pregunta", on_delete=models.CASCADE, related_name='respuestas_solicitud')
    respuesta_texto = models.TextField()

    class Meta:
        db_table = 'respuesta_solicitud'
        verbose_name = 'Respuesta de Solicitud'
        verbose_name_plural = 'Respuestas de Solicitud'
        unique_together = ('solicitud', 'pregunta') 

    def __str__(self):
        return f"R: {self.pregunta.texto_pregunta[:50]}... (Solicitud {self.solicitud.id})"