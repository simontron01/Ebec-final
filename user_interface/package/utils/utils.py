"""Useful functions."""
import logging
from copy import deepcopy
from operator import itemgetter
from typing import Dict, List, Tuple

import folium
import pandas as pd
from branca.element import Figure
from bs4 import BeautifulSoup
import unicodedata
from numpy import array, cross, dot
from numpy.linalg import norm

from ..API.get_nearest_street import get_nearest_street
from ..API.get_ways_from_node import get_ways_from_node

logger = logging.getLogger(__name__)


def get_nodes(
        latitude: float,
        longitude: float,
) -> List[int]:
    """Get nodes near position.

    :param latitude: latitude of your point.
    :param longitude: longitude of your point.

    return nodes, name: nodes in your street and name of the street
    """
    street = get_nearest_street(latitude=latitude,
                                longitude=longitude)
    name = street.get("tags").get("name")
    nodes = street.get("nodes", "Error with API")
    return nodes, name


def get_ways(
        latitude: float,
        longitude: float,
) -> List[Tuple]:
    """Get ways crossing nearest street of point.

    return list of ways crossing the street containing the
    (latitude, longitude) point
    """
    nodes, name = get_nodes(latitude=latitude,
                            longitude=longitude)
    ways = get_ways_from_node(list_node=nodes)
    return ways, name


def get_road_sections(
        intersection_list: List[Tuple],
        road_name: str,
) -> List[List]:
    """Build road sections in which we can place the coordinates.

    :param interp: Output of get_ways function.
    :param road_name: Used to drop it in intersection_list.

    return sections_list : List[str,str, Tuple(float, float), Tuple(float, float)]
    """
    new_intersection_list = deepcopy(intersection_list)
    sections_list = list()
    new_names_list = list()
    new_coordinates_list = list()
    for i in range(len(new_intersection_list)):
        if len(new_intersection_list[i][0]) > 1:
            if road_name in new_intersection_list[i][0]:
                index_road_name = new_intersection_list[i][0].index(road_name)
                new_intersection_list[i][0].pop(index_road_name)
                new_node_name = '/'.join(new_intersection_list[i][0])
                new_names_list.append(new_node_name)
                new_coordinates_list.append(new_intersection_list[i][1])
    for i in range(1, len(new_names_list)):
        sections_list.append([new_names_list[i - 1], new_names_list[i],
                              new_coordinates_list[i - 1], new_coordinates_list[i]])
    return sections_list


def conversion_list_dict(
    sections_list: List[List],
) -> Dict[Tuple, List]:
    """Convert sections list to a dictionnary.

    :param sections_list: Output of get_road_sections.

    return sections_dict
    """
    sections_dict = {tuple([key1, key2]): list_coordinates for key1,
                     key2, *list_coordinates in sections_list}

    return sections_dict


def distance_from_segment(
        reference: Tuple[float, float],
        coordinates_dict: Dict[Tuple, List],
) -> Dict[Tuple, List]:
    """Compute the distance of a given point to segments.

    :param reference: point.
    :param coordinates_dict: keys are the name of the streets
    that bound the segment, values are list of tuples that
    correspond to the coordinates of the crossings.

    return distance_dict: keys are the name of the streets
    that bound a segment, values are the computed distance
    between the point and the associated segment
    """
    logging.info("Computing shortest segment")
    p3 = array(reference)
    distances_dict = dict()
    for key, (p1, p2) in coordinates_dict.items():
        p1, p2 = array(p1), array(p2)
        distance = norm(cross(p2 - p1, p3 - p1))
        # check if the nearest point is in the segment (p1,p2)
        if dot(p3 - p1, p3 - p2) < 0:
            distances_dict[key] = distance
    if not bool(distances_dict):  # if dict is empty
        for key, (p1, p2) in coordinates_dict.items():
            p1, p2 = array(p1), array(p2)
            distance_p1, distance_p2 = norm(
                reference - p1), norm(reference - p2)
            distance = min(distance_p1, distance_p2)
            distances_dict[key] = distance
    return distances_dict


def find_optimal(
        distances_dict: Dict[Tuple, List],
) -> Tuple[str]:
    """Find optimal segment from distances_dict computed by distance_from_segment.

    :param distances_dict: output of distance_from_segment.

    return key_min: name of the street that bounds the minimum distance segment
    """
    key_min = min(distances_dict.items(), key=itemgetter(1))[0]
    return key_min


