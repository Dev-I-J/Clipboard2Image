from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet

import sys
import os

from clipboard2image import Clipboard2Image


def main():
    app = QApplication([])
    win = Clipboard2Image(app)

    apply_stylesheet(app, theme=win.appTheme)

    with open(
        os.path.abspath(
            os.path.realpath("src/style/style.qss")
        ), "r"
    ) as stylesheet:
        app.setStyleSheet(app.styleSheet() + stylesheet.read())

    win.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
