from configuration.config_file_loader import ConfigFileLoader
import src.utils as u

from typing import TypeVar, Type

import os

from dotenv import dotenv_values

T = TypeVar('T')

class EnvConfigFileLoader(ConfigFileLoader[T]):

    _variable_filter: str
    _object_seperator: str
    _raw_data: str

    def __init__(self,
                 model_type: Type,
                 configuration_file: str,
                 variable_filter: str = 'DEVOPS_',
                 object_seperator: str = '__'):
        
        ConfigFileLoader.__init__(self, model_type, configuration_file)
        self._object_seperator = object_seperator
    
        self._variable_filter = variable_filter
        self._raw_data = dotenv_values(self._configuration_file)
    def _load_as_dict(self):
        self._data_as_dict = u.env_vars_to_dict(
            self._raw_data, 
            self._variable_filter, 
            self._object_seperator)
        
