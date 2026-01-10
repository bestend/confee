# Quick Wins - 즉시 실행 가능한 개선사항

**우선순위**: P0-P1 작업 중 빠르게 완료 가능한 항목
**목표**: 1-2주 내 가시적 개선

---

## 🏃 Week 1: Critical Testing & Code Quality

### Day 1-2: Secret Field 테스트 (2시간)
```bash
# 새 테스트 파일 생성
touch tests/test_secrets.py
```

**테스트 케이스**:
- `to_safe_dict()` - flat config
- `to_safe_dict()` - nested config
- `to_safe_json()` - JSON 직렬화
- `print(safe=True)` - 출력 마스킹

**왜 중요한가**: 현재 보안 기능이 테스트되지 않아 회귀 리스크 존재

---

### Day 2-3: Immutability 테스트 (2시간)
```bash
touch tests/test_immutability.py
```

**테스트 케이스**:
- `freeze()` → AttributeError
- `unfreeze()` → mutable
- `copy_unfrozen()` → new instance
- nested config freeze propagation

**왜 중요한가**: freeze 기능이 README에 문서화되어 있지만 미테스트

---

### Day 3: 포맷 감지 로직 통합 (1시간)
```python
# src/confee/loaders.py
def _detect_format(url: str) -> str:
    """Detect format from URL extension."""
    # 기존 로직 통합
    ...

# src/confee/async_loader.py에서 사용
from .loaders import _detect_format
```

**왜 중요한가**: 중복 코드 제거, 유지보수성 향상

---

### Day 4: py.typed 추가 (5분)
```bash
# 빈 파일 생성
touch src/confee/py.typed
```

**pyproject.toml에 추가**:
```toml
[tool.setuptools.package-data]
confee = ["py.typed"]
```

**왜 중요한가**: 타입 힌트 배포, IDE 지원 향상

---

### Day 5: Pre-commit 설정 (30분)
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

**설치**:
```bash
pip install pre-commit
pre-commit install
```

**왜 중요한가**: 코드 품질 자동 검사, PR 전 검증

---

## 📚 Week 2: Documentation Quick Wins

### Day 1-2: CONTRIBUTING.md 작성 (2시간)
```markdown
# CONTRIBUTING.md

## Development Setup
```bash
git clone https://github.com/bestend/confee.git
cd confee
pip install -e ".[dev]"
```

## Running Tests
```bash
pytest
pytest --cov=confee --cov-report=html
```

## Code Quality
```bash
ruff check .
ruff format .
mypy src/
```
```

**왜 중요한가**: 새 기여자 온보딩 시간 단축

---

### Day 3-4: Examples 디렉토리 (3시간)
```bash
mkdir examples
cd examples
```

**최소 예제**:
1. `01_basic_usage.py` - 기본 사용법
2. `02_cli_overrides.py` - CLI 오버라이드
3. `03_secrets.py` - 비밀 필드
4. `04_fastapi.py` - FastAPI 통합

**왜 중요한가**: 사용자가 복사-붙여넣기로 빠르게 시작 가능

---

### Day 5: ARCHITECTURE.md (2시간)
```markdown
# Architecture

## Data Flow
```mermaid
graph LR
    A[Config File] --> B[ConfigLoader]
    B --> C[PluginRegistry]
    C --> D[ConfigParser]
    D --> E[OverrideHandler]
    E --> F[ConfigBase]
```

## Components
- **ConfigBase**: Pydantic 기반 설정 모델
- **ConfigLoader**: 파일 로딩 및 포맷 감지
- **PluginRegistry**: 확장 가능한 플러그인 시스템
```

**왜 중요한가**: 새 기여자가 코드베이스 구조 이해 가능

---

## 🎯 Success Criteria (2주 후)

✅ **테스트**:
- [ ] Secret 테스트 추가됨
- [ ] Immutability 테스트 추가됨
- [ ] 코드 중복 1개 이상 제거됨

✅ **문서**:
- [ ] CONTRIBUTING.md 존재
- [ ] ARCHITECTURE.md 존재
- [ ] examples/ 디렉토리에 4+ 파일

✅ **인프라**:
- [ ] py.typed 배포됨
- [ ] pre-commit 설정됨

---

## 📊 Impact vs Effort

| Task | Impact | Effort | ROI |
|------|--------|--------|-----|
| py.typed 추가 | HIGH | 5min | ⭐⭐⭐⭐⭐ |
| Secret 테스트 | HIGH | 2hr | ⭐⭐⭐⭐ |
| Pre-commit | MEDIUM | 30min | ⭐⭐⭐⭐ |
| CONTRIBUTING.md | MEDIUM | 2hr | ⭐⭐⭐ |
| Examples | MEDIUM | 3hr | ⭐⭐⭐ |
| 포맷 통합 | LOW | 1hr | ⭐⭐ |

---

**Total Time**: ~13-15 hours
**Visible Improvements**: 7개 항목
**Breaking Changes**: 0개
