import os

def create_box(width, title, additional):
    # Top border
    print("┌" + "─" * (width - len(additional) - 2) + additional + "┐")

    # Title with padding
    padding = (width - len(title) - 2) // 2
    print("│" + " " * padding + title + " " * (width - len(title) - 2 - padding) + "│")

def new_column(width, option, command):
    length = len(option)
    print("│" + option + " " * (width - 2 - length) + "│")

def close_box(width):
    print("└" + "─" * (width - 2) + "┘")

def display_server_selection(width, server_names):
    """Display server selection menu"""
    create_box(width, "Connect to a Server", "")
    for index, name in enumerate(server_names, start=1):
        new_column(width, f" {index}. {name}", "")
    close_box(width)

def display_no_servers(width):
    """Display message when no servers are found"""
    create_box(width, "Connect to a Server", "")
    new_column(width, " No servers found. Please add a server in ssh_servers.json .", "")
    close_box(width)

def clear_terminal():
    """Clear the terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')
