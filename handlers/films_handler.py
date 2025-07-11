import asyncio
from .base_handler import BaseHandler

class FilmHandler(BaseHandler):
    API_URL = 'https://swapi.info/api/films/'
    SORTABLE_FIELDS = ['title', 'episode_id', 'release_date', 'director', 'producer']

    DEFAULT_SORT_BY = 'episode_id'

    def __init__(self, params: dict, swapi_client):
        super().__init__(params, swapi_client)

    async def _format_item(self, session, item: dict):
        characters_task = self.swapi_client.get_details_from_urls(session, item.get('characters', []), 'name')
        planets_task = self.swapi_client.get_details_from_urls(session, item.get('planets', []), 'name')
        starships_task = self.swapi_client.get_details_from_urls(session, item.get('starships', []), 'name')
        vehicles_task = self.swapi_client.get_details_from_urls(session, item.get('vehicles', []), 'name')
        species_task = self.swapi_client.get_details_from_urls(session, item.get('species', []), 'name')

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
            'title': item.get('title'),
            'episode_id': item.get('episode_id'),
            'director': item.get('director'),
            'producer': item.get('producer'),
            'release_date': item.get('release_date'),
            'opening_crawl': item.get('opening_crawl'),
            'characters': characters,
            'planets': planets,
            'starships': starships,
            'vehicles': vehicles,
            'especies': species
        }
    
    def _get_sort_key(self, item: dict):
        value = item.get(self.sort_by, '0')
        if self.sort_by in ['episode_id']:
            try:
                return int(value)
            except (ValueError, TypeError):
                return 0
        if isinstance(value, str):
            return value.lower()
        return value