# confee vs OmegaConf 방식 기능 비교

**언어:** 한국어 | [English](./comparison.md)

## 🔍 상세 분석

### 1️⃣ **파일 로딩 및 병합**

#### OmegaConf 방식
```python
from omegaconf import OmegaConf

conf = OmegaConf.load(config_file_path)
conf = OmegaConf.merge(*raw_confs)
```

#### confee ✅
```python
from confee import ConfigBase

class AppConfig(ConfigBase):
    name: str
    debug: bool = False

# 통합 파서로 한 번에 처리
config = AppConfig.load(config_file="config.yaml")
```

**개선점:**
- ✅ YAML/JSON 자동 감지
- ✅ Pydantic으로 타입 검증
- ✅ IDE 자동완성 지원
- ✅ 더 간단한 API

---

### 2️⃣ **환경변수 오버라이드**

#### OmegaConf 방식
```python
def omegaconf_from_env(parameter_cls):
    dotlist_keys = get_dotlist_keys(parameter_cls)
    for key in dotlist_keys:
        key_upper = key.upper()
        if key_upper in os.environ:
            dotlist.append(f"{key}={os.environ[key_upper]}")
    return OmegaConf.from_dotlist(dotlist)
```

#### confee ✅
```python
# 자동으로 CONFEE_ 접두사로 환경변수 처리
# CONFEE_DEBUG=true → debug=True
config = AppConfig.load()

# 커스텀 접두사 지원
config = AppConfig.load(env_prefix="MYAPP_")
```

**개선점:**
- ✅ 자동 접두사 처리
- ✅ 커스텀 접두사 지원
- ✅ Type coercion (true/yes/1/on → Boolean)
- ✅ Nested 필드 지원 (CONFEE_DATABASE_HOST)

---

### 3️⃣ **CLI 오버라이드**

#### OmegaConf 방식
```python
conf = OmegaConf.from_cli(args_list)
```

#### confee ✅
```python
# 자동으로 CLI 인자 수집
config = AppConfig.load()

# 또는 명시적으로
config = AppConfig.load(cli_args=["debug=true", "workers=8"])
```

**개선점:**
- ✅ key=value 형식 명확
- ✅ 자동 타입 변환
- ✅ Boolean 유연한 처리 (true/yes/1/on)
- ✅ Nested 필드 지원 (database.host=localhost)

---

### 4️⃣ **중첩된 설정 (Nested)**

#### OmegaConf 방식
```python
def get_dotlist_keys(cls, root=''):
    for name, field in cls.__fields__.items():
        cur_name = root + "." + name if root else name
        if isinstance(field.annotation, ModelMetaclass):
            outputs.extend(get_dotlist_keys(field.annotation, cur_name))
```

#### confee ✅
```python
class DatabaseConfig(ConfigBase):
    host: str
    port: int

class AppConfig(ConfigBase):
    database: DatabaseConfig

# Nested 구조 자동 지원
config = AppConfig.load(cli_args=["database.host=localhost"])
print(config.database.host)  # "localhost"
```

**개선점:**
- ✅ 더 깔끔한 타입 정의
- ✅ IDE 자동완성 지원
- ✅ CLI/ENV에서도 nested 접근 가능 (a.b.c=value)
- ✅ 런타임 검증

---

### 5️⃣ **타입 검증**

#### OmegaConf 방식
```python
output_param = parameter_cls.parse_obj(OmegaConf.to_container(conf))
```

#### confee ✅
```python
# Pydantic V2 기반 자동 검증
config = AppConfig(name="myapp", workers=8)

# 또는
config = AppConfig.from_dict(data)

# 타입 오류 발생 시 명확한 메시지
```

**개선점:**
- ✅ Pydantic V2 최신 기능
- ✅ 더 나은 오류 메시지
- ✅ JSON Schema 생성 가능

---

### 6️⃣ **파일 참조 기능** 🆕

#### OmegaConf 방식
```python
# 미지원
```

#### confee ✅
```yaml
# config.yaml
api_key: "@file:secrets/api_key.txt"
database: "@config:configs/database.yaml"
```

**개선점:**
- ✅ 텍스트 파일 참조 (@file:)
- ✅ YAML 파일 참조 (@config:)
- ✅ 중첩된 파일 참조 지원
- ✅ 민감 정보 분리 관리

---

