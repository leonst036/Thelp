import executer
import ui
import os
import dotenv

dotenv.load_dotenv()
width = int(os.getenv("WIDTH"))
ui.create_box(width, "Welcome to Thelp")

command_hello_world = "echo 'Hello World!'"
ui.new_column(width, " 1. Execute Hello World", command_hello_world)

ui.close_box(width)

selection = input("Select an option: ")
if selection == "1":
    executer.execute(command_hello_world)