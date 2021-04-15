import logging
from .supercharged_requests import save
from .utils.utils import (conversion_list_dict, distance_from_segment,
                          find_optimal, get_road_sections, get_ways,get_order_in_segment,merge_sections,visualisation_sections_multi)

from  .API.get_nearest_city import (get_nearest_city)
from  .API.get_nearest_street import (get_nearest_street)

log_level = logging.INFO
logging.getLogger("package").setLevel(log_level)

import pandas as pd
import unicodedata

def pipeline_multi(list_input):
    resultat=[]
    city = {}
    ways_dict = {}
    list_data = list()
    for coords in list_input:
        
        result={}
        roads_dict={}
        flag = True
        section = list()
        for coord in coords:
            ways, name = get_ways(*coord)
            ways_dict[coord] = ways
            if flag:
                roads =get_road_sections(intersection_list=ways, road_name=name)
            roads_dict.update(conversion_list_dict(roads))
            dict_distances = distance_from_segment(coord, roads_dict)
            troncon = find_optimal(dict_distances)
            if troncon in result:
                result[troncon].append(coord)
            else:
                result[troncon]=[]
                result[troncon].append(coord)
            if flag:
                city[coords] = ''.join((c for c in unicodedata.normalize('NFD', get_nearest_city(coords[0][0], coords[0][1])) if unicodedata.category(c) != 'Mn')) # Remove accent
                flag = not flag
            section.append([*troncon,*roads_dict[troncon]])
        for tron in result:
            list_data.append(
                [coords[0],coords[1], (*tron, *roads_dict[tron]), ways_dict[coords[0]]])
            resultat_coords=merge_sections(section[0],section[1],roads)
            print(resultat_coords)
            inter=[coords[0][0],coords[0][1],coords[1][0],coords[1][1],''.join((c for c in unicodedata.normalize('NFD', resultat_coords[0]) if unicodedata.category(c) != 'Mn')),''.join((c for c in unicodedata.normalize('NFD', resultat_coords[1]) if unicodedata.category(c) != 'Mn')),city[coords]]
        resultat.append(inter)

    df = pd.DataFrame(resultat)
    df.columns = ['latitude1', 'longitude1','latitude2', 'longitude2',
                  'debut_troncon', 'fin_troncon', 'ville']
    visualisation_sections_multi(list_data, 'map.html')
    save()

    return df
