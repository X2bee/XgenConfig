# controller/helper/singletonHelper.py
from fastapi import Request
from config.config_composer import ConfigComposer


def get_config_composer(request: Request) -> ConfigComposer:
    """request.app.state에서 config_composer 가져오기"""
    if hasattr(request.app.state, 'config_composer') and request.app.state.config_composer:
        return request.app.state.config_composer
    else:
        from config.config_composer import config_composer
        return config_composer
