import os


def _get_env_var(var_name: str, friendly_name: str | None = None) -> str:
    value = os.getenv(var_name, "")
    if not value:
        msg = f"no {friendly_name or var_name} provided"
        raise ValueError(msg)
    return value


def get_contiguity_token() -> str:
    return _get_env_var("CONTIGUITY_TOKEN", "Contiguity token")


def get_data_key() -> str:
    return _get_env_var("CONTIGUITY_DATA_KEY", "data key")


def get_project_id() -> str:
    return _get_env_var("CONTIGUITY_PROJECT_ID", "project ID")
