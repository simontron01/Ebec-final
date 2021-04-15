"""Get nearest city."""
import logging

from .. import config
from ..supercharged_requests import requests
from .queries import query_city

logger = logging.getLogger(__name__)


def get_nearest_city(
        latitude: float,
        longitude: float,
) -> str:
    """Find the nearest city for a given point using binary search.

    :param latitude: latitude of your point.
    :param longitude: longitude of your point.

    return data[0]['tags']['name']: name of the nearest city
    """
    radplus = config.data.get("Nearest_city").get(
        "Binary_search").get("initial_upper_bound_radius", 10000)
    radmoins = config.data.get("Nearest_city").get(
        "Binary_search").get("lower_bound_radius", 0)
    max_iter_before_increased_radius = config.data.get("Nearest_city").get(
        "Binary_search").get("iter_before_increased_radius", 10)

    rad = (radplus + radmoins) / 2
    overpass_query = query_city(
        rad=rad, latitude=latitude, longitude=longitude)
    logging.info(
        "Using openstreetmap API to get nearest city. This can take a while.. ☕")
    response = requests.supercharged_requests(params={'data': overpass_query})
    data = response.get('elements')
    logging.info("Got the response")

    n_iter = 0
    while len(data) != 1:
        if n_iter == max_iter_before_increased_radius:
            n_iter = 0
            radplus += 1000
        else:
            if data:
                n_iter = 0
                radplus = rad
            else:
                n_iter += 1
                radmoins = rad

        rad = (radplus + radmoins) / 2
        overpass_query = query_city(
            rad=rad, latitude=latitude, longitude=longitude)
        response = requests.supercharged_requests(
            params={'data': overpass_query})
        data = response.get('elements')
    return data[0]['tags']['name']
