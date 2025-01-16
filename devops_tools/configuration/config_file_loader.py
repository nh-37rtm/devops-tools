import logging
import os
from typing import Type, TypeVar

from .config_loader import ConfigLoader

T = TypeVar('T')

class ConfigFileLoader(ConfigLoader[T]):

    _configuration_file = None
    _data_as_dict = None
    _model_type: Type = None

    def __init__(self, mode_type: Type[T], configuration_file: str):
        if not os.path.exists( configuration_file ):
            raise(Exception('configuration file %s should exists' % configuration_file))
        self._configuration_file = configuration_file
        self._model_type = mode_type
