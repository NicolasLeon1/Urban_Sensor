from django.db import models
from direccion.models import Direccion  # Asumiendo módulo 'direccion'
from departamento.models import Departamento  # Asumiendo módulo 'departamento'
from django.core.exceptions import ValidationError

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
    ESTADO_ABIERTA = 'abierta'
    ESTADO_DERIVADA = 'derivada'
    ESTADO_RECHAZADA = 'rechazada'
    ESTADO_FINALIZADA = 'finalizada'

    ESTADOS_SOLICITUD = [
        (ESTADO_ABIERTA, 'Abierta'),
        (ESTADO_DERIVADA, 'Derivada'),
        (ESTADO_RECHAZADA, 'Rechazada'),
        (ESTADO_FINALIZADA, 'Finalizada'),
    ]

    encuesta_base = models.ForeignKey('encuesta.Encuesta', on_delete=models.CASCADE)
    creado_por = models.ForeignKey('register.User', on_delete=models.CASCADE)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)

    direccion_asignada = models.ForeignKey(
        Direccion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    cuadrilla_asignada = models.ForeignKey(
    'register.User',            # usamos el mismo modelo User con perfil CUADRILLA
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='incidencias_cuadrilla'
)


    departamento_asignado = models.ForeignKey(
        Departamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_SOLICITUD,
        default=ESTADO_ABIERTA
    )

    descripcion_resolucion = models.TextField(null=True, blank=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'solicitud_incidencia'
        ordering = ['-creado']

    def __str__(self):
        return f"Solicitud #{self.id} - {self.estado}"

    def get_departamento_destino(self):
        """
        Determina Dirección y Departamento destino usando Encuesta / TipoIncidencia.
        """
        encuesta = self.encuesta_base
        

        # 1) Encuesta con departamento directo
        if hasattr(encuesta, 'id_departamento') and encuesta.id_departamento:
            depto = encuesta.id_departamento
            direccion = getattr(depto, 'direccion', None)
            return direccion, depto

        # 2) Usa TipoIncidencia asociado
        tipo = getattr(encuesta, 'id_tipo_incidencia', None)
        if tipo:
            depto = getattr(tipo, 'id_departamento', None)
            direccion = getattr(tipo, 'id_direccion', None)

            if depto and not direccion:
                direccion = getattr(depto, 'direccion', None)

            if depto or direccion:
                return direccion, depto

        # 3) Sin config válida
        raise ValidationError(
            "No existe configuración de Dirección/Departamento para esta incidencia. "
            "Revisa la Encuesta y el Tipo de Incidencia asociados."
        )
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
        
# incidencia/models.py

