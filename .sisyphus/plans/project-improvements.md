# Confee 프로젝트 개선 계획 (Project Improvement Plan)

**생성일**: 2026-01-10
**상태**: DRAFT
**우선순위**: HIGH

---

## 📋 Executive Summary

**confee**는 Python 설정 관리 라이브러리로, Pydantic V2 기반의 타입 안전성과 Hydra 스타일 설정 조합을 제공합니다. 전반적으로 **잘 설계된 코드베이스**이지만, 다음 영역에서 개선이 필요합니다:

1. **테스트 커버리지**: 고급 기능(Secret, Freeze, Async, Plugin) 미테스트
2. **문서화**: 개발자 가이드 및 API 레퍼런스 부재
3. **코드 중복**: 포맷 감지 로직 중복
4. **패키징**: 2025+ 표준(dependency-groups, py.typed) 미적용
5. **성능**: Pydantic v2 최신 패턴 미활용

**현재 상태**: 85% 현대화됨
**목표**: 프로덕션 급 라이브러리로 성장

---

## 🎯 Phase 1: Critical Issues (2-3 weeks)

### 1.1 테스트 커버리지 확대 ⚠️ CRITICAL

**현재 문제**:
- `SecretField` 마스킹 로직 미테스트 → 보안 리스크
- `freeze()`/`unfreeze()` 불변성 미테스트
- 비동기 로딩 및 파일 감시 미테스트
- 플러그인 시스템 미테스트

**구체적 작업**:

```markdown
# 작업 1.1.1: Secret Field 테스트 추가
- [ ] `tests/test_secrets.py` 생성
  - [ ] `to_safe_dict()` 테스트 (flat config)
  - [ ] `to_safe_dict()` 테스트 (nested config)
  - [ ] `to_safe_json()` 테스트
  - [ ] `print(safe=True)` 테스트
  - [ ] 마스킹되지 않은 일반 필드 확인

# 작업 1.1.2: Immutability 테스트 추가
- [ ] `tests/test_immutability.py` 생성
  - [ ] `freeze()` 후 속성 변경 시 `AttributeError` 발생 확인
  - [ ] `unfreeze()` 후 변경 가능 확인
  - [ ] `copy_unfrozen()` 동작 확인
  - [ ] nested config freeze 전파 테스트

# 작업 1.1.3: TOML 로딩 테스트
- [ ] `tests/test_loaders.py`에 실제 TOML 파일 파싱 테스트 추가
  - [ ] Python 3.11+ `tomllib` 테스트
  - [ ] Python 3.10- `tomli` 테스트
  - [ ] TOML 파싱 에러 핸들링 테스트

# 작업 1.1.4: Async 테스트 인프라 구축
- [ ] `pytest-asyncio`, `aioresponses` 설치
- [ ] `tests/test_async.py` 생성
  - [ ] `AsyncConfigLoader.load()` 테스트
  - [ ] `AsyncConfigLoader.watch()` 테스트 (file change detection)
  - [ ] `load_remote()` with mocked HTTP (aioresponses)
  - [ ] 에러 핸들링 (파일 삭제 중 watch, 빠른 변경)

# 작업 1.1.5: Plugin 시스템 테스트
- [ ] `tests/test_plugins.py` 생성
  - [ ] `@PluginRegistry.loader` decorator 테스트
  - [ ] 커스텀 포맷 로더 등록 및 사용 테스트
  - [ ] `PluginRegistry.clear()` 테스트
  - [ ] 로더 충돌 테스트 (같은 확장자에 여러 로더)
```

**예상 소요 시간**: 1주
**우선순위**: P0 (보안 리스크)

---

### 1.2 코드 품질 개선

**현재 문제**:
1. 포맷 감지 로직이 `loaders.py`와 `async_loader.py`에 중복
2. `OverrideHandler.parse()`에서 `SystemExit(1)` 사용 → 라이브러리 통합 시 문제
3. `_frozen_instances`가 `Set[int]` → GC 비결정적, `WeakSet` 권장

**구체적 작업**:

```markdown
# 작업 1.2.1: 포맷 감지 로직 통합
- [ ] `src/confee/loaders.py`에 `_detect_format()` 함수 추출
- [ ] `async_loader.py`에서 공통 함수 사용
- [ ] 기존 테스트 실행하여 회귀 확인

# 작업 1.2.2: SystemExit 제거
- [ ] `src/confee/exceptions.py` 생성
  - [ ] `ConfigValidationError` 클래스 정의
  - [ ] `ConfigLoadError` 클래스 정의
- [ ] `overrides.py`에서 `SystemExit` → `ConfigValidationError` 변경
- [ ] CLI 전용 래퍼에서 예외 → exit code 변환

# 작업 1.2.3: 메모리 안전성 개선
- [ ] `config.py`에서 `_frozen_instances` → `WeakSet[ConfigBase]` 변경
- [ ] `__del__` 제거 (WeakSet은 자동 정리)
```

