import subprocess


def execute(command):
    process = subprocess.run(command, capture_output=True, text=True, shell=True)
    for line in process.stdout.splitlines():
        print(f"Output: {line}")