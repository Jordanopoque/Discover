from django import forms
from .models import Usuario, Empresa, Recomendacion, Genero, TipoRecomendacion, Reporte
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.hashers import make_password
from .models import Recomendacion

class RegistroUsuarioForm(forms.ModelForm):
    repetir_contrasena = forms.CharField(
        widget=forms.PasswordInput(),
        label="Repetir contraseña"
    )

    class Meta:
        model = Usuario
        fields = ['correo', 'p_nombre', 'p_apellido', 'foto_perfil']
        widgets = {
            'contrasena': forms.PasswordInput(),
        }
        labels = {
            'p_nombre': 'Primer nombre',
            'p_apellido': 'Primer apellido',
            'foto_perfil': 'Foto de perfil (opcional)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contrasena'] = forms.CharField(
            widget=forms.PasswordInput(),
            label="Contraseña"
        )
        # Añadir clases CSS a los campos
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        contrasena = cleaned_data.get("contrasena")
        repetir_contrasena = cleaned_data.get("repetir_contrasena")

        if contrasena and repetir_contrasena and contrasena != repetir_contrasena:
            raise ValidationError("Las contraseñas no coinciden")

        # Validación adicional de contraseña (opcional)
        if contrasena and len(contrasena) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres")
        if contrasena and not re.search("[A-Z]", contrasena):
            raise ValidationError("La contraseña debe contener al menos una mayúscula")
        if contrasena and not re.search("[0-9]", contrasena):
            raise ValidationError("La contraseña debe contener al menos un número")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.contrasena = self.cleaned_data["contrasena"]  # En producción, hashear aquí
        if commit:
            user.save()
        return user
    


class RegistroEmpresaForm(forms.ModelForm):
    repetir_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Repetir contraseña"
    )

    class Meta:
        model = Empresa
        fields = ['nombre_empresa', 'correo', 'foto_perfil']
        widgets = {
            'nombre_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre_empresa': 'Nombre de la empresa',
            'foto_perfil': 'Logo de la empresa (opcional)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contrasena'] = forms.CharField(
            widget=forms.PasswordInput(attrs={'class': 'form-control'}),
            label="Contraseña",
            help_text="Mínimo 8 caracteres, con al menos una mayúscula y un número"
        )

    def clean(self):
        cleaned_data = super().clean()
        contrasena = cleaned_data.get("contrasena")
        repetir_contrasena = cleaned_data.get("repetir_contrasena")

        if contrasena and repetir_contrasena and contrasena != repetir_contrasena:
            raise ValidationError("Las contraseñas no coinciden")

        # Validación de fortaleza de contraseña
        if contrasena:
            if len(contrasena) < 8:
                raise ValidationError("La contraseña debe tener al menos 8 caracteres")
            if not re.search("[A-Z]", contrasena):
                raise ValidationError("La contraseña debe contener al menos una mayúscula")
            if not re.search("[0-9]", contrasena):
                raise ValidationError("La contraseña debe contener al menos un número")

        return cleaned_data

    def save(self, commit=True):
        empresa = super().save(commit=False)
        empresa.contrasena = self.cleaned_data["contrasena"]
        if commit:
            empresa.save()
        return empresa
    
class LoginForm(forms.Form):
    correo = forms.EmailField(label='Correo electrónico')
    contrasena = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    tipo_usuario = forms.ChoiceField(
        label='Tipo de cuenta',
        choices=[
            ('usuario', 'Usuario'),
            ('empresa', 'Empresa'),
            ('administrador', 'Administrador')
        ],
        widget=forms.RadioSelect
    )


