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
    parts = path.split('/')
    params = event.get('queryStringParameters', {}) or {}
    
    result, status = {'message': 'Rota inválida'}, 404

    main_resource = parts[0] if len(parts) > 0 else 'people'
    resource_id = parts[1] if len(parts) > 1 else None
    sub_resource = parts[2] if len(parts) > 2 else None

    if main_resource in ROUTES:
        HandlerClass = ROUTES[main_resource]
        handler_instance = HandlerClass(params, swapi_client)

        if resource_id and sub_resource == 'characters' and main_resource == 'films':
            result, status = asyncio.run(handler_instance.list_characters_from_film(resource_id))
        elif resource_id:
            result, status = asyncio.run(handler_instance.get_by_id(resource_id))
        else:
            result, status = asyncio.run(handler_instance.list_resources())
            

    return {
        'statusCode': status,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(result, ensure_ascii=False)
    }