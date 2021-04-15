import logging
import pandas as pd
import unicodedata
from .supercharged_requests import save
from .utils.utils import (conversion_list_dict, distance_from_segment,
                          find_optimal, generate_results, get_order_in_segment,
                          get_road_sections, get_ways, visualisation_sections)

from  .API.get_nearest_city import (get_nearest_city)
from  .API.get_nearest_street import (get_nearest_street)

log_level = logging.INFO
logging.getLogger("package").setLevel(log_level)

coords = [(48.89535, 2.24697), (48.89529, 2.24705),
          (48.89518, 2.2472), (48.89394122, 2.247959188)]

def pipeline_uni(coords):

    result = {}
    roads_dict = {}
    ways_dict = {}
    for coord in coords:
        ways, name = get_ways(*coord)
        roads = get_road_sections(intersection_list=ways, road_name=name)
        ways_dict[coord] = ways
        roads_dict.update(conversion_list_dict(roads))
        dict_distances = distance_from_segment(coord, roads_dict)
        troncon = find_optimal(dict_distances)
        if troncon in result:
            result[troncon].append(coord)
        else:
            result[troncon] = []
            result[troncon].append(coord)

    city = {}
    street = {}
    Resultat_inter = {}
    for troncon in result:
        coords = result[troncon]
        if len(coords) == 1:
            test = {coords[0]: 1}
        else:
            noeuds_troncon = roads_dict[troncon]
            section = [troncon[0], troncon[1],
                       noeuds_troncon[0], noeuds_troncon[1]]
            test = get_order_in_segment(coords, section)
        city[troncon] = ''.join((c for c in unicodedata.normalize('NFD', get_nearest_city(coords[0][0], coords[0][1])) if unicodedata.category(c) != 'Mn')) # Remove accent
        street[troncon] = ''.join((c for c in unicodedata.normalize('NFD', get_nearest_street(coords[0][0], coords[0][1])['tags']['name']) if unicodedata.category(c) != 'Mn')) # Remove accent 
        Resultat_inter[troncon] = test

    Liste_resultat = []
    list_data = []
    for troncon in result:
        coords = result[troncon]
        for coord in coords:
            Liste_resultat.append([coord[0], coord[1], street[troncon], ''.join((c for c in unicodedata.normalize('NFD', troncon[0]) if unicodedata.category(c) != 'Mn')),
                                   ''.join((c for c in unicodedata.normalize('NFD', troncon[1]) if unicodedata.category(c) != 'Mn')), Resultat_inter[troncon][coord], city[troncon]])

            list_data.append(
                [coord, (*troncon, *roads_dict[troncon]), ways_dict[coord]])
    df = pd.DataFrame(Liste_resultat)
    df.columns = ['latitude', 'longitude', 'rue',
                  'debut_troncon', 'fin_troncon', 'num_arbre', 'ville']
    visualisation_sections(list_data, 'map.html')
    save()
    
    return df