class RecomendacionForm(forms.ModelForm):
    class Meta:
        model = Recomendacion
        fields = '__all__'
        exclude = ['usuario', 'empresa', 'estado_aprobacion', 'administrador', 'audio_preview', 'video_preview']

    def __init__(self, *args, **kwargs):
        self.user_type = kwargs.pop('user_type', None)  # Obtener el tipo de usuario
        super().__init__(*args, **kwargs)
        
        # Si es empresa, filtrar los tipos y géneros
        if self.user_type == 'empresa':
            # Filtrar solo el tipo "Promocional"
            self.fields['tipo'].queryset = TipoRecomendacion.objects.filter(nombre='Promocional')
            
            # Filtrar solo el género "Patrocinado"
            self.fields['genero'].queryset = Genero.objects.filter(nombre='Patrocinado')
            
            # Hacer que los campos sean de solo lectura o deshabilitados
            self.fields['tipo'].readonly = True
            self.fields['genero'].readonly = True
        
        # Si es usuario normal, excluir Promocional y Patrocinado
        elif self.user_type == 'usuario':
            # Excluir el tipo "Promocional"
            self.fields['tipo'].queryset = TipoRecomendacion.objects.exclude(nombre='Promocional').order_by('nombre')
            
            # Configurar el campo género excluyendo "Patrocinado"
            if 'tipo' in self.data:
                try:
                    tipo_id = int(self.data.get('tipo'))
                    self.fields['genero'].queryset = Genero.objects.filter(
                        tipo_recomendacion_id=tipo_id
                    ).exclude(nombre='Patrocinado').order_by('nombre')
                except (ValueError, TypeError):
                    pass
            elif self.instance.pk and self.instance.tipo:
                self.fields['genero'].queryset = self.instance.tipo.genero_set.exclude(
                    nombre='Patrocinado'
                ).order_by('nombre')
            else:
                self.fields['genero'].queryset = Genero.objects.none()
        
        # Si es administrador, mostrar todo sin restricciones
        elif self.user_type == 'administrador':
            # Mostrar todos los tipos
            self.fields['tipo'].queryset = TipoRecomendacion.objects.all().order_by('nombre')
            
            # Configurar el campo género sin restricciones
            if 'tipo' in self.data:
                try:
                    tipo_id = int(self.data.get('tipo'))
                    self.fields['genero'].queryset = Genero.objects.filter(
                        tipo_recomendacion_id=tipo_id
                    ).order_by('nombre')
                except (ValueError, TypeError):
                    pass
            elif self.instance.pk and self.instance.tipo:
                self.fields['genero'].queryset = self.instance.tipo.genero_set.order_by('nombre')
            else:
                self.fields['genero'].queryset = Genero.objects.none()

        # Añadir clases CSS a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['correo', 'p_nombre', 'p_apellido', 'foto_perfil']
        widgets = {
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'p_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'p_apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'p_nombre': 'Primer nombre',
            'p_apellido': 'Primer apellido',
            'foto_perfil': 'Foto de perfil (opcional)'
        }

class EditarEmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['correo', 'nombre_empresa', 'foto_perfil']
        widgets = {
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'nombre_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre_empresa': 'Nombre de la empresa',
            'foto_perfil': 'Logo de la empresa (opcional)'
        }


class PasswordResetRequestForm(forms.Form):
    correo = forms.EmailField(label='Correo electrónico')
    tipo_usuario = forms.ChoiceField(
        choices=[('usuario', 'Usuario'), ('empresa', 'Empresa')],
        widget=forms.RadioSelect
    )

class PasswordResetForm(forms.Form):
    nueva_contrasena = forms.CharField(widget=forms.PasswordInput)
    confirmar_contrasena = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('nueva_contrasena') != cleaned_data.get('confirmar_contrasena'):
            raise ValidationError("Las contraseñas no coinciden")
        return cleaned_data
    

from django import forms
from .models import TipoRecomendacion, Genero

class TipoRecomendacionForm(forms.ModelForm):
    class Meta:
        model = TipoRecomendacion
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'})
        }

class GeneroForm(forms.ModelForm):
    class Meta:
        model = Genero
        fields = ['nombre', 'tipo_recomendacion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_recomendacion': forms.Select(attrs={'class': 'form-control'})
        }


class GestionReporteForm(forms.ModelForm):
    class Meta:
        model = Reporte
        fields = ['estado', 'comentario_admin']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'comentario_admin': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }
    
