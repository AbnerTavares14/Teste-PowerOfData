import pytest
from unittest.mock import AsyncMock

from src.starwars_api.handlers import CharacterHandler

@pytest.mark.asyncio
async def test_format_character_item_success():
    """
    Testa se o método _format_item formata corretamente um personagem
    quando todas as chamadas de API (mockadas) são bem-sucedidas.
    """
    mock_swapi_client = AsyncMock()

    mock_swapi_client.get_cached_url_data.return_value = {'name': 'Tatooine'}
    
    mock_swapi_client.get_details_from_urls.side_effect = [
        ['A New Hope'], 
        [],             
        [],             
        []              
    ]

    sample_raw_character = {
        'name': 'Luke Skywalker',
        'height': '172',
        'mass': '77',
        'homeworld': 'https://swapi.info/api/planets/1/',
        'films': ['https://swapi.info/api/films/1/'],
        'species': [],
        'starships': [],
        'vehicles': []
    }

    handler = CharacterHandler(params={}, swapi_client=mock_swapi_client)

    formatted_character = await handler._format_item(session=None, item=sample_raw_character)

    assert formatted_character['name'] == 'Luke Skywalker'
    assert formatted_character['homeworld'] == 'Tatooine'
    assert formatted_character['films'] == ['A New Hope']
    assert formatted_character['species'] == ['desconhecido']
    assert formatted_character['starships'] == ['desconhecido']
    assert formatted_character['vehicles'] == ['desconhecido']

def test_get_sort_key_for_numeric_fields():
    """
    Testa se o método _get_sort_key converte corretamente os campos
    numéricos 'height' e 'peso' para a ordenação.
    """
    handler_height = CharacterHandler(params={'sort_by': 'height'}, swapi_client=None)
    handler_mass = CharacterHandler(params={'sort_by': 'mass'}, swapi_client=None)

    item_com_dados = {'height': '172', 'mass': '77.5'}
    item_com_unknown = {'height': 'unknown', 'mass': 'unknown'}

    assert handler_height._get_sort_key(item_com_dados) == 172
    assert handler_mass._get_sort_key(item_com_dados) == 77.5
    assert handler_height._get_sort_key(item_com_unknown) == 0
    assert handler_mass._get_sort_key(item_com_unknown) == 0