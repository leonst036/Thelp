import subprocess


def execute(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    for line in iter(process.stdout.readline, ''):
        if line:
            print(f"Output: {line.rstrip()}")
    process.wait()