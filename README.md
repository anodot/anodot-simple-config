This library allows to load application configuration in a dataclass from different sources.

To get the configuration:
1. Create a configuration source that implements the `simeple_config.ConfigurationSource` interface or use an existing one.
2. Create a dataclass specifying types of the configuration fields and default values.
3. Call `simple_config.load_config(config_class, config_source())` to get the configuration.


Example:
```python
import simple_config

from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    host: str
    fallback_host: Optional[str]
    port: int = 8080
    debug: bool = False


config = simple_config.load_config(Config, simple_config.EnvVarsConfigSource())
```


### Multiple configuration sources

You can use multiple configuration sources to load the configuration. The configuration will be loaded from the first source that has a value for the field.
For that use the `simple_config.ConfigSourceInterpolation` class, pass the list of configuration sources to it in the order of priority.

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
        simple_config.EnvVarsConfigSource(),
        simple_config.CommandLineArgsConfigSource(),
    ])
)
```
