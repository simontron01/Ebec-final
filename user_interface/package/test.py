import logging

from .utils.utils import (conversion_list_dict, distance_from_segment,
                          find_optimal, get_road_sections, get_ways)

log_level = logging.INFO
logging.getLogger("package").setLevel(log_level)


def test():
    coords = [(48.89394122, 2.247959188), (48.89535, 2.24697)]
    for coord in coords:
        ways, name = get_ways(*coord)
        roads = get_road_sections(intersection_list=ways, road_name=name)
        roads_dict = conversion_list_dict(roads)
        dict_distances = distance_from_segment(coord, roads_dict)
        result = find_optimal(dict_distances)
        print(result)


#coord = 48.89394122, 2.247959188
