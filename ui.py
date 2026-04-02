def create_box(width, title):
    # Top border
    print("┌" + "─" * (width - 2) + "┐")

    # Title with padding
    padding = (width - len(title) - 2) // 2
    print("│" + " " * padding + title + " " * (width - len(title) - 2 - padding) + "│")

def new_column(width, option, command):
    length = len(option)
    print("│" + option + " " * (width - 2 - length) + "│")

def close_box(width):
    print("└" + "─" * (width - 2) + "┘")
