from django.conf import settings
from django.db import models
from django.contrib.auth.hashers import check_password, make_password

import secrets
import string

from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist

class Usuario(models.Model):
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=255)
    p_nombre = models.CharField(max_length=255, blank=True, null=True)
    p_apellido = models.CharField(max_length=255, blank=True, null=True)
    foto_perfil = models.ImageField(blank=True, null=True, editable=True, upload_to='images/')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Para "eliminación" lógica
    is_blocked = models.BooleanField(default=False)  # Para bloqueo
    blocked_reason = models.TextField(blank=True, null=True)  # Razón del bloqueo
    blocked_at = models.DateTimeField(blank=True, null=True)  # Fecha de bloqueo

    class Meta:

        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.p_nombre + " " + self.p_apellido
    
    def save(self, *args, **kwargs):
        if not self.id or not self.contrasena.startswith('pbkdf2_sha256$'):
            self.contrasena = make_password(self.contrasena)
        super().save(*args, **kwargs)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.contrasena)
    
    reset_token = models.CharField(max_length=100, blank=True, null=True)
    reset_token_expires = models.DateTimeField(blank=True, null=True)
    
    def generate_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = timezone.now() + timedelta(hours=1)
        self.save()
        return self.reset_token
    
    def is_reset_token_valid(self):
        return (self.reset_token_expires and 
                timezone.now() < self.reset_token_expires)

    @classmethod
    def get_user_by_token(cls, token):
        try:
            user = cls.objects.get(reset_token=token)
            if user.reset_token_expires and timezone.now() < user.reset_token_expires:
                return user
            return None
        except ObjectDoesNotExist:
            return None


class Empresa(models.Model):
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=255)
    nombre_empresa = models.CharField(max_length=255)
    foto_perfil = models.ImageField(blank=True, null=True, editable=True, upload_to='images/')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    blocked_reason = models.TextField(blank=True, null=True)
    blocked_at = models.DateTimeField(blank=True, null=True)

    class Meta:

        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.nombre_empresa
    
    def save(self, *args, **kwargs):
        if not self.id or not self.contrasena.startswith('pbkdf2_sha256$'):
            self.contrasena = make_password(self.contrasena)
        super().save(*args, **kwargs)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.contrasena)
    
    reset_token = models.CharField(max_length=100, blank=True, null=True)
    reset_token_expires = models.DateTimeField(blank=True, null=True)
    
    def generate_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = timezone.now() + timedelta(hours=1)
        self.save()
        return self.reset_token
    
    def is_reset_token_valid(self):
        return (self.reset_token_expires and 
                timezone.now() < self.reset_token_expires)

    @classmethod
    def get_user_by_token(cls, token):
        try:
            user = cls.objects.get(reset_token=token)
            if user.reset_token_expires and timezone.now() < user.reset_token_expires:
                return user
            return None
        except ObjectDoesNotExist:
            return None
    


class Administrador(models.Model):
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=255)
    p_nombre = models.CharField(max_length=255, blank=True, null=True)  # Cambiado de "nombre" a "p_nombre" para consistencia
    p_apellido = models.CharField(max_length=255, blank=True, null=True)  # Cambiado de "apellido" a "p_apellido"
    foto_perfil = models.ImageField(blank=True, null=True, editable=True, upload_to='images/')  # Añadido como en los otros modelos
    fecha_registro = models.DateTimeField(default=timezone.now)  # Sin auto_now_add inicialmente  # Añadido para consistencia

    class Meta:
        verbose_name_plural = "Administradores"

    def __str__(self):
        if self.p_nombre and self.p_apellido:
            return f"{self.p_nombre} {self.p_apellido}"
        return self.correo
    
    def save(self, *args, **kwargs):
        if not self.id or not self.contrasena.startswith('pbkdf2_sha256$'):
            self.contrasena = make_password(self.contrasena)
        super().save(*args, **kwargs)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.contrasena)
    
    reset_token = models.CharField(max_length=100, blank=True, null=True)
    reset_token_expires = models.DateTimeField(blank=True, null=True)
    
    def generate_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = timezone.now() + timedelta(hours=1)
        self.save()
        return self.reset_token
    
    def is_reset_token_valid(self):
        return (self.reset_token_expires and 
                timezone.now() < self.reset_token_expires)


class TipoRecomendacion(models.Model):
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:

        verbose_name_plural = "Tipos de recomendación"

    def __str__(self):
        return self.nombre


