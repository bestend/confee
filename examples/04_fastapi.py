"""Example 04: FastAPI Integration

This example demonstrates:
- Using confee with FastAPI web framework
- Environment-based configuration selection
- Config validation at application startup
- Dependency injection patterns
- Health check endpoints with config info

NOTE: This example requires FastAPI and uvicorn:
  pip install fastapi uvicorn
"""

from typing import Literal

try:
    from fastapi import Depends, FastAPI
    from fastapi.responses import JSONResponse
except ImportError:
    print("❌ This example requires FastAPI and uvicorn")
    print("   Install with: pip install fastapi uvicorn")
    print()
    exit(1)

from confee import ConfigBase, SecretField


# Step 1: Define configuration schema
class DatabaseConfig(ConfigBase):
    """Database configuration."""

    host: str = "localhost"
    port: int = 5432
    database: str = "myapp"
    username: str = "admin"
    password: str = SecretField(default="", description="Database password")
    pool_size: int = 10
    max_overflow: int = 20


class CacheConfig(ConfigBase):
    """Cache configuration."""

    enabled: bool = True
    host: str = "localhost"
    port: int = 6379
    ttl: int = 3600
    password: str = SecretField(default="", description="Redis password")


class AppConfig(ConfigBase):
    """Application configuration."""

    app_name: str = "my-api"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    secret_key: str = SecretField(default="change-me-in-production", description="JWT signing key")
    database: DatabaseConfig
    cache: CacheConfig


# Step 2: Load configuration based on environment
# In production, you'd load from file:
# config = AppConfig.load(config_file=f"config.{env}.yaml")

# For this example, we'll create different configs
dev_config = AppConfig(
    app_name="my-api",
    environment="development",
    debug=True,
    database=DatabaseConfig(
        database="dev_db",
        password="dev_password",
    ),
    cache=CacheConfig(
        password="dev_redis_password",
    ),
)

prod_config = AppConfig(
    app_name="my-api",
    environment="production",
    debug=False,
    host="0.0.0.0",
    port=8000,
    workers=16,
    secret_key="production-secret-key-xyz",
    database=DatabaseConfig(
        host="prod-db.cluster.local",
        database="production_db",
        password="super_secret_prod_password",
        pool_size=50,
    ),
    cache=CacheConfig(
        host="redis.cluster.local",
        password="redis_prod_password",
    ),
)

# Select config based on environment
import os

env = os.getenv("APP_ENV", "development")
config = prod_config if env == "production" else dev_config

# Freeze config to prevent accidental modification
config.freeze()

print("=" * 60)
print("confee Example 04: FastAPI Integration")
print("=" * 60)
print()
print(f"🚀 Environment: {config.environment}")
print(f"📋 App Name: {config.app_name}")
print(f"🐛 Debug Mode: {config.debug}")
print(f"🔌 Port: {config.port}")
print()

# Step 3: Create FastAPI app with config
app = FastAPI(
    title=config.app_name,
    debug=config.debug,
    version="1.0.0",
)


# Step 4: Dependency injection pattern
def get_config() -> AppConfig:
    """Dependency to inject config into routes."""
    return config


def get_database_url(cfg: AppConfig = Depends(get_config)) -> str:
    """Get database URL from config."""
    # In real app, use actual password from config.database.password
    return f"postgresql://{cfg.database.username}@{cfg.database.host}:{cfg.database.port}/{cfg.database.database}"


# Step 5: Health check endpoint with safe config
@app.get("/health")
async def health_check(cfg: AppConfig = Depends(get_config)):
    """Health check endpoint with config info."""
    return {
        "status": "healthy",
        "app": cfg.app_name,
        "environment": cfg.environment,
        "debug": cfg.debug,
        # Only expose safe config info
        "database_host": cfg.database.host,
        "cache_enabled": cfg.cache.enabled,
    }


# Step 6: Config endpoint (safe output)
@app.get("/config")
async def get_config_endpoint(cfg: AppConfig = Depends(get_config)):
    """Get current configuration (secrets masked)."""
    return JSONResponse(
        content=cfg.to_safe_dict(),
        headers={"X-Environment": cfg.environment},
    )


# Step 7: Example API endpoint using config
@app.get("/api/data")
async def get_data(
    cfg: AppConfig = Depends(get_config),
    db_url: str = Depends(get_database_url),
):
    """Example endpoint that uses config."""
    return {
        "message": f"Data from {cfg.environment} environment",
        "database": db_url,
        "cache_enabled": cfg.cache.enabled,
    }


# Step 8: Startup event with config validation
@app.on_event("startup")
async def startup_event():
    """Validate config and initialize resources on startup."""
    print()
    print("🔧 Application Startup")
    print("-" * 60)
    print(f"  Environment: {config.environment}")
    print(f"  Debug: {config.debug}")
    print(f"  Workers: {config.workers}")
    print(f"  Database: {config.database.host}:{config.database.port}")
    print(f"  Cache: {config.cache.host}:{config.cache.port}")
    print("-" * 60)

    # Log safe config (secrets masked)
    print()
    print("📋 Configuration (safe):")
    config.print(safe=True)
    print()

    # Validate critical config
    if config.environment == "production":
        if config.debug:
            raise ValueError("Debug mode must be disabled in production!")
        if config.secret_key == "change-me-in-production":
            raise ValueError("Production secret key not configured!")

    print("✅ Configuration validated successfully")
    print()


# Step 9: Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print()
    print("🛑 Application Shutdown")
    print()


# Step 10: Run instructions
if __name__ == "__main__":
    print("=" * 60)
    print("💡 How to Run This Example:")
    print("=" * 60)
    print()
    print("  # Development mode")
    print("  uvicorn 04_fastapi:app --reload")
    print()
    print("  # Production mode")
    print("  APP_ENV=production uvicorn 04_fastapi:app --workers 4")
    print()
    print("  # With custom port")
    print("  uvicorn 04_fastapi:app --host 0.0.0.0 --port 3000")
    print()
    print("=" * 60)
    print("📡 Available Endpoints:")
    print("=" * 60)
    print()
    print("  GET http://localhost:8000/health")
    print("      → Health check with basic config info")
    print()
    print("  GET http://localhost:8000/config")
    print("      → Full config (secrets masked)")
    print()
    print("  GET http://localhost:8000/api/data")
    print("      → Example endpoint using config")
    print()
    print("  GET http://localhost:8000/docs")
    print("      → Interactive API documentation")
    print()
    print("=" * 60)
    print("✨ Key Integration Patterns:")
    print("=" * 60)
    print()
    print("  1. Load config once at module level")
    print("  2. Freeze config to prevent modification")
    print("  3. Use Depends(get_config) for injection")
    print("  4. Validate config in startup event")
    print("  5. Only expose safe config in endpoints")
    print("  6. Environment-based config selection")
    print()
    print("=" * 60)
    print()
    print("🚀 Start the server with:")
    print("   uvicorn 04_fastapi:app --reload")
    print()
