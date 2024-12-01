import boto3
import uuid
from datetime import datetime, timedelta
import os
import hashlib

# Acceder al nombre de la tabla desde la variable de entorno
dynamodb = boto3.resource('dynamodb')
auth_table_name = os.environ.get('AUTH_TOKENS_TABLE', 'AuthTokens')  # Obtener el nombre de la tabla desde el entorno
auth_table = dynamodb.Table(auth_table_name)

# Definir una función para generar un hash simple
def generate_token_hash(tenant_id, user_id, secret_key):
    """Genera un hash simple del token basado en tenant_id, user_id y un UUID."""
    token_data = f"{tenant_id}-{user_id}-{str(uuid.uuid4())}"
    token_hash = hashlib.sha256(token_data.encode('utf-8')).hexdigest()
    return token_hash

def generate_token(tenant_id, user_id):
    """Genera un token único con expiración y lo almacena en DynamoDB."""
    try:
        # Crear un token con un hash generado
        token = generate_token_hash(tenant_id, user_id, "some_secret_key")
        expiration = (datetime.utcnow() + timedelta(weeks=208)).isoformat()

        # Guardar el token en la tabla AuthTokens
        auth_table.put_item(Item={
            'tenant_id': tenant_id,
            'user_id': user_id,
            'token': token,
            'expires_at': expiration
        })

        return token
    except Exception as e:
        print(f"Error generando el token: {str(e)}")
        return None

def validate_token(tenant_id,token):
    """Valida un token verificando su existencia y expiración."""
    try:
        # Buscar el token en la base de datos
        response = auth_table.get_item(Key={'tenant_id': tenant_id, 'token': token})
        item = response.get('Item')

        if not item:
            return None  # Token no encontrado

        # Verificar si el token ha expirado
        if datetime.utcnow().isoformat() > item['expires_at']:
            return None  # Token expirado

        # Retorna los datos del token
        return {
            'tenant_id': item['tenant_id'],
            'user_id': item['user_id'],
            'token': token
        }

    except Exception as e:
        print(f"Error validando el token: {str(e)}")
        return None
