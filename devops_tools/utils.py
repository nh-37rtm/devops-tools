from os import environ

def env_vars_to_dict(
        _in: dict[str, str], 
        _filter: str = 'DEVOPS_',
        _object_separator: str = '__') -> dict[str, str]:
    """map environement variables format to dict.
        :param _in: Dict to map data into
        :type _in: dict[str]
        :param _filter: str for using as a prefix to filter environment variables
        :type _filter: str
    """
    _out_map = dict()

    for key, value in _in.items():
    
        if not key.startswith(_filter):
            continue

        key_name = key.replace(_filter, '', 1)
        current_element_position = 0
        key_elements = key_name.lower().split(_object_separator)
        current_attribute = _out_map
        for attribute in key_elements:
            if not attribute in current_attribute:
                if current_element_position == len(key_elements) -1 :
                    current_attribute[attribute] = value
                else:
                    current_attribute[attribute] = dict()
            current_attribute=current_attribute[attribute]
            current_element_position+= 1

    return _out_map
