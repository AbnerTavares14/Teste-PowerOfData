import json
import asyncio

from handlers import character_handler

def lambda_handler(event, context):
    path = event.get('rawPath', '').strip('/')
    parts = path.split('/')
    resource = parts[0] if parts else ''
    
    params = event.get('queryStringParameters', {}) or {}
    
    result, status = None, 404

    if resource == 'characters':
        result, status = asyncio.run(character_handler.list_characters(params))
        
    else:
        result = {'message': 'Endpoint não encontrado.'}
        status = 404
    return {
        'statusCode': status,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*' 
        },
        'body': json.dumps(result, ensure_ascii=False)
    }