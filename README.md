# Thelp
### Thelp is a tool to store and execute your commands as fast as possible.

## To-Do
- [x] Add commands without hardcoding
- [x] Add a way to edit commands
- [x] Add a way to connect to a server
- [x] Add a way to monitor a server

## Features

**Thelp** is a lightweight command-line utility that allows you to:
- Store frequently used commands in a JSON configuration file
- Execute commands quickly through an interactive menu
- Manage commands without hardcoding them into the application
- Connect to SSH servers
- Display commands in a clean, formatted box interface
- Launch an optional Graphical User Interface (GUI)
- Use dynamic input prompts (`{input}`) within commands

## Installation

1. Clone the repository:
```bash
git clone https://github.com/leonst036/Thelp
cd Thelp
```

2. Create a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```
    
3. Install dependencies (if any):
```bash
pip install -r requirements.txt
```

4. Set up your configuration files by copying the example files:
```bash
cp config/commands.json.example config/commands.json
cp config/ssh_servers.json.example config/ssh_servers.json
```

## Usage

### Running Thelp

```bash
python main.py
```

This will display an interactive menu with all available commands. Select a command by entering its number, or enter `f` to connect to a server.

**Graphical User Interface (GUI):**
You can launch the visual application using the `--gui` argument:
```bash
python main.py --gui
```

**Direct Server Connection:**
You can also bypass the menu and connect directly to a server by providing its key or name using the `--server` argument:
```bash
python main.py --server "Server Name"
```

### Adding Commands

Edit `config/commands.json` and add your commands in the following format:

```json
{
  "Command Name": {
    "name": "Command Name",
    "command": "your-shell-command-here"
  },
  "Another Command": {
    "name": "Another Command",
    "command": "another-shell-command"
  }
}
```

**Example:**
```json
{
  "List Files": {
    "name": "List Files",
    "command": "ls -la"
  },
  "Update System": {
    "name": "Update System",
    "command": "sudo apt update && sudo apt upgrade -y"
  },
  "Check Disk Space": {
    "name": "Check Disk Space",
    "command": "df -h"
  }
}
```

### Adding SSH Servers

Edit `config/ssh_servers.json` and add your servers in the following format:

```json
{
  "Server Name": {
    "name": "Server Name",
    "host": "192.168.1.10",
    "port": 22,
    "username": "username",
    "password": "yourpassword",
    "commands": {
      "Update System": {
        "name": "Update System",
        "command": "sudo apt update && sudo apt upgrade -y"
      }
    }
  }
}
```

**SSH host key verification:**
- The app rejects unknown SSH host keys for security.
- Add server host keys to your `~/.ssh/known_hosts` before connecting (for example, by connecting once with `ssh` or using `ssh-keyscan`).

### Configuration

**Environment Variables:**
- `WIDTH` - The width of the command selection box (default: 50 characters)

## Project Structure

```
Thelp/
├── main.py              # Entry point of the application
├── gui.py               # GUI implementation using customtkinter
├── ui.py                # UI utilities for displaying formatted boxes
├── executer.py          # Command execution module
├── jsonParser.py        # JSON configuration parser
├── config/
│   ├── commands.json    # Your commands configuration (git-ignored)
│   ├── commands.json.example    # Example commands file
│   ├── ssh_servers.json         # SSH servers configuration (git-ignored)
│   └── ssh_servers.json.example # Example SSH servers file
├── .env                 # Environment variables
└── README.md            # This file
```

## How It Works

1. **main.py** loads environment variables and initializes the UI
2. **jsonParser.py** reads the commands from `config/commands.json`
3. Commands are displayed in a formatted menu
4. User selects a command by number
5. **executer.py** runs the selected command using subprocess
6. Output is captured and displayed in real-time

## Requirements

- Python 3.7+


All dependencies are listed in `requirements.txt` and will be installed with `pip install -r requirements.txt`

## Planned Features

- Server monitoring capabilities
- Command history tracking
- Category sorting of commands
- Full SSH commander
## More Features soon
