from enum import Enum
from typing import Union

from ..utils.io_utils import dump_data

class SerializationType(Enum):
    JSON = 'json'
    PKL = 'pkl'

class IODict(dict):
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = filepath
    
    @property
    def file_path(self):
        return self._file_path
    
    @file_path.setter
    def path(self, val):
        self._file_path = val

    def __setitem__(self, key, value) -> None:
        super().__setitem__(key, value)
        dump_data(data=self, file_path=self.file_path)
    
    def __delitem__(self, key) -> None:
        super().__delitem__(key)
        dump_data(data=self, file_path=self.file_path)
