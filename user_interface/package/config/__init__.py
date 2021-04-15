"""Load yaml config file."""
from contextlib import contextmanager

import yaml


@contextmanager
def opened_w_error(filename, mode="r"):
    """Open file and raise error if any."""
    try:
        file = open(filename, mode)
    except IOError as err:
        yield None, err
    else:
        try:
            yield file, None
        finally:
            file.close()


with opened_w_error("config.yaml") as (config_file, err):
    if err:
        print("Error while reading config file")
    else:
        data = yaml.load(config_file, Loader=yaml.FullLoader)

__all__ = ["data"]
