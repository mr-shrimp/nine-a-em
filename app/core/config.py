import os
from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings

from app.core.enums import Environment


class Settings(BaseSettings):
    # ==========================================
    # Application
    # ==========================================
    APP_NAME: str = "Nine-A-Em Trading Bot"
    ENVIRONMENT: Environment = Environment.DEV
    DEBUG: bool = True

    # ==========================================
    # Database
    # ==========================================
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    DB_DRIVER: str = "ODBC Driver 18 for SQL Server"

    # ==========================================
    # Exchange
    # =========================================
    EXCHANGE_NAME: str = "BINANCE"

    EXCHANGE_API_KEY: Optional[str] = None
    EXCHANGE_API_SECRET: Optional[str] = None

    USE_TESTNET: bool = True

    # =========================================
    # Risk Defaults
    # ========================================
    MAX_DAILY_LOSS_PERCENT: float = 5.0
    MAX_POSITION_SIZE_PERCENT: float = 2.0
    MAX_OPEN_POSITIONS: int = 5
    MAX_ACCOUNT_DRAWDOWN_PERCENT: float = 20.0

    # =========================================
    # Execution
    # ========================================
    DEFAULT_ORDER_TYPE: str = "MARKET"
    SLIPPAGE_BPS: int = 5  # basis points assumption

    # ========================================
    # Monitoring
    # =======================================
    ENABLE_EMAIL_ALERTS: bool = False
    ALERT_EMAIL_ADDRESS: Optional[str] = None

    # ========================================
    # AI
    # ======================================
    ENABLE_AI: bool = False
    AI_MODEL_NAME: Optional[str] = None
    AI_MODEL_VERSION: Optional[str] = None

    # ========================================
    #  Performance
    # ======================================
    HEARTBEAT_INTERVAL_SECONDS: int = 5

    @property
    def database_url(self) -> str:
        return (
            f"mssql+pyodbc://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?driver={self.DB_DRIVER.replace(' ', '+')}"
        )

    @model_validator(mode="after")
    def validate_live_environment(self):
        if self.ENVIRONMENT == Environment.LIVE:
            if not self.EXCHANGE_API_KEY or not self.EXCHANGE_API_SECRET:
                raise ValueError("LIVE mode requires exchange credentials.")
        return self

    class Config:
        # Allows you to run with different .env files based on the environment
        # For example, ENVIRONMENT=LIVE python app/main.py
        # will load .env.live, while ENVIRONMENT=DEV python app/main.py will load .env.dev
        env_file = f".env.{os.getenv('ENVIRONMENT', 'DEV').lower()}"
        case_sensitive = True


settings = Settings()
