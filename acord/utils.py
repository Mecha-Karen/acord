# Some helper objects used in the lib

from typing import Any
from copy import deepcopy


def _payload_dict_to_json(base, **keys) -> Any:
    # Converts kwargs to base excluding all keys
    base = base(**keys)
    to_exclude = list()
    
    for key, value in base.dict().items():
        if value is None and key not in keys:
            to_exclude.append(key)
    
    return base.json(exclude=set(to_exclude))


def copy(obj, **kwds) -> Any:
    return deepcopy(obj, **kwds)
