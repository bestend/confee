<p align="center">
  <img src="https://raw.githubusercontent.com/bestend/confee/main/assets/logo.png" width="360" />
</p>

<div align="center">

**Language:** 한국어 | [English](./README.md)

Hydra 스타일 설정 + Pydantic 타입 안전성 + 자동 도움말 생성

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/bestend/confee/actions/workflows/tests.yml/badge.svg)](https://github.com/bestend/confee/actions/workflows/tests.yml)

</div>

---

## ☕️ 개요

**confee**는 Python 설정 관리를 단순하고 타입 안전하며 직관적으로 만들어줍니다. Hydra 스타일 설정 파일, Pydantic 검증, 환경 변수, CLI 인자를 매끄럽게 통합합니다.

---

## ✨ 기능

- **🎯 타입 안전** — Pydantic V2 검증 & IDE 자동완성
- **📋 다중 포맷** — YAML, JSON, TOML 자동 감지
- **🔄 오버라이드** — CLI 인자 & 환경 변수
- **🔐 시크릿 마스킹** — `SecretField()`로 민감 데이터 보호
- **🧊 설정 동결** — 런타임 불변성
- **📐 JSON 스키마** — 스키마 내보내기 & 검증
- **⚡ 비동기 로딩** — 논블로킹 I/O 및 파일 감시
- **🔌 플러그인** — 커스텀 포맷 로더
- **💬 자동 도움말** — `--help` 플래그 지원

---

## 📦 설치

```bash
pip install confee

# 선택적 기능
pip install confee[toml]    # TOML 지원 (Python < 3.11)
pip install confee[remote]  # 비동기 원격 로딩
pip install confee[all]     # 모든 기능
```

---

## 🚀 빠른 시작

```python
from confee import ConfigBase, SecretField

class AppConfig(ConfigBase):
    name: str
    debug: bool = False
    workers: int = 4
    api_key: str = SecretField(default="")  # 출력 시 마스킹

config = AppConfig.load(config_file="config.yaml")
print(config.name)  # IDE 지원과 함께 타입 안전한 접근
```

```yaml
# config.yaml
name: my-app
debug: false
workers: 8
api_key: secret123
```

```bash
# CLI로 오버라이드
python app.py name=production debug=true

# 환경 변수로 오버라이드
export CONFEE_NAME=production
export CONFEE_DEBUG=true
```

---

## 🎯 고급 사용법

### 중첩 설정

```python
class DatabaseConfig(ConfigBase):
    host: str = "localhost"
    port: int = 5432

class AppConfig(ConfigBase):
    name: str
    database: DatabaseConfig

# 중첩 필드 오버라이드: python app.py database.host=prod.db
```

### 파일 참조

```yaml
api_key: "@file:secrets/api_key.txt"
database: "@config:configs/database.yaml"
```

### 시크릿 마스킹

```python
config.to_safe_dict()  # {'api_key': '***MASKED***', ...}
config.print(safe=True)  # 마스킹된 시크릿과 함께 출력
```

### 설정 동결

```python
config.freeze()
config.name = "new"  # AttributeError 발생

# 수정 가능한 복사본 생성
unfrozen = config.copy_unfrozen()
```

### JSON 스키마

```python
schema = AppConfig.to_json_schema()
AppConfig.save_schema("config.schema.json")
```

### 원격 설정

```python
# 동기 (stdlib urllib)
data = ConfigLoader.load_remote("https://example.com/config.yaml")

# 비동기 (aiohttp 필요)
data = await AsyncConfigLoader.load_remote("https://example.com/config.yaml")
```

### 플러그인 시스템

```python
from confee import PluginRegistry

@PluginRegistry.loader(".ini")
def load_ini(path: str) -> dict:
    import configparser
    parser = configparser.ConfigParser()
    parser.read(path)
    return {s: dict(parser[s]) for s in parser.sections()}
```

### 설정 비교 & 병합

```python
diff = config1.diff(config2)  # {'name': ('app1', 'app2')}
merged = config1.merge(config2)  # config2가 우선
```

---

## ⚙️ 설정 옵션

```python
config = AppConfig.load(
    config_file="config.yaml",
    env_prefix="MYAPP_",  # 커스텀 환경변수 접두사
    source_order=["cli", "env", "file"],  # 우선순위 순서
    strict=False,  # 알 수 없는 필드 허용
)
```

---

## 🔄 통합

### FastAPI

```python
config = AppConfig.load(config_file="config.yaml", source_order=["env", "file"])
app = FastAPI(title=config.name, debug=config.debug)
```

### Kubernetes

```yaml
env:
  - name: CONFEE_DEBUG
    value: "false"
  - name: CONFEE_WORKERS
    value: "16"
```

---

## � 라이선스

MIT License © 2025 — 자세한 내용은 [LICENSE](./LICENSE) 참조

---

**☕️ 설정 관리를 즐기세요!**
