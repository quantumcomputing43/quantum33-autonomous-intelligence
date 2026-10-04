from program.runtime import AutonomousPhoneRuntime

_runtime = AutonomousPhoneRuntime()

def validate_configuration(source_repo, simulation_repo, simulation_workflow,
                           github_token, model_endpoint, model_name, model_api_key):
    return _runtime.validate_configuration(
        source_repo=source_repo,
        simulation_repo=simulation_repo,
        simulation_workflow=simulation_workflow,
        github_token=github_token,
        model_endpoint=model_endpoint,
        model_name=model_name,
        model_api_key=model_api_key,
    )

def handle_command(
    command: str,
    repository: str = "",
    github_token: str = "",
    explicit_write_authorization: bool = False,
    model_endpoint: str = "",
    model_name: str = "",
    model_api_key: str = "",
    simulation_repository: str = "",
) -> str:
    return _runtime.handle_human_command(
        command=command,
        repository=repository,
        github_token=github_token,
        explicit_write_authorization=explicit_write_authorization,
        model_endpoint=model_endpoint,
        model_name=model_name,
        model_api_key=model_api_key,
        simulation_repository=simulation_repository,
    )
