"""Example 03: Managing Secrets with SecretField

This example demonstrates:
- Using SecretField for sensitive data
- Masking secrets in output (to_safe_dict, to_safe_json)
- Safe vs unsafe printing
- Loading secrets from environment or files
- Best practices for secret management
"""

import os

from confee import ConfigBase, SecretField


class DatabaseConfig(ConfigBase):
    """Database configuration with sensitive credentials."""

    host: str = "localhost"
    port: int = 5432
    database: str = "myapp"
    username: str = "admin"
    # Mark password as secret - will be masked in outputs
    password: str = SecretField(default="", description="Database password")


class APIConfig(ConfigBase):
    """External API configuration."""

    base_url: str = "https://api.example.com"
    # API keys should always be secrets
    api_key: str = SecretField(default="", description="API authentication key")
    # OAuth tokens are also sensitive
    access_token: str = SecretField(default="", description="OAuth access token")
    timeout: int = 30


class AppConfig(ConfigBase):
    """Application configuration with multiple secrets."""

    app_name: str = "secure-app"
    environment: str = "production"
    # Application-level secret
    secret_key: str = SecretField(default="", description="Application secret for signing")
    database: DatabaseConfig
    api: APIConfig


print("=" * 60)
print("confee Example 03: Secret Management")
print("=" * 60)
print()

# Step 1: Create config with secrets
print("🔐 Creating Configuration with Secrets:")
config = AppConfig(
    app_name="my-secure-app",
    environment="production",
    secret_key="app-secret-key-12345",
    database=DatabaseConfig(
        host="prod-db.example.com",
        username="prod_user",
        password="super_secret_db_password_xyz",
    ),
    api=APIConfig(
        base_url="https://api.example.com",
        api_key="sk-1234567890abcdefghijklmnop",
        access_token="oauth-token-abcdefgh123456",
    ),
)
print("  ✅ Config created with 4 secret fields")
print()

# Step 2: Direct access still works (for application logic)
print("🔓 Direct Access (for application use):")
print(f"  Database Password: {config.database.password}")
print(f"  API Key: {config.api.api_key}")
print(f"  App Secret: {config.secret_key}")
print()

# Step 3: Safe dictionary output (masks secrets)
print("🛡️  Safe Dictionary (secrets masked):")
safe_dict = config.to_safe_dict()
print(f"  App Name: {safe_dict['app_name']}")
print(f"  Secret Key: {safe_dict['secret_key']}")
print(f"  Database Password: {safe_dict['database']['password']}")
print(f"  API Key: {safe_dict['api']['api_key']}")
print(f"  Access Token: {safe_dict['api']['access_token']}")
print()

# Step 4: Unsafe dictionary (shows actual values)
print("⚠️  Unsafe Dictionary (actual values):")
unsafe_dict = config.to_dict()
print(f"  Database Password: {unsafe_dict['database']['password']}")
print(f"  API Key: {unsafe_dict['api']['api_key']}")
print()

# Step 5: Safe JSON output
print("📦 Safe JSON Output:")
safe_json = config.to_safe_json(indent=2)
print(safe_json)
print()

# Step 6: Custom mask character
print("🎭 Custom Mask Character:")
custom_safe_dict = config.to_safe_dict(mask="[REDACTED]")
print(f"  Database Password: {custom_safe_dict['database']['password']}")
print(f"  API Key: {custom_safe_dict['api']['api_key']}")
print()

# Step 7: Safe printing (for logs)
print("📝 Safe Print (for logging):")
print("  " + "-" * 56)
config.print(safe=True)
print("  " + "-" * 56)
print()

# Step 8: Loading secrets from environment
print("🌍 Loading Secrets from Environment:")
os.environ["CONFEE_DATABASE__PASSWORD"] = "env_db_password"
os.environ["CONFEE_API__API_KEY"] = "env_api_key_xyz"

env_config = AppConfig(
    app_name="env-app",
    secret_key="app-key-from-env",
    database=DatabaseConfig(
        password=os.getenv("CONFEE_DATABASE__PASSWORD", ""),
    ),
    api=APIConfig(
        api_key=os.getenv("CONFEE_API__API_KEY", ""),
        access_token="token-from-vault",
    ),
)

print("  Loaded secrets from environment variables:")
safe_env = env_config.to_safe_dict()
print(f"    DB Password: {safe_env['database']['password']}")
print(f"    API Key: {safe_env['api']['api_key']}")
print()

# Clean up
os.environ.pop("CONFEE_DATABASE__PASSWORD", None)
os.environ.pop("CONFEE_API__API_KEY", None)

# Step 9: Best practices
print("💡 Best Practices:")
print()
print("  1. ✅ DO: Mark all sensitive fields with SecretField()")
print("     - Passwords, API keys, tokens, certificates")
print("     - Encryption keys, signing secrets")
print()
print("  2. ✅ DO: Use to_safe_dict() for logging")
print("     - Prevents accidental secret exposure in logs")
print("     - Safe for error messages and debugging")
print()
print("  3. ✅ DO: Load secrets from environment or secret managers")
print("     - Environment variables (CONFEE_* prefix)")
print("     - File references: api_key: '@file:secrets/api_key.txt'")
print("     - Secret management tools (Vault, AWS Secrets Manager)")
print()
print("  4. ❌ DON'T: Commit secrets to version control")
print("     - Use .gitignore for config files with secrets")
print("     - Use template files (config.yaml.example)")
print()
print("  5. ❌ DON'T: Print unsafe config in production")
print("     - Always use print(safe=True) in production code")
print("     - Never log to_dict() or to_json() without safe=True")
print()

# Step 10: Practical patterns
print("🔧 Practical Patterns:")
print()
print("  # Pattern 1: Logging safe config at startup")
print("  logger.info('Starting with config: %s', config.to_safe_json())")
print()
print("  # Pattern 2: Environment-based secret loading")
print("  class Config(ConfigBase):")
print("      db_password: str = SecretField(")
print("          default=os.getenv('DB_PASSWORD', '')")
print("      )")
print()
print("  # Pattern 3: File-based secrets (Kubernetes)")
print("  # config.yaml:")
print("  # database:")
print("  #   password: '@file:/var/run/secrets/db-password'")
print()
print("  # Pattern 4: Conditional masking")
print("  if os.getenv('DEBUG') == 'true':")
print("      print(config.to_dict())  # Show secrets in dev")
print("  else:")
print("      print(config.to_safe_dict())  # Mask in production")
print()

print("=" * 60)
print("✨ Key Takeaways:")
print("  1. Use SecretField() for all sensitive data")
print("  2. to_safe_dict() and to_safe_json() mask secrets")
print("  3. Direct access still works (config.api_key)")
print("  4. print(safe=True) for safe logging")
print("  5. Load from env vars or secret managers")
print("=" * 60)
print()
print("📚 Next: Try 04_fastapi.py for web framework integration")
