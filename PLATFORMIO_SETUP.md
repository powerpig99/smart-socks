# PlatformIO Setup Guide

**Smart Socks - ELEC-E7840 Smart Wearables (Aalto University)**

This guide covers PlatformIO setup for building and uploading firmware to the ESP32S3 XIAO.

---

## Quick Start

### 1. Add PlatformIO to PATH

PlatformIO is installed but not in your system PATH. Add this to your shell:

**For zsh (default on macOS):**
```bash
echo 'export PATH="$PATH:$HOME/.platformio/penv/bin"' >> ~/.zshrc
source ~/.zshrc
```

**For bash:**
```bash
echo 'export PATH="$PATH:$HOME/.platformio/penv/bin"' >> ~/.bashrc
source ~/.bashrc
```

**Verify installation:**
```bash
platformio --version
# Should output: PlatformIO Core, version x.x.x

# Short alias also works:
pio --version
```

---

## Build Commands

### Using VS Code Plugin (Recommended)
1. Open project folder in VS Code
2. Click PlatformIO icon in left sidebar (ant icon)
3. Under `env:xiao_esp32s3`, click:
   - **Build** - Compile firmware
   - **Upload** - Upload to ESP32
   - **Monitor** - Open serial monitor

### Using Command Line

**Build firmware:**
```bash
cd ~/Projects/Smart-Socks
platformio run --environment xiao_esp32s3

# Or using short alias:
pio run -e xiao_esp32s3
```

**Upload to ESP32:**
```bash
# Auto-detects port
platformio run --environment xiao_esp32s3 --target upload

# Specify port explicitly:
platformio run --environment xiao_esp32s3 --target upload --upload-port /dev/cu.usbmodem2101
```

**Open serial monitor:**
```bash
platformio device monitor --environment xiao_esp32s3

# Or:
pio device monitor -e xiao_esp32s3
```

**Build + Upload + Monitor (one command):**
```bash
platformio run -e xiao_esp32s3 -t upload && platformio device monitor -e xiao_esp32s3
```

---

## Project Structure

```
Smart Socks/
├── platformio.ini          # PlatformIO configuration
├── src/
│   └── main.cpp            # Main firmware (reads 6 sensors)
└── 04_Code/
    └── arduino/            # Reference sketches (not used by PlatformIO)
```

### About src/main.cpp

This is the unified firmware that:
- Reads all 6 sensors (A0-A5) at 50Hz
- Creates WiFi AP (SmartSocks-Cal)
- Serves web dashboard at http://192.168.4.1
- Outputs CSV data over serial

**Wiring:**
| Pin | Left Leg | Right Leg |
|-----|----------|-----------|
| A0 | L_P_Heel | R_P_Heel |
| A1 | L_P_Ball | R_P_Ball |
| A2 | L_S_Knee | R_S_Knee |

For single-leg deployment, connect sensors to A0-A2 only.

---

## Troubleshooting

### "command not found: platformio"

**Solution:** Add PlatformIO to PATH (see Quick Start above).

**Alternative (one-time use):**
```bash
# Use full path
~/.platformio/penv/bin/platformio run --environment xiao_esp32s3
```

### "Nothing to build"

**Cause:** `src/` folder is empty or missing.

**Solution:** Check that `src/main.cpp` exists:
```bash
ls src/
# Should show: main.cpp
```

If missing, restore from git:
```bash
git checkout src/main.cpp
```

### "Failed to connect to ESP32"

**Check port:**
```bash
# List available ports
platformio device list

# Or macOS specific:
ls /dev/cu.usbmodem*
ls /dev/tty.usbmodem*
```

**Specify port manually:**
```bash
platformio run -e xiao_esp32s3 -t upload --upload-port /dev/cu.usbmodem2101
```

### "Permission denied" on macOS

macOS may block serial port access:
1. Open **System Preferences → Security & Privacy**
2. Check if VS Code or Terminal needs permission
3. Grant access to USB devices

### Build errors after git pull

Clean and rebuild:
```bash
platformio run -e xiao_esp32s3 -t clean
platformio run -e xiao_esp32s3
```

---

## VS Code Integration

### Recommended Extensions
1. **PlatformIO IDE** (platformio.platformio-ide)
2. **C/C++** (ms-vscode.cpptools)

### Useful Shortcuts
- **Cmd+Shift+P** → "PlatformIO: Build"
- **Cmd+Shift+P** → "PlatformIO: Upload"
- **Cmd+Shift+P** → "PlatformIO: Serial Monitor"

### Auto-detect Board
PlatformIO should auto-detect the ESP32S3 XIAO when connected. If not:
1. Connect ESP32 via USB
2. Click PlatformIO icon
3. Click "PIO Home" → "Devices"
4. Select your board from the list

---

## Firmware Upload Methods

### Method 1: USB Serial (Default)
```bash
platformio run -e xiao_esp32s3 -t upload
```

### Method 2: If USB detection fails
Hold **BOOT** button while clicking upload, or:
1. Hold BOOT button
2. Press RESET button
3. Release BOOT button
4. Run upload command

### Method 3: Using Arduino IDE (Fallback)
If PlatformIO fails:
1. Open `src/main.cpp` in Arduino IDE
2. Select Board: "XIAO_ESP32S3"
3. Select Port: `/dev/cu.usbmodem2101` (or similar)
4. Click Upload

---

## Configuration Details

### platformio.ini
```ini
[env:xiao_esp32s3]
platform = espressif32
board = seeed_xiao_esp32s3
framework = arduino
upload_speed = 921600
monitor_speed = 115200
lib_deps = 
    bblanchon/ArduinoJson@^6.21.0
```

### Serial Monitor Settings
- **Baud rate:** 115200
- **Data bits:** 8
- **Parity:** None
- **Stop bits:** 1

---

## Reference

- **PlatformIO Docs:** https://docs.platformio.org/
- **XIAO ESP32S3 Wiki:** https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/
- **ESP32 Arduino Core:** https://docs.espressif.com/projects/arduino-esp32/

---

**Last Updated:** January 30, 2026
