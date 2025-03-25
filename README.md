# Nericx

Nericx is an application that allows you to back up osu! data (replays, scores, beatmaps, etc.) and integrate with osu! to play music seamlessly.

[![Download Nericx](https://img.shields.io/github/v/release/MegumiKatou02/Nericx?label=Download&style=for-the-badge)](https://github.com/MegumiKatou02/Nericx/releases/latest)  <img src="https://i.ppy.sh/013ed2c11b34720790e74035d9f49078d5e9aa64/68747470733a2f2f6f73752e7070792e73682f77696b692f696d616765732f4272616e645f6964656e746974795f67756964656c696e65732f696d672f75736167652d66756c6c2d636f6c6f75722e706e67" alt="." width="32" height="32"/>

## Features
- Backup and restore osu! data (replays, scores, beatmaps, etc.)
- Integrate with osu! to play music
- View osu! profile (beatmaps, pp, recent play, etc.)
- User-friendly interface

## Installation

1. Clone this repository:
   ```sh
   git clone https://github.com/MegumiKatou02/Nericx.git
   cd Nericx
   ```
2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Copy the example configuration file:
   ```sh
   cp config/example.config.py config/config.py
   ```
4. Ensure that you have the necessary additional files:
   - `icon.ico`

## Building the Project
To create a standalone executable, use `pyinstaller`:

### Standard Build:
```sh
pyinstaller --onefile --windowed --icon=icon.ico --name "Nericx" \
  --add-data "themes;themes" --add-data "config;config" \
  --add-data "models;models" --add-data "ui;ui" \
  --add-data "utils;utils" --add-data "lib;lib" main.py
```

### Build with Reduced False Positives:
```sh
pyinstaller --onefile --windowed --icon=icon.ico --name "Nericx" \
  --add-data "themes;themes" --add-data "config;config" \
  --add-data "models;models" --add-data "ui;ui" \
  --add-data "utils;utils" --add-data "lib;lib" \
  --noupx main.py
```

## License
This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Contributing
Contributions are welcome! Feel free to open issues and submit pull requests.

## Acknowledgments

- Thanks to the osu! community

- Thank you, Nerine, for giving me the idea for the name <(")
