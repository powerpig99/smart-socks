# Python Environment Setup (UV)

This project uses `uv` for Python environment management.

## Prerequisites

Install UV if not already installed:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with Homebrew
brew install uv
```

Verify installation:
```bash
uv --version  # Should show uv version
```

## Quick Setup

```bash
# 1. Navigate to Python code directory
cd 04_Code/python

# 2. Create virtual environment and install dependencies
uv sync

# 3. Activate environment (for running scripts)
source .venv/bin/activate

# 4. Verify installation
python -c "import serial; import numpy; import matplotlib; import imageio; print('✅ All imports working!')"
```

## Alternative: Using UV without activating environment

```bash
# Run any Python script directly with UV (no activation needed)
cd 04_Code/python

# Run with UV
uv run calibration_visualizer.py --port /dev/cu.usbmodem2101

# Or with explicit Python
uv run python calibration_visualizer.py --port /dev/cu.usbmodem2101
```

## Running Python Scripts

### Option 1: With activated environment (traditional)

```bash
cd 04_Code/python
source .venv/bin/activate

# Run with your port (find with: pio device list)
python calibration_visualizer.py --port /dev/cu.usbmodem2101
```

### Option 2: With UV run (recommended)

```bash
cd 04_Code/python

# No activation needed - UV handles it
uv run calibration_visualizer.py --port /dev/cu.usbmodem2101

# Common ports:
#   macOS:   /dev/cu.usbmodem2101
#   Linux:   /dev/ttyUSB0
#   Windows: COM3
```

### Working Directory

**Always work from `04_Code/python/` directory for Python tasks:**

```bash
cd ~/Projects/Smart-Socks/04_Code/python

# Then use UV commands
uv sync
uv run calibration_visualizer.py --port /dev/cu.usbmodem2101
```

This keeps the Python environment co-located with the code.

## Project Structure

| Location | Purpose |
|----------|---------|
| `Smart Socks/04_Code/python/pyproject.toml` | UV project configuration |
| `Smart Socks/04_Code/python/.venv/` | Virtual environment (auto-created by UV) |
| `Smart Socks/04_Code/python/` | Python source code |

## UV Commands Reference

```bash
# Sync dependencies (install/update)
uv sync

# Add a new dependency
uv add package_name

# Add a dev dependency
uv add --dev package_name

# Run a script
uv run script.py

# Run Python module
uv run python -m module_name

# Update lock file
uv lock

# Check for updates
uv tree

# Remove a dependency
uv remove package_name
```

## Why UV?

✅ **Fast**: Written in Rust, much faster than pip
✅ **Reliable**: Lock file ensures reproducible builds
✅ **Simple**: One tool for everything (venv, pip, pip-tools, poetry)
✅ **Standards**: Uses pyproject.toml (PEP 518/621)

## Troubleshooting

### "No module named 'serial'"

```bash
# Re-sync dependencies
cd 04_Code/python
uv sync

# Or install specific package
uv add pyserial
```

### Port Permission Errors (macOS/Linux)

```bash
# Check port permissions
ls -la /dev/cu.usbmodem*  # macOS
ls -la /dev/ttyUSB*       # Linux

# Fix Linux permissions
sudo usermod -a -G dialout $USER
# Then logout and login again
```

### matplotlib backend issues

```bash
# If you get display errors, set backend
export MPLBACKEND=MacOSX
```

### UV not found

```bash
# Reinstall UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or update
uv self update
```

## Development Dependencies

Install development tools (formatters, linters):

```bash
cd 04_Code/python
uv sync --extra dev
```

Then use:
```bash
# Format code
uv run black .

# Lint code
uv run flake8

# Type check
uv run mypy .
```

## Legacy: requirements.txt

For backward compatibility, `requirements.txt` is maintained but **UV with pyproject.toml is preferred**.

If you must use pip:
```bash
cd 04_Code/python
pip install -r requirements.txt
```

See [UV documentation](https://docs.astral.sh/uv/) for more details.
