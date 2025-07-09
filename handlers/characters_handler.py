import asyncio
import aiohttp
import logging
from utils import swapi_client

async def _format_character_details(session: aiohttp.ClientSession, item: dict):
    planet_url = item.get('homeworld')
    planet_task = asyncio.create_task(swapi_client.get_cached_url_data(session, planet_url))
    
    film_titles_task = swapi_client.get_details_from_urls(session, item.get('films', []), 'title')
    species_names_task = swapi_client.get_details_from_urls(session, item.get('species', []), 'name')
    starship_names_task = swapi_client.get_details_from_urls(session, item.get('starships', []), 'name')
    vehicle_names_task = swapi_client.get_details_from_urls(session, item.get('vehicles', []), 'name')

    results = await asyncio.gather(
        planet_task, film_titles_task, species_names_task,
        starship_names_task, vehicle_names_task, return_exceptions=True
    )

    planet_data = results[0]
    planet_name = planet_data.get('name') if isinstance(planet_data, dict) else 'desconhecido'
    film_titles = results[1] if not isinstance(results[1], Exception) else ['desconhecido']
    species_names = results[2] if not isinstance(results[2], Exception) else ['desconhecido']
    starship_names = results[3] if not isinstance(results[3], Exception) else ['desconhecido']
    vehicle_names = results[4] if not isinstance(results[4], Exception) else ['desconhecido']

    return {
        'nome': item.get('name', 'desconhecido'),
        'altura': item.get('height', 'unknown') + ' cm' if item.get('height') != 'unknown' else 'desconhecido',
        'peso': item.get('mass', 'unknown') + ' kg' if item.get('mass') != 'unknown' else 'desconhecido',
        'planeta_natal': planet_name,
        'filmes': film_titles or ['desconhecido'],
        'especies': species_names or ['desconhecido'],
        'naves': starship_names or ['desconhecido'],
        'veiculos': vehicle_names or ['desconhecido'],
    }


async def list_characters(params: dict):
    try:
        name_filter = params.get('name', '').lower()
        sort_by = params.get('sort_by', 'nome')
        order = params.get('order', 'asc')
        page = int(params.get('page', 1))
        limit = int(params.get('limit', 10))

        if sort_by not in ['nome', 'altura', 'peso']:
            return {'message': f"sort_by deve ser 'nome', 'altura' ou 'peso'"}, 400
        if page < 1 or limit < 1:
            return {'message': 'page e limit devem ser maiores que 0'}, 400

        async with aiohttp.ClientSession() as session:
            url = 'https://swapi.info/api/people'
            data = await swapi_client.get_cached_url_data(session, url)
            all_results = data.get('results', []) if data else []

            if name_filter:
                all_results = [item for item in all_results if name_filter in item.get('name', '').lower()]

            tasks = [_format_character_details(session, item) for item in all_results]
            formatted_data = await asyncio.gather(*tasks, return_exceptions=True)
            formatted_data = [item for item in formatted_data if not isinstance(item, Exception)]

            reverse = (order == 'desc')
            formatted_data.sort(key=lambda x: x[sort_by] if x[sort_by] != 'desconhecido' else '', reverse=reverse)

            start = (page - 1) * limit
            end = start + limit
            paginated_data = formatted_data[start:end]

        return {
            'total_results': len(formatted_data),
            'page': page,
            'limit': limit,
            'results': paginated_data
        }, 200

    except Exception as e:
        logging.exception("Erro no handler de personagens.")
        return {'message': f'Um erro inesperado ocorreu: {str(e)}'}, 500