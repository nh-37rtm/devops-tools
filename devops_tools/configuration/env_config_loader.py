from configuration.config_loader import ConfigLoader
import src.utils as u

import logging
from typing import TypeVar, Type

T = TypeVar('T')

class EnvConfigLoader(ConfigLoader[T]):

    _variable_filter: str
    _object_seperator: str

    def __init__(self, 
                 model_type: Type[T],
                 environnement_dictionary: dict[str, str],
                 variable_filter: str,
                 object_separator: str = '__'):

        ConfigLoader.__init__(self, model_type)
        self._variable_filter = variable_filter
        self._data_as_dict = environnement_dictionary
        self._object_seperator = object_separator

    def _load_as_dict(self):
        self._data_as_dict =  u.env_vars_to_dict(
            self._data_as_dict, self._variable_filter,
            self._object_seperator)
