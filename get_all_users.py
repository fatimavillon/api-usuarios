import boto3
import json
from auth_service import validate_token

dynamodb = boto3.resource('dynamodb')
user_table = dynamodb.Table('Usuarios')

def lambda_handler(event, context):
    try:
        # Validar token
        
        tenant_id = event['headers'].get('tenant_id', '')
        token = event['headers'].get('Authorization', '')
        token_data = validate_token(tenant_id,token)
        if not token_data:
            return {
                'statusCode': 401,
                'body': json.dumps({'message': 'Token inválido o expirado.{token}'})
            }

        tenant_id = token_data['tenant_id']

        # Obtener usuarios del tenant
        response = user_table.query(
            KeyConditionExpression="tenant_id = :tenant_id",
            ExpressionAttributeValues={':tenant_id': tenant_id}
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'users': response.get('Items', [])})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error interno: {str(e)}'})
        }
