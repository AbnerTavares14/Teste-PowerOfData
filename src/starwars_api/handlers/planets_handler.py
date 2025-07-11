import asyncio
from .base_handler import BaseHandler

class PlanetHandler(BaseHandler):
    API_URL = 'https://swapi.info/api/planets/'
    SORTABLE_FIELDS = ['name', 'rotation_period', 'orbital_period', 'diameter', 'climate', 'gravity', 'terrain']
    DEFAULT_SORT_BY = 'name'

    def __init__(self, params: dict, swapi_client):
        super().__init__(params, swapi_client)

    async def _format_item(self, session, item: dict):
        residents_task = self.swapi_client.get_details_from_urls(session, item.get('residents', []), 'name')
        films_task = self.swapi_client.get_details_from_urls(session, item.get('films', []), 'title')

        results = await asyncio.gather(
            residents_task, films_task, return_exceptions=True
        )

        residents = results[0] if not isinstance(results[0], Exception) else ['desconhecido']
        films = results[1] if not isinstance(results[1], Exception) else ['desconhecido']

        return {
            'nome': item.get('name'),
            'periodo_rotaçao': item.get('rotation_period'),
            'periodo_orbital': item.get('orbital_period'),
            'diametro': item.get('diameter'),
            'clima': item.get('climate'),
            'gravidade': item.get('gravity'),
            'terreno': item.get('terrain'),
            'superficie_agua': item.get('surface_water'),
            'populacao': item.get('population'),
            'residentes': residents,
            'filmes': films
        }
    
    def _get_sort_key(self, item: dict):
        value = item.get(self.sort_by, '')
        if isinstance(value, str):
            return value.lower()
        return value