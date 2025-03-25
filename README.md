# Nericx

Nericx is an application that allows you to back up osu! data (replays, scores, beatmaps, etc.) and integrate with osu! to play music seamlessly.

[![Download Nericx](https://img.shields.io/github/v/release/MegumiKatou02/Nericx?label=Download&style=for-the-badge)](https://github.com/MegumiKatou02/Nericx/releases/latest)

## Features
- Backup and restore osu! data (replays, scores, beatmaps, etc.)
- Integrate with osu! to play music
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
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing
Contributions are welcome! Feel free to open issues and submit pull requests.

## Acknowledgments

- Thanks to the osu! community

- Thank you, Nerine, for giving me the idea for the name <(")
