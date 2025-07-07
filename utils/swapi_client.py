import asyncio
import aiohttp
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

_fetch_data_results = {}
_fetch_data_locks = {}

async def _fetch_url_data(session: aiohttp.ClientSession, url: str):
    if not url:
        logging.warning("Tentativa de buscar URL vazia.")
        return None
    try:
        await asyncio.sleep(0.05)
        async with session.get(url, timeout=5) as response:
            response.raise_for_status()
            data = await response.json()
            return data
    except aiohttp.ClientError as e:
        logging.error(f"Erro aiohttp ao buscar {url}: {e}")
        return None
    except asyncio.TimeoutError:
        logging.error(f"Timeout ao buscar {url}")
        return None
    except Exception as e:
        logging.error(f"Erro inesperado ao buscar {url}: {e}")
        return None

async def get_cached_url_data(session: aiohttp.ClientSession, url: str):
    if not url:
        return None
    if url not in _fetch_data_locks:
        _fetch_data_locks[url] = asyncio.Lock()
        
    async with _fetch_data_locks[url]:
        if url in _fetch_data_results:
            return _fetch_data_results[url]

        data = await _fetch_url_data(session, url)
        _fetch_data_results[url] = data
        
        if len(_fetch_data_results) > 100:
            oldest_key = next(iter(_fetch_data_results))
            del _fetch_data_results[oldest_key]
            if oldest_key in _fetch_data_locks:
                del _fetch_data_locks[oldest_key]
        return data

async def get_details_from_urls(session: aiohttp.ClientSession, urls: list[str], key: str):
    if not urls:
        return []
    tasks = [get_cached_url_data(session, url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    names = []
    for r in results:
        if isinstance(r, dict) and r.get(key):
            names.append(r[key])
        else:
            names.append('desconhecido')
    return names