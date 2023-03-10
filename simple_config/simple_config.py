import dataclasses
import typing

from enum import EnumMeta
from simple_config.config_sources import ConfigSource
from typing import Any, Optional, Type

TRUE_VALUES = {'true', 'yes', 'on', '1', 1, True}
FALSE_VALUES = {'false', 'no', 'off', '0', 0, False}

DataclassType = typing.TypeVar('DataclassType')


def load_config(config_class: Type[DataclassType], config_source: ConfigSource) -> DataclassType:
    """
    Accepts a dataclass and a config source and returns an instance of the dataclass with loaded config values
    """

    if not dataclasses.is_dataclass(config_class):
        raise TypeError('`config_class` parameter must be a dataclass')

    fields, error_fields = [], {}
    for field in dataclasses.fields(config_class):
        try:
            value = _extract_value(config_source, field)

            if value is None and not is_optional(field):
                raise ConfigException(f'Config key `{field.name}` is missing')

            fields.append(value)
        except ConfigException as e:
            error_fields[field.name] = str(e)

    if error_fields:
        raise ConfigException(f'Failed to load config fields: {error_fields}')

    return config_class(*fields)


def _extract_value(config_source: ConfigSource, field: dataclasses.Field) -> Optional[Any]:
    value = config_source.get_key(field.name)
    if value is None and _has_default_value(field):
        value = field.default
    elif value is not None:
        value = _cast_to_config_field_type(field, value)
    return value


def _has_default_value(field: dataclasses.Field):
    return field.default is not dataclasses.MISSING


def _cast_to_config_field_type(field: dataclasses.Field, value: Any):
    if value is None:
        raise ValueError('Expecting a non-None value')
    type_ = extract_type_from_optional(field.type) if is_optional(field) else field.type
    try:
        return _cast_to_bool(value) if type_ is bool else type_(value)
    except ValueError:
        message = f'Failed to convert value `{value}` to the type {type_}'
        if isinstance(type_, EnumMeta):
            message += ', the value must be one of: ' + ', '.join(x.value for x in type_)

        raise ConfigException(message)


def _cast_to_bool(value) -> bool:
    if isinstance(value, str):
        value = value.lower()
    if value not in [*TRUE_VALUES, *FALSE_VALUES]:
        raise ConfigException((
            f'Invalid value `{value}` for the boolean type field. '
            f'Must be one of {[*TRUE_VALUES, *FALSE_VALUES]} (case insensitive)'
        ))
    return value in TRUE_VALUES


def is_optional(field: dataclasses.Field) -> bool:
    return get_origin(field.type) is typing.Union and type(None) in get_args(field.type)


def extract_type_from_optional(type_: typing.Type) -> typing.Type:
    for type_ in get_args(type_):
        if not isinstance(type_, type(None)):
            return type_


def get_args(t: typing.Type):
    return getattr(t, '__args__', ()) if t is not typing.Generic else typing.Generic


def get_origin(t: typing.Type):
    return getattr(t, '__origin__', None)


class ConfigException(Exception):
    pass
