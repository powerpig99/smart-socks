# Smart Socks - Software Installation Guide

**ELEC-E7840 Smart Wearables — Aalto University**

> **⚠️ WORKSHOP PREPARATION (Wednesday 04-02)**
> 
> **Before the WiFi Data Collection Workshop, install:**
> 
> 1. **Python** (3.8 or higher)
>    - Guide: https://realpython.com/installing-python/
>    - Video Tutorial: https://www.youtube.com/watch?v=QhukcScB9W0
> 
> 2. **IDE** (choose one)
>    - Visual Studio Code (recommended): https://code.visualstudio.com/
>    - PyCharm: https://www.jetbrains.com/pycharm/
>    - Arduino IDE (alternative): https://www.arduino.cc/en/software
> 
> 3. **Required Hardware to Bring:**
>    - USB-C cable
>    - Microcontrollers (ESP32S3 XIAO)
>    - Breadboard, jumper wires, resistors
>    - Sensors
> 
> ---

> **Quick Links:** [[README]] | [[README_PYTHON_SETUP]] | [[PLATFORMIO_SETUP]]

This guide covers all software installation steps for the Smart Socks project using **UV** for Python environment management.

---

## Quick Start (UV - Recommended)

```bash
# 1. Install UV (Python environment manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or on Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Navigate to project
cd ~/Projects/Smart-Socks

# 3. Create UV environment
uv venv

# 4. Activate environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 5. Install dependencies
uv pip install -r 04_Code/python/requirements.txt

# 6. Verify installation
python 04_Code/python/quick_test.py --skip-hardware
```

See [[README_PYTHON_SETUP]] for detailed Python setup instructions.

---

## System Requirements

### Minimum Requirements
- **OS:** Windows 10, macOS 10.15, or Linux (Ubuntu 18.04+)
- **Python:** 3.8 or higher (managed by UV)
- **RAM:** 4 GB
- **Storage:** 2 GB free space
- **USB:** Available USB port

### Recommended Requirements
- **OS:** Windows 11, macOS 12+, or Linux (Ubuntu 20.04+)
- **Python:** 3.10 or higher
- **RAM:** 8 GB
- **Storage:** 5 GB free space
- **USB:** USB 3.0 port
- **Bluetooth:** Bluetooth 4.0+ (for wireless features)

---

## Step-by-Step Installation

### Step 1: Install UV (Python Environment Manager)

UV is a fast Python package installer and resolver. It's much faster than pip and replaces both pip and venv.

#### macOS / Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Verify Installation
```bash
uv --version  # Should show version number
```

---

### Step 2: Install PlatformIO (Embedded Development)

PlatformIO is used for ESP32 firmware development.

#### Option A: VS Code Extension (Recommended)
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search "PlatformIO IDE"
4. Install and reload VS Code

#### Option B: Command Line
```bash
# Install PlatformIO Core
pip install platformio

# Verify
pio --version
```

---

### Step 3: Install Arduino Support for ESP32

#### Using PlatformIO (Automatic)
The ESP32 platform will be installed automatically when you first build the project.

#### Using Arduino IDE (Alternative)
1. Open Arduino IDE
2. File → Preferences
3. Add to "Additional Board Manager URLs":
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Tools → Board → Board Manager
5. Search "ESP32" and install "ESP32 by Espressif Systems"

---

### Step 4: Setup Python Environment

```bash
# Navigate to project directory
cd ~/Projects/Smart-Socks

# Create UV virtual environment (at project root)
uv venv

# Activate environment
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate    # Windows

# Install all dependencies
uv pip install -r 04_Code/python/requirements.txt

# Verify key packages
python -c "import numpy, pandas, sklearn, matplotlib, serial; print('✅ All packages installed')"
```

**Why UV instead of venv/pip?**
- **10-100x faster** package installation
- **Automatic lock files** for reproducible builds
- **No Python version conflicts**
- **Replaces both pip and venv**

---

## Platform-Specific Notes

