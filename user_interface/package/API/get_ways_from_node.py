"""Get ways from node."""
import asyncio
from typing import List, Tuple

from ..supercharged_requests import requests
from .queries import query_nodes, query_ways


async def get_ways_from_node_async(
        list_node: List[int]
) -> List[Tuple]:
    """Async implementation."""

    task_list = []
    sem = asyncio.Semaphore(2)
    for indice_delay, id_node in enumerate(list_node):

        task_list.append(
            asyncio.ensure_future(
                requests.async_request(sem=sem, id_node=id_node, delay_async=indice_delay)))
    return await asyncio.gather(*task_list)


def get_ways_from_node(
    list_node: List[int]
) -> List[Tuple]:
    """Find the ways that have common node with your street.

    :param list_node: list of the nodes in your street.

    return list_ways: list of ways that have common nodes with your street
    """

    list_ways = asyncio.run(
        get_ways_from_node_async(
            list_node=list_node))
    return list_ways
