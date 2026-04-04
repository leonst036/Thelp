import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMMANDS_PATH = os.path.join(BASE_DIR, "config", "commands.json")
SERVERS_PATH = os.path.join(BASE_DIR, "config", "ssh_servers.json")

def parse_commands():
    with open(COMMANDS_PATH, "r", encoding="utf-8") as f:
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

def get_full_command_by_index(index):
    """Retrieves a full command dict by its display index (0-based)"""
    commands = parse_commands()
    command_keys = list(commands.keys())
    if 0 <= index < len(command_keys):
        return commands[command_keys[index]]
    return None

def update_command(index, name, command):
    """Updates an existing command at the given index"""
    commands = parse_commands()
    command_keys = list(commands.keys())
    if 0 <= index < len(command_keys):
        key = command_keys[index]
        commands[key]["name"] = name
        commands[key]["command"] = command
        with open(COMMANDS_PATH, "w", encoding="utf-8") as f:
            import json
            json.dump(commands, f, indent=4)

def get_total_commands():
    """Returns the total number of commands"""
    return len(parse_commands())

def add_command(name, command):
    """Adds a new command to the configuration file"""
    import uuid
    try:
        commands = parse_commands()
    except Exception:
        commands = {}

    key = str(uuid.uuid4())[:8]
    commands[key] = {
        "name": name,
        "command": command
    }

    with open(COMMANDS_PATH, "w", encoding="utf-8") as f:
        import json
        json.dump(commands, f, indent=4)

def parse_servers():
    with open(SERVERS_PATH, "r", encoding="utf-8") as f:
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

def get_full_server_command_by_index(server_index, cmd_index):
    """Retrieves a full command dict for a server by display indices (0-based)"""
    servers = parse_servers()
    server_keys = list(servers.keys())
    if 0 <= server_index < len(server_keys):
        server_data = servers[server_keys[server_index]]
        commands = server_data.get('commands', {})
        cmd_keys = list(commands.keys())
        if 0 <= cmd_index < len(cmd_keys):
            return commands[cmd_keys[cmd_index]]
    return None

def update_server_command(server_index, cmd_index, name, command):
    """Updates an existing command for a server at the given indices"""
    servers = parse_servers()
    server_keys = list(servers.keys())
    if 0 <= server_index < len(server_keys):
        key = server_keys[server_index]
        server_data = servers[key]
        commands = server_data.get('commands', {})
        cmd_keys = list(commands.keys())
        if 0 <= cmd_index < len(cmd_keys):
            cmd_key = cmd_keys[cmd_index]
            servers[key]["commands"][cmd_key]["name"] = name
            servers[key]["commands"][cmd_key]["command"] = command
            with open(SERVERS_PATH, "w", encoding="utf-8") as f:
                import json
                json.dump(servers, f, indent=4)

def add_server_command(server_index, name, command):
    """Adds a new command for a server at the given index"""
    import uuid
    servers = parse_servers()
    server_keys = list(servers.keys())
    if 0 <= server_index < len(server_keys):
        key = server_keys[server_index]
        if "commands" not in servers[key]:
            servers[key]["commands"] = {}

        cmd_key = str(uuid.uuid4())[:8]
        servers[key]["commands"][cmd_key] = {
            "name": name,
            "command": command
        }
        with open(SERVERS_PATH, "w", encoding="utf-8") as f:
            import json
            json.dump(servers, f, indent=4)

def get_total_servers():
    """Returns the total number of servers"""
    return len(parse_servers())

def add_server(name, host, username, password, port):
    """Adds a new server to the configuration file"""
    import uuid
    try:
        servers = parse_servers()
    except Exception:
        servers = {}

    key = str(uuid.uuid4())[:8]
    servers[key] = {
        "name": name,
        "host": host,
        "username": username,
        "password": password,
        "port": port,
        "commands": {}
    }

    with open(SERVERS_PATH, "w", encoding="utf-8") as f:
        import json
        json.dump(servers, f, indent=4)

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
