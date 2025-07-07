import asyncio
import aiohttp
import logging
from utils import swapi_client

async def _format_film_details(session: aiohttp.ClientSession, item: dict):
    
    characters_task = swapi_client.get_details_from_urls(session, item.get('characters', []), 'name')
    planets_task = swapi_client.get_details_from_urls(session, item.get('planets', []), 'name')
    starships_task = swapi_client.get_details_from_urls(session, item.get('starships', []), 'name')
    vehicles_task = swapi_client.get_details_from_urls(session, item.get('vehicles', []), 'name')
    species_task = swapi_client.get_details_from_urls(session, item.get('species', []), 'name')

    results = await asyncio.gather(
        characters_task, planets_task, starships_task,
        vehicles_task, species_task, return_exceptions=True
    )
    
    characters = results[0] if not isinstance(results[0], Exception) else ['desconhecido']
    planets = results[1] if not isinstance(results[1], Exception) else ['desconhecido']
    starships = results[2] if not isinstance(results[2], Exception) else ['desconhecido']
    vehicles = results[3] if not isinstance(results[3], Exception) else ['desconhecido']
    species = results[4] if not isinstance(results[4], Exception) else ['desconhecido']

    return {
        'titulo': item.get('title'),
        'episodio_id': item.get('episode_id'),
        'diretor': item.get('director'),
        'produtor': item.get('producer'),
        'data_lancamento': item.get('release_date'),
        'resumo_abertura': item.get('opening_crawl'),
        'personagens': characters,
        'planetas': planets,
        'naves': starships,
        'veiculos': vehicles,
        'especies': species
    }

async def list_films(params: dict):
    try:
        sort_by = params.get('sort_by', 'episodio_id')
        order = params.get('order', 'asc')
        
        valid_sort_fields = ['titulo', 'episodio_id', 'data_lancamento']
        if sort_by not in valid_sort_fields:
            return {'message': f'sort_by deve ser um de: {valid_sort_fields}'}, 400

        async with aiohttp.ClientSession() as session:
            url = 'https://swapi.dev/api/films/'
            data = await swapi_client.get_cached_url_data(session, url)
            all_results = data.get('results', []) if data else []

            tasks = [_format_film_details(session, item) for item in all_results]
            formatted_data = await asyncio.gather(*tasks)

            formatted_data.sort(key=lambda x: x.get(sort_by, 0), reverse=(order == 'desc'))

        return formatted_data, 200

    except Exception as e:
        logging.exception("Erro no handler de filmes.")
        return {'message': f'Um erro inesperado ocorreu: {str(e)}'}, 500