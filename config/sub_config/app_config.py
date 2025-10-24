"""
Application 기본 설정 (Redis 기반)
"""
from typing import Dict
from config.base_config import (
    BaseConfig,
    PersistentConfig,
    convert_to_str,
    convert_to_bool,
    convert_to_int
)


class AppConfig(BaseConfig):
    def initialize(self) -> Dict[str, PersistentConfig]:
        """애플리케이션 기본 설정 초기화"""

        self.ENVIRONMENT = self.create_persistent_config(
            env_name="ENVIRONMENT",
            config_path="app.environment",
            default_value="development"
        )

        self.DEBUG_MODE = self.create_persistent_config(
            env_name="DEBUG_MODE",
            config_path="app.debug_mode",
            default_value=True,
            type_converter=convert_to_bool
        )

        self.PORT = self.create_persistent_config(
            env_name="PORT",
            config_path="app.port",
            default_value=8000,
            type_converter=convert_to_int
        )

        self.HOST = self.create_persistent_config(
            env_name="HOST",
            config_path="app.host",
            default_value="0.0.0.0"
        )

        return self.configs
