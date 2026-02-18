from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings"""

    # Server configuration
    server_host: str = "0.0.0.0"  # Allow network access by default
    server_port: int = 8000
    server_reload: bool = True  # Auto-reload on code changes

    # Frontend configuration
    frontend_build_command: str = "pnpm build"

    # Paths (computed)
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

    class Config:
        env_prefix = "GINKGO_"  # Environment variables like GINKGO_SERVER_PORT=8080
        case_sensitive = False


# Global settings instance
settings = Settings()
