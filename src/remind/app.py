import sys
import ctypes
import logging

from PyQt6.QtWidgets import QApplication

from remind.brand import APP_ID
from remind.services.logging_setup import init_logging
from remind.app_bootstrapper import AppBootstrapper
from remind.services.crash_report import install_crash_hook


def main():
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

    app = QApplication(sys.argv)

    logger = init_logging(level=logging.INFO)
    logger.info("App start")
    install_crash_hook(logger)
    
    window = AppBootstrapper(app=app, logger=logger).build()
    window.resize(1000, 600)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()