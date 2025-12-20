# confee - 개발 가이드

**언어:** 한국어 | [English](./development.md)

## 프로젝트 구조

```
confee/
├── src/confee/                 # 주요 패키지
│   ├── __init__.py            # 패키지 초기화 및 공개 API
│   ├── config.py              # ConfigBase 및 설정 기본 클래스
│   ├── loaders.py             # YAML/JSON 파일 로더
│   ├── overrides.py           # CLI/환경변수 오버라이드
│   ├── parser.py              # Hydra 스타일 파서
│   └── py.typed               # PEP 561 타입 힌팅 마커
├── tests/                      # 테스트
│   ├── test_config.py         # ConfigBase 테스트
│   ├── test_loaders.py        # 로더 테스트
│   ├── test_overrides.py      # 오버라이드 테스트
│   └── test_parser.py         # 파서 테스트
├── pyproject.toml             # 패키지 메타데이터 및 설정
├── README.md                  # 사용자 문서
├── LICENSE                    # MIT 라이센스
└── .gitignore                 # Git 무시 파일
```

## 주요 기능

### 1. ConfigBase - 기본 설정 클래스
- Pydantic V2 기반 타입 검증
- 딕셔너리/JSON 변환
- Lenient/Strict 모드 지원

```python
from confee import ConfigBase

class AppConfig(ConfigBase):
    name: str
    debug: bool = False
    workers: int = 4
```

### 2. ConfigLoader - 파일 로더
- YAML/JSON 자동 감지
- 단일/다중 파일 로드 및 병합
- 엄격/유연 오류 처리

```python
from confee import load_from_file, load_config

config = load_from_file("config.yaml", AppConfig)
config = load_config("base.yaml", "local.yaml", config_class=AppConfig)
```

### 3. OverrideHandler - 오버라이드
- CLI 인자: `key=value` 형식
- 환경변수: `CONFEE_*` 또는 커스텀 접두사
- 타입 강제 변환

```python
from confee import OverrideHandler

config = OverrideHandler.from_cli_and_env(
    AppConfig,
    cli_overrides=["debug=true"],
    env_prefix="CONFEE_"
)
```

### 4. ConfigParser - Hydra 스타일 파서
- Defaults 목록 지원
- 프로필 기반 설정 (dev, prod, test)
- 설정 상속

```python
from confee import ConfigParser

parser = ConfigParser("./configs")
config = parser.parse("config.yaml", AppConfig)
```

## 테스트 실행

```bash
# 모든 테스트 실행
pytest tests/ -v

# 커버리지 포함
pytest tests/ --cov=confee --cov-report=html

# 특정 테스트 파일만 실행
pytest tests/test_config.py -v
```

## 개발 환경 설정

```bash
# 개발 모드 설치
pip install -e ".[dev]"

# 코드 포매팅
black src/ tests/

# 린트 확인
ruff check src/ tests/

# 타입 체킹
mypy src/confee
```

## 배포 준비

```bash
# 빌드
pip install build
python -m build

# PyPI에 배포 (나중에)
pip install twine
twine upload dist/*
```

## 향후 개선 사항

- [ ] Nested field overrides (db.host=localhost)
- [ ] 설정 유효성 검사 훅
- [ ] CLI 자동 생성 (Typer 통합)
- [ ] 상세한 로깅 및 디버깅
- [ ] 설정 병합 전략 커스터마이징
- [ ] 성능 최적화

## 라이센스

MIT License © 2025

---

**언어:** 한국어 | [English](./development.md)

