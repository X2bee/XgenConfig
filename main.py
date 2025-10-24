"""
XgenConfig Main Application

Redis 기반 설정 관리 시스템의 FastAPI 애플리케이션
"""
import os
import sys
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config_composer import ConfigComposer
from service.redis_config_manager import RedisConfigManager
from controller.appController import router as app_router

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # Startup
    logger.info("XgenConfig 애플리케이션 시작 중...")

    try:
        # Redis Config Manager 초기화
        redis_manager = RedisConfigManager()
        app.state.redis_manager = redis_manager
        logger.info("Redis Config Manager 초기화 완료")

        # Config Composer 초기화 (모든 설정 자동 로드)
        config_composer = ConfigComposer(redis_manager=redis_manager)
        app.state.config_composer = config_composer
        logger.info(f"Config Composer 초기화 완료 - {len(config_composer.all_configs)} 개의 설정 로드됨")

        # 환경 정보 로그
        environment = config_composer.get_config_by_name("ENVIRONMENT")
        if environment:
            logger.info(f"실행 환경: {environment.value}")

        logger.info("XgenConfig 애플리케이션 시작 완료!")

    except Exception as e:
        logger.error(f"애플리케이션 초기화 실패: {str(e)}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("XgenConfig 애플리케이션 종료 중...")

    # Redis 연결 정리
    if hasattr(app.state, 'redis_manager'):
        try:
            app.state.redis_manager.redis_client.close()
            logger.info("Redis 연결 종료 완료")
        except Exception as e:
            logger.error(f"Redis 연결 종료 실패: {str(e)}")

    logger.info("XgenConfig 애플리케이션 종료 완료")


# FastAPI 앱 생성
app = FastAPI(
    title="XgenConfig API",
    description="Redis 기반 설정 관리 시스템",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(app_router)

# Health check 엔드포인트
@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "service": "XgenConfig",
        "version": "1.0.0"
    }

# Root 엔드포인트
@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "XgenConfig API",
        "description": "Redis 기반 설정 관리 시스템",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn

    # 환경 변수에서 포트 및 호스트 설정
    logger.info(f"{int(os.getenv("API_PORT"))}")
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8010"))

    logger.info(f"서버 시작: http://{host}:{port}")
    logger.info(f"API 문서: http://{host}:{port}/docs")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # 개발 모드에서 자동 리로드
        log_level="info"
    )
