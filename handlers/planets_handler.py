import asyncio
import aiohttp
import logging
from utils import swapi_client

async def _format_planets_details(session: aiohttp.ClientSession, item: dict):
    
    films_task = swapi_client.get_details_from_urls(session, item.get('films', []), 'title')
    residents_task = swapi_client.get_details_from_urls(session, item.get('residents', []), 'name')

    results = await asyncio.gather(
        films_task, residents_task, return_exceptions=True
    )

    films = results[0] if not isinstance(results[0], Exception) else ['desconhecido']
    residents = results[1] if not isinstance(results[1], Exception) else ['desconhecido']

    return {
        'name': item.get('name'),
        'rotation_period': item.get('rotation_period', 'desconhecido') + ' horas' if item.get('rotation_period') != 'unknown' else 'desconhecido',
        'orbital_period': item.get('orbital_period', 'desconhecido') + ' dias' if item.get('orbital_period') != 'unknown' else 'desconhecido',
        'diameter': item.get('diameter', 'desconhecido') + ' km' if item.get('diameter') != 'unknown' else 'desconhecido',
        'climate': item.get('climate', 'desconhecido'),
        'gravity': item.get('gravity', 'desconhecido'),
        'terrain': item.get('terrain', 'desconhecido'),
        'surface_water': item.get('surface_water', 'desconhecido') + '%' if item.get('surface_water') != 'unknown' else 'desconhecido',
        'population': item.get('population', 'desconhecido') + ' habitantes' if item.get('population') != 'unknown' else 'desconhecido',
        'residents': residents or ['desconhecido'],
        'films': films or ['desconhecido'],
    }

async def list_planets(params: dict):
    try:
        name_filter = params.get('name', '').lower()
        sort_by = params.get('sort_by', 'episodio_id')
        order = params.get('order', 'asc')
        page = int(params.get('page', 1))
        limit = int(params.get('limit', 10))
        
        valid_sort_fields = ['titulo', 'episodio_id', 'data_lancamento']
        if sort_by not in valid_sort_fields:
            return {'message': f'sort_by deve ser um de: {valid_sort_fields}'}, 400
        if page < 1 or limit < 1:
            return {'message': 'page e limit devem ser maiores que 0'}, 400

        async with aiohttp.ClientSession() as session:
            url = 'https://swapi.info/api/planets/'
            data = await swapi_client.get_cached_url_data(session, url)
            all_results = []
            all_results.extend(data)

            if name_filter:
                all_results = [item for item in all_results if name_filter in item.get('name', '').lower()]
            tasks = [_format_planets_details(session, item) for item in all_results]
            formatted_data = await asyncio.gather(*tasks, return_exceptions=True)
            formatted_data = [item for item in formatted_data if not isinstance(item, Exception)]

            formatted_data.sort(key=lambda x: x.get(sort_by, 0), reverse=(order == 'desc'))
            start = (page - 1) * limit
            end = start + limit
            paginated_data = formatted_data[start:end]
            

        return {
            'total': len(formatted_data),
            'page': page,
            'limit': limit,
            'data': paginated_data
        }, 200

    except Exception as e:
        logging.exception("Erro no handler de planetas.")
        return {'message': f'Um erro inesperado ocorreu: {str(e)}'}, 500