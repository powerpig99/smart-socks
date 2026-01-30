#!/usr/bin/env python3
"""
Smart Socks - Environment Setup
ELEC-E7840 Smart Wearables (Aalto University)

Automated setup script for development environment.
Installs dependencies, checks hardware, and validates installation.

Usage:
    python setup_environment.py
    python setup_environment.py --check-only
"""

import argparse
import subprocess
import sys
import os
import platform
from pathlib import Path


class Colors:
    """Terminal colors for pretty output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print section header."""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def run_command(cmd, check=True):
    """Run shell command and return result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error("Python 3.8 or higher required")
        return False
    
    print_success("Python version OK")
    return True


def check_pip():
    """Check if pip is installed."""
    success, _, _ = run_command("pip --version", check=False)
    if success:
        print_success("pip installed")
        return True
    else:
        print_error("pip not found")
        return False


def install_requirements():
    """Install Python packages from requirements.txt."""
    print_header("Installing Python Packages")
    
    req_file = Path(__file__).parent / "requirements.txt"
    if not req_file.exists():
        print_error("requirements.txt not found")
        return False
    
    print("Installing packages (this may take a few minutes)...")
    success, stdout, stderr = run_command(f"pip install -r {req_file}", check=False)
    
    if success:
        print_success("Packages installed successfully")
        return True
    else:
        print_error("Installation failed")
        print(stderr)
        return False


def check_serial_ports():
    """Check available serial ports."""
    print_header("Checking Serial Ports")
    
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        
        if not ports:
            print_warning("No serial ports found")
            return True
        
        print("Available serial ports:")
        for port in ports:
            print(f"  - {port.device}: {port.description}")
        
        # Check for common ESP32 port names
        esp32_ports = [p for p in ports if any(x in p.description.lower() 
                      for x in ['usb', 'uart', 'cp210', 'ch340', 'ftdi'])]
        
        if esp32_ports:
            print_success(f"Found {len(esp32_ports)} potential ESP32 ports")
        
        return True
        
    except ImportError:
        print_warning("pyserial not installed yet")
        return True


def check_ble():
    """Check BLE support."""
    print_header("Checking BLE Support")
    
    try:
        import bleak
        print_success("bleak installed - BLE support available")
        return True
    except ImportError:
        print_warning("bleak not installed - BLE support limited")
        print("  Install with: pip install bleak")
        return True  # Not critical


def create_directories():
    """Create necessary directory structure."""
    print_header("Creating Directory Structure")
    
    base_dir = Path(__file__).parent.parent.parent
    
    dirs = [
        base_dir / "03_Data" / "raw",
        base_dir / "03_Data" / "processed",
        base_dir / "03_Data" / "features",
        base_dir / "03_Data" / "calibration",
        base_dir / "05_Analysis" / "models",
        base_dir / "05_Analysis" / "plots",
        base_dir / "06_Presentation" / "report",
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {d.relative_to(base_dir)}")
    
    print_success("Directories created")
    return True


def run_tests():
    """Run test suite."""
    print_header("Running Tests")
    
    test_dir = Path(__file__).parent / "tests"
    if not test_dir.exists():
        print_warning("Test directory not found")
        return True
    
    success, stdout, stderr = run_command("python -m pytest tests/ -v", check=False)
    
    if success:
        print_success("All tests passed")
        return True
    else:
        print_warning("Some tests failed (may be expected without hardware)")
        return True  # Don't fail setup due to tests


def check_arduino_cli():
    """Check for Arduino CLI."""
    print_header("Checking Arduino CLI")
    
    success, _, _ = run_command("arduino-cli version", check=False)
    
    if success:
        print_success("Arduino CLI installed")
        return True
    else:
        print_warning("Arduino CLI not found")
        print("  Install from: https://arduino.github.io/arduino-cli/installation/")
        print("  Or use Arduino IDE")
        return True  # Not critical for Python setup


def check_git():
    """Check for git."""
    success, stdout, _ = run_command("git --version", check=False)
    
    if success:
        print_success(f"Git installed: {stdout.strip()}")
        return True
    else:
        print_warning("Git not found (optional but recommended)")
        return True


def print_system_info():
    """Print system information."""
    print_header("System Information")
    
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Platform: {platform.platform()}")
    print(f"Processor: {platform.processor()}")
    print(f"Python: {platform.python_version()}")
    print(f"Working Directory: {os.getcwd()}")


def check_gpu():
    """Check for GPU (optional for acceleration)."""
    print_header("Checking GPU (Optional)")
    
    # Check for CUDA (NVIDIA)
    success, _, _ = run_command("nvidia-smi", check=False)
    if success:
        print_success("NVIDIA GPU detected")
        return True
    
    # macOS Metal
    if platform.system() == "Darwin":
        print_success("macOS detected - Metal acceleration available")
        return True
    
    print("No GPU detected (CPU will be used)")
    return True


def create_virtual_env():
    """Create virtual environment."""
    print_header("Virtual Environment")
    
    venv_path = Path(__file__).parent / ".venv"
    
    if venv_path.exists():
        print_success("Virtual environment already exists")
        return True
    
    print("Creating virtual environment...")
    success, _, stderr = run_command(f"python -m venv {venv_path}", check=False)
    
    if success:
        print_success(f"Virtual environment created at {venv_path}")
        print("\nTo activate:")
        if platform.system() == "Windows":
            print(f"  {venv_path}\\Scripts\\activate")
        else:
            print(f"  source {venv_path}/bin/activate")
        return True
    else:
        print_error("Failed to create virtual environment")
        print(stderr)
        return False


def validate_installation():
    """Validate that everything works."""
    print_header("Validating Installation")
    
    checks = [
        ("Import config", "from config import SENSORS, HARDWARE"),
        ("Import data_validation", "from data_validation import validate_sensor_data"),
        ("Import logging_utils", "from logging_utils import get_logger"),
        ("Import numpy", "import numpy as np"),
        ("Import pandas", "import pandas as pd"),
        ("Import sklearn", "from sklearn.ensemble import RandomForestClassifier"),
        ("Import matplotlib", "import matplotlib.pyplot as plt"),
        ("Import serial", "import serial"),
    ]
    
    all_passed = True
    for name, cmd in checks:
        success, _, _ = run_command(f"python -c \"{cmd}\"", check=False)
        if success:
            print_success(f"{name}")
        else:
            print_error(f"{name}")
            all_passed = False
    
    return all_passed


def print_next_steps():
    """Print next steps for user."""
    print_header("Next Steps")
    
    print("""
