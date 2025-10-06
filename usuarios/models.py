from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# -------------------
# Usuario base
# -------------------
class Usuario(AbstractUser):
    rol = models.CharField(max_length=20, choices=[
        ('operador', 'Operador'),
        ('coordinador', 'Coordinador'),
        ('soporte', 'Soporte'),
        ('monitor', 'Monitor'),
    ])

    groups = models.ManyToManyField(
        Group,
        related_name='usuarios_groups',
        blank=True,
        help_text='Grupos a los que pertenece este usuario.',
        verbose_name='grupos',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='usuarios_permissions',
        blank=True,
        help_text='Permisos específicos para este usuario.',
        verbose_name='permisos de usuario',
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


# -------------------
# Perfil Coordinador
# -------------------
class PerfilCoordinador(models.Model):
    codigo = models.CharField(max_length=20, primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="perfil_coordinador")
    nombres = models.CharField(max_length=100)
    paterno = models.CharField(max_length=50)
    materno = models.CharField(max_length=50)
    celular = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.nombres} {self.paterno} {self.materno}"


# -------------------
# Perfil Soporte
# -------------------
class PerfilSoporte(models.Model):
    codigo = models.CharField(max_length=20, primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="perfil_soporte")
    nombres = models.CharField(max_length=100)
    paterno = models.CharField(max_length=50)
    materno = models.CharField(max_length=50)
    celular = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombres} {self.paterno} {self.materno}" 


# -------------------
# Perfil Monitor
# -------------------
class PerfilMonitor(models.Model):
    codigo = models.CharField(max_length=20, primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="perfil_monitor")
    nombres = models.CharField(max_length=100)
    paterno = models.CharField(max_length=50)
    materno = models.CharField(max_length=50)
    celular = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombres} {self.paterno} {self.materno}"


# -------------------
# Perfil Operador
# -------------------
class PerfilOperador(models.Model):

    class Meta:
        verbose_name = "Operador"
        verbose_name_plural = "Informacion Operadores"
    
    ci = models.CharField(max_length=20, primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="perfil_operador")
    nombres = models.CharField(max_length=100)
    paterno = models.CharField(max_length=50)
    materno = models.CharField(max_length=50)
    celular = models.CharField(max_length=20)
    tipo_personal = models.CharField(max_length=50)

    coordinador = models.ForeignKey(
        PerfilCoordinador,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="operadores"
    )

    monitor = models.ForeignKey(
        PerfilMonitor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="operadores"
    )

    soporte = models.ForeignKey(
        PerfilSoporte,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="operadores_asignados"
    )

    def __str__(self):
        return f"{self.nombres} {self.paterno} {self.materno}"


# -------------------
# Actas de Operador
# -------------------
class Acta(models.Model):

    class Meta:
        verbose_name = "Actas Operador"
        verbose_name_plural = "Actas Asignadas"

    operador = models.OneToOneField(
        PerfilOperador,       # Relación 1 a 1
        on_delete=models.CASCADE,
        related_name='acta_operador'
    )
    codigo = models.CharField(max_length=20, primary_key=True, editable=False)  # A000001, A000002...
    actas_asignadas = models.CharField(max_length=100, blank=True, default="-")
    provincia = models.CharField(max_length=100, blank=True, default="-")
    municipio = models.CharField(max_length=100, blank=True, default="-")
    localidad = models.CharField(max_length=100, blank=True, default="-")
    recinto = models.CharField(max_length=100, blank=True, default="-")

    # Corrigiendo: no existe StringField en Django → usar CharField
    mesa1 = models.CharField(max_length=10, default="-")
    mesa2 = models.CharField(max_length=10, default="-")
    mesa3 = models.CharField(max_length=10, default="-")
    mesa4 = models.CharField(max_length=10, default="-")
    mesa5 = models.CharField(max_length=10, default="-")
    mesa6 = models.CharField(max_length=10, default="-")
    mesa7 = models.CharField(max_length=10, default="-")
    mesa8 = models.CharField(max_length=10, default="-")

    def save(self, *args, **kwargs):
        # Generar código único si no existe
        if not self.codigo:
            next_num = Acta.objects.count() + 1
            # Genera A000001, A000002, etc.
            self.codigo = f"A{str(next_num).zfill(6)}"

        # Reemplazar valores vacíos por "-"
        for field in ["actas_asignadas", "provincia", "municipio", "localidad", "recinto"]:
            value = getattr(self, field)
            if not value or str(value).strip() == "":
                setattr(self, field, "-")

        # Validar campos de mesas (si están vacíos → "-")
        for i in range(1, 9):
            mesa_val = getattr(self, f"mesa{i}")
            if not mesa_val or str(mesa_val).strip() == "":
                setattr(self, f"mesa{i}", "-")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.codigo


