"""Supercharged requests to handle errors from the API."""
import asyncio
import logging
from functools import wraps
from os import path
from typing import Any, List, Tuple

import httpx
import joblib
import requests

from .. import config
from ..API import queries

logger = logging.getLogger(__name__)
overpass_url = config.data.get("API").get(
    "overpass_url", "http://overpass-api.de/api/interpreter")

cache_dict = dict()


def load():
    """Load the cache dictionary cache_dict from repertory."""
    global cache_dict
    if path.exists("cached_requests/raw_cache"):
        cache_dict = joblib.load("cached_requests/raw_cache")
    else:
        logger.warning("cache not found")


def save():
    """Save the cache dictionary cache_dict."""
    joblib.dump(cache_dict, "cached_requests/raw_cache")


def add_method(cls):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        setattr(cls, func.__name__, wrapper)
        # Note we are not binding func, but wrapper which accepts self but does exactly the same as func
        return func  # returning func means func can still be used normally
    return decorator


@add_method(requests)
def supercharged_requests(*args, **kwargs):

    asked_query = kwargs.get("params").get("data")
    if asked_query in cache_dict.keys():
        logger.info("Cache : hit non async !")
        return cache_dict.get(asked_query)
    logger.info(f"cache missed {asked_query}")
    retrieved_data = requests.get(url=overpass_url, *args, **kwargs)
    counter_requests = 0
    while retrieved_data.status_code != 200:
        logger.warning(
            f"Error {retrieved_data.status_code} from API not async. Requesting again...")
        retrieved_data = requests.get(url=overpass_url, *args, **kwargs)
        counter_requests += 1
        if counter_requests > 30:
            logger.warning("DEAD API")
    data = retrieved_data.json()
    cache_dict[asked_query] = data

    return data


@add_method(requests)
async def async_request(
    sem: Any,
    id_node: int,
    delay_async: int,
    *args,
    **kwargs,
) -> Tuple[List, Tuple]:
    async with sem, httpx.AsyncClient() as client:
        timeout = httpx.Timeout(800.0)
        overpass_query_get_node = queries.query_nodes(id_node)
        if overpass_query_get_node in cache_dict.keys():
            logger.info("Cacha : hit async")
            node = cache_dict.get(overpass_query_get_node)
        else:
            logger.info("cache missed")
            await asyncio.sleep(delay_async * 0.1)
            retrieved_data = await client.get(
                f"{overpass_url}?data={overpass_query_get_node}", timeout=timeout)
            counter_requests = 0
            while retrieved_data.status_code != 200:
                logger.warning(
                    f"Error {retrieved_data.status_code} from API. Requesting async {delay_async} again...")
                retrieved_data = await client.get(
                    f"{overpass_url}?data={overpass_query_get_node}", timeout=timeout)
                counter_requests += 1
            node = retrieved_data.json()
            cache_dict[overpass_query_get_node] = node
        logger.warning(node)
        try:
            latitude = node['elements'][0]['lat']
            longitude = node['elements'][0]['lon']
        except:
            logger.warning(node)

        overpass_query_get_ways = queries.query_ways(
            latitude=latitude, longitude=longitude)
        if overpass_query_get_ways in cache_dict.keys():
            logger.info("Cacha : hit async")
            data = cache_dict.get(overpass_query_get_ways)
        else:
            retrieved_data = await client.get(
                f"{overpass_url}?data={overpass_query_get_ways}", timeout=timeout)
            counter_requests = 0
            while retrieved_data.status_code != 200:
                logger.warning(
                    f"Error {retrieved_data.status_code} from API. Requesting async {delay_async} again...")
                retrieved_data = await client.get(
                    f"{overpass_url}?data={overpass_query_get_ways}", timeout=timeout)
                counter_requests += 1
            data = retrieved_data.json()
            cache_dict[overpass_query_get_ways] = data
        ways = [x for x in data['elements']
                if x['type'] == 'way']
        names = [way['tags']['name'] for way in ways]
        output_request = ((list(set(names))), (latitude, longitude))
        return output_request
