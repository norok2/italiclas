"""Configurations and settings."""

import importlib.metadata
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_APP_NAME = Path(__file__).parent.name


# ======================================================================
class AppInfo(BaseModel):
    """Application information."""

    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    pkg_dir: Path = Path(__file__).resolve().parent
    name: str = _APP_NAME
    version: str = importlib.metadata.version(_APP_NAME)
    description: str = str(importlib.metadata.metadata(_APP_NAME)["Summary"])
    author: str = "{} <{}>".format(
        importlib.metadata.metadata(_APP_NAME)["Author"],
        importlib.metadata.metadata(_APP_NAME)["Author-email"],
    )
    license: str = str(importlib.metadata.metadata(_APP_NAME)["License"])
    year: int = 2024


info = AppInfo()


# ======================================================================
# type: ignore[call-arg]
# mypy: disable-error-code="call-arg"
class Settings(BaseSettings):
    """Application settings."""

    api_prefix: str = Field(..., json_schema_extra={"env": "API_PREFIX"})
    api_version: str = Field(..., json_schema_extra={"env": "API_VERSION"})

    allowed_hosts: list[str] = Field(
        ...,
        json_schema_extra={"env": "ALLOWED_HOSTS"},
    )

    log_level: str = Field(..., json_schema_extra={"env": "LOG_LEVEL"})
    max_log_file_size: int = Field(
        ...,
        json_schema_extra={"env": "MAX_LOG_FILE_SIZE"},
    )
    max_log_file_count: int = Field(
        ...,
        json_schema_extra={"env": "MAX_LOG_FILE_COUNT"},
    )

    data_dir: Path = Field(..., json_schema_extra={"env": "DATA_DIR"})
    ml_dir: Path = Field(..., json_schema_extra={"env": "ML_DIR"})

    raw_data_source: str = Field(
        ...,
        json_schema_extra={"env": "RAW_DATA_SOURCE"},
    )
    raw_data_source_filename: str = Field(
        ...,
        json_schema_extra={"env": "RAW_DATA_SOURCE_FILENAME"},
    )

    raw_filename: str = Field(..., json_schema_extra={"env": "RAW_FILENAME"})
    clean_filename: str = Field(
        ...,
        json_schema_extra={"env": "CLEAN_FILENAME"},
    )
    ml_model_pipeline_filename: str = Field(
        ...,
        json_schema_extra={"env": "ML_MODEL_PIPELINE_FILENAME"},
    )
    optim_params_filename: str = Field(
        ...,
        json_schema_extra={"env": "OPTIM_PARAMS_FILENAME"},
    )

    @property
    def api_base_endpoint(self) -> str:
        """Get the API base endpoint."""
        tokens = [self.api_prefix, self.api_version]
        return "/".join(token for token in tokens if token)

    @property
    def log_file_name(self) -> str:
        """Get the Log filename."""
        return f"{info.name}.log"

    model_config = SettingsConfigDict(extra="ignore", env_file=".env.app")


cfg = Settings()
