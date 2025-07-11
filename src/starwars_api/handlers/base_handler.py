import asyncio
import aiohttp
import logging

class BaseHandler:
    API_URL = None
    SORTABLE_FIELDS = ['name']
    DEFAULT_SORT_BY = 'name'
    FILTERABLE_FIELDS = ['name'] 


    def __init__(self, params: dict, swapi_client):
        self.params = params
        self.swapi_client = swapi_client
        self.sort_by = self.params.get('sort_by', self.DEFAULT_SORT_BY)
        self.order = self.params.get('order', 'asc')
        self.page = int(self.params.get('page', 1))
        self.limit = int(self.params.get('limit', 10))
        self.name_filter = self.params.get('name', '').lower()

    
    async def get_by_id(self, resource_id: str):
        if not self.API_URL:
            return {'message': 'API URL não configurada'}, 500
        url = f"{self.API_URL}{resource_id}/"
        try:
            async with aiohttp.ClientSession() as session:
                item_data = await self.swapi_client.get_cached_url_data(session, url)
                if not item_data:
                    return {'message': 'Recurso não encontrado'}, 404
                
                formatted_item = await self._format_item(session, item_data)
                return formatted_item, 200
        except Exception as e:
            logging.exception(f"Erro ao buscar recurso por ID {resource_id}")
            return {'message': f'Um erro inesperado ocorreu: {str(e)}'}, 500
    
    async def _format_item(self, session, item: dict):
        logging.warning(f"O método _format_item não foi implementado para {self.__class__.__name__}")
        return item

    def _get_sort_key(self, item: dict):
        value = item.get(self.sort_by, '0')
        if isinstance(value, str) and value.isnumeric():
            return int(value)
        if isinstance(value, str):
            return value.lower()
        return value

    async def list_resources(self):
        if self.sort_by not in self.SORTABLE_FIELDS:
            return {'message': f'sort_by deve ser um de: {self.SORTABLE_FIELDS}'}, 400

        try:
            async with aiohttp.ClientSession() as session:
                all_results = await self.swapi_client.get_cached_url_data(session, self.API_URL)

                filtered_results = []
                
                reserved_params = {'page', 'limit', 'sort_by', 'order'}

                active_filters = {
                    key: value for key, value in self.params.items() 
                    if key in self.FILTERABLE_FIELDS and key not in reserved_params
                }

                if not active_filters:
                    filtered_results = all_results
                else:
                    for item in all_results:
                        match = True
                        for key, value in active_filters.items():
                            if str(item.get(key, '')).lower() != str(value).lower():
                                match = False
                                break
                        if match:
                            filtered_results.append(item)

                tasks = [self._format_item(session, item) for item in filtered_results]
                formatted_data = await asyncio.gather(*tasks)

                formatted_data.sort(key=self._get_sort_key, reverse=(self.order == 'desc'))

                start = (self.page - 1) * self.limit
                end = start + self.limit
                paginated_data = formatted_data[start:end]

            return {
                'total_results': len(formatted_data),
                'page': self.page,
                'limit': self.limit,
                'results': paginated_data,
            }, 200
        except Exception as e:
            logging.exception(f"Erro ao listar recursos para {self.__class__.__name__}")
            return {'message': f'Um erro inesperado ocorreu: {str(e)}'}, 500