import logging
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings"""

    # Main
    query_init_entry_limit: int = 200
    decree_eval_limit: int = 32
    send_keystrokes: bool = True
    log_level: int = logging.INFO
    websocket_keepalive_interval: int = 45

    # Misc
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    server_reload: bool = False
    database_echo: bool = False
    cpu_inference: bool = False
    enable_quantization: bool = False

    frontend_build_command: str = "pnpm build"

    @property
    def project_root(self) -> Path:
        """Root directory of the project"""
        return Path(__file__).parent.parent.parent.parent

    @property
    def frontend_dir(self) -> Path:
        """Frontend source directory"""
        return self.project_root / "GinkgoFrontend"

    @property
    def frontend_dist(self) -> Path:
        """Frontend build output directory"""
        return self.frontend_dir / "dist"

    @property
    def data_dir(self) -> Path:
        """Data directory for database files"""
        data_path = self.project_root / "GinkgoPython" / "data"
        data_path.mkdir(parents=True, exist_ok=True)
        return data_path

    @property
    def model_path(self) -> Path:
        """Path to the local LLM weights"""
        return self.project_root / "GinkgoPython" / "weights" / "gemma-3-4b-it"
        # return self.project_root / "GinkgoPython" / "weights" / "gemma-3-1b-it"

    @property
    def database_path(self) -> Path:
        """SQLite database file path"""
        return self.data_dir / "ginkgo.db"

    class Config:
        env_prefix = "GINKGO_"
        case_sensitive = False


settings = Settings()
