"""CLI and environment variable overrides

confee automatically reads environment variables with CONFEE_ prefix
and CLI arguments. No manual parsing needed!
"""

import os

from confee import ConfigBase


class AppConfig(ConfigBase):
    name: str = "my-app"
    debug: bool = False
    workers: int = 4


# Set environment variables (CONFEE_ prefix by default)
os.environ["CONFEE_NAME"] = "env-app"
os.environ["CONFEE_WORKERS"] = "8"

# .load() automatically reads env vars and CLI args
config = AppConfig.load()

print(f"Name: {config.name}")
print(f"Workers: {config.workers}")
print(f"Debug: {config.debug}")

print("\nPriority: CLI > Env > File > Defaults")
print("Try: CONFEE_DEBUG=true python 02_cli_overrides.py workers=16")

# Clean up
os.environ.pop("CONFEE_NAME", None)
os.environ.pop("CONFEE_WORKERS", None)
