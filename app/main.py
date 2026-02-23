from app.ui.screen_manager import ScreenManager
from app.core.config import settings
from app.core.logger import setup_logging, get_logger

if __name__ == "__main__":
    setup_logging()
    logger = get_logger("main")

    screen = ScreenManager(refresh_rate=0.5)

    screen.update_state("app_name", settings.APP_NAME)
    screen.update_state("environment", settings.ENVIRONMENT.value)
    screen.update_state("status", "RUNNING")

    logger.info("Application started")
    logger.warning("Low liquidity detected on BTC/USDT")
    logger.error("Failed to fetch market data for ETH/USDT")

    try:
        screen.start()
    except KeyboardInterrupt:
        screen.stop()
# TO RUN:
# $env:ENVIRONMENT="DEV"; python -m app.main
