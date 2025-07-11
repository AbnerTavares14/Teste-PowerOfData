import pytest
from unittest.mock import AsyncMock

from src.starwars_api.handlers import FilmHandler

@pytest.mark.asyncio
async def test_list_characters_from_film():
    """
    Testa a lógica de buscar os personagens de um filme específico.
    Verifica se o FilmHandler orquestra corretamente as chamadas
    e reutiliza o CharacterHandler para formatação.
    """
    sample_film_data = {
        'title': 'A New Hope',
        'characters': [
            'https://swapi.info/api/people/1/', 
            'https://swapi.info/api/people/5/'  
        ]
    }
    sample_character_luke = {'name': 'Luke Skywalker', 'homeworld': 'p1'}
    sample_character_leia = {'name': 'Leia Organa', 'homeworld': 'p2'}

    mock_swapi_client = AsyncMock()

    async def get_data_side_effect(session, url):
        if url == 'https://swapi.info/api/films/1/':
            return sample_film_data
        elif url == 'https://swapi.info/api/people/1/':
            return sample_character_luke
        elif url == 'https://swapi.info/api/people/5/':
            return sample_character_leia
        else:
            return {'name': 'mocked_detail'}

    mock_swapi_client.get_cached_url_data.side_effect = get_data_side_effect
    mock_swapi_client.get_details_from_urls.return_value = ['mocked_list_item']

    film_handler = FilmHandler(params={}, swapi_client=mock_swapi_client)

    result, status = await film_handler.list_characters_from_film(film_id='1')

    assert status == 200
    assert len(result) == 2
    assert result[0]['nome'] == 'Luke Skywalker'
    assert result[1]['nome'] == 'Leia Organa'
    
    assert mock_swapi_client.get_cached_url_data.call_count == 5