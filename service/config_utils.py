"""
Config 유틸리티 함수들

Redis에서 설정을 dictionary 형태로 쉽게 가져오는 함수들
"""
import logging
from typing import Dict, Any, Optional, List
from service.redis_config_manager import RedisConfigManager

logger = logging.getLogger(__name__)


def get_config_dict(
    redis_manager: Optional[RedisConfigManager] = None,
    category: Optional[str] = None,
    flatten: bool = False
) -> Dict[str, Any]:
    """
    Redis에서 설정을 dictionary 형태로 가져옵니다.

    Args:
        redis_manager: RedisConfigManager 인스턴스 (없으면 자동 생성)
        category: 특정 카테고리만 가져오기 (None이면 전체)
        flatten: True면 평탄화된 구조 {"app.environment": "dev"},
                False면 중첩 구조 {"app": {"environment": "dev"}}

    Returns:
        Dict: 설정 딕셔너리

    Examples:
        >>> # 모든 설정을 중첩 구조로
        >>> configs = get_config_dict()
        >>> print(configs["app"]["environment"])  # "development"

        >>> # 특정 카테고리만 중첩 구조로
        >>> openai_config = get_config_dict(category="openai")
        >>> print(openai_config["openai"]["api_key"])

        >>> # 평탄화된 구조로
        >>> flat_config = get_config_dict(flatten=True)
        >>> print(flat_config["app.environment"])  # "development"
    """
    if redis_manager is None:
        redis_manager = RedisConfigManager()

    try:
        if category:
            # 특정 카테고리만 가져오기
            if flatten:
                # 평탄화된 구조
                configs = redis_manager.get_category_configs(category)
                return {config['path']: config['value'] for config in configs}
            else:
                # 중첩 구조
                return redis_manager.get_category_configs_nested(category)
        else:
            # 모든 설정 가져오기
            all_configs = redis_manager.get_all_configs()

            if flatten:
                # 평탄화된 구조
                return {config['path']: config['value'] for config in all_configs}
            else:
                # 중첩 구조
                result = {}
                for config in all_configs:
                    path = config['path']
                    value = config['value']

                    # 경로를 '.'로 분리하여 중첩 딕셔너리 생성
                    keys = path.split('.')
                    current = result

                    for key in keys[:-1]:
                        if key not in current:
                            current[key] = {}
                        current = current[key]

                    current[keys[-1]] = value

                return result

    except Exception as e:
        logger.error(f"설정 가져오기 실패: {str(e)}")
        return {}


def get_category_config(
    category: str,
    redis_manager: Optional[RedisConfigManager] = None
) -> Dict[str, Any]:
    """
    특정 카테고리의 설정을 중첩 dictionary로 가져옵니다.

    Args:
        category: 카테고리 이름 (예: "openai", "app", "vast")
        redis_manager: RedisConfigManager 인스턴스 (없으면 자동 생성)

    Returns:
        Dict: 중첩된 설정 딕셔너리

    Example:
        >>> openai = get_category_config("openai")
        >>> print(openai)
        {
            "openai": {
                "api_key": "sk-...",
                "model_default": "gpt-4o",
                "temperature_default": 0.7
            }
        }
    """
    return get_config_dict(redis_manager=redis_manager, category=category, flatten=False)


def get_flat_config(
    category: Optional[str] = None,
    redis_manager: Optional[RedisConfigManager] = None
) -> Dict[str, Any]:
    """
    설정을 평탄화된 dictionary로 가져옵니다.

    Args:
        category: 특정 카테고리만 (None이면 전체)
        redis_manager: RedisConfigManager 인스턴스

    Returns:
        Dict: 평탄화된 설정 딕셔너리 {"path.to.config": value}

    Example:
        >>> flat = get_flat_config(category="app")
        >>> print(flat)
        {
            "app.environment": "development",
            "app.port": 8000,
            "app.debug_mode": True
        }
    """
    return get_config_dict(redis_manager=redis_manager, category=category, flatten=True)


