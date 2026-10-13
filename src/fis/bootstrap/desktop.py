"""Qt desktop entry point for frame-interpolation-studio.

Boots the QApplication, wires the main window, and hands control to the
Qt event loop. All heavy work runs off the UI thread via the job
dispatcher in :mod:`fis.services.job_queue`.
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from fis import __version__
from fis.config.settings import load_settings
from fis.services.logging_setup import configure_logging
from fis.ui.main_window import MainWindow


def main() -> int:
    configure_logging()
    settings = load_settings()
    app = QApplication(sys.argv)
    app.setApplicationName("frame-interpolation-studio")
    app.setApplicationVersion(__version__)
    window = MainWindow(settings=settings)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())