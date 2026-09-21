from program.runtime import AutonomousPhoneRuntime

_runtime = AutonomousPhoneRuntime()

def handle_command(command: str) -> str:
    return _runtime.handle_human_command(command)
