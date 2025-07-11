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

    assert formatted_character['nome'] == 'Luke Skywalker'
    assert formatted_character['planeta_natal'] == 'Tatooine'
    assert formatted_character['filmes'] == ['A New Hope']
    assert formatted_character['especies'] == ['desconhecido']
    assert formatted_character['naves'] == ['desconhecido']
    assert formatted_character['veiculos'] == ['desconhecido']

def test_get_sort_key_for_numeric_fields():
    """
    Testa se o método _get_sort_key converte corretamente os campos
    numéricos 'altura' e 'peso' para a ordenação.
    """
    handler_altura = CharacterHandler(params={'sort_by': 'altura'}, swapi_client=None)
    handler_peso = CharacterHandler(params={'sort_by': 'peso'}, swapi_client=None)

    item_com_dados = {'altura': '172', 'peso': '77.5'}
    item_com_unknown = {'altura': 'unknown', 'peso': 'unknown'}

    assert handler_altura._get_sort_key(item_com_dados) == 172.0
    assert handler_peso._get_sort_key(item_com_dados) == 77.5
    assert handler_altura._get_sort_key(item_com_unknown) == 0
    assert handler_peso._get_sort_key(item_com_unknown) == 0