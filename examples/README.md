# confee Examples

Simple, focused examples demonstrating core confee features.

## Examples

### 01_basic_usage.py
Basic configuration with type safety and freezing.

```bash
python examples/01_basic_usage.py
```

### 02_cli_overrides.py
Automatic CLI args and environment variable handling.

```bash
# With env vars
CONFEE_NAME=prod python examples/02_cli_overrides.py

# With CLI args
python examples/02_cli_overrides.py debug=true workers=16
```

### 03_secrets.py
Secret masking with SecretField.

```bash
python examples/03_secrets.py
```

### 04_fastapi.py
FastAPI integration with config freezing.

```bash
# Requires: pip install fastapi uvicorn
python examples/04_fastapi.py
# Then: uvicorn 04_fastapi:app --reload
```

## What You'll Learn

- **01**: Type-safe config, dict/JSON conversion, freezing
- **02**: Auto CLI/env parsing, priority order
- **03**: Secret masking, safe output
- **04**: FastAPI dependency injection, startup validation

## Key Concepts

### Automatic Overrides
confee automatically reads:
- Environment variables (`CONFEE_*` prefix)
- CLI arguments (`python app.py key=value`)
- Config files (YAML/JSON/TOML)

Priority: **CLI > Env > File > Defaults**

### Type Safety
All configs use Pydantic for validation and IDE autocomplete.

### Secret Masking
Use `SecretField()` for sensitive data. Automatically masked in `to_safe_dict()`.