### 7️⃣ **Help 자동 생성** 🆕

#### OmegaConf 방식
```python
def make_help_str(parameter_cls, config_param_str: str):
    # 복잡한 포맷팅 로직
    help_str = f'Usage: {sys.argv[0]} [Arguments]\n'
    # ... 복잡한 처리
```

#### confee ✅
```python
# --help 플래그로 자동 생성
python app.py --help

# 커스텀 Help flag
config = AppConfig.load(help_flags=["--help", "-h", "--info"])
```

**개선점:**
- ✅ 자동으로 Help 생성
- ✅ 모든 옵션과 기본값 표시
- ✅ 커스텀 Help flag 지원

---

### 8️⃣ **파싱 순서 제어** 🆕

#### OmegaConf 방식
```python
# 고정된 순서
# File → Env → CLI
```

#### confee ✅
```python
# 기본값: CLI > Env > File
config = AppConfig.load(config_file="config.yaml")

# 커스텀 순서
config = AppConfig.load(
    config_file="config.yaml",
    source_order=["file", "env"]  # File만 사용
)
```

**개선점:**
- ✅ 파싱 순서 자유롭게 제어
- ✅ 특정 소스만 사용 가능

---

### 9️⃣ **설정 상속**

#### OmegaConf 방식
```python
# 수동으로 병합 처리
parent_dict = parent.model_dump()
child_dict = child.model_dump()
merged = {**parent_dict, **child_dict}
```

#### confee ✅
```python
# override_with() 메서드로 간단히 처리
defaults = AppConfig(host="prod-host")
custom = AppConfig(host="localhost")
merged = custom.override_with(defaults)
```

**개선점:**
- ✅ 명확한 API (override_with)
- ✅ 부모-자식 관계 명시적

---

## 📊 기능 비교 표

| 기능 | OmegaConf | confee | 설명 |
|------|-----------|--------|------|
| 파일 로드 | ✅ | ✅ | YAML/JSON 지원 |
| CLI 오버라이드 | ✅ | ✅ | key=value 형식 |
| 환경변수 | ✅ | ✅ | 접두사 지원 |
| 다중 파일 병합 | ✅ | ✅ | 자동 병합 |
| Nested 설정 | ✅ | ✅ | Pydantic 지원 |
| 타입 검증 | ✅ | ✅ | Pydantic V2 |
| 타입 힌트/IDE | ❌ | ✅ | 자동완성 지원 |
| Strict/Lenient | ❌ | ✅ | 모드 선택 |
| 파일 참조 (@file:, @config:) | ❌ | ✅ | 민감 정보 분리 |
| Help 자동 생성 | ✅ (복잡함) | ✅ (간단함) | --help 지원 |
| Nested CLI/ENV | ❌ | ✅ | database.host=value |
| 파싱 순서 제어 | ❌ | ✅ | source_order 파라미터 |
| 설정 상속 | 수동 | ✅ | override_with() |

---

## 🎯 마이그레이션 가이드

### Before (OmegaConf 방식)
```python
from omegaconf import OmegaConf

def load_param(parameter_cls, config_file_path=None, args_list=None):
    raw_confs = []
    
    if os.path.exists(config_file_path):
        raw_confs.append(OmegaConf.load(config_file_path))
    
    raw_confs.append(omegaconf_from_env(parameter_cls))
    raw_confs.append(OmegaConf.from_cli(args_list))
    
    conf = OmegaConf.merge(*raw_confs)
    return parameter_cls.parse_obj(OmegaConf.to_container(conf))
```

### After (confee)
```python
from confee import ConfigBase

class AppConfig(ConfigBase):
    name: str
    debug: bool = False

# 이 한 줄로 충분!
config = AppConfig.load(config_file="config.yaml")
```

---

## ✨ 주요 개선점

1. **더 간결한 API** — 보일러플레이트 코드 제거
2. **타입 안정성** — Pydantic V2 기반 강력한 검증
3. **IDE 지원** — 자동완성 및 타입 힌트
4. **확장성** — 파일 참조, 상속 등
5. **문서화** — 명확한 사용 예제

---

**결론:** confee는 OmegaConf 방식의 핵심 기능을 모두 갖추면서, 더 간결하고 타입 안전하며 현대적인 패키지입니다! ☕️

---

**언어:** 한국어 | [English](./comparison.md)

