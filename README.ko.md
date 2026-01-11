<p align="center">
  <img src="https://raw.githubusercontent.com/bestend/confee/main/assets/logo.png" width="360" />
</p>

<div align="center">

**Language:** 한국어 | [English](./README.md)

Hydra 스타일 설정 + Pydantic 타입 안전성 + 자동 도움말 생성

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/bestend/confee/actions/workflows/tests.yml/badge.svg)](https://github.com/bestend/confee/actions/workflows/tests.yml)

</div>

---

## ☕️ 개요

**confee**는 설정 관리를 단순하고, 타입 안전하며, 직관적으로 만들어줍니다. 설정 파일, Pydantic 검증, 환경 변수, CLI 인자를 매끄럽게 통합합니다.

---

## ✨ 기능

- **🎯 타입 안전** — Pydantic V2 검증 & IDE 자동완성
- **📋 다중 포맷** — YAML, JSON, TOML 자동 감지
- **🔄 오버라이드** — CLI 인자 & 환경 변수, 우선순위 제어
- **🔐 시크릿 마스킹** — `SecretField()`로 민감 데이터 보호
- **🧊 불변성** — 런타임 설정 동결
- **📐 확장 가능** — 플러그인 시스템, JSON 스키마, 비동기 로딩

---

## 📦 설치

```bash
pip install confee
```

---

## 🚀 빠른 시작

```python
from confee import ConfigBase, SecretField

class AppConfig(ConfigBase):
    name: str
    debug: bool = False
    workers: int = 4
    api_key: str = SecretField(default="")

config = AppConfig.load(config_file="config.yaml")
print(config.name)  # 타입 안전한 접근
```

```yaml
# config.yaml
name: my-app
workers: 8
api_key: secret123
```

```bash
# CLI로 오버라이드
python app.py name=production debug=true

# 환경 변수로 오버라이드
export CONFEE_NAME=production
```

---

## 💡 주요 패턴

### 중첩 설정

```python
class DatabaseConfig(ConfigBase):
    host: str = "localhost"
    port: int = 5432

class AppConfig(ConfigBase):
    database: DatabaseConfig

# 오버라이드: python app.py database.host=prod.db
```

### 파일 참조 & 시크릿 마스킹

```yaml
api_key: "@file:secrets/api_key.txt"
```

```python
config.to_safe_dict()  # {'api_key': '***MASKED***', ...}
```

### 설정 동결 & 커스텀 접두사

```python
config = AppConfig.load(
    config_file="config.yaml",
    env_prefix="MYAPP_",
    strict=False
)
config.freeze()  # 불변
```

---

## 📚 문서

고급 기능은 [ADVANCED.md](./ADVANCED.md) 참조 (영문):
- Config Freezing & Immutability
- JSON Schema Generation
- Remote Config Loading (HTTP/HTTPS)
- Plugin System (Custom Loaders, Validators, Hooks)
- Config Diff & Merge
- Integration Examples (FastAPI, Django, Kubernetes, AWS Lambda)

---

## 📄 라이선스

MIT License © 2025 — 자세한 내용은 [LICENSE](./LICENSE) 참조
