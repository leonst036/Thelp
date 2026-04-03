import executer
import ui
import os
import dotenv
import jsonParser
import sshManager
import argparse
import sys

dotenv.load_dotenv()
width = int(os.getenv("WIDTH") or 80)

parser = argparse.ArgumentParser(description="Thelp CLI")
parser.add_argument("--server", type=str, help="Directly connect to a specified server by name or key")
parser.add_argument("--gui", action="store_true", help="Launch the Graphical User Interface")
args = parser.parse_args()

if args.gui:
    import gui
    gui.launch()
    sys.exit(0)

if args.server:
    server_data = jsonParser.get_server_by_name_or_key(args.server)
    if not server_data:
        print(f"Server '{args.server}' not found.")
        sys.exit(1)

    client = sshManager.connect_ssh_server(
        server_data['host'],
        server_data['port'],
        server_data['username'],
        server_data['password']
    )
    if client:
        sshManager.handle_server_commands(client, server_data, width)
    else:
        sys.exit(1)
    sys.exit(0)

ui.clear_terminal()
ui.create_box(width, "Welcome to Thelp", " F: Connect to a Server─")

# Detect if the commands.json file exists, if not display a message and exit
if not os.path.isfile("config/commands.json"):
    ui.new_column(width, " No commands found. Please add a command in commands.json .", "")
    ui.close_box(width)
    exit(0)

# Display each command as a numbered option
command_names = jsonParser.get_command_names()
for index, name in enumerate(command_names, start=1):
    ui.new_column(width, f" {index}. {name}", "")

ui.close_box(width)

selection = input("Select an option: ").lower()
try:
    if selection == "f":
        # Check if servers exist and display selection menu
        ui.clear_terminal()
        if not os.path.isfile("config/ssh_servers.json"):
            ui.display_no_servers(width)
        else:
            server_names = jsonParser.get_server_names()
            ui.display_server_selection(width, server_names)
            sshManager.select_and_connect_server(width)
    else:
        selection_index = int(selection) - 1
        selected_command = jsonParser.get_command_by_index(selection_index)
        if selected_command:
            executer.execute(selected_command, width)
        else:
            print("Invalid selection")
except ValueError:
    print("Invalid selection")
