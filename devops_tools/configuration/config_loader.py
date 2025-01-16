import os
import logging
from typing import TypeVar, Generic, Type
import pydantic

T = TypeVar('T')


class ConfigLoader(Generic[T]):
    _data_as_dict: dict = None
    _model_type = None

    def __init__(self, mode_type: Type[T]):
        self._model_type = mode_type
        self._data_as_dict = dict()

    def load_config(self) -> T:
        self.load_as_dict()
        # this line is not correctly interpreted by pylint but this is not an error
        return pydantic.parse_obj_as(self._model_type, self._data_as_dict)

    def load_as_dict(self) -> dict:
        self._load_as_dict()
        return self._data_as_dict

    def _load_as_dict(self):
        raise NotImplementedError('this method should be redefined')