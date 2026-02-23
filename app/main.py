import signal
import sys

from app.core.config import settings
from app.core.logger import get_logger, setup_logging
from app.core.orchestrator import ApplicationOrchestrator
from app.ui.screen_manager import ScreenManager


def main():

    setup_logging()
    logger = get_logger("main")

    screen = ScreenManager(refresh_rate=0.5)

    screen.update_state("app_name", settings.APP_NAME)
    screen.update_state("environment", settings.ENVIRONMENT.value)
    screen.update_state("status", "RUNNING")

    orchestrator = ApplicationOrchestrator(screen)

    def shutdown_handler(sig, frame):
        logger.warning("Shutdown signal received, stopping application")
        orchestrator.stop()
        screen.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)

    # 🔥 START ORCHESTRATOR FIRST
    orchestrator.start()

    # 🔥 THEN BLOCK ON UI
    screen.start()


if __name__ == "__main__":
    main()

# TO RUN:
# $env:ENVIRONMENT="DEV"; python -m app.main
