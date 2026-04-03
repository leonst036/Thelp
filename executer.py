import subprocess
import shlex
import ui


def execute(command, width):
    if "{input}" in command:
        user_input = input("Enter input for command: ")
        command = command.replace("{input}", shlex.quote(user_input))

    ui.clear_terminal()
    ui.create_box(width, "Execution Output", "")

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

        for line in iter(process.stdout.readline, ''):
            if line:
                cleaned_line = line.rstrip().replace('\t', '    ')
                max_len = width - 4
                if not cleaned_line:
                    ui.new_column(width, " ", "")
                    continue
                for i in range(0, len(cleaned_line), max_len):
                    chunk = cleaned_line[i:i + max_len]
                    ui.new_column(width, f" {chunk}", "")

        for line in iter(process.stderr.readline, ''):
            if line:
                cleaned_line = line.rstrip().replace('\t', '    ')
                max_len = width - 4
                if not cleaned_line:
                    ui.new_column(width, " ", "")
                    continue
                for i in range(0, len(cleaned_line), max_len):
                    chunk = cleaned_line[i:i + max_len]
                    ui.new_column(width, f" [ERROR] {chunk}"[:max_len + 1], "")

        process.wait()
    except Exception as e:
        ui.new_column(width, f" Error: {str(e)}"[:width - 3], "")

    ui.close_box(width)
