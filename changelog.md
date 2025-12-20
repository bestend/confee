# Changelog

All notable changes to this project will be documented in this file.

## [0.1.2] - 2025-12-21

### Added
- Initial stable release
- Type-safe configuration with Pydantic V2
- Multi-source configuration (file/env/CLI)
- Nested field access with dot notation
- File reference support (@file:, @config:)
- Configuration inheritance with override_with()
- Strict/non-strict validation modes
- Auto help generation with --help flag
- Bilingual documentation (English & Korean)
- GitHub Actions CI/CD automation
- Automated PyPI deployment on tag push
- pyproject.toml auto-version update in workflow
- Automatic GitHub Release creation
- 116 test cases with 91% code coverage
- Full documentation (README, comparison with OmegaConf, development guide)

### Features
- YAML/JSON auto-detection
- Environment variable override with custom prefix
- CLI argument parsing with flexible syntax
- Nested configuration support
- Color-coded terminal output
- Comprehensive error messages

### Fixed
- Python 3.9 type hint compatibility (`Optional[str]` instead of `str | None`)
- Tag pattern now accepts both `v0.1.0` and `0.1.0` formats

---

## Format

This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

Versions follow [Semantic Versioning](https://semver.org/) (Major.Minor.Patch).

