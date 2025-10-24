"""
Redis 기반 Base Configuration 클래스
"""
import os
import logging
from typing import Any, Optional, Union, List, Dict
from abc import ABC, abstractmethod
from service.redis_config_manager import RedisConfigManager

logger = logging.getLogger("config-base")


class PersistentConfig:
    """Redis에 저장되는 설정 값을 관리하는 클래스"""

    def __init__(self, env_name: str, config_path: str, env_value: Any,
                 type_converter: Optional[callable] = None,
                 redis_manager: Optional[RedisConfigManager] = None):
        self.env_name = env_name
        self.config_path = config_path
        self.env_value = env_value
        self.type_converter = type_converter
        self.redis_manager = redis_manager or RedisConfigManager()

        # Redis에서 값 로드 시도
        self._value = self._load_from_redis()

    def _load_from_redis(self) -> Any:
        """Redis에서 설정 값 로드"""
        try:
            redis_value = self.redis_manager.get_config_value(self.config_path)

            if redis_value is not None:
                # 타입 변환 적용
                if self.type_converter:
                    return self.type_converter(redis_value)
                return redis_value
            else:
                # Redis에 없으면 환경변수 값 사용 & Redis에 저장
                self.redis_manager.set_config(
                    config_path=self.config_path,
                    config_value=self.env_value,
                    data_type=self._infer_data_type(self.env_value)
                )
                return self.env_value

        except Exception as e:
            logger.warning(f"Failed to load from Redis for {self.config_path}: {e}")
            return self.env_value

    def _infer_data_type(self, value: Any) -> str:
        """값의 타입 추론"""
        if isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, list):
            return "list"
        elif isinstance(value, dict):
            return "dict"
        else:
            return "string"

    @property
    def value(self) -> Any:
        """현재 설정 값 반환"""
        return self._value

    @value.setter
    def value(self, new_value: Any):
        """설정 값 업데이트 (메모리 + Redis)"""
        try:
            # 타입 변환 적용
            if self.type_converter:
                new_value = self.type_converter(new_value)

            # Redis에 저장
            self.redis_manager.set_config(
                config_path=self.config_path,
                config_value=new_value,
                data_type=self._infer_data_type(new_value)
            )

            # 메모리 값 업데이트
            self._value = new_value

            logger.info(f"Updated config {self.config_path}: {new_value}")

        except Exception as e:
            logger.error(f"Failed to update config {self.config_path}: {e}")
            raise

    def refresh(self):
        """Redis에서 최신 값 다시 로드"""
        self._value = self._load_from_redis()


class BaseConfig(ABC):
    """
    모든 설정 클래스의 기본 클래스 (Redis 기반)
    """

    def __init__(self, redis_manager: Optional[RedisConfigManager] = None):
        self.configs: Dict[str, PersistentConfig] = {}
        self.redis_manager = redis_manager or RedisConfigManager()
        self.logger = logging.getLogger(f"config-{self.__class__.__name__.lower()}")

        # 설정 자동 초기화
        try:
            self.initialize()
        except Exception as e:
            self.logger.error(f"Failed to initialize config: {e}")
            raise

    @abstractmethod
    def initialize(self) -> Dict[str, PersistentConfig]:
        """
        설정을 초기화하고 PersistentConfig 객체들을 반환
        """
        pass

    def get_env_value(self, env_name: str, default_value: Any,
                     file_path: Optional[str] = None,
                     type_converter: Optional[callable] = None) -> Any:
        """
        환경변수에서 값을 가져오고, 없으면 파일에서 읽거나 기본값 사용

        Args:
            env_name: 환경변수 이름
            default_value: 기본값
            file_path: 파일 경로 (선택사항)
            type_converter: 타입 변환 함수 (선택사항)

        Returns:
            설정값
        """
        # 1. 환경변수에서 확인
        env_value = os.environ.get(env_name)
        if env_value is not None:
            try:
                if type_converter:
                    converted_value = type_converter(env_value)
                    self.logger.debug("'%s' loaded from environment: %s", env_name, converted_value)
                    return converted_value
                else:
                    self.logger.debug("'%s' loaded from environment: %s", env_name, env_value)
                    return env_value
            except (ValueError, TypeError) as e:
                self.logger.warning("Failed to convert environment value for '%s': %s", env_name, e)

        # 2. 파일에서 확인 (제공된 경우)
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_value = f.read().strip()
                    if file_value:
                        if type_converter:
                            converted_value = type_converter(file_value)
                            self.logger.debug("'%s' loaded from file %s: %s", env_name, file_path, converted_value)
                            return converted_value
                        else:
                            os.environ[env_name] = file_value  # 환경변수에도 설정
                            self.logger.debug("'%s' loaded from file %s: %s", env_name, file_path, file_value)
                            return file_value
            except (IOError, OSError) as e:
                self.logger.warning("Failed to read %s for '%s': %s", file_path, env_name, e)

        # 3. 기본값 사용
        self.logger.debug("'%s' using default value: %s", env_name, default_value)
        return default_value

    def create_persistent_config(self, env_name: str, config_path: str,
                               default_value: Any, file_path: Optional[str] = None,
                               type_converter: Optional[callable] = None) -> PersistentConfig:
        """
        PersistentConfig 객체 생성 (Redis 기반)
        """
        env_value = self.get_env_value(env_name, default_value, file_path, type_converter)

        config = PersistentConfig(
            env_name=env_name,
            config_path=config_path,
            env_value=env_value,
            type_converter=type_converter,
            redis_manager=self.redis_manager
        )

        self.configs[env_name] = config
        return config

    def __getitem__(self, key: str) -> PersistentConfig:
        """
        설정에 딕셔너리 형태로 접근할 수 있도록 지원
        """
        if key in self.configs:
            return self.configs[key]
        raise KeyError(f"Configuration '{key}' not found in {self.__class__.__name__}")

    def get_config_summary(self) -> Dict[str, Any]:
        """
        이 설정 클래스의 요약 정보 반환
        """
        return {
            "class_name": self.__class__.__name__,
            "config_count": len(self.configs),
            "configs": {
                name: {
                    "current_value": config.value,
                    "default_value": config.env_value,
                    "config_path": config.config_path
                }
                for name, config in self.configs.items()
            }
        }


# 타입 변환 함수들
def convert_to_str(value: Any) -> str:
    """값을 문자열로 변환"""
    return str(value)


def convert_to_int(value: Union[str, int]) -> int:
    """문자열을 int로 변환"""
    return int(value)


def convert_to_float(value: Union[str, float]) -> float:
    """문자열을 float로 변환"""
    return float(value)


def convert_to_bool(value: Union[str, bool]) -> bool:
    """문자열을 bool로 변환"""
    if isinstance(value, bool):
        return value
    return str(value).lower() in ('true', '1', 'yes', 'on', 'enabled')


def convert_to_list(value: Union[str, list], separator: str = ',') -> List[str]:
    """문자열을 리스트로 변환"""
    if isinstance(value, list):
        return value
    return [item.strip() for item in str(value).split(separator) if item.strip()]


def convert_to_int_list(value: Union[str, List[int]], separator: str = ',') -> List[int]:
    """문자열 또는 리스트를 정수 리스트로 변환"""
    if isinstance(value, list):
        # 이미 리스트인 경우, 모든 요소를 int로 변환
        return [int(item) for item in value if str(item).strip().isdigit() or isinstance(item, int)]
    elif isinstance(value, str):
        # 문자열인 경우 분리해서 변환
        return [int(p.strip()) for p in value.split(separator) if p.strip().isdigit()]
    else:
        # 다른 타입인 경우 빈 리스트 반환
        return []
