"""
App 컨트롤러

애플리케이션 관리 API 엔드포인트를 제공합니다.
애플리케이션 상태, 설정 관리, 데모 기능 등을 담당합니다.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any
import logging

from controller.helper.singletonHelper import get_config_composer

logger = logging.getLogger("app-controller")
router = APIRouter(prefix="/app", tags=["app"])


class ConfigUpdateRequest(BaseModel):
    value: Any

class UserCreateRequest(BaseModel):
    username: str
    email: str
    full_name: str = None

@router.get("/status")
async def get_app_status(request: Request):
    """애플리케이션 상태 조회"""
    config_composer = get_config_composer(request)

    try:
        node_count = getattr(request.app.state, 'node_count', 0)
        node_registry = getattr(request.app.state, 'node_registry', [])
        available_nodes = [node["id"] for node in node_registry]

        status_data = {
            "config": {
                "app_name": "PlateeRAG Backend",
                "version": "1.0.0",
                "environment": config_composer.get_config_by_name("ENVIRONMENT").value,
                "debug_mode": config_composer.get_config_by_name("DEBUG_MODE").value
            },
            "node_count": node_count,
            "available_nodes": available_nodes,
            "status": "running"
        }

        return status_data

    except Exception as e:
        logger.error("Error getting app status: %s", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve application status")

@router.get("/config")
async def get_app_config(request: Request):
    """애플리케이션 설정 반환"""
    try:
        config_composer = get_config_composer(request)
        config_summary = config_composer.get_config_summary()

        return config_summary
    except Exception as e:
        logger.error("Error getting app config: %s", e)
        return {"error": "Failed to get configuration"}

@router.get("/config/persistent")
async def get_persistent_configs(request: Request):
    """모든 PersistentConfig 설정 정보 반환"""
    try:
        config_composer = get_config_composer(request)
        config_summary = config_composer.get_config_summary()

        return config_summary
    except Exception as e:
        logger.error("Error getting persistent configs: %s", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve persistent configurations")

@router.put("/config/persistent/{config_name}")
async def update_persistent_config(config_name: str, new_value: ConfigUpdateRequest, request: Request):
    """특정 PersistentConfig 값 업데이트"""
    try:
        config_composer = get_config_composer(request)
        update_result = config_composer.update_config(config_name, new_value.value)
        old_value = update_result["old_value"]
        new_config_value = update_result["new_value"]

        logger.info("Successfully updated config '%s': %s -> %s", config_name, old_value, new_config_value)

        response_data = {
            "message": f"Config '{config_name}' updated successfully",
            "old_value": old_value,
            "new_value": new_config_value,
            "updated_in_memory": True,
        }

        return response_data

    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Config '{config_name}' not found") from exc
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid value type: {e}") from e
    except Exception as e:
        logger.error("Error updating config '%s': %s", config_name, e)
        raise HTTPException(status_code=500, detail="Failed to update configuration")

@router.post("/config/persistent/refresh")
async def refresh_persistent_configs(request: Request):
    """모든 PersistentConfig를 데이터베이스에서 다시 로드"""
    try:
        config_composer = get_config_composer(request)
        config_composer.refresh_all()

        response_data = {"message": "All persistent configs refreshed successfully from database"}

        return response_data

    except Exception as e:
        logger.error("Error refreshing persistent configs: %s", e)
        raise HTTPException(status_code=500, detail="Failed to refresh persistent configurations")
