import commands

def update_display():
    lines = ["line one", "line two", "line three"]
    for i, line in enumerate(lines):
        commands.send_serial_command(f"DISPLAY {i+1} {line}")
