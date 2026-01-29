# Python Environment Setup (UV)

This project uses `uv` for Python environment management.

## Quick Setup

```bash
# 1. Navigate to project root
cd ~/Projects/Smart-Socks  # Adjust path as needed

# 2. Create virtual environment (at project root)
uv venv

# 3. Activate environment
source .venv/bin/activate

# 4. Install dependencies
uv pip install -r 04_Code/python/requirements.txt

# 5. Verify installation
python -c "import serial; import numpy; import matplotlib; print('✅ All imports working!')"
```

## Running Python Scripts

After activation, run scripts from the **project root** (`Smart-Socks/`):

```bash
# Run with your port (find with: pio device list)
python 04_Code/python/calibration_visualizer.py --port /dev/cu.usbmodem2101
# Common ports:
#   macOS:   /dev/cu.usbmodem2101
#   Linux:   /dev/ttyUSB0
#   Windows: COM3

# Other scripts
python 04_Code/python/train_model.py --help
python 04_Code/python/real_time_classifier.py --help
```

## Environment Location

| Location | Purpose |
|----------|---------|
| `Smart Socks/.venv/` | Virtual environment (kept at root) |
| `04_Code/python/` | Python source code only |
| `04_Code/python/requirements.txt` | Dependency specifications |

## Why Project Root?

✅ **Cleaner**: Code directory contains only source files
✅ **Clear**: One environment for entire project
✅ **Standard**: Matches most Python project structures
✅ **Git**: `.venv/` is already in `.gitignore`

## Troubleshooting

### "No module named 'serial'"
```bash
# Make sure you're in the virtual environment
source .venv/bin/activate

# Install missing package
uv pip install pyserial
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