**예상 소요 시간**: 3일
**우선순위**: P1

---

### 1.3 문서화 개선 📚

**현재 문제**:
- README가 200+ 줄로 비대함
- `/examples` 디렉토리 없음
- API 레퍼런스 자동 생성 없음
- `CONTRIBUTING.md`, `ARCHITECTURE.md` 부재

**구체적 작업**:

```markdown
# 작업 1.3.1: MkDocs 사이트 구축
- [ ] `pip install mkdocs-material mkdocstrings[python]`
- [ ] `docs/` 디렉토리 생성
  - [ ] `docs/index.md` - Overview (README에서 발췌)
  - [ ] `docs/installation.md` - 설치 및 셋업
  - [ ] `docs/quickstart.md` - 빠른 시작 가이드
  - [ ] `docs/advanced/` - 고급 기능별 페이지
    - [ ] `nested-config.md`
    - [ ] `file-references.md`
    - [ ] `secrets.md`
    - [ ] `freezing.md`
    - [ ] `plugins.md`
    - [ ] `async-loading.md`
  - [ ] `docs/api/` - 자동 생성 API 레퍼런스
  - [ ] `docs/contributing.md` - 기여 가이드
  - [ ] `docs/architecture.md` - 아키텍처 설명
- [ ] `mkdocs.yml` 설정
- [ ] GitHub Pages 배포 설정

# 작업 1.3.2: Examples 디렉토리 생성
- [ ] `examples/` 디렉토리 생성
  - [ ] `01_basic_usage.py` - 기본 사용법
  - [ ] `02_cli_overrides.py` - CLI 오버라이드
  - [ ] `03_nested_config.py` - 중첩 설정
  - [ ] `04_secrets.py` - 비밀 필드
  - [ ] `05_fastapi_integration.py` - FastAPI 통합
  - [ ] `06_custom_loader.py` - 커스텀 로더 플러그인
  - [ ] `07_async_loading.py` - 비동기 로딩
  - [ ] `README.md` - 예제 실행 방법

# 작업 1.3.3: 개발자 문서
- [ ] `CONTRIBUTING.md` 작성
  - [ ] 개발 환경 셋업 (`uv sync --group dev`)
  - [ ] 테스트 실행 (`pytest`)
  - [ ] 린팅 (`ruff check`, `ruff format`)
  - [ ] 타입 체크 (`mypy`)
  - [ ] PR 프로세스
- [ ] `ARCHITECTURE.md` 작성
  - [ ] 데이터 흐름 다이어그램 (mermaid)
  - [ ] 주요 컴포넌트 설명
  - [ ] 플러그인 시스템 구조
```

**예상 소요 시간**: 1주
**우선순위**: P1

---

## 🚀 Phase 2: Modernization (2-3 weeks)

### 2.1 패키징 현대화 (2025+ 표준)

**현재 상태**:
- ✅ `src/` 레이아웃 사용 중
- ❌ `setuptools` 사용 (hatchling 권장)
- ❌ `[dependency-groups]` (PEP 735) 미사용
- ❌ `py.typed` 마커 없음
- ❌ 수동 버전 관리 (`sed` 사용)

**구체적 작업**:

```markdown
# 작업 2.1.1: Hatchling 전환
- [ ] `pyproject.toml` 업데이트
  ```toml
  [build-system]
  requires = ["hatchling>=1.27.0", "hatch-vcs"]
  build-backend = "hatchling.build"
  ```
- [ ] `[tool.hatch.build]` 설정 추가
- [ ] 빌드 테스트 (`uv build`)
- [ ] GitHub Actions에서 빌드 확인

# 작업 2.1.2: PEP 735 Dependency Groups
- [ ] `pyproject.toml`에 `[dependency-groups]` 섹션 추가
  ```toml
  [dependency-groups]
  dev = [
      "pytest>=8.0.0",
      "pytest-cov>=6.0.0",
      "pytest-asyncio>=0.24.0",
      "aioresponses>=0.7.6",
      "ruff>=0.9.0",
      "mypy>=1.14.0",
      "pre-commit>=4.0.0",
  ]

  lint = ["ruff>=0.9.0", "mypy>=1.14.0"]
  test = ["pytest>=8.0.0", "pytest-cov>=6.0.0"]
  docs = ["mkdocs-material>=9.0.0", "mkdocstrings[python]>=0.24.0"]
  ```
- [ ] `[project.optional-dependencies]` 정리 (사용자용만 유지)

# 작업 2.1.3: Type Stub 배포
- [ ] `src/confee/py.typed` 빈 파일 생성
- [ ] `pyproject.toml`에 포함 설정
  ```toml
  [tool.hatch.build.targets.wheel.force-include]
  "src/confee/py.typed" = "confee/py.typed"
  ```
- [ ] 설치 후 타입 힌트 동작 확인

# 작업 2.1.4: VCS 기반 버전 관리
- [ ] `pyproject.toml`에 dynamic version 설정
  ```toml
  [project]
  dynamic = ["version"]
  ```
- [ ] `hatch-vcs` 설정
- [ ] GitHub Actions 워크플로우 업데이트 (sed 제거)
```

