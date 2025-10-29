from typing import Dict
from config.base_config import (
    BaseConfig,
    PersistentConfig,
)

class MlflowConfig(BaseConfig):
    """Mlflow 관련 설정 관리"""

    def initialize(self) -> Dict[str, PersistentConfig]:
        """Mlflow 관련 설정들을 초기화"""

        self.TRACKING_URL = self.create_persistent_config(
            env_name="MLFLOW_TRACKING_URL",
            config_path="mlflow.tracking_uri",
            default_value="https://polar-mlflow-git.x2bee.com/",
        )

        self.DEFAULT_EXPERIMENT_ID = self.create_persistent_config(
            env_name="MLFLOW_DEFAULT_EXPERIMENT_ID",
            config_path="mlflow.default_experiment_id",
            default_value="test"
        )

        self.CACHE_DIR = self.create_persistent_config(
            env_name="MLFLOW_CACHE_DIR",
            config_path="mlflow.cache_dir",
            default_value=".mlflow_cache"
        )

        self.TRACKING_TOKEN = self.create_persistent_config(
            env_name="MLFOW_TRACKING_TOKEN",
            config_path="mlflow.tracking_token",
            default_value='',
        )


        return self.configs
