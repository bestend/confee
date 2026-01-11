# Advanced Features

This document covers advanced confee features for power users.

---

## Table of Contents

- [Config Freezing](#config-freezing)
- [JSON Schema](#json-schema)
- [Remote Config Loading](#remote-config-loading)
- [Plugin System](#plugin-system)
- [Config Diff & Merge](#config-diff--merge)
- [Configuration Options](#configuration-options)
- [File References](#file-references)
- [Integration Examples](#integration-examples)

---

## Config Freezing

Make configurations immutable at runtime to prevent accidental modifications.

```python
from confee import ConfigBase

class AppConfig(ConfigBase):
    name: str
    debug: bool = False

config = AppConfig.load(config_file="config.yaml")

# Freeze the configuration
config.freeze()

# This will raise AttributeError
try:
    config.name = "new-name"
except AttributeError:
    print("Config is frozen!")

# Check if frozen
print(config.is_frozen())  # True

# Unfreeze to allow modifications
config.unfreeze()
config.name = "updated"  # OK now

# Create a mutable copy of frozen config
frozen_config.freeze()
mutable_copy = frozen_config.copy_unfrozen()
```

---

## JSON Schema

Generate and validate JSON schemas for your configurations.

### Generate Schema

```python
from confee import ConfigBase

class AppConfig(ConfigBase):
    """Application configuration"""
    name: str
    port: int = 8080

# Generate schema as dict
schema = AppConfig.to_json_schema()

# Save to file
AppConfig.save_schema("config.schema.json")

# Generate with custom title/description
schema = AppConfig.to_json_schema(
    title="My App Config",
    description="Configuration for my application"
)
```

### Generate Example Config

```python
# Generate example YAML
example_yaml = AppConfig.generate_example_config(format="yaml")
print(example_yaml)
# Output:
# name: example_string
# port: 8080

# Generate example JSON
example_json = AppConfig.generate_example_config(format="json")

# Without comments
example = AppConfig.generate_example_config(
    format="yaml",
    with_comments=False
)
```

### Validate Data

```python
from confee.schema import SchemaValidator

validator = SchemaValidator(AppConfig)

# Validate data
data = {"name": "myapp", "port": 3000}
is_valid = validator.validate(data)

# Check without raising
if validator.is_valid(data):
    config = AppConfig(**data)
```

---

## Remote Config Loading

Load configurations from remote URLs.

### Sync Loading (stdlib)

Uses `urllib` from standard library (no extra dependencies).

```python
from confee.loaders import ConfigLoader

# Load from URL (auto-detects format)
data = ConfigLoader.load_remote("https://example.com/config.yaml")
config = AppConfig(**data)

# Specify format explicitly
data = ConfigLoader.load_remote(
    "https://example.com/config",
    format="json"
)
```

### Async Loading (requires aiohttp)

Install with remote support:

```bash
pip install confee[remote]
```

```python
from confee.async_loader import AsyncConfigLoader
import asyncio

async def load_config():
    loader = AsyncConfigLoader()
    
    # Load single file
    data = await loader.load_remote("https://example.com/config.yaml")
    
    # Load multiple files and merge
    configs = await loader.load_files([
        "https://example.com/base.yaml",
        "https://example.com/prod.yaml"
    ])
    
    return AppConfig(**configs)

config = asyncio.run(load_config())
```

### File Watching

Watch for configuration file changes:

```python
from confee.async_loader import ConfigWatcher
import asyncio

async def watch_config():
    def on_change(new_data):
        print(f"Config changed: {new_data}")
    
    watcher = ConfigWatcher("config.yaml", callback=on_change)
    watcher.start()
    
    # Keep watching
    await asyncio.sleep(3600)
    
    # Stop watching
    watcher.stop()

asyncio.run(watch_config())
```

---

## Plugin System

Extend confee with custom loaders, validators, and hooks.

### Custom Format Loaders

```python
from confee import PluginRegistry

# Register with decorator
@PluginRegistry.loader(".ini")
def load_ini(path: str) -> dict:
    import configparser
    parser = configparser.ConfigParser()
    parser.read(path)
    return {s: dict(parser[s]) for s in parser.sections()}

# Or register directly
def load_custom(path: str) -> dict:
    # Your loading logic
    return {}

PluginRegistry.register_loader(".custom", load_custom)

# Now use it
config = AppConfig.load(config_file="config.ini")
```

### Multiple Extensions

```python
@PluginRegistry.loader([".conf", ".cfg"])
def load_conf(path: str) -> dict:
    # Handle both .conf and .cfg files
    return {}
```

### Validators

Add custom validation logic:

```python
@PluginRegistry.validator
def validate_ports(data: dict) -> dict:
    if "port" in data and not (1024 <= data["port"] <= 65535):
        raise ValueError("Port must be between 1024 and 65535")
    return data

# Validators run automatically during load
config = AppConfig.load(config_file="config.yaml")
```

### Pre/Post Load Hooks

```python
@PluginRegistry.pre_load
def before_load(data: dict) -> dict:
    print("Loading config...")
    # Modify data before validation
    data["timestamp"] = datetime.now()
    return data

@PluginRegistry.post_load
def after_load(config: ConfigBase) -> ConfigBase:
    print("Config loaded successfully!")
    # Post-process config
    return config
```

### List Registered Plugins

```python
# List all supported extensions
extensions = PluginRegistry.list_extensions()
print(extensions)  # ['.yaml', '.yml', '.json', '.toml', '.ini']

# Clear all plugins (use with caution)
PluginRegistry.clear()
```

---

## Config Diff & Merge

Compare and merge configurations.

### Diff Configs

```python
config1 = AppConfig(name="app1", debug=True, workers=4)
config2 = AppConfig(name="app2", debug=True, workers=8)

# Get differences
diff = config1.diff(config2)
print(diff)
# Output: {'name': ('app1', 'app2'), 'workers': (4, 8)}

# Only changed fields are returned
```

### Merge Configs

```python
base_config = AppConfig(name="app", debug=False, workers=4)
override_config = AppConfig.from_dict({"debug": True})

# Merge (right side takes precedence)
merged = base_config.merge(override_config)
print(merged.debug)  # True
print(merged.workers)  # 4 (from base)
```

### Nested Config Merge

```python
from confee.async_loader import ConfigMerger

merger = ConfigMerger()

base = {
    "app": {"name": "myapp", "version": "1.0"},
    "database": {"host": "localhost"}
}

override = {
    "app": {"version": "2.0"},
    "database": {"port": 5432}
}

# Deep merge
result = merger.deep_merge(base, override)
print(result)
# {
#   "app": {"name": "myapp", "version": "2.0"},
#   "database": {"host": "localhost", "port": 5432}
# }
```

---

## Configuration Options

Fine-tune how configurations are loaded and merged.

### Source Order

Control priority of configuration sources:

```python
# Default order: CLI > Environment > File
config = AppConfig.load(
    config_file="config.yaml",
    source_order=["cli", "env", "file"]
)

# File takes precedence
config = AppConfig.load(
    config_file="config.yaml",
    source_order=["file", "cli", "env"]
)

# Only use environment and file
config = AppConfig.load(
    config_file="config.yaml",
    source_order=["env", "file"]
)
```

### Custom Environment Prefix

```python
# Default prefix: CONFEE_
config = AppConfig.load(
    config_file="config.yaml",
    env_prefix="MYAPP_"
)

# Now use: MYAPP_NAME, MYAPP_DEBUG, etc.
```

### Strict Mode

```python
# Strict mode (reject unknown fields) - default
config = AppConfig.load(
    config_file="config.yaml",
    strict=True
)

# Non-strict mode (allow unknown fields)
config = AppConfig.load(
    config_file="config.yaml",
    strict=False
)

# Toggle at class level
AppConfig.set_strict_mode(False)
```

### Lenient File Loading

```python
# Raise error if file not found (default)
config = AppConfig.load(
    config_file="config.yaml",
    lenient=False
)

# Continue with defaults if file not found
config = AppConfig.load(
    config_file="config.yaml",
    lenient=True
)
```

---

## File References

Reference external files and configs within your configuration files.

### Text File References

```yaml
# config.yaml
api_key: "@file:secrets/api_key.txt"
ssh_key: "@file:/absolute/path/to/key.txt"
```

The content of the file will be read and used as the value.

### Config File References

```yaml
# config.yaml
database: "@config:configs/database.yaml"
logging: "@config:configs/logging.json"
```

The referenced config file will be loaded and merged.

### Nested References

```yaml
# config.yaml
app:
  name: myapp
  secrets: "@config:secrets.yaml"

# secrets.yaml
api_key: "@file:api_key.txt"
db_password: "@file:db_password.txt"
```

### Circular Reference Detection

confee automatically detects circular references and raises an error:

```yaml
# a.yaml
b: "@config:b.yaml"

# b.yaml
a: "@config:a.yaml"  # Circular reference!
```

---

## Integration Examples

### FastAPI

```python
from fastapi import FastAPI
from confee import ConfigBase

class AppConfig(ConfigBase):
    app_name: str
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

# Load config from environment and file
config = AppConfig.load(
    config_file="config.yaml",
    source_order=["env", "file"]
)

app = FastAPI(
    title=config.app_name,
    debug=config.debug
)

@app.get("/config")
def get_config():
    # Return safe config (secrets masked)
    return config.to_safe_dict()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.host, port=config.port)
```

### Django

```python
# settings.py
from confee import ConfigBase

class DjangoConfig(ConfigBase):
    secret_key: str = SecretField()
    debug: bool = False
    database_url: str
    allowed_hosts: list[str] = []

config = DjangoConfig.load(
    config_file="config.yaml",
    env_prefix="DJANGO_"
)

SECRET_KEY = config.secret_key
DEBUG = config.debug
DATABASES = {
    'default': dj_database_url.parse(config.database_url)
}
ALLOWED_HOSTS = config.allowed_hosts
```

### Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  config.yaml: |
    name: production-app
    debug: false
    workers: 16

---
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
  - name: app
    image: myapp:latest
    env:
    - name: CONFEE_DEBUG
      value: "false"
    - name: CONFEE_WORKERS
      value: "16"
    volumeMounts:
    - name: config
      mountPath: /etc/config
  volumes:
  - name: config
    configMap:
      name: app-config
```

### Docker Compose

```yaml
version: '3.8'
services:
  app:
    build: .
    environment:
      - CONFEE_DEBUG=false
      - CONFEE_DATABASE__HOST=postgres
      - CONFEE_DATABASE__PORT=5432
    volumes:
      - ./config.yaml:/app/config.yaml
    depends_on:
      - postgres
  
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=secret
```

### AWS Lambda

```python
import os
from confee import ConfigBase, SecretField

class LambdaConfig(ConfigBase):
    function_name: str
    timeout: int = 30
    memory: int = 512
    api_key: str = SecretField()

def lambda_handler(event, context):
    # Load from environment variables
    config = LambdaConfig.load(
        env_prefix="LAMBDA_",
        source_order=["env"]
    )
    
    # Your logic here
    return {
        'statusCode': 200,
        'body': f'Function: {config.function_name}'
    }
```

---

## Additional Resources

- **GitHub**: [https://github.com/bestend/confee](https://github.com/bestend/confee)
- **PyPI**: [https://pypi.org/project/confee](https://pypi.org/project/confee)
- **Issues**: [https://github.com/bestend/confee/issues](https://github.com/bestend/confee/issues)

---

**Back to [README](./README.md)**
