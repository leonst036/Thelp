import json

def parse_commands():
    with open("commands.json", "r", encoding="utf-8") as f:
        commands = json.load(f)
    return commands

def get_command_names():
    """Returns a list of command display names in order"""
    commands = parse_commands()
    return [command_data.get('name', key) for key, command_data in commands.items()]

def get_command_by_index(index):
    """Retrieves a command by its display index (0-based)"""
    commands = parse_commands()
    command_keys = list(commands.keys())
    if 0 <= index < len(command_keys):
        return commands[command_keys[index]]["command"]
    return None

def get_total_commands():
    """Returns the total number of commands"""
    return len(parse_commands())
