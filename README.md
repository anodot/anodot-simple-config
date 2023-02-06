This library allows to load application configuration in a dataclass from different sources.

To get the configuration:
1. Create a configuration source that implements the `simple_config.ConfigurationSource` interface or use an existing one from `simple_config`. The configuration source should implement the `def get_key(self, key: str) -> Optional[Any]:` method 
2. Create a config dataclass specifying types of the configuration fields and default values.
3. Call `simple_config.load_config(config_class, config_source())` to get the configuration.


Example:
```python
import simple_config

from dataclasses import dataclass
from typing import Any, Optional


class DummyConfigSource(simple_config.ConfigSource):
    def get_key(self, key: str) -> Optional[Any]:
            return {
                "host": "localhost",
                "port": 8080,
                "debug": True,
            }.get(key)

@dataclass
class Config:
    host: str
    fallback_host: Optional[str]
    port: int = 80
    debug: bool = False


config_1 = simple_config.load_config(Config, DummyConfigSource())
config_2 = simple_config.load_config(Config, simple_config.EnvVarsConfigSource())
```


### Multiple configuration sources

You can use multiple configuration sources to load the configuration. The configuration will be loaded from the first source that has a value for the field.
For that use the `simple_config.ConfigSourceInterpolation` class, pass a list of configuration sources to it in the order of priority.

Example:
```python
import simple_config

from dataclasses import dataclass


@dataclass
class Config:
    host: str
    port: int


config = simple_config.load_config(
    Config,
    simple_config.ConfigSourceInterpolation([
        simple_config.CommandLineArgsConfigSource(),
        simple_config.EnvVarsConfigSource(),
    ])
)
```
