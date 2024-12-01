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
        token_data = validate_token(tenant_id, token)

        if not token_data:
            return {
                'statusCode': 401,
                'body': json.dumps({'message': 'Token inválido o expirado.'})
            }

        # Validar si el usuario pertenece al tenant del token
        tenant_id = token_data['tenant_id']
        user_id = event['pathParameters']['user_id']
        body = json.loads(event['body'])

        # Construir expresiones de actualización
        update_expression = "SET " + ", ".join([f"#{key} = :{key}" for key in body.keys()])
        expression_attribute_names = {f"#{key}": key for key in body.keys()}
        expression_attribute_values = {f":{key}": value for key, value in body.items()}

        # Actualizar usuario
        user_table.update_item(
            Key={'tenant_id': tenant_id, 'user_id': user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Usuario actualizado'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error interno: {str(e)}'})
        }