# -------------------
# Actividades Operador
# -------------------
class Actividad(models.Model):

    class Meta:
        verbose_name = "Actividad Operador"
        verbose_name_plural = "Actividades Operadores"

    operador = models.ForeignKey(
        PerfilOperador,
        on_delete=models.CASCADE,
        related_name="actividades_operador"
    )
    
    descripcion = models.CharField(max_length=200)

    # Estado como booleano (check en admin)
    estado = models.BooleanField(default=False)

    fecha = models.CharField(max_length=50, blank=True, default="-")
    observacion = models.TextField(blank=True, default="-")

    def save(self, *args, **kwargs):
        # Si fecha está vacía, poner "-"
        if not self.fecha or str(self.fecha).strip() == "":
            self.fecha = "-"
        # Si observación está vacía, poner "-"
        if not self.observacion or str(self.observacion).strip() == "":
            self.observacion = "-"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.descripcion} ({'✔' if self.estado else '✘'})"



# -------------------
# Observaciones adicionales de un operador
# -------------------
class ObservacionAdicional(models.Model):
    class Meta:
        verbose_name = "observación adicional Operador"
        verbose_name_plural = "observaciones Operadores"

    operador = models.ForeignKey(
        PerfilOperador,   # Relación con el operador
        on_delete=models.CASCADE,
        related_name='observaciones_adicionales'  # Para acceder: operador.observaciones_adicionales.all()
    )
    observacion = models.TextField()  # Texto de la observación
    fecha = models.CharField(max_length=50, blank=True, default="-")  # Fecha en dd/mm/aaaa o "-"

    def save(self, *args, **kwargs):
        # Si la fecha está vacía, colocar "-"
        if not self.fecha or str(self.fecha).strip() == "":
            self.fecha = "-"
        super().save(*args, **kwargs)

    def __str__(self):
        # Muestra los primeros 30 caracteres de la observación y la fecha
        return f"CI: {self.operador.ci}"    


# -------------------
# Detalle Adicional de un operador
# -------------------
class DetalleAdicional(models.Model):

    class Meta:
        verbose_name = "Detalle Adicional Operador"
        verbose_name_plural = "Detalles Operadores"

    operador = models.OneToOneField(
        'PerfilOperador',
        on_delete=models.CASCADE,
        related_name='detalle_adicional'
    )
    usuario_apk = models.CharField(max_length=100, blank=True, default="-")
    transmitido = models.CharField(max_length=20, blank=True, default="-")
    no_transmitido = models.CharField(max_length=20, blank=True, default="-")

    def save(self, *args, **kwargs):
        # Normalizar campos vacíos
        if not self.usuario_apk or str(self.usuario_apk).strip() == "":
            self.usuario_apk = "-"
        if not self.transmitido or str(self.transmitido).strip() == "":
            self.transmitido = "-"
        if not self.no_transmitido or str(self.no_transmitido).strip() == "":
            self.no_transmitido = "-"
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"CI: {self.operador.ci} "
            f"(T:{self.transmitido}/NT:{self.no_transmitido})"
        )

