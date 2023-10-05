from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Users  # Importa tu modelo Users desde tu aplicación

# Define un administrador personalizado para Users
class CustomUserAdmin(UserAdmin):
    model = Users
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'date_joined')  # Campos que deseas mostrar en la lista
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')  # Filtros para la lista de usuarios
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')  # Campos por los que se puede buscar
    ordering = ('email',)  # Campo por el que se ordenan los registros

# Registra el modelo Users con el administrador personalizado
admin.site.register(Users, CustomUserAdmin)