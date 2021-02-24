from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QShortcut,
    QStackedWidget,
    QMenuBar,
    QMenu,
    QAction,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QTextBrowser,
    QComboBox
)

from PyQt5.QtCore import (
    QSize,
    Qt,
    pyqtProperty,
    pyqtSignal,
    pyqtSlot,
    PYQT_VERSION_STR,
    QT_VERSION_STR
)

from PyQt5.QtGui import (
    QIcon,
    QKeySequence,
    QCloseEvent,
    QPixmap,
    QTextOption
)

from PyQt5.sip import SIP_VERSION_STR

from PIL import Image, ImageGrab
from PIL import __version__ as pil_version

from qt_material import list_themes, apply_stylesheet

from appdirs import user_config_dir

from PyInstaller import __version__ as pyinstaller_version

from pip import __version__ as pip_version

from pkg_resources import working_set
from subprocess import run

import toml

import sys
import os

from exceptions import NoImageInClipboard


class Clipboard2Image(QMainWindow):
    appTitle = "Clipboard2Image"
    appVersion = "0.0.1-alpha"
    appTheme = "light_blue.xml"
    appThemeName = "Light Blue"
    appIconPath = os.path.abspath(
        os.path.realpath("src/icons/appicon.png")
    )

    activeImageChanged = pyqtSignal()

    _activeImage = None

    def __init__(self, app: QApplication) -> None:
        super().__init__()

        self.app = app

        self._loadSettings()
        self._processArgs()
        self._createWindow()
        self._createWidgets()
        self._createMenuBar()
        self._createKeyShortcuts()
        self._createSignalBindings()

        self.activeImageChanged.emit()

    def _createWindow(self) -> None:
        __screenSize = self.app.desktop().screenGeometry()
        __screenWidth = int(__screenSize.width() -
                            ((__screenSize.width() / 6) * 3))
        __screenHeight = int(__screenSize.height() -
                             (__screenSize.height() / 12) * 3)

        __windowSize = QSize(__screenWidth, __screenHeight)

        self.centralWidget = QStackedWidget(self)

        self.setWindowTitle(f"{self.appTitle} {self.appVersion}")
        self.setWindowIcon(QIcon(self.appIconPath))
        self.setCentralWidget(self.centralWidget)
        self.resize(__windowSize)

    def _loadSettings(self) -> None:
        settingsFilePath = os.path.join(
            user_config_dir(self.appTitle), "settings.toml"
        )

        if os.path.exists(settingsFilePath):
            with open(settingsFilePath, "r") as settingsFile:
                tomlObject = toml.load(settingsFile)
                self.appTheme = tomlObject["theme"]["xml"]
                self.appThemeName = tomlObject["theme"]["name"]
        else:
            os.makedirs(os.path.dirname(settingsFilePath))
            with open(settingsFilePath, "w") as settingsFile:
                settingsDict = {
                    "theme": {
                        "xml": self.appTheme,
                        "name": self.appThemeName
                    }
                }
                toml.dump(settingsDict, settingsFile)

        self._createMenuBar()

    def _processArgs(self) -> None:
        if (len(sys.argv) >= 3) and (sys.argv[1] == "--theme") and (
            theme := sys.argv[2].replace('-', '_')+'.xml'
        ) in list_themes():
            self.appTheme = theme
            self.appThemeName = sys.argv[2].replace('-', ' ').title()
        self._createMenuBar()

    def _createWidgets(self) -> None:
        pasteLabel = QLabel(
            "Paste Your Image Here (Ctrl + V), Or Click The Button Below \
To Get The Last Copied Item!", self
        )

        getLatestCopyItem = QPushButton("Get The Last Copied Item!", self)
        getLatestCopyItem.clicked.connect(self.imagePasted)

        homeWidget = QWidget(self.centralWidget)

        homeLayout = QVBoxLayout(homeWidget)
        homeLayout.setAlignment(Qt.AlignCenter)

        homeLayout.addWidget(pasteLabel)
        homeLayout.addSpacing(50)
        homeLayout.addWidget(getLatestCopyItem)

        homeWidget.setLayout(homeLayout)

        self.centralWidget.addWidget(homeWidget)

    def _createMenuBar(self) -> None:
        menuBar = QMenuBar(self)

        fileMenu = QMenu("File", self)
        editMenu = QMenu("Edit", self)
        imageMenu = QMenu("Image", self)
        helpMenu = QMenu("Help", self)

        newWindowAction = QAction("New Window", self)
        newWindowAction.setIcon(QIcon(
            os.path.abspath(
                os.path.realpath(
                    "src/icons/icons8/icons8-new-window-50.png"
                    if self.appTheme.startswith('light') else
                    "src/icons/icons8/icons8-new-window-white-50.png"
                )
            )
        ))
        newWindowAction.setShortcut(QKeySequence.New)
        newWindowAction.triggered.connect(self.onNewWindowActionTriggered)

        exitAction = QAction("Exit", self)
        exitAction.setIcon(QIcon(
            os.path.abspath(
                os.path.realpath(
                    "src/icons/icons8/icons8-exit-50.png"
                    if self.appTheme.startswith('light') else
                    "src/icons/icons8/icons8-exit-white-50.png"
                )
            )
        ))
        exitAction.setShortcut(QKeySequence.Quit)
        exitAction.triggered.connect(self.close)

        settingsAction = QAction("Settings", self)
        settingsAction.setIcon(QIcon(
            os.path.abspath(
                os.path.realpath(
                    "src/icons/icons8/icons8-settings-50.png"
                    if self.appTheme.startswith('light') else
                    "src/icons/icons8/icons8-settings-white-50.png"
                )
            )
        ))
        settingsAction.setShortcut(Qt.CTRL+Qt.SHIFT+Qt.Key_S)
        settingsAction.triggered.connect(self.onSettingsActionTriggered)

        aboutAction = QAction("About", self)
        aboutAction.setIcon(QIcon(
            os.path.abspath(
                os.path.realpath(
                    "src/icons/icons8/icons8-about-50.png"
                    if self.appTheme.startswith('light') else
                    "src/icons/icons8/icons8-about-white-50.png"
                )
            )
        ))
        aboutAction.setShortcut(Qt.CTRL+Qt.SHIFT+Qt.Key_A)
        aboutAction.triggered.connect(self.onAboutActionTriggered)

        licenseAction = QAction("License", self)
        licenseAction.setIcon(QIcon(
            os.path.abspath(
                os.path.realpath(
                    "src/icons/icons8/icons8-software-license-50.png"
                    if self.appTheme.startswith('light') else
                    "src/icons/icons8/icons8-software-license-white-50.png"
                )
            )
        ))
        licenseAction.setShortcut(Qt.CTRL+Qt.SHIFT+Qt.Key_L)
        licenseAction.triggered.connect(self.onLicenseActionTriggered)

        devInfoAction = QAction("Developer Info", self)
        devInfoAction.setIcon(QIcon(
            os.path.abspath(
                "src/icons/icons8/icons8-code-50.png"
                if self.appTheme.startswith('light') else
                "src/icons/icons8/icons8-code-white-50.png"
            )
        ))
        devInfoAction.setShortcut(Qt.CTRL+Qt.SHIFT+Qt.Key_D)
        devInfoAction.triggered.connect(self.onDevInfoActionTriggered)

        fileMenu.addActions([
            newWindowAction,
            exitAction
        ])

        editMenu.addActions([
            settingsAction
        ])

        helpMenu.addActions([
            aboutAction,
            licenseAction,
            devInfoAction
        ])

        menuBar.addMenu(fileMenu)
        menuBar.addMenu(editMenu)
        menuBar.addMenu(imageMenu)
        menuBar.addMenu(helpMenu)

        self.imageMenu = imageMenu

        self.setMenuBar(menuBar)

    def _createKeyShortcuts(self) -> None:
        imagePaste = QShortcut(QKeySequence.Paste, self)
        imagePaste.activated.connect(self.imagePasted)

        quitApp = QShortcut(QKeySequence(Qt.CTRL+Qt.Key_Q), self)
        quitApp.activated.connect(self.close)

    def _createSignalBindings(self) -> None:
        self.activeImageChanged.connect(self.onActiveImageChanged)

    def closeEvent(self, event: QCloseEvent) -> None:
        event.ignore()
        exitConfirmation = QMessageBox(
            QMessageBox.Warning,
            self.appTitle,
            f"Are You Sure You Want To Exit {self.appTitle}?",
            QMessageBox.Yes | QMessageBox.No,
            self
        ).exec()
        if exitConfirmation == QMessageBox.Yes:
            event.accept()

    @pyqtSlot()
    def onNewWindowActionTriggered(_) -> None:
        if not getattr(sys, "frozen", False):
            run([sys.executable, sys.argv[0]])
        else:
            run([sys.executable])

    @pyqtSlot()
    def onSettingsActionTriggered(self) -> None:
        def __saveSettings() -> None:
            selectedThemeName = settingsDialogThemeSetting.currentText()
            selectedTheme = selectedThemeName.replace(' ', '_').lower()+'.xml'

            apply_stylesheet(self.app, theme=selectedTheme)

            self.appThemeName = selectedThemeName
            self.appTheme = selectedTheme

            settingsFilePath = os.path.join(
                user_config_dir(self.appTitle), "settings.toml"
            )

            if os.path.exists(settingsFilePath):
                with open(settingsFilePath, "r") as settingsFile:
                    tomlObject = toml.load(settingsFile)
                with open(settingsFilePath, "w") as settingsFile:
                    tomlObject["theme"]["xml"] = selectedTheme
                    tomlObject["theme"]["name"] = selectedThemeName
                    toml.dump(tomlObject, settingsFile)
            else:
                os.makedirs(os.path.dirname(settingsFilePath))
                with open(settingsFilePath, "w") as settingsFile:
                    settingsDict = {
                        "theme": {
                            "xml": selectedTheme,
                            "name": selectedThemeName
                        }
                    }
                    toml.dump(settingsDict, settingsFile)

            self._createMenuBar()
            settingsDialog.close()

        settingsDialog = QDialog(self)

        settingsDialogLayout = QVBoxLayout(settingsDialog)

        settingsDialogThemeTitle = QLabel("Select Theme", settingsDialog)

        settingsDialogThemeSetting = QComboBox(settingsDialog)
        settingsDialogThemeSetting.addItems([
            theme.replace('.xml', '').replace('_', ' ').title()
            for theme in list_themes()
        ])
        settingsDialogThemeSetting.setCurrentText(self.appThemeName)

        settingsDialogButtons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, settingsDialog
        )
        settingsDialogButtons.accepted.connect(__saveSettings)
        settingsDialogButtons.rejected.connect(settingsDialog.close)

        settingsDialogLayout.setAlignment(Qt.AlignCenter)
        settingsDialogLayout.addWidget(settingsDialogThemeTitle)
        settingsDialogLayout.addWidget(settingsDialogThemeSetting)
        settingsDialogLayout.addSpacing(25)
        settingsDialogLayout.addWidget(settingsDialogButtons)

        settingsDialog.setWindowTitle(self.appTitle)
        settingsDialog.setLayout(settingsDialogLayout)
        settingsDialog.resize(400, 100)
        settingsDialog.exec()

    @pyqtSlot()
    def onAboutActionTriggered(self) -> None:
        aboutDialog = QDialog(self)

        aboutDialogLayout = QVBoxLayout(aboutDialog)

        aboutDialogLogo = QLabel(aboutDialog)
        aboutDialogLogo.setPixmap(
            QPixmap(
                os.path.abspath(
                    os.path.realpath("src/icons/logo.png")
                )
            ).scaled(
                QSize(
                    (self.width() - 110),
                    (self.height() - 100)
                ), Qt.KeepAspectRatio
            )
        )

        aboutDialogText = QLabel(
            """\
<b>Clipboard2Image</b>, Or <i>C2I</i> For Short, Is A Free And
Open-Source Tool To Convert Copied/Cut Images To Files
(<code>.jpg</code>, <code>.png</code>, etc.).<br><br>
Clipboard2Image Is Licensed Under
<a href="https://www.gnu.org/licenses/gpl-3.0.en.html">
The GNU GPL v3 License</a>. Use <code>Help > License</code>
(<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>L</kbd>)
For Viewing The License.<br><br>
The Clipboard2Image Logo And Icon Is Generated With The
<a href="https://cooltext.com/Logo-Design-3D-Outline-Gradient">
Cooltext Graphics Generator</a><br></i><br>
All Icons Used In The Menu Bar Are Provided By
<a href="https://icons8.com/icons/fluent-systems-regular">
Icons8 (Fluent System Regular)</a>.<br><br>
Clipboard2Image Is Written In <a href="https://python.org">Python</a>
Using The <a href="https://pypi.org/project/pyqt5">PyQt5 Library</a>.<br><br>
The <code>Light Blue</code> Theme Of
<a href="https://pypi.org/project/qt-material/"><code>qt-material</code></a>
Is Used.<br><br>
For More Developer Info, Use <code>Help > Developer Info</code>
(<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>D</kbd>).
            """, aboutDialog
        )
        aboutDialogText.setTextFormat(Qt.RichText)
        aboutDialogText.setWordWrap(True)
        aboutDialogText.setAlignment(Qt.AlignCenter)
        aboutDialogText.setTextInteractionFlags(Qt.TextBrowserInteraction)
        aboutDialogText.setOpenExternalLinks(True)

        aboutDialogButtons = QDialogButtonBox(QDialogButtonBox.Ok, aboutDialog)
        aboutDialogButtons.accepted.connect(aboutDialog.close)

        aboutDialogLayout.setAlignment(Qt.AlignCenter)
        aboutDialogLayout.addWidget(aboutDialogLogo)
        aboutDialogLayout.addSpacing(25)
        aboutDialogLayout.addWidget(aboutDialogText)
        aboutDialogLayout.addSpacing(25)
        aboutDialogLayout.addWidget(aboutDialogButtons)

        aboutDialog.setWindowTitle(self.appTitle)
        aboutDialog.setLayout(aboutDialogLayout)
        aboutDialog.resize(QSize((self.width() - 100), (self.height() - 200)))
        aboutDialog.exec()

    @pyqtSlot()
    def onLicenseActionTriggered(self) -> None:
        licenseDialog = QDialog(self)

        licenseDialogLayout = QVBoxLayout(licenseDialog)

        licenseDialogText = QTextBrowser(licenseDialog)
        licenseDialogText.setOpenExternalLinks(True)

        with open(
            os.path.abspath(os.path.realpath("src/html/license.html")), "r"
        ) as license:
            licenseDialogText.setHtml(license.read())

        licenseDialogButtons = QDialogButtonBox(
            QDialogButtonBox.Ok, licenseDialog
        )
        licenseDialogButtons.accepted.connect(licenseDialog.close)

        licenseDialogLayout.setAlignment(Qt.AlignCenter)
        licenseDialogLayout.addWidget(licenseDialogText)
        licenseDialogLayout.addSpacing(25)
        licenseDialogLayout.addWidget(licenseDialogButtons)

        licenseDialog.setWindowTitle(self.appTitle)
        licenseDialog.setLayout(licenseDialogLayout)
        licenseDialog.resize(
            QSize((self.width() - 100), (self.height() - 200))
        )
        licenseDialog.exec()

    @pyqtSlot()
    def onDevInfoActionTriggered(self) -> None:
        sysVersion = sys.version
        sysVersionInfo = sys.version_info

        pipVersion = pip_version
        pipModulesStr = "<br>"

        for m in working_set:
            pipModulesStr += f"<br><span>{m.project_name} - {m.parsed_version}"

        pilVersion = pil_version

        pyqtVersion = PYQT_VERSION_STR
        qtVersion = QT_VERSION_STR
        sipVersion = SIP_VERSION_STR

        pyInstallerVersion = pyinstaller_version
        pyInstallerExe = "Yes" if getattr(sys, "frozen", False) else "No"

        devInfoDialog = QDialog(self)

        devInfoDialogLayout = QVBoxLayout(devInfoDialog)

        devInfoDialogText = QTextBrowser(devInfoDialog)
        devInfoDialogText.setWordWrapMode(QTextOption.NoWrap)
        devInfoDialogText.setHtml(f"""
<h3>Clipboard2Image</h3>
<b>Current version:</b> <i><code>{self.appVersion}</code></i></i><br>
<b>Current theme:</b> <i><code>{self.appTheme}</code></i></i><br>
<b>Current theme (human readable):</b> <i><code>{self.appThemeName}</code>
</i></i><br>
<h3>Python</h3>
<b><code><b>sys.version</code>:</b> <i><code>{sysVersion}</code></i></i><br>
<b><code><b>sys.version_info</code>:</b>
<i><code>{sysVersionInfo}</code></i></i><br>
<h3>pip</h3>
<b><code><b>pip</code> version:</b> <i><code>{pipVersion}</code></i><br>
<b><code><b>pip</code> modules:</b> <i><code>{pipModulesStr}</code></i><br>
<h3>PIL</h3>
<b><code>PIL (pillow)</code> version:</b> <i><code>{pilVersion}</code></i><br>
<h3>PyQt</h3>
<b><code><b>PyQt</code> version:</b> <i><code<>{pyqtVersion}</code></i><br>
<b><code><b>Qt</code> version:</b> <i><code>{qtVersion}</code></i><br>
<b><code><b>sip</code> version:</b> <i><code>{sipVersion}</code></i><br>
<h3>PyInstaller</h3>
<b><code>PyInstaller</code> version:</b>
<i><code>{pyInstallerVersion}</code></i><br>
<b>App is running inside a <code>PyInstaller</code>
executable:</b> <i><code>{pyInstallerExe}</code></i><br>
        """)

        devInfoDialogButtons = QDialogButtonBox(
            QDialogButtonBox.Ok, devInfoDialog
        )
        devInfoDialogButtons.accepted.connect(devInfoDialog.close)

        devInfoDialogLayout.setAlignment(Qt.AlignCenter)
        devInfoDialogLayout.addWidget(devInfoDialogText)
        devInfoDialogLayout.addSpacing(25)
        devInfoDialogLayout.addWidget(devInfoDialogButtons)

        devInfoDialog.setWindowTitle(self.appTitle)
        devInfoDialog.setLayout(devInfoDialogLayout)
        devInfoDialog.resize(
            QSize((self.width() - 100), (self.height() - 200))
        )
        devInfoDialog.exec()

    @pyqtSlot()
    def onActiveImageChanged(self) -> None:
        if self.activeImage is not None:
            self.imageMenu.setEnabled(True)
        else:
            self.imageMenu.setEnabled(False)

    @pyqtSlot()
    def imagePasted(self) -> None:
        image = ImageGrab.grabclipboard()
        if type(image) is not Image and type(image) is list:
            image = Image.open(image[0])
        else:
            raise NoImageInClipboard(self.app.clipboard().text())
        self.activeImage = image

    @pyqtProperty(Image.Image, notify=activeImageChanged)
    def activeImage(self) -> Image.Image:
        return self._activeImage

    @activeImage.setter
    def activeImage(self, image: Image.Image) -> None:
        self._activeImage = image
        self.activeImageChanged.emit()
