"""
Config Composer - 모든 설정을 통합 관리 (Redis 기반)
"""
import os
import importlib
import logging
from typing import Dict, Any
from pathlib import Path
from config.base_config import BaseConfig, PersistentConfig
from service.redis_config_manager import RedisConfigManager

logger = logging.getLogger("config-composer")


class ConfigComposer:
    """
    모든 설정을 자동 발견하여 통합적으로 관리하는 클래스 (Redis 기반)
    sub_config/ 디렉토리의 *_config.py 파일들을 자동으로 스캔하고 로드합니다.
    """

    def __init__(self, redis_manager: RedisConfigManager = None):
        # 동적으로 로드된 설정 카테고리들을 저장
        self.config_categories: Dict[str, Any] = {}

        # 모든 설정을 저장하는 딕셔너리
        self.all_configs: Dict[str, PersistentConfig] = {}

        # Redis 매니저
        self.redis_manager = redis_manager or RedisConfigManager()

        self.logger = logger

        # 설정 카테고리들을 자동으로 발견하고 로드
        self._discover_and_load_configs()

    def _discover_and_load_configs(self):
        """
        sub_config/ 디렉토리에서 *_config.py 파일들을 자동으로 발견하고 로드
        """
        sub_config_dir = Path(__file__).parent / "sub_config"

        # sub_config 디렉토리가 없으면 생성
        if not sub_config_dir.exists():
            sub_config_dir.mkdir(parents=True, exist_ok=True)
            self.logger.warning(f"Created sub_config directory: {sub_config_dir}")
            return

        # *_config.py 패턴의 파일들 찾기
        config_files = []
        for file in sub_config_dir.glob("*_config.py"):
            if file.name != "__init__.py":
                config_files.append(file)

        self.logger.info("Found %d config files: %s", len(config_files), [f.name for f in config_files])

        # 각 설정 파일을 동적으로 로드
        for config_file in config_files:
            try:
                # 파일명에서 카테고리명 추출 (예: openai_config.py -> openai)
                category_name = config_file.stem.replace("_config", "")

                # 모듈 이름 생성
                module_name = f"config.sub_config.{config_file.stem}"

                # 동적으로 모듈 import
                module = importlib.import_module(module_name)

                # 클래스 이름을 다양한 방식으로 시도
                possible_class_names = [
                    f"{category_name.title()}Config",           # OpenaiConfig
                    f"{category_name.upper()}Config",           # OPENAIConfig
                    f"{category_name.capitalize()}Config",      # OpenaiConfig
                    "".join(word.capitalize() for word in category_name.split("_")) + "Config"  # OpenAIConfig
                ]

                config_class = None
                for class_name in possible_class_names:
                    if hasattr(module, class_name):
                        config_class = getattr(module, class_name)
                        break

                if config_class is None:
                    # 마지막 시도: 모듈에서 BaseConfig를 상속받은 클래스 찾기
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and
                            issubclass(attr, BaseConfig) and
                            attr != BaseConfig):
                            config_class = attr
                            break

                if config_class is None:
                    raise AttributeError(f"No valid config class found in {module_name}")

                # 인스턴스 생성 (Redis 매니저 전달)
                config_instance = config_class(redis_manager=self.redis_manager)

                # 카테고리로 저장
                self.config_categories[category_name] = config_instance

                # 동적 속성으로 설정 (self.openai, self.app 등)
                setattr(self, category_name, config_instance)

                # all_configs에 추가
                self.all_configs.update(config_instance.configs)

                self.logger.info("Successfully loaded config category: %s", category_name)

            except Exception as e:
                self.logger.error("Failed to load config file %s: %s", config_file.name, e)

        self.logger.info("Auto-discovered %d config categories: %s",
                        len(self.config_categories), list(self.config_categories.keys()))

    def get_config_by_name(self, config_name: str) -> PersistentConfig:
        """
        설정 이름으로 PersistentConfig 객체 가져오기

        Args:
            config_name: 설정 이름 (env_name)

        Returns:
            PersistentConfig: 설정 객체
        """
        if config_name in self.all_configs:
            return self.all_configs[config_name]

        raise KeyError(f"Configuration '{config_name}' not found")

    def update_config(self, config_name: str, new_value: Any) -> Dict[str, Any]:
        """
        설정 값 업데이트

        Args:
            config_name: 설정 이름
            new_value: 새로운 값

        Returns:
            Dict: 업데이트 결과
        """
        config = self.get_config_by_name(config_name)
        old_value = config.value

        # 값 업데이트 (자동으로 Redis에도 저장됨)
        config.value = new_value

        return {
            "old_value": old_value,
            "new_value": config.value
        }

    def refresh_all(self):
        """모든 설정을 Redis에서 다시 로드"""
        for config_name, config in self.all_configs.items():
            try:
                config.refresh()
                self.logger.debug(f"Refreshed config: {config_name}")
            except Exception as e:
                self.logger.error(f"Failed to refresh config {config_name}: {e}")

    def get_config_summary(self) -> Dict[str, Any]:
        """
        모든 설정의 요약 정보 반환

        Returns:
            Dict: 카테고리별 설정 요약
        """
        summary = {}
        for category_name, category_instance in self.config_categories.items():
            summary[category_name] = category_instance.get_config_summary()

        return summary

    def get_category_configs(self, category_name: str) -> Dict[str, Any]:
        """
        특정 카테고리의 모든 설정 반환

        Args:
            category_name: 카테고리 이름

        Returns:
            Dict: 설정 딕셔너리
        """
        if category_name not in self.config_categories:
            raise KeyError(f"Category '{category_name}' not found")

        category = self.config_categories[category_name]
        return {
            name: config.value
            for name, config in category.configs.items()
        }


# 전역 ConfigComposer 인스턴스
config_composer = ConfigComposer()
