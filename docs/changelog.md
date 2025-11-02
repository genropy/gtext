# Changelog

All notable changes to gtext will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-02

### Added

- Initial release of gtext
- Core `TextProcessor` class for text transformation
- `IncludeExtension` with support for:
  - Static file includes
  - CLI command output includes
  - Glob pattern includes
  - Mixed includes in single block
- CLI with three commands:
  - `gtext cast` - Process single file
  - `gtext cast-all` - Process multiple files
  - `gtext watch` - Watch mode (not yet implemented)
- File extension convention: `.gtext` (e.g., `document.md.gtext`)
- Auto-detect output by stripping `.gtext` extension
- Pluggable extension system
- Comprehensive documentation with MkDocs
- Complete test suite with pytest
- Zero runtime dependencies
- Python 3.10+ support
- MIT License

### Documentation

- Quick Start guide
- Installation instructions
- User guides (Basic, CLI, Extensions, Configuration)
- Extension documentation
- Examples (Documentation, Code, Reports)
- Contributing guidelines
- Architecture documentation
- API reference

## [Unreleased]

### Planned

- Watch mode implementation
- Configuration file support (`.gtextrc`, `pyproject.toml`)
- Safe mode for restricted execution
- Parallel file processing
- Incremental builds
- Extension registry
- Pre/post processing hooks

---

**Legend**:
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Features that will be removed
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security fixes

---

## How to Read This

### Version Numbers

We use [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.1.0): New features, backwards compatible
- **PATCH** (0.1.1): Bug fixes, backwards compatible

### Release Dates

Dates are in YYYY-MM-DD format.

### Categories

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Vulnerability fixes

## Links

- [GitHub Releases](https://github.com/genropy/gtext/releases)
- [PyPI History](https://pypi.org/project/gtext/#history)
- [Roadmap](https://github.com/genropy/gtext/issues)
