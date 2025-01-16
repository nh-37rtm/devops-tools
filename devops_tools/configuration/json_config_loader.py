from .config_file_loader import ConfigFileLoader
import logging
from typing import TypeVar, Type

import json

T = TypeVar('T')

class JsonConfigFileLoader(ConfigFileLoader[T]):
    def _load_as_dict(self):
        with open(self._configuration_file) as configuration_file_descriptor:
            self._data_as_dict = json.load(configuration_file_descriptor)
    
