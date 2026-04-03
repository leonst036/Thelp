import json

def parse_commands():
    with open("config/commands.json", "r", encoding="utf-8") as f:
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

def parse_servers():
    with open("config/ssh_servers.json", "r", encoding="utf-8") as f:
        servers = json.load(f)
    return servers

def get_server_names():
    """Returns a list of server display names in order"""
    servers = parse_servers()
    return [server_data.get('name', key) for key, server_data in servers.items()]

def get_server_by_index(index):
    """Retrieves a server by its display index (0-based)"""
    servers = parse_servers()
    server_keys = list(servers.keys())
    if 0 <= index < len(server_keys):
        return servers[server_keys[index]]
    return None

def get_server_command_by_index(server_data, index):
    """Retrieves a command for a specific server by its display index (0-based)"""
    commands = server_data.get('commands', {})
    command_keys = list(commands.keys())
    if 0 <= index < len(command_keys):
        return commands[command_keys[index]]["command"]
    return None

def get_total_servers():
    """Returns the total number of servers"""
    return len(parse_servers())

def get_server_by_name_or_key(name_or_key):
    """Retrieves a server by its key or display name"""
    try:
        servers = parse_servers()
    except Exception:
        return None

    if name_or_key in servers:
        return servers[name_or_key]

    for key, data in servers.items():
        if data.get('name') == name_or_key:
            return data

    return None