class Genero(models.Model):
    nombre = models.CharField(max_length=255)
    tipo_recomendacion = models.ForeignKey(TipoRecomendacion, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Géneros de recomendación"
        unique_together = ('nombre', 'tipo_recomendacion')  # Evita duplicados por tipo

    def __str__(self):
        return f"{self.nombre} ({self.tipo_recomendacion})"


class EstadoAprobacion(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:

        verbose_name_plural = "Estados de aprobación"

    def __str__(self):
        return self.nombre


class Recomendacion(models.Model):
    usuario = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL)
    empresa = models.ForeignKey(Empresa, null=True, blank=True, on_delete=models.SET_NULL)
    tipo = models.ForeignKey(TipoRecomendacion, on_delete=models.CASCADE)
    genero = models.ForeignKey(Genero, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    resumen = models.TextField(blank=True, null=True)
    trivia = models.TextField(blank=True, null=True)
    frase_destacada = models.TextField(blank=True, null=True)
    portada = models.ImageField(blank=True, null=True, editable=True, upload_to='images/portadas_recomendaciones/')
    video_preview = models.FileField(blank=True, null=True, upload_to='videos/previews/')  # Para películas y videojuegos
    audio_preview = models.FileField(blank=True, null=True, upload_to='audios/previews/')  # Para música y libros
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado_aprobacion = models.ForeignKey(EstadoAprobacion, default=1, on_delete=models.RESTRICT)
    administrador = models.ForeignKey(Administrador, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:

        verbose_name_plural = "Recomendaciones"

    def __str__(self):
        return self.titulo


class RecomendacionGuardada(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    recomendacion = models.ForeignKey(Recomendacion, on_delete=models.CASCADE)
    fecha_guardado = models.DateTimeField(auto_now_add=True)

    class Meta:

        verbose_name_plural = "Recomendaciones guardadas"


class MeGusta(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    recomendacion = models.ForeignKey(Recomendacion, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:

        verbose_name_plural = "Megusteos"


class Reporte(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_revision', 'En Revisión'),
        ('resuelto', 'Resuelto'),
        ('rechazado', 'Rechazado')
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    recomendacion = models.ForeignKey(Recomendacion, on_delete=models.CASCADE)
    motivo = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    administrador = models.ForeignKey(Administrador, null=True, blank=True, on_delete=models.SET_NULL)
    comentario_admin = models.TextField(blank=True, null=True)
    fecha_resolucion = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Reportes"
        ordering = ['-fecha']

    def __str__(self):
        return f"Reporte de {self.usuario} sobre {self.recomendacion} (Estado: {self.get_estado_display()})"


class GestionUsuario(models.Model):
    administrador = models.ForeignKey(Administrador, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    accion = models.CharField(max_length=50)
    detalle = models.TextField(default='Sin detalles proporcionados')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:

        verbose_name_plural = "Acciones sobre usuarios"


class GestionEmpresa(models.Model):
    administrador = models.ForeignKey(Administrador, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    accion = models.CharField(max_length=50)
    detalle = models.TextField(default='Sin detalles proporcionados')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:

        verbose_name_plural = "Acciones sobre empresas"


class AprobacionRecomendacion(models.Model):
    administrador = models.ForeignKey(Administrador, on_delete=models.CASCADE)
    recomendacion = models.ForeignKey(Recomendacion, on_delete=models.CASCADE)
    estado_aprobacion = models.ForeignKey(EstadoAprobacion, on_delete=models.RESTRICT)
    fecha = models.DateTimeField(auto_now_add=True)
    comentario = models.TextField(blank=True, null=True)

    class Meta:

        verbose_name_plural = "Gestión de aprobación"


class SesionActividad(models.Model):
    session_key_hash = models.CharField(max_length=64, db_index=True)
    user_type = models.CharField(max_length=20)
    account_id = models.PositiveBigIntegerField()
    started_at = models.DateTimeField(default=timezone.now, db_index=True)
    last_activity_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(blank=True, null=True)
    duration_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "sesión de actividad"
        verbose_name_plural = "sesiones de actividad"
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user_type} #{self.account_id} - {self.started_at}"

    @property
    def activity_status(self):
        if self.ended_at:
            idle_minutes = getattr(
                settings, 'DISCOVER_ANALYTICS_SESSION_IDLE_MINUTES', 30
            )
            if self.ended_at - self.last_activity_at > timedelta(minutes=idle_minutes):
                return "Finalizada por inactividad"
            return "Finalizada"
        idle_minutes = getattr(
            settings, 'DISCOVER_ANALYTICS_SESSION_IDLE_MINUTES', 30
        )
        if timezone.now() - self.last_activity_at > timedelta(minutes=idle_minutes):
            return "Finalizada por inactividad"
        return "Actividad reciente"
