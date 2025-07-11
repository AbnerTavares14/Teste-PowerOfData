import json
import asyncio

from handlers import characters_handler, films_handler, starships_handler, planets_handler


routes = {
    'characters': characters_handler.list_characters,
    'films': films_handler.list_films,
    'starships': starships_handler.list_starships,
    'planets': planets_handler.list_planets
}

def lambda_handler(event, context):
    path = event.get('rawPath', '').strip('/')
    parts = path.split('/')
    resource = parts[0] if parts else ''
    
    params = event.get('queryStringParameters', {}) or {}
    
    result, status = None, 404
    
    if resource in routes:
        result, status = asyncio.run(routes[resource](params))
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