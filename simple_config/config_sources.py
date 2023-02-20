import configparser
import os
import sys
import typing

from abc import ABC, abstractmethod
from typing import Optional, Any


class ConfigSource(ABC):
    @abstractmethod
    def get_key(self, key: str) -> Optional[Any]:
        pass


class EnvVarsConfigSource(ConfigSource):
    def get_key(self, key: str) -> Optional[Any]:
        return os.environ.get(key.upper())


class CommandLineArgsConfigSource(ConfigSource):
    def __init__(self):
        for arg in sys.argv[1:]:
            if arg.startswith('--'):
                key, value = arg[2:].split('=')
                setattr(self, key, value)

    def get_key(self, key: str) -> Optional[Any]:
        try:
            return getattr(self, key.lower())
        except AttributeError:
            return None


class IniFileFlatConfigSource(ConfigSource):
    """
    Config source that reads keys from all sections from an .ini file, ALL keys must be unique.

    WARNING: please be aware that keys in the config file that are specified as `key =` (without a value)
    will be loaded as an empty string, not None, so the default value from the dataclass will not be applied
    and type casting of that field will fail if it is not a string.
    If you want to specify a key without a value, use `key` (without the `=` sign).
    """

    def __init__(self, file_path: str):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f'Config file not found: {file_path}')

        self.flat_config = {}
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(file_path)

        for section in config.sections():
            self.flat_config.update(dict(config[section]))

    def get_key(self, key: str) -> Optional[Any]:
        return self.flat_config.get(key)


class ConfigSourceInterpolation(ConfigSource):
    def __init__(self, config_sources: typing.List[ConfigSource]):
        self.config_sources = config_sources

    def get_key(self, key: str) -> Optional[Any]:
        for config_source in self.config_sources:
            value = config_source.get_key(key)
            if value is not None:
                return value
        return None
