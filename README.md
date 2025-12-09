# OTA

All future OTA updates for all MicroPython projects to be released from here. Each project will have its own OTA folder underneath.

## Structure

```
OTA/
├── README.md
└── projects/
    ├── project1/
    │   └── (OTA files for project1)
    └── project2/
        └── (OTA files for project2)
```

## Adding a New Project

1. Create a new folder under `projects/` with your project name
2. Add your OTA files to that folder, typically including:
   - `firmware.bin` - The compiled firmware binary
   - `version.json` - Version information and metadata
   - `manifest.json` - OTA manifest with file checksums (optional)

## Usage

Each project folder contains the necessary files for OTA updates specific to that MicroPython project. Devices can fetch updates from their respective project folder.
