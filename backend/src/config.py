"""
Configuration loading and validation for AI Code Flow.

Provides centralized configuration management with validation and
virtual environment path verification.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, ValidationError, validator

from .logging_config import get_logger

logger = get_logger()


class MiniMaxConfig(BaseModel):
    """MiniMax AI service configuration."""
    api_key: str = Field(..., description="MiniMax API key")
    base_url: str = Field(default="https://api.minimax.chat/v1", description="MiniMax API base URL")


class OpenAIConfig(BaseModel):
    """OpenAI service configuration."""
    api_key: str = Field(..., description="OpenAI API key")
    base_url: str = Field(default="https://api.openai.com/v1", description="OpenAI API base URL")


class GenerationConfig(BaseModel):
    """Code generation configuration."""
    model: str = Field(default="MiniMax-Text-01", description="AI model to use")
    max_tokens: int = Field(default=4000, ge=100, le=8000, description="Maximum tokens per request")
    temperature: float = Field(default=0.1, ge=0.0, le=1.0, description="AI creativity level")
    timeout: int = Field(default=60, ge=10, le=300, description="Request timeout in seconds")


class SystemConfig(BaseModel):
    """System-wide configuration."""
    max_concurrent_users: int = Field(default=5, ge=1, le=50, description="Maximum concurrent users")
    log_level: str = Field(default="INFO", description="Logging level")
    projects_dir: str = Field(default="../projects", description="Generated projects directory")
    logs_dir: str = Field(default="../logs", description="Logs directory")

    @validator('log_level')
    def validate_log_level(cls, v):
        allowed_levels = ['TRACE', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed_levels:
            raise ValueError(f'Log level must be one of: {allowed_levels}')
        return v.upper()


class CircuitBreakerConfig(BaseModel):
    """Circuit breaker configuration."""
    failure_threshold: int = Field(default=3, ge=1, le=10, description="Failures before opening")
    recovery_timeout: int = Field(default=60, ge=10, le=300, description="Recovery timeout in seconds")
    expected_exception: list[str] = Field(
        default=["httpx.TimeoutException", "httpx.ConnectError"],
        description="Exceptions to count as failures"
    )


class AppConfig(BaseModel):
    """Main application configuration."""
    minimax: MiniMaxConfig
    openai: OpenAIConfig
    generation: GenerationConfig
    system: SystemConfig
    circuit_breaker: CircuitBreakerConfig

    class Config:
        """Pydantic configuration."""
        validate_assignment = True


class ConfigManager:
    """Configuration manager with validation and virtual environment checking."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to config.json file. If None, uses default location.
        """
        if config_path is None:
            # Default to backend/config.json relative to this file
            config_path = Path(__file__).parent.parent / "config.json"

        self.config_path = config_path
        self._config: Optional[AppConfig] = None
        self._last_load_time: Optional[float] = None

    def _validate_virtual_environment(self) -> None:
        """
        Validate that we're running in the correct virtual environment.

        Raises:
            RuntimeError: If virtual environment validation fails
        """
        expected_venv_path = Path(__file__).parent.parent / ".venv"

        if not expected_venv_path.exists():
            raise RuntimeError(
                "虚拟环境未找到: 请确保 backend/.venv 目录存在且已激活"
            )

        # Check if sys.prefix points to the expected virtual environment
        expected_prefix = str(expected_venv_path.resolve())
        current_prefix = str(Path(sys.prefix).resolve())

        if not current_prefix.startswith(expected_prefix):
            raise RuntimeError(
                f"虚拟环境未激活: 当前环境路径 '{current_prefix}' 不匹配预期路径 '{expected_prefix}'。请运行: backend\\.venv\\Scripts\\activate"
            )

        logger.info("虚拟环境验证通过", {
            "expected_prefix": expected_prefix,
            "current_prefix": current_prefix
        })

    def _load_config_file(self) -> Dict[str, Any]:
        """
        Load configuration from JSON file.

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"配置文件未找到: {self.config_path}。请创建配置文件并设置必要的API密钥。"
            )

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件格式错误: {e}")

        return config_data

    def _validate_config(self, config_data: Dict[str, Any]) -> AppConfig:
        """
        Validate and parse configuration data.

        Args:
            config_data: Raw configuration dictionary

        Returns:
            Validated AppConfig instance

        Raises:
            ValidationError: If configuration is invalid
        """
        try:
            config = AppConfig(**config_data)
            return config
        except ValidationError as e:
            error_messages = []
            for error in e.errors():
                field_path = '.'.join(str(loc) for loc in error['loc'])
                error_messages.append(f"{field_path}: {error['msg']}")

            raise ValueError(f"配置验证失败:\n" + '\n'.join(error_messages))

    def load_config(self, force_reload: bool = False) -> AppConfig:
        """
        Load and validate configuration.

        Args:
            force_reload: Force reload even if already loaded

        Returns:
            Validated application configuration

        Raises:
            RuntimeError: If virtual environment validation fails
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        # Validate virtual environment first
        self._validate_virtual_environment()

        # Check if we need to reload
        if not force_reload and self._config is not None:
            return self._config

        # Load configuration file
        config_data = self._load_config_file()

        # Validate and parse configuration
        self._config = self._validate_config(config_data)
        self._last_load_time = Path(self.config_path).stat().st_mtime

        logger.info("配置加载成功", {
            "config_path": str(self.config_path),
            "log_level": self._config.system.log_level,
            "max_concurrent_users": self._config.system.max_concurrent_users
        })

        return self._config

    def get_config(self) -> AppConfig:
        """
        Get current configuration, loading if necessary.

        Returns:
            Current application configuration
        """
        if self._config is None:
            return self.load_config()
        return self._config

    def is_config_changed(self) -> bool:
        """
        Check if configuration file has been modified since last load.

        Returns:
            True if config file has changed
        """
        if self._last_load_time is None:
            return True

        try:
            current_mtime = Path(self.config_path).stat().st_mtime
            return current_mtime > self._last_load_time
        except OSError:
            return True

    def reload_if_changed(self) -> Optional[AppConfig]:
        """
        Reload configuration if file has changed.

        Returns:
            New configuration if reloaded, None if no change
        """
        if self.is_config_changed():
            logger.info("检测到配置变更，正在重新加载")
            return self.load_config(force_reload=True)
        return None


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> AppConfig:
    """Get current application configuration."""
    return get_config_manager().get_config()


def reload_config() -> AppConfig:
    """Force reload configuration."""
    return get_config_manager().load_config(force_reload=True)
