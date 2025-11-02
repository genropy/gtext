# Architecture

gtext follows a simple, pluggable architecture designed for extensibility and ease of use.

## Overview

```
┌─────────────────┐
│   CLI / API     │  User Interface
└────────┬────────┘
         │
┌────────▼────────┐
│  TextProcessor  │  Core Engine
└────────┬────────┘
         │
    ┌────▼────┐
    │Extension│  Extension 1
    │  System │
    └────┬────┘
         │
    ┌────▼────┐
    │Extension│  Extension 2
    │  System │
    └────┬────┘
         │
    ┌────▼────┐
    │  Output  │  Generated Files
    └─────────┘
```

## Components

### 1. CLI (`gtext/cli.py`)

**Purpose**: Command-line interface

**Commands**:
- `cast` - Process single file
- `cast-all` - Process multiple files
- `watch` - Watch and regenerate (planned)

**Responsibilities**:
- Argument parsing
- File discovery
- Error reporting
- User feedback

### 2. TextProcessor (`gtext/processor.py`)

**Purpose**: Core processing engine

**Key Methods**:
- `process_file()` - Process a `.gtext` file
- `process_string()` - Process text content
- `add_extension()` - Register an extension

**Responsibilities**:
- File I/O
- Extension management
- Processing pipeline
- Context management

### 3. Extension System (`gtext/extensions/`)

**Purpose**: Pluggable transformations

**Base Class**: `BaseExtension`

**Built-in Extensions**:
- `IncludeExtension` - File includes, CLI, globs

**Responsibilities**:
- Text transformation
- Content generation
- Validation
- Custom processing

## Data Flow

### File Processing

```
1. User runs: gtext cast document.md.gtext

2. CLI parses arguments
   ├─ Input: document.md.gtext
   └─ Output: document.md (auto-detected)

3. TextProcessor reads file
   └─ content = read(document.md.gtext)

4. Extensions process content sequentially
   ├─ Extension 1: content = ext1.process(content, context)
   ├─ Extension 2: content = ext2.process(content, context)
   └─ Extension N: content = extN.process(content, context)

5. Write output
   └─ write(document.md, processed_content)

6. CLI reports success
   └─ "✓ Processed document.md.gtext → document.md"
```

### Extension Pipeline

```
Input Content
     │
     ▼
┌─────────────────┐
│  Extension 1    │  IncludeExtension
│  - Static files │
│  - CLI commands │
│  - Glob patterns│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Extension 2    │  Custom Extension
│  - Variables    │
│  - Conditionals │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Extension N    │  Another Extension
│  - Validation   │
│  - Formatting   │
└────────┬────────┘
         │
         ▼
   Output Content
```

## Extension Architecture

### BaseExtension

```python
class BaseExtension(ABC):
    name: str = "base"

    @abstractmethod
    def process(self, content: str, context: Dict) -> str:
        pass
```

### Extension Lifecycle

```
1. Instantiation
   ext = MyExtension(option1=value)

2. Registration
   processor.add_extension(ext)

3. Execution (for each file)
   result = ext.process(content, context)

4. Cleanup
   (extensions are stateless)
```

## Context Dictionary

The context dict carries metadata through the processing pipeline:

```python
context = {
    "input_path": Path("document.md.gtext"),
    # Extensions can add custom keys
    "custom_key": "custom_value"
}
```

**Usage**:
- Read by extensions for path resolution
- Write by extensions to share data
- Passed through entire pipeline

## File Extension Convention

```
source.md.gtext
  │      │    │
  │      │    └─ Identifies as gtext source
  │      └────── Target format (Markdown)
  └───────────── Base name

Output: source.md
```

## Error Handling Strategy

### Fault Tolerance

- **Philosophy**: Never break the build
- **Implementation**: Errors become HTML comments
- **Example**: `<!-- ERROR: File not found: missing.md -->`

### Error Propagation

```
Extension encounters error
     │
     ▼
Catch exception
     │
     ▼
Generate error comment
     │
     ▼
Continue processing
```

## Design Principles

### 1. Zero Configuration

Works immediately after installation:

```bash
pip install gtext
gtext cast document.md.gtext
```

### 2. Convention over Configuration

- `.gtext` extension identifies source files
- Auto-detect output by stripping extension
- Relative paths from source file location

### 3. Extensibility

- Plugin architecture
- Simple base class
- Sequential processing
- Shared context

### 4. Fault Tolerance

- Errors don't stop builds
- Clear error messages
- Continue on failure

### 5. Simplicity

- Small core
- Clear interfaces
- Minimal dependencies
- Easy to understand

## Performance Considerations

### File I/O

- Read once, write once
- UTF-8 encoding
- Buffered I/O

### Extension Processing

- Sequential (not parallel)
- Each extension processes full content
- No caching (stateless)

### Optimization Opportunities

- Parallel file processing (future)
- Incremental processing (future)
- Caching for expensive operations (future)

## Security Model

### Current

- **Trust model**: Process only trusted `.gtext` files
- **CLI execution**: Full shell access with `shell=True`
- **File access**: No restrictions

### Future

- `--safe-mode` flag
- Sandboxed CLI execution
- Restricted file access
- Command whitelist

## Extension Points

### Current

1. **Extensions**: Inherit from `BaseExtension`

### Future

1. **Hooks**: Pre/post processing hooks
2. **Filters**: Content filters
3. **Validators**: Content validators
4. **Generators**: Content generators

## Dependencies

**Runtime**: None (zero dependencies)

**Development**:
- pytest
- pytest-cov
- black
- ruff
- mypy

**Documentation**:
- mkdocs
- mkdocs-material
- mkdocstrings

## Future Directions

### Planned Features

1. **Watch mode**: Auto-regenerate on changes
2. **Configuration files**: `.gtextrc`, `pyproject.toml`
3. **Safe mode**: Restricted execution
4. **Parallel processing**: Process multiple files concurrently
5. **Incremental builds**: Only process changed files
6. **Extension registry**: Discover and load extensions
7. **Hooks system**: Pre/post processing hooks

### Extension Ideas

- Variable substitution
- Conditional blocks
- Table of contents generation
- Link validation
- Spell checking
- AI-powered transformations

## Related Documentation

- [Extension System](guide/extensions.md)
- [Creating Custom Extensions](extensions/custom.md)
- [API Reference](api/processor.md)
