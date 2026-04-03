import paramiko
import os
import jsonParser
import ui

def connect_ssh_server(host, port, username, password):
    """Connects to a server"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=username, password=password, port=port)
        return client
    except paramiko.AuthenticationException:
        print("Authentication failed")
        return None
    except paramiko.SSHException as e:
        print(f"SSH error: {e}")
        return None

def select_and_connect_server(width):
    """Handle server selection, SSH connection and command execution"""
    # Check if ssh_servers.json exists
    if not os.path.isfile("config/ssh_servers.json"):
        print("No servers found. Please add a server in ssh_servers.json")
        return None
    
    # Get available servers
    server_names = jsonParser.get_server_names()
    if not server_names:
        print("No servers configured")
        return None
    
    # Prompt user for server selection
    server_selection = input("Select a server: ").lower()
    try:
        server_index = int(server_selection) - 1
        selected_server = jsonParser.get_server_by_index(server_index)
        
        if selected_server:
            print(f"Connecting to {selected_server['name']}...")
            client = connect_ssh_server(
                selected_server['host'],
                selected_server['port'],
                selected_server['username'],
                selected_server['password']
            )
            if client:
                handle_server_commands(client, selected_server, width)
        else:
            print("Invalid server selection")
            return None
    except ValueError:
        print("Invalid server selection")
        return None

def handle_server_commands(client, server_data, width):
    """Display and handle commands execution for the connected server"""
    ui.clear_terminal()
    commands = server_data.get('commands', {})
    
    if not commands:
        ui.create_box(width, f"{server_data.get('name', 'Server')} Commands", "")
        ui.new_column(width, " No commands found. Add 'commands' to ssh_servers.json.", "")
        ui.close_box(width)
        client.close()
        return

    ui.create_box(width, f"{server_data.get('name', 'Server')} Commands", "")
    command_keys = list(commands.keys())
    for index, key in enumerate(command_keys, start=1):
        cmd = commands[key]
        ui.new_column(width, f" {index}. {cmd.get('name', key)}", "")
    ui.close_box(width)

    selection = input("Select a command: ")
    try:
        selection_index = int(selection) - 1
        command_str = jsonParser.get_server_command_by_index(server_data, selection_index)
        
        if command_str:
            if "{input}" in command_str:
                user_input = input("Enter input for command: ")
                command_str = command_str.replace("{input}", user_input)

            ui.clear_terminal()
            ui.create_box(width, "Execution Output", f" {server_data['name']}─")

            stdin, stdout, stderr = client.exec_command(command_str)
            for line in stdout:
                cleaned = line.strip().replace('\t', '    ')
                max_len = width - 4
                if not cleaned:
                    ui.new_column(width, " ", "")
                    continue
                for i in range(0, len(cleaned), max_len):
                    ui.new_column(width, f" {cleaned[i:i+max_len]}", "")

            for line in stderr:
                cleaned = line.strip().replace('\t', '    ')
                max_len = width - 4
                if not cleaned:
                    ui.new_column(width, " ", "")
                    continue
                for i in range(0, len(cleaned), max_len):
                    ui.new_column(width, f" [ERROR] {cleaned[i:i+max_len]}", "")

            ui.close_box(width)
        else:
            print("Invalid command selection")
    except ValueError:
        print("Invalid command selection")
    finally:
        client.close()
