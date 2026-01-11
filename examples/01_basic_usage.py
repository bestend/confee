"""Basic confee usage - load config, access values, type safety"""

from confee import ConfigBase


class DatabaseConfig(ConfigBase):
    host: str = "localhost"
    port: int = 5432


class AppConfig(ConfigBase):
    name: str
    debug: bool = False
    database: DatabaseConfig = DatabaseConfig()


# Create config from dict
config = AppConfig(
    name="my-app",
    debug=True,
    database=DatabaseConfig(host="prod.db", port=5432),
)

# Type-safe access
print(f"App: {config.name}")
print(f"Debug: {config.debug}")
print(f"DB: {config.database.host}:{config.database.port}")

# Convert to dict/JSON
print(config.to_dict())
print(config.to_json())

# Freeze config (immutable)
config.freeze()
try:
    config.name = "changed"
except AttributeError:
    print("Config is frozen!")
