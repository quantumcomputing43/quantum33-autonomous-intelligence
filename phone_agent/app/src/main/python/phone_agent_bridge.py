from program.runtime import AutonomousPhoneRuntime

_runtime = AutonomousPhoneRuntime()

def handle_command(
    command: str,
    repository: str = "",
    github_token: str = "",
    explicit_write_authorization: bool = False,
) -> str:
    return _runtime.handle_human_command(
        command=command,
        repository=repository,
        github_token=github_token,
        explicit_write_authorization=explicit_write_authorization,
    )
