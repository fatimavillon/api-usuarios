import boto3
import json
import uuid
from auth_service import generate_token

dynamodb = boto3.resource('dynamodb')
user_table = dynamodb.Table('Usuarios')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])

        # Validar tenant_id
        tenant_id = body.get('tenant_id')
        if not tenant_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'El campo tenant_id es obligatorio.'})
            }

        # Validar los campos obligatorios: email, password, y role
        email = body.get('email')
        password = body.get('password')
        role = body.get('role', 'usuario')  # Asignar "usuario" como rol predeterminado

        if not email or not password:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Email y contraseña son obligatorios.'})
            }

        # Crear usuario
        user_id = str(uuid.uuid4())
        body['user_id'] = user_id
        body['tenant_id'] = tenant_id
        body['role'] = role  # Guardar el rol

        # Guardar el usuario con email, password y role
        user_table.put_item(Item=body)

        # Generar token
        token = generate_token(tenant_id, user_id)

        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'Usuario creado', 'user_id': user_id, 'token': token})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error interno: {str(e)}'})
        }