**예상 소요 시간**: 3일
**우선순위**: P2

---

### 2.2 Pydantic V2 최적화

**현재 상태**:
- Pydantic v2 사용 중이지만 v1 패턴 일부 사용
- v2 최적화 기능 미활용 (TypeAdapter, computed_field 등)

**구체적 작업**:

```markdown
# 작업 2.2.1: Pydantic v2 마이그레이션 검증
- [ ] `bump-pydantic` 도구로 코드베이스 스캔
  ```bash
  pip install bump-pydantic
  bump-pydantic src/
  ```
- [ ] deprecated API 사용 여부 확인
- [ ] 필요 시 수정

# 작업 2.2.2: Performance 최적화
- [ ] `ConfigLoader`에서 신뢰할 수 있는 데이터에 `model_construct()` 사용
  ```python
  # 예: 내부 config 파일에서 로딩 시
  def load_trusted_config(path: Path) -> ConfigBase:
      data = yaml.safe_load(path.read_text())
      # Validation skip for trusted internal configs
      return ConfigBase.model_construct(**data)
  ```
- [ ] `@computed_field` 활용 가능 영역 식별
  ```python
  class AppConfig(ConfigBase):
      @computed_field
      @property
      def is_production(self) -> bool:
          return self.environment == "production"
  ```

# 작업 2.2.3: Validation 개선
- [ ] `@validator` → `@field_validator` 전환 확인
- [ ] `@model_validator` 활용 (cross-field validation)
- [ ] `ValidationInfo` 활용하여 context-aware validation
```

**예상 소요 시간**: 2일
**우선순위**: P2

---

### 2.3 개발 경험 개선

**구체적 작업**:

```markdown
# 작업 2.3.1: Pre-commit Hooks 설정
- [ ] `.pre-commit-config.yaml` 생성
  ```yaml
  repos:
    - repo: https://github.com/astral-sh/ruff-pre-commit
      rev: v0.9.0
      hooks:
        - id: ruff
          args: [--fix]
        - id: ruff-format

    - repo: https://github.com/pre-commit/mirrors-mypy
      rev: v1.14.0
      hooks:
        - id: mypy
          additional_dependencies: [pydantic>=2.0]
  ```
- [ ] `pre-commit install` 가이드 추가

# 작업 2.3.2: GitHub Actions 매트릭스 확대
- [ ] Python 버전 매트릭스: 3.9, 3.10, 3.11, 3.12, 3.13
- [ ] OS 매트릭스: ubuntu, macos, windows
- [ ] 의존성 캐싱 최적화

# 작업 2.3.3: Dev Container 설정
- [ ] `.devcontainer/devcontainer.json` 생성
- [ ] VSCode 확장 추천 (Python, Pylance, Ruff, etc.)
```

**예상 소요 시간**: 2일
**우선순위**: P3

---

## 🔬 Phase 3: Advanced Features (3-4 weeks)

### 3.1 성능 벤치마크 및 최적화

```markdown
# 작업 3.1.1: 벤치마크 스위트 구축
- [ ] `benchmarks/` 디렉토리 생성
- [ ] `pytest-benchmark` 통합
- [ ] 주요 작업 벤치마크:
  - [ ] Config 로딩 속도 (YAML/JSON/TOML)
  - [ ] Validation 속도 (flat vs nested)
  - [ ] Override 처리 속도
  - [ ] 메모리 사용량

# 작업 3.1.2: 성능 최적화
- [ ] 재귀 깊이 제한 (deep_merge, resolve_file_references)
- [ ] 파일 캐싱 (동일 파일 여러 번 로딩 방지)
- [ ] Lazy loading (플러그인, 비동기 로더)
```

