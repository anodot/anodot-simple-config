import os
import pytest

from dataclasses import dataclass
from enum import Enum
from simple_config import config_sources, simple_config
from typing import Optional

current_dir = os.path.dirname(os.path.realpath(__file__))


def test_create_config_success():
    class SomeEnum(Enum):
        A = 'a'
        B = 'b'

    @dataclass
    class Config:
        a: str
        b: int
        c: bool
        d: bool
        e: float
        enum_value: SomeEnum
        f: Optional[str]
        g: Optional[int]
        h: str = 'default'

    class MockConfigSource(config_sources.EnvVarsConfigSource):
        def get_key(self, key):
            return {
                'a': 'a',
                'b': '1',
                'c': 'true',
                'd': 0,
                'e': '1.1',
                'enum_value': 'b',
                'g': '1',
            }.get(key)

    config = simple_config.load_config(Config, MockConfigSource())
    assert config == Config('a', 1, True, False, 1.1, SomeEnum('b'), None, 1, 'default')


def test_fail_create_config_missing_field():
    @dataclass
    class Config:
        not_existing: str

    class MockConfigSource(config_sources.EnvVarsConfigSource):
        def get_key(self, key):
            return None

    with pytest.raises(simple_config.ConfigException):
        simple_config.load_config(Config, MockConfigSource())


def test_fail_create_config_invalid_float():
    @dataclass
    class Config:
        float_val: float

    class MockConfigSource(config_sources.EnvVarsConfigSource):
        def get_key(self, key):
            return {
                'float_val': 'not_a_float',
            }.get(key)

    with pytest.raises(simple_config.ConfigException):
        simple_config.load_config(Config, MockConfigSource())


def test_fail_create_config_invalid_bool():
    @dataclass
    class Config:
        invalid_bool_1: bool

    class MockConfigSource(config_sources.EnvVarsConfigSource):
        def get_key(self, key):
            return {
                'invalid_bool_1': 'not_a_bool',
            }.get(key)

    with pytest.raises(simple_config.ConfigException):
        simple_config.load_config(Config, MockConfigSource())


def test_fail_create_config_invalid_enum():
    class SomeEnum(Enum):
        A = 'a'
        B = 'b'

    @dataclass
    class Config:
        enum_val: SomeEnum

    class MockConfigSource(config_sources.EnvVarsConfigSource):
        def get_key(self, key):
            return {
                'enum_val': 'c',
            }.get(key)

    with pytest.raises(simple_config.ConfigException):
        simple_config.load_config(Config, MockConfigSource())


def test_fail_create_config_invalid_config_class():
    class NotAConfig:
        pass

    with pytest.raises(TypeError):
        simple_config.load_config(NotAConfig, config_sources.EnvVarsConfigSource())


def test_create_config_success_from_ini():
    @dataclass
    class Config:
        float_val: float
        int_val: int

    config = simple_config.load_config(
        Config, config_sources.IniFileFlatConfigSource(f'{current_dir}/data/test_config.ini')
    )
    assert config == Config(1.0, 2)


def test_create_config_success_from_interpolation():
    @dataclass
    class Config:
        float_val: float
        int_val: int
        str_val: str

    class MockConfigSource(config_sources.EnvVarsConfigSource):
        def get_key(self, key):
            return {
                'int_val': 10,
                'str_val': 'string',
            }.get(key)

    config = simple_config.load_config(
        Config,
        config_sources.ConfigSourceInterpolation([
            config_sources.IniFileFlatConfigSource(f'{current_dir}/data/test_config.ini'),
            MockConfigSource(),
        ])
    )
    assert config == Config(1.0, 2, 'string')