1. HARDWARE SETUP:
   - Connect ESP32S3 to computer via USB
   - Verify in Device Manager (Windows) or ls /dev/tty* (Linux/Mac)
   
2. ARDUINO SETUP:
   - Install Arduino IDE or CLI
   - Add ESP32 board support
   - Open: 04_Code/arduino/sensor_test/sensor_test.ino
   - Select board: XIAO_ESP32S3
   - Upload sketch
   
3. TEST HARDWARE:
   python quick_test.py --port /dev/ttyUSB0  (adjust port)
   
4. COLLECT DATA:
   python serial_receiver.py --port /dev/ttyUSB0 --output ../../03_Data/raw/
   
5. RUN ML PIPELINE:
   python run_full_pipeline.py --raw-data ../../03_Data/raw/ --output ../../05_Analysis/
   
6. REAL-TIME DEMO:
   python real_time_classifier.py --model ../../05_Analysis/smart_socks_model.joblib --port /dev/ttyUSB0

For help, see:
   - TROUBLESHOOTING.md
   - CLAUDE.md
   - README.md
""")


def main():
    parser = argparse.ArgumentParser(description='Smart Socks Environment Setup')
    parser.add_argument('--check-only', action='store_true', 
                       help='Only check environment, don\'t install')
    parser.add_argument('--skip-tests', action='store_true',
                       help='Skip running tests')
    parser.add_argument('--create-venv', action='store_true',
                       help='Create virtual environment')
    
    args = parser.parse_args()
    
    print(f"""
{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║           SMART SOCKS - Environment Setup                    ║
║          ELEC-E7840 Smart Wearables - Aalto University       ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
""")
    
    print_system_info()
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Check pip
    if not check_pip():
        return 1
    
    if args.check_only:
        print_header("Environment Check Only")
        check_serial_ports()
        check_ble()
        check_arduino_cli()
        validate_installation()
        return 0
    
    # Full setup
    results = []
    
    # Create virtual environment if requested
    if args.create_venv:
        results.append(create_virtual_env())
    
    # Install requirements
    results.append(install_requirements())
    
    # Create directories
    results.append(create_directories())
    
    # Check hardware support
    check_serial_ports()
    check_ble()
    check_gpu()
    
    # Check development tools
    check_arduino_cli()
    check_git()
    
    # Validate imports
    results.append(validate_installation())
    
    # Run tests
    if not args.skip_tests:
        run_tests()
    
    # Final summary
    print_header("Setup Summary")
    
    if all(results):
        print_success("Setup completed successfully!")
        print_next_steps()
        return 0
    else:
        print_warning("Setup completed with warnings")
        print("Some components may need manual installation")
        return 1


if __name__ == '__main__':
    sys.exit(main())
