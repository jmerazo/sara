from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        auth_type = self.context['request'].data.get('auth_type', 'local')

        if auth_type == 'google':
            code = self.context['request'].data.get('code')
            if not code:
                raise serializers.ValidationError("Code is required for Google auth.")
            # Intercambiar el código por un token de Google y validar el usuario
            return self.validate_google_auth(code)
        else:
            # Continuar con la validación normal para autenticación local
            return super().validate(attrs)

    def validate_google_auth(self, code):
        # Asumiendo que tienes una función para manejar la lógica de Google
        return handle_google_auth(code)