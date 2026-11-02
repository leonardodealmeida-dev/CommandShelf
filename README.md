# CommandShelf

A searchable desktop command library for Linux, Git, Python, JavaScript, Java, Docker, databases, networking, and developer tools.

Built with **Python** and **PySide6**.

## Library size\n\nThe bundled library currently contains **163 curated command examples** across multiple categories. It is a practical reference, not an exhaustive index of every command or option available on Linux.\n\n## Features

- Search by title, command, description, example, or category\n- Browse a larger curated library of Linux and developer commands
- Filter commands by category
- Mark commands as favorites
- Copy commands to the clipboard
- Add personal commands through a dialog
- Save personal commands and favorites locally between sessions
- Dark interface and keyboard shortcuts

## Requirements

- Python 3.10+
- PySide6

## Run on Linux or macOS

```bash
git clone https://github.com/YOUR-USERNAME/CommandShelf.git
cd CommandShelf
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

## Run on Windows

```powershell
git clone https://github.com/YOUR-USERNAME/CommandShelf.git
cd CommandShelf
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

## Shortcuts

- `Ctrl+F`: focus the search box
- `Ctrl+Shift+C`: copy the selected command

## Data storage

Built-in commands are in `commands.json`. Personal commands and favorites are stored in `~/.commandshelf/` on Linux/macOS and `%USERPROFILE%\\.commandshelf\\` on Windows. This keeps your private commands out of the Git repository.

## Safety

CommandShelf **displays commands but does not execute them**. Always understand a command before pasting it into a terminal, especially commands that delete files or change system settings.

## Project structure

```text
CommandShelf/
├── main.py
├── commands.json
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
└── assets/
```

## Roadmap

- [ ] Edit and delete custom commands
- [ ] Import/export the command library
- [ ] Tags and sorting options
- [ ] Light/dark theme toggle
- [ ] Automated tests

## License

This project uses the MIT License. See `LICENSE`.
