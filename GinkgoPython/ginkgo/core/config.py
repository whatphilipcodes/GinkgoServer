from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings"""

    server_host: str = "0.0.0.0"
    server_port: int = 8000
    server_reload: bool = False
    enable_test_ui: bool = True
    database_echo: bool = False
    gpu_memory_limit_mb: int | None = 7600  # MB
    disable_library_logging: bool = False

    # Model quantization settings
    enable_quantization: bool = True
    quantization_bits: int = 4
    bnb_4bit_compute_dtype: str = "bfloat16"
    bnb_4bit_quant_type: str = "nf4"
    bnb_4bit_use_double_quant: bool = True

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
        # return self.project_root / "GinkgoPython" / "weights" / "gemma-3-4b-it"
        return self.project_root / "GinkgoPython" / "weights" / "gemma-3-1b-it"

    @property
    def database_path(self) -> Path:
        """SQLite database file path"""
        return self.data_dir / "ginkgo.db"

    class Config:
        env_prefix = "GINKGO_"
        case_sensitive = False


settings = Settings()
