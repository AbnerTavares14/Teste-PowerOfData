import asyncio
from .base_handler import BaseHandler

class CharacterHandler(BaseHandler):
    API_URL = 'https://swapi.info/api/people/'
    SORTABLE_FIELDS = ['nome', 'altura', 'peso']
    DEFAULT_SORT_BY = 'nome'

    def __init__(self, params: dict, swapi_client):
        super().__init__(params, swapi_client)

    async def _format_item(self, session, item: dict):
        planet_url = item.get('homeworld')
        planet_task = asyncio.create_task(self.swapi_client.get_cached_url_data(session, planet_url))

        film_titles_task = self.swapi_client.get_details_from_urls(session, item.get('films', []), 'title')
        species_names_task = self.swapi_client.get_details_from_urls(session, item.get('species', []), 'name')
        starship_names_task = self.swapi_client.get_details_from_urls(session, item.get('starships', []), 'name')
        vehicle_names_task = self.swapi_client.get_details_from_urls(session, item.get('vehicles', []), 'name')

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
            'altura': item.get('height', 'unknown'), 
            'peso': item.get('mass', 'unknown'), 
            'planeta_natal': planet_name,
            'filmes': film_titles or ['desconhecido'],
            'especies': species_names or ['desconhecido'],
            'naves': starship_names or ['desconhecido'],
            'veiculos': vehicle_names or ['desconhecido'],
        }

    def _get_sort_key(self, item: dict):
        value = item.get(self.sort_by, '0')
        if self.sort_by in ['altura', 'peso']:
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0
        if isinstance(value, str):
            return value.lower()
        return value