def visualisation_sections(
    list_data: List[Tuple],
    map_filename: str,
) -> None:
    """Save the HTML code of the map visualisation. Every tuple correspond to a different point.
    :param list_data: list of tuples which contains
            in position 0: coordinates of the point as a tuple (latitude,longitude),
            in position 1: section of the road related with the point (outpput of find_optimal) with the type List['str','str',tuple,tuple] as the output of get_road_section,
            in position 2: list of all the node of a street (output of get_ways_from_node).
    :param map_filename: name of the map HTML code file.
    return None: the function just save the code with the correct path.
    """

    figure = Figure(height=550, width=750)
    map_display = folium.Map(
        location=[48.896205, 2.260466], tiles='cartodbpositron', zoom_start=14)
    figure.add_child(map_display)
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen',
              'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']
    color_index = 0
    for data in list_data:
        latitude, longitude = data[0]
        section = data[1]
        list_node_street = data[2]
        begin_coordinates = section[2]
        end_coordinates = section[3]
        coordinates = [node[1] for node in list_node_street]
        coordinates = coordinates[coordinates.index(
            begin_coordinates):coordinates.index(end_coordinates) + 1]
        feature_group = folium.FeatureGroup(
            f"Tronçon Point ({latitude}, {longitude})")
        folium.vector_layers.PolyLine(coordinates, popup=f'<b>Tronçon Point ({latitude}, {longitude})</b>',
                                      tooltip=f'Tronçon Point ({latitude}, {longitude})', color=colors[color_index % len(colors)], weight=10).add_to(feature_group)
        folium.Marker(location=[latitude, longitude], popup='Custom Marker 1', tooltip=f'<strong>Point d\'interet ({latitude}, {longitude}) </strong>', icon=folium.Icon(
            color=colors[color_index % len(colors)], icon='none')).add_to(map_display)
        color_index += 1
        feature_group.add_to(map_display)
    folium.LayerControl().add_to(map_display)
    map_display.save(map_filename)
    return None

def visualisation_sections_multi(
    list_data: List[Tuple],
    map_filename: str,
) -> None:
    """Save the HTML code of the map visualisation. Every tuple correspond to a different point.
    :param list_data: list of tuples which contains
            in position 0: coordinates of the point as a tuple (latitude,longitude),
            in position 1: section of the road related with the point (outpput of find_optimal) with the type List['str','str',tuple,tuple] as the output of get_road_section,
            in position 2: list of all the node of a street (output of get_ways_from_node).
    :param map_filename: name of the map HTML code file.
    return None: the function just save the code with the correct path.
    """

    figure = Figure(height=550, width=750)
    map_display = folium.Map(
        location=[48.896205, 2.260466], tiles='cartodbpositron', zoom_start=14)
    figure.add_child(map_display)
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen',
              'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']
    color_index = 0
    for data in list_data:
        latitude1, longitude1 = data[0]
        latitude2, longitude2 = data[1]
        section = data[2]
        list_node_street = data[3]
        begin_coordinates = section[2]
        end_coordinates = section[3]
        coordinates = [node[1] for node in list_node_street]
        coordinates = coordinates[coordinates.index(
            begin_coordinates):coordinates.index(end_coordinates) + 1]
        feature_group = folium.FeatureGroup(
            f"Tronçon Point ({latitude1}, {longitude1})")
        folium.vector_layers.PolyLine(coordinates, popup=f'<b>Tronçon Point ({latitude1}, {longitude1})</b>',
                                      tooltip=f'Tronçon Point ({latitude1}, {longitude1})', color=colors[color_index % len(colors)], weight=10).add_to(feature_group)
        folium.Marker(location=[latitude1, longitude1], popup='Custom Marker 1', tooltip=f'<strong>Point d\'interet ({latitude1}, {longitude1}) </strong>', icon=folium.Icon(
            color=colors[color_index % len(colors)], icon='none')).add_to(map_display)
        folium.Marker(location=[latitude2, longitude2], popup='Custom Marker 1', tooltip=f'<strong>Point d\'interet ({latitude2}, {longitude2}) </strong>', icon=folium.Icon(
            color=colors[color_index % len(colors)], icon='none')).add_to(map_display)
        color_index += 1
        feature_group.add_to(map_display)
    folium.LayerControl().add_to(map_display)
    map_display.save(map_filename)
    return None


