from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet

import sys
import os

from clipboard2image import Clipboard2Image

callpath = os.getcwd()

os.chdir(os.path.dirname(
    __file__ if not getattr(sys, "frozen", False) else sys.executable
))


def main() -> None:
    app = QApplication([])
    win = Clipboard2Image(app, callpath)

    apply_stylesheet(app, theme=win.appTheme)

    with open("style/style.qss", "r") as stylesheet:
        app.setStyleSheet(
            app.styleSheet() + stylesheet.read().format(**os.environ)
        )

    win.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
