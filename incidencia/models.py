from django.db import models
from direccion.models import Direccion
from departamento.models import Departamento
from register.models import User, Perfiles


class TipoIncidencia(models.Model):
    nombre_incidencia = models.CharField(max_length=240, blank=False, unique=True)

    # AHORA PUEDEN ESTAR VACÍOS
    id_direccion = models.ForeignKey(
        Direccion,
        on_delete=models.CASCADE,
        related_name='incidencias',
        null=True,
        blank=True
    )

    id_departamento = models.ForeignKey(
        Departamento,
        on_delete=models.CASCADE,
        related_name='incidencias',
        null=True,
        blank=True
    )

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

    encuesta_base = models.ForeignKey(
        "encuesta.Encuesta",
        on_delete=models.CASCADE,
        related_name='solicitudes'
    )

    ubicacion = models.CharField()

    creado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='solicitudes_creadas'
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_SOLICITUD,
        default='abierta'
    )

    # AHORA TAMBIÉN PUEDEN SER NULL
    direccion_asignada = models.ForeignKey(
        Direccion,
        on_delete=models.CASCADE,
        related_name='solicitudes_asignadas',
        null=True,
        blank=True
    )

    departamento_asignado = models.ForeignKey(
        Departamento,
        on_delete=models.CASCADE,
        related_name='solicitudes_asignadas',
        null=True,
        blank=True
    )

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

    # ========================
    # LÓGICA DE RECHAZO AQUÍ
    # ========================
    def _aplicar_reglas_rechazo(self):
        """
        Aplica las reglas de rechazo automático basadas en el TipoIncidencia:
        - nombre_incidencia con menos de 8 caracteres
        - sin dirección asociada
        - sin departamento asociado
        """
        motivos = []

        tipo = getattr(self.encuesta_base, 'id_tipo_incidencia', None)

        if not tipo:
            motivos.append("La encuesta no tiene un tipo de incidencia asociado.")
        else:
            nombre = (tipo.nombre_incidencia or "").strip()
            if len(nombre) < 8:
                motivos.append("El nombre del tipo de incidencia tiene menos de 8 caracteres.")

            if tipo.id_direccion is None:
                motivos.append("El tipo de incidencia no tiene una Dirección asociada.")

            if tipo.id_departamento is None:
                motivos.append("El tipo de incidencia no tiene un Departamento asociado.")

        if motivos:
            self.estado = 'rechazada'
            texto_motivos = "\n".join(motivos)
            if self.descripcion_rechazo:
                self.descripcion_rechazo = (self.descripcion_rechazo.strip() + "\n" + texto_motivos).strip()
            else:
                self.descripcion_rechazo = texto_motivos

    def save(self, *args, **kwargs):
        """
        Sobrescribimos save para que:
        - Al CREAR la solicitud (solo la primera vez),
        se apliquen las reglas de rechazo automático.
        """
        es_nueva = self.pk is None

        # Si no viene estado explícito, dejamos 'abierta' como estado "activo"
        if es_nueva and not self.estado:
            self.estado = 'abierta'

        if es_nueva:
            # Al crear, aplicamos las reglas de rechazo.
            self._aplicar_reglas_rechazo()

        super().save(*args, **kwargs)


class RespuestaSolicitud(models.Model):
    solicitud = models.ForeignKey(
        SolicitudIncidencia,
        on_delete=models.CASCADE,
        related_name='respuestas'
    )
    pregunta = models.ForeignKey(
        "encuesta.Pregunta",
        on_delete=models.CASCADE,
        related_name='respuestas_solicitud'
    )
    respuesta_texto = models.TextField()

    class Meta:
        db_table = 'respuesta_solicitud'
        verbose_name = 'Respuesta de Solicitud'
        verbose_name_plural = 'Respuestas de Solicitud'
        unique_together = ('solicitud', 'pregunta')

    def __str__(self):
        return f"R: {self.pregunta.texto_pregunta[:50]}... (Solicitud {self.solicitud.id})"
