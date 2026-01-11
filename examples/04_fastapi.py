"""FastAPI integration with confee

Requires: pip install fastapi uvicorn
"""

import os

try:
    from fastapi import Depends, FastAPI
except ImportError:
    print("Install: pip install fastapi uvicorn")
    exit(1)

from confee import ConfigBase, SecretField


class AppConfig(ConfigBase):
    name: str = "my-api"
    debug: bool = False
    secret_key: str = SecretField(default="change-me")


# Load config once
env = os.getenv("ENV", "dev")
config = AppConfig(
    name=f"my-api-{env}",
    debug=env == "dev",
    secret_key="prod-secret" if env == "prod" else "dev-secret",
)
config.freeze()

# Create app
app = FastAPI(title=config.name, debug=config.debug)


def get_config() -> AppConfig:
    return config


@app.get("/health")
async def health(cfg: AppConfig = Depends(get_config)):
    return {"status": "ok", "app": cfg.name, "debug": cfg.debug}


@app.get("/config")
async def get_config_endpoint(cfg: AppConfig = Depends(get_config)):
    return cfg.to_safe_dict()


if __name__ == "__main__":
    print("Run: uvicorn 04_fastapi:app --reload")
    print("Docs: http://localhost:8000/docs")