**예상 소요 시간**: 1주
**우선순위**: P3

---

### 3.2 기능 확장

```markdown
# 작업 3.2.1: Config 비교 및 병합 개선
- [ ] `diff()` 메서드 고도화 (타입별 비교)
- [ ] `merge()` 충돌 해결 전략 옵션
- [ ] JSON Patch (RFC 6902) 지원

# 작업 3.2.2: 원격 소스 확장
- [ ] S3 플러그인 (`s3://bucket/config.yaml`)
- [ ] HTTP Basic Auth 지원
- [ ] Vault 통합 예제

# 작업 3.2.3: CLI 도구
- [ ] `confee validate <file>` - 설정 파일 검증
- [ ] `confee schema <class>` - JSON 스키마 생성
- [ ] `confee diff <file1> <file2>` - 설정 비교
```

**예상 소요 시간**: 2주
**우선순위**: P4 (선택적)

---

## 📊 우선순위 매트릭스

| Task | Impact | Effort | Priority | Timeline |
|------|--------|--------|----------|----------|
| 테스트 커버리지 확대 | HIGH | MEDIUM | P0 | Week 1-2 |
| 코드 품질 개선 | HIGH | LOW | P1 | Week 2 |
| 문서화 개선 | HIGH | MEDIUM | P1 | Week 2-3 |
| 패키징 현대화 | MEDIUM | LOW | P2 | Week 3 |
| Pydantic V2 최적화 | MEDIUM | LOW | P2 | Week 3 |
| 개발 경험 개선 | MEDIUM | LOW | P3 | Week 4 |
| 성능 벤치마크 | LOW | MEDIUM | P3 | Week 5 |
| 기능 확장 | LOW | HIGH | P4 | Week 6+ |

---

## 🎯 Success Metrics

**완료 기준**:

1. **테스트**:
   - [ ] 전체 커버리지 > 90%
   - [ ] 모든 공개 API 테스트됨
   - [ ] CI/CD 모든 테스트 통과

2. **문서**:
   - [ ] MkDocs 사이트 배포됨
   - [ ] `/examples` 디렉토리에 7+ 예제
   - [ ] API 레퍼런스 자동 생성
   - [ ] CONTRIBUTING.md, ARCHITECTURE.md 존재

3. **코드 품질**:
   - [ ] Ruff 경고 0개
   - [ ] Mypy strict mode 통과
   - [ ] 중복 코드 제거됨
   - [ ] py.typed 배포됨

4. **성능**:
   - [ ] Benchmark 스위트 존재
   - [ ] 성능 회귀 테스트 자동화

---

## 🚨 Breaking Changes (향후 고려)

**v1.0 릴리스 전 고려사항**:

1. **API 변경**:
   - `SystemExit` 제거 → 예외 기반 에러 처리
   - `_frozen_instances` 구현 변경 (WeakSet)

2. **Deprecation 경고**:
   - 현재 버전에 deprecation 경고 추가
   - 최소 2개 마이너 버전 동안 유지

3. **마이그레이션 가이드**:
   - v0.x → v1.0 업그레이드 가이드 작성

---

## 📝 Notes & Decisions

**결정된 사항**:

1. **Build System**: Hatchling 선택 (Pure Python 라이브러리에 최적)
2. **문서 도구**: MkDocs Material (현대적 UI, 검색 기능)
3. **패키지 매니저**: uv 권장 (속도), pip 호환성 유지
4. **버전 관리**: VCS 태그 기반 (hatch-vcs)

**보류된 사항**:

1. **Poetry 전환**: 현재 setuptools→hatchling으로 충분
2. **전체 리팩토링**: 점진적 개선 우선

---

## 🔗 References

- [Pydantic v2 Best Practices](https://docs.pydantic.dev/latest/)
- [Python Packaging Guide 2025](https://packaging.python.org/en/latest/)
- [PEP 735 - Dependency Groups](https://peps.python.org/pep-0735/)
- [PEP 561 - Type Stubs](https://peps.python.org/pep-0561/)
- Research Sessions:
  - Architecture Analysis: ses_458357f27ffeRjT1yN2VJhcrwS
  - Test Coverage: ses_458356dcbffeyfTbGRl15fJXEG
  - Documentation: ses_458355c2cffe1MWCTjOd2pfBkM
  - Pydantic v2: ses_458354f47ffeycuhAu1O9MSPu6
  - Packaging: ses_458353ea4ffeLSXkyzi3fsBrUi

---

**Plan Created**: 2026-01-10
**Next Review**: After Phase 1 completion
**Owner**: Development Team