def get_config_value(
    config_path: str,
    default: Any = None,
    redis_manager: Optional[RedisConfigManager] = None
) -> Any:
    """
    특정 설정 값만 가져옵니다.

    Args:
        config_path: 설정 경로 (예: "app.environment", "openai.api_key")
        default: 기본값
        redis_manager: RedisConfigManager 인스턴스

    Returns:
        설정 값 또는 기본값

    Example:
        >>> env = get_config_value("app.environment")
        >>> print(env)  # "development"

        >>> api_key = get_config_value("openai.api_key", default="")
    """
    if redis_manager is None:
        redis_manager = RedisConfigManager()

    return redis_manager.get_config_value(config_path, default=default)


def get_multiple_configs(
    config_paths: List[str],
    redis_manager: Optional[RedisConfigManager] = None
) -> Dict[str, Any]:
    """
    여러 설정을 한 번에 가져옵니다.

    Args:
        config_paths: 설정 경로 리스트
        redis_manager: RedisConfigManager 인스턴스

    Returns:
        Dict: {config_path: value}

    Example:
        >>> configs = get_multiple_configs([
        ...     "app.environment",
        ...     "openai.api_key",
        ...     "vast.vllm.port"
        ... ])
        >>> print(configs)
        {
            "app.environment": "development",
            "openai.api_key": "sk-...",
            "vast.vllm.port": 12434
        }
    """
    if redis_manager is None:
        redis_manager = RedisConfigManager()

    result = {}
    for path in config_paths:
        try:
            result[path] = redis_manager.get_config_value(path)
        except Exception as e:
            logger.warning(f"설정 가져오기 실패: {path} - {str(e)}")
            result[path] = None

    return result


def get_all_categories(
    redis_manager: Optional[RedisConfigManager] = None
) -> List[str]:
    """
    모든 카테고리 목록을 가져옵니다.

    Args:
        redis_manager: RedisConfigManager 인스턴스

    Returns:
        List[str]: 카테고리 목록

    Example:
        >>> categories = get_all_categories()
        >>> print(categories)
        ['app', 'openai', 'anthropic', 'vast', ...]
    """
    if redis_manager is None:
        redis_manager = RedisConfigManager()

    return redis_manager.get_all_categories()


def update_config(
    config_path: str,
    new_value: Any,
    data_type: Optional[str] = None,
    redis_manager: Optional[RedisConfigManager] = None
) -> bool:
    """
    설정 값을 업데이트합니다.

    Args:
        config_path: 설정 경로
        new_value: 새로운 값
        data_type: 데이터 타입 (자동 추론 가능)
        redis_manager: RedisConfigManager 인스턴스

    Returns:
        bool: 성공 여부

    Example:
        >>> update_config("app.environment", "production")
        >>> update_config("app.port", 9000)
    """
    if redis_manager is None:
        redis_manager = RedisConfigManager()

    # 데이터 타입 자동 추론
    if data_type is None:
        if isinstance(new_value, bool):
            data_type = "bool"
        elif isinstance(new_value, int):
            data_type = "int"
        elif isinstance(new_value, float):
            data_type = "float"
        elif isinstance(new_value, list):
            data_type = "list"
        elif isinstance(new_value, dict):
            data_type = "dict"
        else:
            data_type = "string"

    # 카테고리 추출
    category = config_path.split('.')[0]

    return redis_manager.set_config(
        config_path=config_path,
        config_value=new_value,
        data_type=data_type,
        category=category
    )


# 편의 함수들
def get_app_config(redis_manager: Optional[RedisConfigManager] = None) -> Dict[str, Any]:
    """app 카테고리 설정 가져오기"""
    return get_category_config("app", redis_manager)


def get_openai_config(redis_manager: Optional[RedisConfigManager] = None) -> Dict[str, Any]:
    """openai 카테고리 설정 가져오기"""
    return get_category_config("openai", redis_manager)


def get_anthropic_config(redis_manager: Optional[RedisConfigManager] = None) -> Dict[str, Any]:
    """anthropic 카테고리 설정 가져오기"""
    return get_category_config("anthropic", redis_manager)


def get_vast_config(redis_manager: Optional[RedisConfigManager] = None) -> Dict[str, Any]:
    """vast 카테고리 설정 가져오기"""
    return get_category_config("vast", redis_manager)


def get_vllm_config(redis_manager: Optional[RedisConfigManager] = None) -> Dict[str, Any]:
    """vllm 카테고리 설정 가져오기"""
    return get_category_config("vllm", redis_manager)
