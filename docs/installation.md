# Installation

## Requirements

- **Python**: 3.10 or higher
- **Operating System**: Linux, macOS, or Windows
- **Dependencies**: None (gtext is standalone)

## Install from PyPI

The recommended way to install gtext is from PyPI using pip:

```bash
pip install gtext
```

### Verify Installation

Check that gtext is installed correctly:

```bash
gtext --version
```

You should see output like:

```
gtext 0.1.0
```

## Install from Source

If you want the latest development version or want to contribute:

### 1. Clone the Repository

```bash
git clone https://github.com/genropy/gtext.git
cd gtext
```

### 2. Install in Development Mode

```bash
pip install -e .
```

### 3. Install Development Dependencies

For running tests and building documentation:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Or install all dependencies (dev + docs)
pip install -e ".[all]"
```

## Virtual Environment (Recommended)

It's recommended to use a virtual environment:

### Using venv

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install gtext
pip install gtext
```

### Using conda

```bash
# Create conda environment
conda create -n gtext python=3.10

# Activate
conda activate gtext

# Install gtext
pip install gtext
```

## Verify Installation with Test

Create a test file to verify gtext is working:

**File: `test.md.gtext`**

```markdown
# Test Document

This is a test.
```

**Run gtext:**

```bash
gtext cast test.md.gtext
```

**Expected output:**

```
✓ Processed test.md.gtext → test.md
```

Check that `test.md` was created with the same content.

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade gtext
```

## Uninstalling

To remove gtext:

```bash
pip uninstall gtext
```

## Troubleshooting

### Command not found

If `gtext` command is not found after installation:

1. **Check if pip bin directory is in PATH**:
   ```bash
   python -m gtext --version
   ```

2. **Reinstall with user flag** (if not using virtual environment):
   ```bash
   pip install --user gtext
   ```

### Permission errors

If you get permission errors during installation:

```bash
# Use --user flag
pip install --user gtext

# Or use a virtual environment (recommended)
```

### Python version issues

Ensure you're using Python 3.10 or higher:

```bash
python --version
```

If you have multiple Python versions, you may need to use:

```bash
python3.10 -m pip install gtext
```

## Next Steps

Now that gtext is installed, proceed to the [Quick Start Guide](quickstart.md) to learn how to use it.
