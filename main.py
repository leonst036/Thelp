import executer
import ui
import os
import dotenv
import jsonParser

dotenv.load_dotenv()
width = int(os.getenv("WIDTH"))
ui.create_box(width, "Welcome to Thelp")

# Detect if the commands.json file exists, if not display a message and exit
if not os.path.isfile("./commands.json"):
    ui.new_column(width, " 1. No commands found. Please add a command in commands.json .", "")
    ui.close_box(width)
    exit(0)

# Display each command as a numbered option
command_names = jsonParser.get_command_names()
for index, name in enumerate(command_names, start=1):
    ui.new_column(width, f" {index}. {name}", "")

ui.close_box(width)

selection = input("Select an option: ")
try:
    selection_index = int(selection) - 1
    selected_command = jsonParser.get_command_by_index(selection_index)
    if selected_command:
        executer.execute(selected_command)
    else:
        print("Invalid selection")
except ValueError:
    print("Invalid selection")
