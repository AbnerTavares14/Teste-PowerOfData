import asyncio
from .base_handler import BaseHandler

class StarshipHandler(BaseHandler):
    API_URL = 'https://swapi.info/api/starships/'
    SORTABLE_FIELDS =  ['name', 'model', 'manufacturer', 'cost_in_credits']
    DEFAULT_SORT_BY = 'name'

    def __init__(self, params: dict, swapi_client):
        super().__init__(params, swapi_client)

    async def _format_item(self, session, item: dict):
        pilots_task = self.swapi_client.get_details_from_urls(session, item.get('pilots', []), 'name')
        films_task = self.swapi_client.get_details_from_urls(session, item.get('films', []), 'title')

        pilots, films = await asyncio.gather(pilots_task, films_task, return_exceptions=True)

        return {
            'nome': item.get('name'),
            'model': item.get('model'),
            'manufacturer': item.get('manufacturer'),
            'cost_in_credits': item.get('cost_in_credits'),
            'length': item.get('length'),
            'max_atmosphering_speed': item.get('max_atmosphering_speed'),
            'crew': item.get('crew'),
            'passengers': item.get('passengers'),
            'cargo_capacity': item.get('cargo_capacity'),
            'consumables': item.get('consumables'),
            'hyperdrive_rating': item.get('hyperdrive_rating'),
            'MGLT': item.get('MGLT'),
            'starship_class': item.get('starship_class'),
            'films': films if not isinstance(films, Exception) else [],
            'pilots': pilots if not isinstance(pilots, Exception) else [],
        }

    def _get_sort_key(self, item: dict):
        value = item.get(self.sort_by)

        numeric_fields = ['cost_in_credits', 'length', 'crew', 'passengers', 'cargo_capacity', 'hyperdrive_rating']

        if self.sort_by in numeric_fields:
            try:
                cleaned_value = ''.join(c for c in str(value) if c.isdigit() or c == '.')
                return float(cleaned_value)
            except (ValueError, TypeError):
                return 0
        
        return super()._get_sort_key(item)