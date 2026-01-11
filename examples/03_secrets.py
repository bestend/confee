"""Secret management with SecretField"""

from confee import ConfigBase, SecretField


class AppConfig(ConfigBase):
    name: str = "my-app"
    api_key: str = SecretField(default="")
    db_password: str = SecretField(default="")


config = AppConfig(
    name="secure-app",
    api_key="sk-1234567890",
    db_password="super_secret_password",
)

# Direct access works
print(f"API Key: {config.api_key}")
print(f"DB Password: {config.db_password}")

# Safe output (secrets masked)
print("\nSafe dict:")
print(config.to_safe_dict())

print("\nSafe JSON:")
print(config.to_safe_json(indent=2))

# Custom mask
print("\nCustom mask:")
print(config.to_safe_dict(mask="[REDACTED]"))