### macOS

#### Apple Silicon (M1/M2) Notes
Most packages work natively. If you encounter issues:
```bash
# Install Rosetta 2 (if not already installed)
softwareupdate --install-rosetta --agree-to-license
```

#### USB Port Names
ESP32 will appear as:
```bash
# Default port on most Macs
/dev/cu.usbmodem2101

# Find your port
ls /dev/cu.usbmodem*
```

### Linux (Ubuntu/Debian)

#### USB Permissions
Add user to dialout group:
```bash
sudo usermod -a -G dialout $USER
# Log out and back in for changes to take effect
```

#### Bluetooth Permissions
```bash
sudo usermod -a -G bluetooth $USER
```

#### Serial Port Issues
If port not accessible:
```bash
# Check port permissions
ls -la /dev/ttyUSB0

# Fix permissions (temporary)
sudo chmod 666 /dev/ttyUSB0

# Or add udev rule (permanent)
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="10c4", ATTR{idProduct}=="ea60", MODE="0666", GROUP="dialout"' | sudo tee /etc/udev/rules.d/50-esp32.rules
sudo udevadm control --reload-rules
```

### Windows

#### USB Port Permissions
If you get "Permission denied" errors:
1. Open Device Manager
2. Find your ESP32 under "Ports (COM & LPT)"
3. Right-click → Properties → Port Settings → Advanced
4. Uncheck "Use automatic settings"
5. Try different COM port numbers

#### Python Path Issues
If `python` or `pip` not found after UV installation:
```powershell
# UV installs to:
# Windows: %USERPROFILE%\.cargo\bin
# Add to PATH if needed:
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$env:USERPROFILE\.cargo\bin", "User")
```

---

## Optional Software

### Development Tools

#### VS Code (Recommended IDE)
1. Download from https://code.visualstudio.com/
2. Install extensions:
   - **PlatformIO IDE** (for ESP32 development)
   - **Python** (Microsoft)
   - **Pylance** (Microsoft)
   - **Markdown All in One**

#### Obsidian (Documentation)
For viewing linked markdown documentation:
1. Download from https://obsidian.md/
2. Open `Smart-Socks` folder as vault
3. Install plugins: Graph View, Page Preview

---

## Verification

### Test Python Environment
```bash
# Activate environment
source .venv/bin/activate

# Run quick test
python 04_Code/python/quick_test.py --skip-hardware
```

### Test ESP32 Connection
```bash
# List available ports
pio device list

# Upload test firmware
pio run --target upload --environment xiao_esp32s3
```

---

## Troubleshooting

### UV Issues

#### "uv: command not found"
```bash
# Reinstall UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or manually add to PATH
export PATH="$HOME/.cargo/bin:$PATH"
```

#### Package Installation Fails
```bash
# Clear UV cache
uv cache clean

# Try installing with verbose output
uv pip install -r 04_Code/python/requirements.txt -v
```

### ESP32 Issues

#### "Port not found"
- Check USB cable (must be data cable, not charge-only)
- Try different USB port
- Install CH340/CP210x drivers (Windows)

#### "Permission denied" (macOS/Linux)
```bash
# Check port permissions
ls -la /dev/cu.usbmodem*  # macOS
ls -la /dev/ttyUSB*       # Linux

# Fix (Linux)
sudo usermod -a -G dialout $USER
```

---

## Next Steps

After installation:
1. [[PLATFORMIO_SETUP]] - Configure PlatformIO for ESP32
2. [[README_PYTHON_SETUP]] - Detailed Python setup
3. [[calibration_visualizer]] - Run calibration tools

---

## Navigation

| Document | Description |
|----------|-------------|
| [[README]] | Project overview |
| [[README_PYTHON_SETUP]] | Detailed Python + UV setup |
| [[PLATFORMIO_SETUP]] | ESP32 development setup |
| [[CODE_REVIEW]] | Code quality documentation |

---

*Last updated: 2026-01-29 · Using UV for Python environment management*
