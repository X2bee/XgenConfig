"""
데이터베이스 관련 설정
"""
from typing import Dict
from config.base_config import BaseConfig, PersistentConfig, convert_to_bool, convert_to_int

class DatabaseConfig(BaseConfig):
    """데이터베이스 연결 및 설정 관리"""
    
    def initialize(self) -> Dict[str, PersistentConfig]:
        """데이터베이스 관련 설정들을 초기화"""
        
        # 데이터베이스 타입 (auto, sqlite, postgresql)
        self.DATABASE_TYPE = self.create_persistent_config(
            env_name="DATABASE_TYPE",
            config_path="database.type",
            default_value="auto"
        )
        
        self.POSTGRES_HOST = self.create_persistent_config(
            env_name="POSTGRES_HOST",
            config_path="database.postgres.host",
            default_value="host.docker.internal"
        )
        
        self.POSTGRES_PORT = self.create_persistent_config(
            env_name="POSTGRES_PORT",
            config_path="database.postgres.port",
            default_value=5432,
            type_converter=convert_to_int
        )
        
        self.POSTGRES_DB = self.create_persistent_config(
            env_name="POSTGRES_DB",
            config_path="database.postgres.database",
            default_value="plateerag"
        )
        
        self.POSTGRES_USER = self.create_persistent_config(
            env_name="POSTGRES_USER",
            config_path="database.postgres.user",
            default_value="ailab"
        )
        
        self.POSTGRES_PASSWORD = self.create_persistent_config(
            env_name="POSTGRES_PASSWORD",
            config_path="database.postgres.password",
            default_value="ailab123"
        )
        
        # SQLite 설정
        self.SQLITE_PATH = self.create_persistent_config(
            env_name="SQLITE_PATH",
            config_path="database.sqlite.path",
            default_value="constants/config.db"
        )
                
        # 마이그레이션 설정
        self.AUTO_MIGRATION = self.create_persistent_config(
            env_name="AUTO_MIGRATION",
            config_path="database.auto_migration",
            default_value=True,
            type_converter=convert_to_bool
        )
        
        return self.configs