def generate_results(
    results_dataframe: pd.core.frame.DataFrame,
    layout_filename: str,
    map_filename: str,
    results_filename: str,
) -> None:
    """ Save the HTML file to display the results with the website theme.

    :param results_dataframe: Output of the pipeline as a pandas DataFrame.
    :param layout_filename: Path to get the layout HTML code file.
    :param map_filename: Path to get the map HTML code file.
    :param results_filename: Path to save the results HTML code file.

    return None: the function just save the HTML code in a file.
    """
    layout = open(layout_filename, 'r')
    html_layout = layout.read()
    soup_layout = BeautifulSoup(html_layout)
    head_layout = soup_layout.find('head')
    footer_layout = soup_layout.find('footer')
    navigation = soup_layout.find('nav')
    scripts_layout = soup_layout.findAll('script')
    map_display = open(map_filename, 'r')
    html_map = map_display.read()
    soup_map = BeautifulSoup(html_map)
    head_map = soup_map.find('head')
    body_map = soup_map.find('body')
    scripts_map = soup_map.findAll('script')
    dataframe_html = results_dataframe.to_html(index=False, classes='striped')
    help_message = ''
    if 'latitude' in results_dataframe.keys():# uni
        for row in range(len(results_dataframe)):
            help_message += f"""<li>votre point {row+1} aux coordonnées ({results_dataframe['latitude'][row]},{results_dataframe['longitude'][row]}) est le point {results_dataframe['num_arbre'][row]} dans {results_dataframe['rue'][row]} entre {results_dataframe['debut_troncon'][row]} et {results_dataframe['fin_troncon'][row]}</li>"""
        help_message = '<div><ul id="help_message">' + help_message + '</ul></div>'
    elif 'latitude1'in results_dataframe.keys(): # multi
        for row in range(len(results_dataframe)):
            help_message += f"""<li>Vos points aux coordonnées ({results_dataframe['latitude1'][row]},{results_dataframe['longitude1'][row]}) et {results_dataframe['latitude2'][row]},{results_dataframe['longitude2'][row]} se trouve entre {results_dataframe['debut_troncon'][row]} et {results_dataframe['fin_troncon'][row]}</li>"""
        help_message = '<div><ul id="help_message">' + help_message + '</ul></div>'
    else:
        help_message = '<div><p> Impossible afficher le texte</p></div>'
    head = str(head_layout)[:-7] + str(head_map)[6:]
    body = '<body>' + str(navigation) + '<div class="row" id = "div_map">' + str(body_map)[
        6:-7]+ '</div>' + '<div>' + dataframe_html + '</div>' + help_message + str(footer_layout) + '</body>'

    message = '<html>' + head + body
    f = open(results_filename, 'w')
    f.write(message)
    for script in scripts_layout:
        f.write(str(script))
        message = message + str(script)
    for script in scripts_map:
        f.write(str(script))
        message =  message + str(script)
    f.close()
    message_html = ''.join((c for c in unicodedata.normalize('NFD', message) if unicodedata.category(c) != 'Mn')) # Remove accent
    return message_html


def get_order_in_segment(
        list_coordinates: List[Tuple],
        section: List[List],
) -> Dict[Tuple, int]:
    """Give the order of coordinates in the segment.

    :param list_coordinates: List of the coordinates of the points you want to order.
    :param section: names of the street that bound the segment, coordinates of the node
    of the bounds of the segment.

    return position:keys are the coordinates, values are their position in the street
    """
    reference_point_coordinates = section[2]
    reference_point = array(reference_point_coordinates)
    distance = dict()
    for x in list_coordinates:
        point = array(x)
        distance[x] = norm(reference_point - point)
    position = dict()
    position_in_street = 1
    while bool(distance):
        coordinates = min(distance, key=lambda k: distance[k])
        distance.pop(coordinates)
        position[coordinates] = position_in_street
        position_in_street += 1
    return position


def merge_sections(
        section_1: List[List],
        section_2: List[List],
        list_sections: List[List],
) -> List[List]:
    """Give the merge name of the streets that bound the merge sections.

    :param section_1:first section to merge.
    :param section_2:second section to merge.
    :param list_sections: output of get_road_sections.
    return merge_sections: names of the street that bound the segment, coordinates of the node
    of the bounds of the segment
    """
    if (section_1 in list_sections) and (section_2 in list_sections):
        is_seen = False
        merge_sections = [0,0,0,0]
        if section_1 == section_2:
            return section_1
        for x in list_sections:
            if x == section_1:
                if is_seen:
                    merge_sections[1] = section_1[1]
                    merge_sections[3] = section_1[3]
                else:
                    merge_sections[0] = section_1[0]
                    merge_sections[2] = section_1[2]
                is_seen = not is_seen
            elif x == section_2:
                if is_seen:
                    merge_sections[1] = section_2[1]
                    merge_sections[3] = section_2[3]
                else:
                    merge_sections[0] = section_2[0]
                    merge_sections[2] = section_2[2]
                is_seen = not is_seen
        return merge_sections
    return 'merge impossible'
