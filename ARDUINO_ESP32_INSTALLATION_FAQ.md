# 🔧 Arduino IDE ESP32 Installation FAQ

**ELEC-E7840 Smart Wearables — Aalto University**

---

## Problem: "DEADLINE_EXCEEDED" / Timeout Error

**Error Message:**
```
Failed to install platform: 'esp32:esp32:3.3.5'.
Error: 4 DEADLINE_EXCEEDED: net/http: request canceled 
(Client.Timeout or context cancellation while reading body)
```

### Root Cause
The ESP32 package is **~500MB** and downloads slowly from GitHub/CDN. Arduino IDE's default timeout is too short, causing the download to fail before completion.

---

## ✅ Foolproof Solution: Manual Installation

Bypass the Arduino IDE downloader entirely by installing manually:

### Step 1: Download Package
Download directly from GitHub releases:
```
https://github.com/espressif/arduino-esp32/releases/download/3.3.5/esp32-3.3.5.zip
```

**Alternative versions:**
- Latest: Check https://github.com/espressif/arduino-esp32/releases
- Older (smaller): `esp32-3.3.4.zip` or `esp32-2.0.17.zip`

### Step 2: Extract to Arduino Packages Folder

**macOS:**
```bash
~/Library/Arduino15/packages/esp32/hardware/esp32/3.3.5/
```

**Windows:**
```
%LOCALAPPDATA%\Arduino15\packages\esp32\hardware\esp32\3.3.5\
```

**Linux:**
```bash
~/.arduino15/packages/esp32/hardware/esp32/3.3.5/
```

#### One-Liner Extraction Command (macOS/Linux):
```bash
mkdir -p ~/Library/Arduino15/packages/esp32/hardware/esp32/3.3.5 && \
unzip -o ~/Downloads/esp32-3.3.5.zip -d ~/Library/Arduino15/packages/esp32/hardware/esp32/3.3.5 && \
mv ~/Library/Arduino15/packages/esp32/hardware/esp32/3.3.5/esp32-3.3.5/* \
   ~/Library/Arduino15/packages/esp32/hardware/esp32/3.3.5/ && \
rmdir ~/Library/Arduino15/packages/esp32/hardware/esp32/3.3.5/esp32-3.3.5 && \
echo "✅ ESP32 3.3.5 installed successfully"
```

> **Note:** The ZIP extracts to a nested folder `esp32-3.3.5/`. Move contents up one level as shown above.

### Step 3: Restart Arduino IDE
Close and reopen Arduino IDE to detect the new package.

---

## 📁 Accessing Hidden Library Folder

The `~/Library/` folder is hidden in macOS. Access it via:

### Option 1: Finder (GUI)
1. Open Finder
2. Press `Cmd + Shift + G`
3. Type: `~/Library/Arduino15`
4. Click **Go**

### Option 2: Terminal
```bash
open ~/Library/Arduino15
```

### Option 3: Show Hidden Files in Finder
Press `Cmd + Shift + .` to toggle hidden files visibility.

---

## 🛠️ Alternative Solutions

### Solution A: Increase Timeout (May Still Fail)
1. Arduino IDE → **Settings/Preferences**
2. Find **Network** section
3. Increase **Connection timeout** to 300+ seconds
4. Retry installation

### Solution B: Use Older Version (Smaller Download)
```
Version 2.0.17 = ~200MB (vs 3.3.5 = ~500MB)
```
Install via Board Manager:
1. Tools → Board → Board Manager
2. Search "esp32"
3. Select version **2.0.17** from dropdown
4. Click Install

### Solution C: Arduino CLI (More Reliable)
```bash
# Install with extended timeout
arduino-cli config set network.timeout 600
arduino-cli core update-index
arduino-cli core install esp32:esp32@3.3.5
```

---

## ✅ Verification

After installation, verify ESP32 boards are available:

1. **Tools** → **Board** → **ESP32 Arduino**
2. You should see boards like:
   - "ESP32 Dev Module"
   - "ESP32-S3-DevKitC-1"
   - "ESP32-C3-DevKitM-1"

---

## 🚨 Troubleshooting

### Issue: "Platform already installed"
**Fix:** Delete partial installation first:
```bash
rm -rf ~/Library/Arduino15/staging/packages/esp32*
rm -rf ~/Library/Arduino15/packages/esp32
```

### Issue: ZIP extracts to nested folder
**Symptom:** Path shows `.../3.3.5/esp32-3.3.5/boards.txt` (wrong)
**Fix:** Move contents up one level:
```bash
cd ~/Library/Arduino15/packages/esp32/hardware/esp32/3.3.5
mv esp32-3.3.5/* . && rmdir esp32-3.3.5
```

### Issue: Boards don't appear after restart
**Fix:** Check folder structure:
```bash
ls ~/Library/Arduino15/packages/esp32/hardware/esp32/3.3.5/boards.txt
```
Should exist at that path (not in a subfolder).

---

## 📋 Quick Reference

| Platform | Package Path |
|----------|-------------|
| macOS | `~/Library/Arduino15/packages/esp32/hardware/esp32/3.3.5/` |
| Windows | `%LOCALAPPDATA%\Arduino15\packages\esp32\hardware\esp32\3.3.5\` |
| Linux | `~/.arduino15/packages/esp32/hardware/esp32/3.3.5/` |

---

## 🔗 Useful Links

- **ESP32 Arduino Core:** https://github.com/espressif/arduino-esp32
- **Releases:** https://github.com/espressif/arduino-esp32/releases
- **Documentation:** https://docs.espressif.com/projects/arduino-esp32/
- **See Also:** [[SOFTWARE_INSTALLATION]] | [[TROUBLESHOOTING]] | [[PLATFORMIO_SETUP]]

---

**Note:** While Arduino IDE is supported, **PlatformIO + VS Code** is the recommended development environment for this project. See [[PLATFORMIO_SETUP]] for details.

---

**Last Updated:** 2026-01-29
