"""
Bragi - AI Writing Assistant

A Windows background utility for system-wide AI writing assistance.

Usage:
    python main.py

Features:
    - Global hotkeys
    - Selected-text processing and replacement
    - ChatML prompt support
    - Windows DPAPI protection for API keys
    - System tray management
"""

import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QMessageBox

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_smoke_test() -> int:
    """Verify that critical packaged modules can be imported."""
    try:
        from app.application import BragiApp  # noqa: F401
        from core.app_paths import get_user_data_dir  # noqa: F401
        from core.config_manager import ConfigManager  # noqa: F401
        from core.prompt_manager import PromptManager  # noqa: F401
        from core.single_instance import SingleInstanceLock  # noqa: F401
    except Exception:
        return 1

    return 0


def setup_logging():
    """Configure application logging."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main() -> int:
    """Application entry point."""
    if "--smoke-test" in sys.argv:
        return run_smoke_test()

    from app.application import BragiApp
    from core.single_instance import SingleInstanceLock

    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        lock = SingleInstanceLock()
        if not lock.acquire():
            logger.warning("Another instance of Bragi is already running")
            from PySide6.QtWidgets import QApplication
            temp_app = QApplication(sys.argv)
            QMessageBox.warning(
                None,
                "Bragi Already Running",
                "Another instance of Bragi is already running.\n\nPlease check the system tray."
            )
            return 1

        logger.info("=" * 50)
        logger.info("Bragi - AI Writing Assistant")
        logger.info("=" * 50)

        app = BragiApp(sys.argv)
        exit_code = app.exec()

        lock.release()
        return exit_code

    except KeyboardInterrupt:
        logger.info("\nInterrupted by user, exiting...")
        return 0

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
