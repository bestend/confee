<p align="center">
  <img src="assets/logo.png" width="360" />
</p>

<div align="center">

**언어:** 한국어 | [English](./readme.md)

Hydra 스타일의 Configuration 관리 + Pydantic 타입 안전성의 결합 + Typer 스타일 CLI Help 자동 생성

[![PyPI Version](https://img.shields.io/pypi/v/confee.svg)](https://pypi.org/project/confee/)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-alpha-yellow)](https://github.com/bestend/confee)

</div>

---

## ☕️ 개요

**confee**는 Python 애플리케이션의 Configuration 관리를 간단하고 타입 안전하게 만드는 패키지입니다. Hydra와 Pydantic의 장점을 결합하여, 설정 파일, 환경변수, CLI 인자를 통합적으로 처리할 수 있습니다.

---

## ✨ 주요 기능

- **🎯 Type-Safe Configuration** — Pydantic V2로 자동 타입 검증 & IDE 자동완성
- **📋 Multi-Format Support** — YAML과 JSON 자동 감지 및 파싱
- **🔄 Flexible Override System** — CLI 인자, 환경변수로 값 오버라이드
- **🏗️ Configuration Inheritance** — 설정 병합 및 부모-자식 설정 조합
- **📁 File Reference** — `@file:` & `@config:` 접두사로 파일 내용을 자동 로드
- **🔐 Strict Mode** — unknown fields 거부 또는 검증 오류 처리 방식 제어
- **📦 Zero Configuration** — 기본값으로 즉시 사용 가능
- **⚙️ Parse Order Control** — file/env/cli 소스의 우선순위를 자유롭게 조정
- **💬 Auto Help Generation** — `--help` 플래그로 모든 설정 옵션과 기본값 표시
- **🪆 Nested Field Access** — `database.host=localhost` 형식으로 nested 필드 오버라이드
- **🧾 Error/Warning Verbosity Control** `--quiet`/`--verbose`/`--no-color` 플래그와 ENV로 출력 수준·컬러 제어

---

## 📦 설치

```bash
pip install confee
```

---

## 🚀 빠른 시작

### 기본 사용법

```python
from confee import ConfigBase

class AppConfig(ConfigBase):
    name: str
    debug: bool = False
    workers: int = 4

# 기본값으로 생성
config = AppConfig(name="myapp")

# 모든 소스(파일/환경변수/CLI)를 한 번에 파싱
config = AppConfig.load(config_file="config.yaml")
```

### CLI 오버라이드

```bash
# 기본 필드
python app.py debug=true workers=8

# Nested 필드 접근
python app.py database.host=localhost database.port=5432

# 헬프 보기
python app.py --help
```

### 환경변수 오버라이드

```bash
# CONFEE_ 접두사 자동 적용
export CONFEE_DEBUG=true
export CONFEE_WORKERS=8
export CONFEE_DATABASE_HOST=localhost

python app.py
```

### K8s Pod YAML 예제

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-prod
spec:
  containers:
  - name: myapp
    image: myapp:latest
    env:
    - name: CONFEE_ENV
      value: "prod"
    - name: CONFEE_DEBUG
      value: "false"
    - name: CONFEE_DATABASE_HOST
      value: "prod-db.example.com"
    - name: CONFEE_DATABASE_PORT
      value: "3306"
    - name: CONFEE_LOG_LEVEL
      value: "warn"
```

**주의:** confee는 환경변수에 `CONFEE_` 접두사를 자동으로 처리합니다.
- `CONFEE_DEBUG` → `debug` 필드로 매핑
- `CONFEE_DATABASE_HOST` → `database.host` 필드로 매핑
- 커스텀 접두사: `AppConfig.load(env_prefix="MYAPP_")`

---

## 📚 API 레퍼런스

### ConfigBase.load() — 파서

**가장 권장되는 방식입니다.**

```python
from confee import ConfigBase

class AppConfig(ConfigBase):
    name: str
    debug: bool = False
    workers: int = 4

# ✅ 가장 간단한 방식 - 파일, 환경변수, CLI를 한 번에 파싱
config = AppConfig.load(config_file="config.yaml")

# 환경변수 접두사 커스터마이징
config = AppConfig.load(
    config_file="config.yaml",
    env_prefix="MYAPP_"
)

# 파싱 순서 제어 (CLI > Env > File > defaults)
config = AppConfig.load(
    config_file="config.yaml",
    source_order=["cli", "env", "file"]  # 기본값
)

# 파일만 사용 (env/cli 무시)
config = AppConfig.load(
    config_file="config.yaml",
    source_order=["file"]
)

# 헬프 플래그 커스터마이징
config = AppConfig.load(
    help_flags=["--help", "-h", "--info"]
)

# Strict 모드 활성화
config = AppConfig.load(
    config_file="config.yaml",
    strict=True
)
```

**파라미터:**

| 파라미터 | 설명 | 기본값 |
|---------|------|--------|
| `config_file` | 설정 파일 경로 | None |
| `cli_args` | CLI 인자 리스트 | sys.argv[1:] |
| `env_prefix` | 환경변수 접두사 | "CONFEE_" |
| `source_order` | 파싱 우선순위 | ["cli", "env", "file"] |
| `help_flags` | Help 플래그 | ["--help", "-h"] |
| `strict` | Strict 모드: True로 설정하면 unknown fields나 검증 오류 발생 시 예외 발생 | False |

### ConfigBase 메서드

```python
class DatabaseConfig(ConfigBase):
    host: str
    port: int = 5432
    username: str
    password: str

# 인스턴스 생성
config = DatabaseConfig(host="localhost")

# 딕셔너리로 변환
config_dict = config.to_dict()

# JSON으로 변환
json_str = config.to_json()

# JSON에서 로드
loaded = DatabaseConfig.from_json(json_str)

# 설정 병합 (기본값 제공)
defaults = DatabaseConfig(host="prod-host", port=5432)
custom = DatabaseConfig(host="localhost")
merged = custom.override_with(defaults)  # custom이 기본값을 오버라이드
```

### Strict 모드

기본적으로 confee는 unknown fields를 무시합니다. 

**Strict 모드 활성화:** unknown fields나 검증 오류 발생 시 예외 발생 (오설정 방지)

```python
# 기본: unknown fields 무시
config = AppConfig.load()

# Strict 모드 활성화 (strict=True)
config = AppConfig.load(strict=True)
```

> **strict=True와 model_config = {"extra": "forbid"}의 차이?**
> 
> - **strict=True (파라미터)**: AppConfig.load()에서 설정하는 것
>   - 주로 검증 오류를 무시할지 예외 발생할지 제어
> 
> - **model_config = {"extra": "forbid"} (클래스 정의)**: Pydantic 클래스에서 설정하는 것
>   - 정의되지 않은 필드(unknown fields)가 들어올 때 처리 방식 제어
>   - `"forbid"` = unknown fields 거부 (오류 발생)
>   - `"ignore"` (기본값) = unknown fields 무시
>
> **함께 사용하면:** 더 엄격한 검증
> ```python
> class StrictConfig(ConfigBase):
>     name: str
>     model_config = {"extra": "forbid"}  # unknown fields 거부
> 
> config = StrictConfig.load(strict=True)  # 검증 오류도 예외 발생
> ```

### 파일 참조 (`@file:`, `@config:`)

**텍스트 파일 참조:**

```yaml
name: myapp
api_key: "@file:secrets/api_key.txt"
database:
  password: "@file:secrets/db_password.txt"
```

**YAML 파일 참조:**

```yaml
name: myapp
database: "@config:configs/database.yaml"
```

`configs/database.yaml`:
```yaml
host: localhost
port: 5432
password: "@file:secrets/db_password.txt"  # 중첩된 파일 참조도 지원
```

### 오류/경고 출력 제어

confee는 사용자 친화적인 오류/경고 출력을 제공합니다. 기본은 “컴팩트(compact)” 모드로, 핵심만 한 줄로 보여주고, `--verbose` 또는 환경변수로 상세 블록을 볼 수 있습니다. 컬러 출력은 `--no-color` 또는 `NO_COLOR=1`로 끌 수 있습니다.

- CLI 플래그
  - `--verbose` 또는 `-v`: 상세 모드 활성화
  - `--quiet` 또는 `-q`: 컴팩트 모드 강제(기본도 compact)
  - `--no-color`: ANSI 컬러 비활성화
- 환경변수
  - `CONFEE_VERBOSITY=verbose|compact` (별칭: `rich|detailed`/`quiet|minimal`)
  - `CONFEE_QUIET=1` → compact 강제
  - `NO_COLOR=1` 또는 `CONFEE_NO_COLOR=1` → 컬러 비활성화

우선순위(높음 → 낮음): CLI 플래그 > 환경변수 > 기본값(compact, color=on)

#### 예시: 파일 로드 경고

```bash
# compact (기본)
Warning: config.yaml not found

# verbose
Warning: Failed to load config file: Configuration file not found: config.yaml
```

#### 예시: 검증 오류(필수 필드 누락)

```bash
# compact (기본)
Warning: Config error: missing required field 'name'

# verbose
❌ Configuration Validation Error

  Missing required field: name
  This field is required for configuration.

  💡 How to fix:
    1. Add the required field to your configuration file
    2. Or pass the value via CLI: python main.py name=myapp
    3. Or set an environment variable: export CONFEE_NAME=myapp
```
#### 참고: 오버라이드 파싱 규칙

- CLI에서 제어 플래그(`--quiet`, `--verbose`, `--no-color`)는 설정 키로 간주되지 않습니다.
- 설정 오버라이드는 `key=value` 형태만 파싱됩니다. 예: `debug=true workers=8 database.port=5432`

---

## 📖 사용 예제

### 예제 1: 간단한 애플리케이션 설정

```python
from confee import ConfigBase

class AppConfig(ConfigBase):
    app_name: str
    version: str
    debug: bool = False
    port: int = 8000

config = AppConfig.load(config_file="config.yaml")
print(f"{config.app_name} v{config.version}를 포트 {config.port}에서 실행 중")
```

### 예제 2: 설정 병합 (기본값 제공)

```python
class DatabaseConfig(ConfigBase):
    host: str
    port: int = 5432
    username: str

defaults = DatabaseConfig(
    host="prod-host",
    port=5432,
    username="admin"
)

custom = DatabaseConfig(
    host="localhost",
    port=3306,
    username="user"
)

config = custom.override_with(defaults)
# host="localhost", port=3306, username="user" (custom이 우선)
```

### 예제 3: 민감 정보 관리

```python
class AppConfig(ConfigBase):
    name: str
    api_key: str
    database_password: str

# config.yaml
# name: production-app
# api_key: "@file:secrets/api_key.txt"
# database_password: "@file:secrets/db_password.txt"

config = AppConfig.load(config_file="config.yaml")
print(config.api_key)              # secrets/api_key.txt의 내용
print(config.database_password)    # secrets/db_password.txt의 내용
```

### 예제 4: YAML 설정 분리

```python
class DatabaseConfig(ConfigBase):
    host: str
    port: int

class CacheConfig(ConfigBase):
    ttl: int

class AppConfig(ConfigBase):
    name: str
    database: DatabaseConfig
    cache: CacheConfig

# config.yaml
# name: myapp
# database: "@config:configs/database.yaml"
# cache: "@config:configs/cache.yaml"

config = AppConfig.load(config_file="config.yaml")
```

### 예제 5: Nested 필드 오버라이드

```python
class DatabaseConfig(ConfigBase):
    host: str = "localhost"
    port: int = 5432

class AppConfig(ConfigBase):
    name: str
    database: DatabaseConfig

# CLI: python app.py name=prod database.host=prod-db.com database.port=3306
# ENV:  export CONFEE_DATABASE_HOST=prod-db.com

config = AppConfig.load()
print(config.database.host)  # "prod-db.com"
print(config.database.port)  # 3306
```

### 예제 6: 파싱 순서 제어

```python
# 파일만 사용
config = AppConfig.load(
    config_file="config.yaml",
    source_order=["file"]
)

# CLI 인자만 사용
config = AppConfig.load(source_order=["cli"])

# 역순: 파일 > CLI > 환경변수
config = AppConfig.load(
    config_file="config.yaml",
    source_order=["file", "cli", "env"]
)
```

---

## 🧪 테스트

```bash
# 설치
pip install ".[dev]"

# 모든 테스트 실행
pytest

# 커버리지 포함
pytest --cov=confee

# 상세 출력
pytest -v
```

---

## 🤝 기여하기

기여는 환영합니다! Pull Request를 자유롭게 제출해주세요.

---

## 📄 라이센스

MIT 라이센스 - [LICENSE](LICENSE) 파일 참고

---

## 🔗 관련 프로젝트

- **[Hydra](https://hydra.cc/)** — 복잡한 애플리케이션 설정 프레임워크
- **[Pydantic](https://docs.pydantic.dev/)** — Python 타입 어노테이션 기반 데이터 검증
- **[Typer](https://typer.tiangolo.com/)** — CLI 앱 빌드 도구

---

즐거운 ☕️ Configuration 관리 되세요!

---

**언어:** 한국어 | [English](./readme.md)

