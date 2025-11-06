from django.db import models
from direccion.models import Direccion  # Asumiendo módulo 'direccion'
from departamento.models import Departamento  # Asumiendo módulo 'departamento'

# --- IMPORTS AÑADIDOS ---
# from encuesta.models import Encuesta, Pregunta # <-- SE ELIMINA ESTA IMPORTACIÓN
from register.models import User, Perfiles

class TipoIncidencia(models.Model):
    nombre_incidencia = models.CharField(max_length=240, blank=False, unique=True)
    id_direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE, related_name='incidencias')
    id_departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='incidencias')
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'tipo_incidencia'  # Nombre distinto para evitar conflicto
        verbose_name = 'Tipo de Incidencia'
        verbose_name_plural = 'Tipos de Incidencia'
    
    def __str__(self):
        return self.nombre_incidencia

# --- NUEVO MODELO: SolicitudIncidencia (El incidente real creado por Territorial) ---
class SolicitudIncidencia(models.Model):
    ESTADOS_SOLICITUD = [
        ('abierta', 'Abierta'),             # Creada por Territorial, visible para Depto
        ('derivada', 'Derivada'),           # Asignada a Cuadrilla por Depto
        ('rechazada', 'Rechazada'),         # Rechazada por Depto/Direccion
        ('finalizada', 'Finalizada'),       # Resuelta por Cuadrilla
    ]

    # --- CAMBIO AQUÍ: Se usa el string 'encuesta.Encuesta' ---
    encuesta_base = models.ForeignKey("encuesta.Encuesta", on_delete=models.PROTECT, related_name='solicitudes')
    
    ubicacion = models.CharField()

    # Quien la crea (Perfil Territorial)
    creado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='solicitudes_creadas')
    
    # Estado actual del ticket
    estado = models.CharField(max_length=20, choices=ESTADOS_SOLICITUD, default='abierta')
    
    # A quién se asigna (copiado de la plantilla para facilitar queries)
    direccion_asignada = models.ForeignKey(Direccion, on_delete=models.PROTECT, related_name='solicitudes_asignadas')
    departamento_asignado = models.ForeignKey(Departamento, on_delete=models.PROTECT, related_name='solicitudes_asignadas')

    # A quién se deriva (Perfil Cuadrilla)
    cuadrilla_asignada = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='tareas_asignadas', 
        limit_choices_to={'perfil__id': Perfiles.CUADRILLA.value} # Solo usuarios con perfil Cuadrilla
    )

    # Info de resolución (para Cuadrilla)
    descripcion_resolucion = models.TextField(null=True, blank=True)
    # imagen_resolucion = models.ImageField(upload_to='resoluciones/', null=True, blank=True) # Campo de imagen (requiere configuración de media)
    
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'solicitud_incidencia'
        verbose_name = 'Solicitud de Incidencia'
        verbose_name_plural = 'Solicitudes de Incidencia'
        ordering = ['-creado']

    def __str__(self):
        # __str__ puede fallar si la encuesta_base aún no está cargada (raro)
        # Es mejor manejarlo con cuidado, aunque para makemigrations no importa.
        try:
            return f"Solicitud {self.id} - {self.encuesta_base.titulo_encuesta} ({self.get_estado_display()})"
        except Exception:
            return f"Solicitud {self.id} ({self.get_estado_display()})"


# --- NUEVO MODELO: RespuestaSolicitud (Las respuestas del Territorial a la encuesta) ---
class RespuestaSolicitud(models.Model):
    solicitud = models.ForeignKey(SolicitudIncidencia, on_delete=models.CASCADE, related_name='respuestas')
    
    # --- CAMBIO AQUÍ: Se usa el string 'encuesta.Pregunta' ---
    pregunta = models.ForeignKey("encuesta.Pregunta", on_delete=models.PROTECT, related_name='respuestas_solicitud')
    respuesta_texto = models.TextField()

    class Meta:
        db_table = 'respuesta_solicitud'
        verbose_name = 'Respuesta de Solicitud'
        verbose_name_plural = 'Respuestas de Solicitud'
        # Asegura que solo haya una respuesta por pregunta para cada solicitud
        unique_together = ('solicitud', 'pregunta') 

    def __str__(self):
        try:
            return f"R: {self.pregunta.texto_pregunta[:50]}... (Solicitud {self.solicitud.id})"
        except Exception:
            return f"Respuesta (Solicitud {self.solicitud.id})"