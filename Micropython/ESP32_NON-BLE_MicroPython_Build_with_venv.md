# Build WiFi-Only / BLE-Free MicroPython Firmware for ESP32-WROOM-32 (Raspberry Pi)

This guide explains how to build a MicroPython firmware for ESP32-WROOM-32 that includes WiFi but disables BLE, maximizing available RAM.

---

## Step 0 — Create and activate Python virtual environment

```bash
# Create a new Python virtual environment
python3 -m venv ~/micropython-build-env

# Activate the virtual environment
source ~/micropython-build-env/bin/activate

# Upgrade pip, setuptools, wheel inside the venv
pip install --upgrade pip setuptools wheel
```

> After activation, your shell prompt will show `(micropython-build-env)`.
> All Python commands for building MicroPython should be run inside this environment.

When done, you can deactivate the environment with:

```bash
deactivate
```

To reactivate later:

```bash
source ~/micropython-build-env/bin/activate
```

---

## Step 1 — Install prerequisites

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install git and build tools
sudo apt install git make gcc wget libffi-dev build-essential python3-pip -y

# Install ESP-IDF dependencies
sudo apt install libncurses-dev flex bison gperf python3-pyelftools python3-setuptools python3-wheel cmake ninja-build ccache -y
```

---

## Step 2 — Clone MicroPython and list available versions

```bash
# Clone the MicroPython repository
git clone https://github.com/micropython/micropython.git
cd micropython

# Fetch all tags (versions)
git fetch --all --tags

# List the latest 20 MicroPython versions
git tag --sort=-version:refname | head -20
```

> Choose a version from the list above. For the latest preview/development version, use `master` branch.

```bash
# Option 1: Use master branch for latest preview version
git checkout master

# Option 2: Or checkout a specific stable version
# git checkout v1.24.1
```

---

## Step 3 — Get submodules

```bash
git submodule update --init --recursive
```

---

## Step 4 — Build the cross-compiler

```bash
cd mpy-cross
make
cd ..
```

---

## Step 5 — Check ESP-IDF compatibility and clone

```bash
cd ports/esp32

# Check which ESP-IDF version is required
cat README.md | grep -A 10 "ESP-IDF"
```

> The README will specify the compatible ESP-IDF version (e.g., v5.5.1 for latest master).

```bash
# Clone the compatible ESP-IDF version (replace v5.5.1 with version from README)
git clone -b v5.5.1 --recursive https://github.com/espressif/esp-idf.git

# Install ESP-IDF (use existing venv instead of creating a new one)
cd esp-idf
export IDF_PYTHON_ENV_PATH=$VIRTUAL_ENV
./install.sh

# Source the ESP-IDF environment (must be done in every new terminal session)
source export.sh

# Go back to esp32 port directory
cd ..
```

---

## Step 6 — Prepare ESP32 firmware build

```bash
make submodules
```

---

## Step 7 — Disable BLE

```bash
idf.py menuconfig
```

Navigate in the menu:

```
Component config  ---> 
    Bluetooth  ---> 
        [ ] Bluetooth (uncheck)
```

Save (`S`) and exit (`Q`).

> This ensures BLE/NimBLE is completely removed. WiFi remains active.

---

## Step 8 — Build the firmware

```bash
make -j4  # use 4 cores; adjust if needed
```

After building, the firmware binary will be at:

```
~/micropython/ports/esp32/build-ESP32_GENERIC/firmware.bin
```

To see all build outputs:

```bash
cd build-ESP32_GENERIC
ls -lh *.bin
```

---

## Step 9 — Flash to ESP32-WROOM

### Option 1: Flash single firmware.bin file (Simple)

```bash
cd ~/micropython/ports/esp32

# Erase flash first (recommended)
esptool.py --chip esp32 --port /dev/ttyACM0 erase_flash

# Flash firmware built in this guide
esptool.py --chip esp32 --port /dev/ttyACM0 write_flash -z 0x1000 build-ESP32_GENERIC/firmware.bin

# To flash a custom firmware .bin file (e.g., from another location):
esptool.py --chip esp32 --port /dev/ttyACM0 erase_flash
esptool.py --chip esp32 --port /dev/ttyACM0 write_flash -z 0x1000 /path/to/your/firmware.bin
# Example:
# esptool.py --chip esp32 --port /dev/ttyACM0 write_flash -z 0x1000 /home/pi/Desktop/OTA/OTA/Micropython/micropython-BG-NoBLE-1.24.1.bin
```

### Option 2: Flash all partitions (Recommended for idf.py builds)

```bash
cd ~/micropython/ports/esp32

# Erase flash first
esptool.py --chip esp32 --port /dev/ttyACM0 erase_flash

# Flash bootloader, partition table, and firmware
esptool.py --chip esp32 --port /dev/ttyACM0 write_flash -z \
  0x1000 build/bootloader/bootloader.bin \
  0x8000 build/partition_table/partition-table.bin \
  0x10000 build/micropython.bin
```

### Option 3: Using make deploy

```bash
make deploy PORT=/dev/ttyACM0
```

> Replace `/dev/ttyACM0` with your ESP32's serial port if different.

---

## Step 10 — Verify firmware

Connect via REPL and run:

```python
# Check Bluetooth module
try:
    import bluetooth
except ImportError:
    print("BLE disabled ✔")

# Check free RAM
import gc
gc.collect()
print("Free RAM:", gc.mem_free())
```

Expected free RAM: **~130–145 KB** (instead of 70–90 KB with BLE).

---

## Notes

- You now have full MicroPython features + WiFi + no BLE.
- Suitable for uGit, Microdot, and other RAM-intensive applications.
- You can repeat the same steps for future firmware updates and include custom modules.
