"""Example 02: CLI and Environment Variable Overrides

This example demonstrates:
- Overriding config values from command line
- Environment variable integration
- Override priority (CLI > env > file)
- Nested field overrides (database.host=...)
"""

import os

from confee import ConfigBase


class DatabaseConfig(ConfigBase):
    """Database connection settings."""

    host: str = "localhost"
    port: int = 5432
    max_connections: int = 10


class CacheConfig(ConfigBase):
    """Cache settings."""

    enabled: bool = True
    ttl: int = 3600
    provider: str = "redis"


class AppConfig(ConfigBase):
    """Main application configuration."""

    name: str = "my-app"
    environment: str = "development"
    debug: bool = False
    workers: int = 4
    database: DatabaseConfig
    cache: CacheConfig


print("=" * 60)
print("confee Example 02: CLI and Environment Overrides")
print("=" * 60)
print()

# Step 1: Show base configuration (from defaults)
print("📋 Base Configuration (defaults):")
base_config = AppConfig(
    database=DatabaseConfig(),
    cache=CacheConfig(),
)
print(f"  Environment: {base_config.environment}")
print(f"  Debug: {base_config.debug}")
print(f"  Workers: {base_config.workers}")
print(f"  Database Host: {base_config.database.host}")
print(f"  Cache Enabled: {base_config.cache.enabled}")
print()

# Step 2: Simulate environment variables
print("🌍 Setting Environment Variables:")
os.environ["CONFEE_ENVIRONMENT"] = "production"
os.environ["CONFEE_DEBUG"] = "false"
os.environ["CONFEE_WORKERS"] = "16"
os.environ["CONFEE_DATABASE__HOST"] = "prod-db.example.com"  # Note: double underscore for nested
os.environ["CONFEE_CACHE__ENABLED"] = "true"

print("  CONFEE_ENVIRONMENT=production")
print("  CONFEE_DEBUG=false")
print("  CONFEE_WORKERS=16")
print("  CONFEE_DATABASE__HOST=prod-db.example.com")
print("  CONFEE_CACHE__ENABLED=true")
print()

# Step 3: Create config with environment overrides
print("📦 Config with Environment Overrides:")
print("  (In real usage: AppConfig.load(config_file='app.yaml'))")
print()

# Manually apply env overrides for demo
env_config = AppConfig(
    environment=os.getenv("CONFEE_ENVIRONMENT", "development"),
    debug=os.getenv("CONFEE_DEBUG", "false").lower() == "true",
    workers=int(os.getenv("CONFEE_WORKERS", "4")),
    database=DatabaseConfig(
        host=os.getenv("CONFEE_DATABASE__HOST", "localhost"),
    ),
    cache=CacheConfig(
        enabled=os.getenv("CONFEE_CACHE__ENABLED", "true").lower() == "true",
    ),
)

print(f"  Environment: {env_config.environment} (from env)")
print(f"  Debug: {env_config.debug} (from env)")
print(f"  Workers: {env_config.workers} (from env)")
print(f"  Database Host: {env_config.database.host} (from env)")
print(f"  Cache Enabled: {env_config.cache.enabled} (from env)")
print()

# Step 4: Simulate CLI arguments
print("⌨️  Simulating CLI Arguments:")
print("  python app.py environment=staging workers=32 database.port=3306")
print()

# In real usage, confee parses sys.argv automatically
# For demo, we'll manually apply overrides
cli_overrides = {
    "environment": "staging",
    "workers": 32,
    "database": {"port": 3306},
}

# Apply CLI overrides (highest priority)
final_config = env_config.model_copy(
    update={
        "environment": cli_overrides["environment"],
        "workers": cli_overrides["workers"],
        "database": env_config.database.model_copy(update=cli_overrides["database"]),
    }
)

print("🎯 Final Configuration (CLI > Env > File > Defaults):")
print(f"  Environment: {final_config.environment} (from CLI)")
print(f"  Debug: {final_config.debug} (from env)")
print(f"  Workers: {final_config.workers} (from CLI)")
print(f"  Database Host: {final_config.database.host} (from env)")
print(f"  Database Port: {final_config.database.port} (from CLI)")
print(f"  Cache Enabled: {final_config.cache.enabled} (from env)")
print()

# Step 5: Show priority order
print("📊 Override Priority (highest to lowest):")
print("  1. ⌨️  CLI arguments     (e.g., python app.py debug=true)")
print("  2. 🌍 Environment vars  (e.g., CONFEE_DEBUG=true)")
print("  3. 📄 Config file       (e.g., debug: true in yaml)")
print("  4. 🎯 Default values    (e.g., debug: bool = False)")
print()

# Step 6: Nested field override syntax
print("🔗 Nested Field Override Syntax:")
print("  CLI:  database.host=prod.example.com")
print("  Env:  CONFEE_DATABASE__HOST=prod.example.com")
print("        (note: double underscore __ for nesting)")
print()

# Step 7: Practical examples
print("💡 Practical Usage Examples:")
print()
print("  # Development (defaults)")
print("  python app.py")
print()
print("  # Production (env vars in Kubernetes/Docker)")
print("  CONFEE_ENVIRONMENT=production \\")
print("  CONFEE_DATABASE__HOST=prod-db.cluster.local \\")
print("  python app.py")
print()
print("  # Staging with debug (CLI override)")
print("  python app.py environment=staging debug=true workers=2")
print()
print("  # Override multiple nested fields")
print("  python app.py \\")
print("    database.host=localhost \\")
print("    database.port=3306 \\")
print("    cache.provider=memcached \\")
print("    cache.ttl=7200")
print()

# Clean up environment variables
for key in [
    "CONFEE_ENVIRONMENT",
    "CONFEE_DEBUG",
    "CONFEE_WORKERS",
    "CONFEE_DATABASE__HOST",
    "CONFEE_CACHE__ENABLED",
]:
    os.environ.pop(key, None)

print("=" * 60)
print("✨ Key Takeaways:")
print("  1. CLI args have highest priority")
print("  2. Environment vars second (CONFEE_ prefix)")
print("  3. Use __ (double underscore) for nested env vars")
print("  4. Use . (dot) for nested CLI args")
print("  5. Great for 12-factor app patterns")
print("=" * 60)
print()
print("📚 Next: Try 03_secrets.py for secure config management")
