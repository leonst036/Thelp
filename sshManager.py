import paramiko
import os
import shlex
import jsonParser
import ui

def connect_ssh_server(host, port, username, password):
    """Connects to a server"""
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
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
    except ValueError:
        print("Invalid server selection")
        return None
        
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

def select_and_monitor_server(width):
    """Handle server selection, SSH connection and monitoring"""
    if not os.path.isfile("config/ssh_servers.json"):
        print("No servers found. Please add a server in ssh_servers.json")
        return None
    
    server_names = jsonParser.get_server_names()
    if not server_names:
        print("No servers configured")
        return None
    
    server_selection = input("Select a server to monitor: ").lower()
    try:
        server_index = int(server_selection) - 1
        selected_server = jsonParser.get_server_by_index(server_index)
    except ValueError:
        print("Invalid server selection")
        return None
        
    if selected_server:
        print(f"Connecting to {selected_server['name']} for monitoring...")
        client = connect_ssh_server(
            selected_server['host'],
            selected_server['port'],
            selected_server['username'],
            selected_server['password']
        )
        if client:
            monitor_server(client, selected_server, width)
    else:
        print("Invalid server selection")
        return None

def monitor_server(client, server_data, width):
    """Monitor server resources"""
    import time
    cpu_hist = []
    ram_hist = []
    blocks = [' ', '▂', '▃', '▄', '▅', '▆', '▇', '█']

    def sparkline(data, max_len):
        if not data: return ""
        chars = [blocks[min(7, max(0, int(v / 12.5)))] for v in data[-max_len:]]
        return "".join(chars)

    def format_bytes(b):
        if b < 1024: return f"{b:.0f} B"
        elif b < 1024*1024: return f"{b/1024:.1f} KB"
        else: return f"{b/1024/1024:.1f} MB"

    try:
        last_rx = 0
        last_tx = 0
        last_time = 0

        while True:
            # Gather all info in single ssh command for speed
            cmd = (
                "top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'; "
                "free -m | awk 'NR==2{printf \"%.1f\\n\", $3*100/$2}'; "
                "df -h / | awk '$NF==\"/\"{print $5}'; "
                "cat /proc/net/dev | grep -v 'lo:' | awk '{rx+=$2; tx+=$10} END {print rx\" \"tx}'; "
                "ps aux --sort=-%cpu | head -n 4 | tail -n 3 | awk '{print $11\" \"$3}'"
            )
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode().strip().split('\n')
            
            if len(out) >= 4:
                try:
                    cpu_val = float(out[0].strip() or 0)
                    ram_val = float(out[1].strip() or 0)
                    disk_val = out[2].strip()
                    net_vals = out[3].strip().split()
                    if len(net_vals) == 2:
                        current_rx, current_tx = float(net_vals[0]), float(net_vals[1])
                    else:
                        current_rx, current_tx = 0, 0

                    top_procs = out[4:]

                    t = time.time()
                    if last_time > 0:
                        dt = t - last_time
                        rx_speed = (current_rx - last_rx) / dt
                        tx_speed = (current_tx - last_tx) / dt
                    else:
                        rx_speed, tx_speed = 0, 0
                    last_rx, last_tx, last_time = current_rx, current_tx, t

                    cpu_hist.append(cpu_val)
                    ram_hist.append(ram_val)
                    
                    max_graph_width = max(10, width - 25)
                    if len(cpu_hist) > max_graph_width: cpu_hist.pop(0)
                    if len(ram_hist) > max_graph_width: ram_hist.pop(0)

                    ui.clear_terminal()
                    ui.create_box(width, f"Monitoring {server_data.get('name', 'Server')}", " Ctrl+C to exit─")
                    
                    ui.new_column(width, f" CPU {cpu_val:5.1f}% [{sparkline(cpu_hist, max_graph_width):<{max_graph_width}}]", "")
                    ui.new_column(width, f" RAM {ram_val:5.1f}% [{sparkline(ram_hist, max_graph_width):<{max_graph_width}}]", "")
                    
                    ui.new_column(width, f" Disk Usage: {disk_val}", "")
                    ui.new_column(width, f" Network:    RX: {format_bytes(rx_speed)}/s | TX: {format_bytes(tx_speed)}/s", "")
                    
                    ui.new_column(width, " Top 3 Resource Users:", "")
                    for p in top_procs:
                        parts = p.split()
                        if len(parts) >= 2:
                            name = os.path.basename(parts[0])
                            if len(name) > 30: name = name[:27] + "..."
                            ui.new_column(width, f"   {name:<30} {parts[1]}% CPU", "")

                    ui.close_box(width)
                except ValueError:
                    pass
            
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        client.close()

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
                command_str = command_str.replace("{input}", shlex.quote(user_input))

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
