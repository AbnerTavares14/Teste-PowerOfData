import json
import asyncio
from handlers import CharacterHandler, FilmHandler, VehicleHandler, StarshipHandler, PlanetHandler
from utils import swapi_client

ROUTES = {
    'people': CharacterHandler,
    'films': FilmHandler,
    'vehicles': VehicleHandler,
    'starships': StarshipHandler,
    'planets': PlanetHandler,
}

def lambda_handler(event, context):
    path = event.get('rawPath', '').strip('/')
    resource = path.split('/')[0] if path else 'people' 
    params = event.get('queryStringParameters', {}) or {}
    
    result, status = None, 404

    if resource in ROUTES:
        HandlerClass = ROUTES[resource]
        
        handler_instance = HandlerClass(params, swapi_client)
        
        result, status = asyncio.run(handler_instance.list_resources())
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
