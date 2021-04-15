"""Queries used with API."""


def query_city(
        rad: float,
        latitude: float,
        longitude: float,
) -> str:
    """Create an overpass query to find the nearest city from the point.

    :param rad: Initial search radius.
    :param latitude: Latitude of the point.
    :param longitude: Longitude of the point.

    return overpass_query : build the query to find the nearest city from your
    point
    """
    overpass_query = f"""[out:json][timeout:800];(node["place"="town"](around:{rad},{latitude},{longitude});node["place"="city"](around:{rad},{latitude},{longitude});node["place"="village"](around:{rad},{latitude},{longitude}););out body;>;out skel qt;"""
    return overpass_query


def query_street(
        rad: float,
        latitude: float,
        longitude: float,
) -> str:
    """Create an overpass query to find the nearest street from the point.

    :param rad: Initial search radius.
    :param latitude: Latitude of the point.
    :param longitude: Longitude of the point.

    return overpass_query : build the query to find the nearest street
    from your point
    """
    overpass_query = f"[out:json][timeout:800];way(around:{rad},{latitude},{longitude})[name];(._;>;);out;"
    return overpass_query


def query_ways(
        latitude: float,
        longitude: float,
) -> str:
    """."""
    overpass_query_get_ways = f"[out:json][timeout:800];way(around:2,{latitude},{longitude})[name];(._;>;);out;"
    return overpass_query_get_ways


def query_nodes(
        id_node: int,
) -> str:
    """Create the query to find a node defined by its id.

    :param id_node: Integer that is a primary key for nodes.

    return overpass_query_get_node : build the query to get the node associated
    to the id
    """
    overpass_query_get_node = f"[out:json][timeout:800];node({id_node});out;"
    return overpass_query_get_node


__all__ = ["query_city", "query_street", "query_ways", "query_nodes"]
