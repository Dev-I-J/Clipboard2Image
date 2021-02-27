from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QMenuBar,
    QMenu,
    QAction,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QTextBrowser,
    QComboBox,
    QScrollArea,
    QToolBar,
    QStatusBar,
    QFileDialog,
    QLineEdit,
    QCheckBox,
    QRadioButton,
    QColorDialog
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

from PIL import Image, ImageGrab, ImageOps, ImageQt, UnidentifiedImageError
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


class Clipboard2Image(QMainWindow):
    appTitle = "Clipboard2Image"
    appVersion = "0.0.1-alpha"
    appTheme = "light_blue.xml"
    appThemeName = "Light Blue"
    appIconPath = os.path.abspath(
        os.path.realpath("src/icons/appicon.png")
    )

    supportedFormats = [
        "BMP Image (*.bmp)",
        "DIB Image (*.dib)",
        "PCX File (*.pcx)",
        "EPS File (*.eps)",
        "GIF Image (*.gif)",
        "ICNS File (*.icns)",
        "ICO Image (*.ico)",
        "IM File (*.im)",
        "JPEG Image (*.jpeg)",
        "JPG Image - Same As JPEG (*.jpg)",
        "JPEG 2000 Image (*.jp2)",
        "JPEG 2000 Raw Codestream (*.j2k)",
        "Boxed JPEG 2000 File - jp2 (*.j2p)",
        "Boxed JPEG 2000 File - jpx (*.jxp)",
        "PNG Image (*.png)"
    ]
    supportedExtensions = [
        "*.bmp",
        "*.dib",
        "*.pcx",
        "*.eps",
        "*.gif",
        "*.icns",
        "*.ico",
        "*.im",
        "*.jpg",
        "*.jpeg",
        "*.jp2"
        "*.j2k",
        "*.j2p",
        "*.jpx",
        "*.png"
    ]

    activeImageChanged = pyqtSignal()
    activeImagePathChanged = pyqtSignal()

    _activeImage = None
    _activeImagePath = None

    def __init__(self, app: QApplication) -> None:
        super().__init__()

        self.app = app

        self._loadSettings()
        self._processArgs()
        self._createWindow()
        self._createMenuBar()
        self._createWidgets()
        self._createToolBar()
        self._createStatusBar()
        self._createSignalBindings()

        self.activeImageChanged.emit()

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

    def _processArgs(self) -> None:
        if (len(sys.argv) >= 3) and (sys.argv[1] == "--theme") and (
            theme := sys.argv[2].replace('-', '_')+'.xml'
        ) in list_themes():
            self.appTheme = theme
            self.appThemeName = sys.argv[2].replace('-', ' ').title()
        self._createMenuBar()

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

    def _createMenuBar(self) -> None:
        menuBar = QMenuBar(self)

        fileMenu = QMenu("File", self)
        editMenu = QMenu("Edit", self)
        self.imageMenu = QMenu("Image", self)
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

        self.pasteAction = QAction("Paste", self)
        self.pasteAction.setIcon(QIcon(
            os.path.abspath(
                os.path.realpath(
                    "src/icons/icons8/icons8-paste-50.png"
                    if self.appTheme.startswith('light') else
                    "src/icons/icons8/icons8-paste-white-50.png"
                )
            )
        ))
        self.pasteAction.setShortcut(QKeySequence.Paste)
        self.pasteAction.triggered.connect(self.imagePasted)

        self.openAction = QAction("Open", self)
        self.openAction.setIcon(QIcon(
            os.path.abspath(
                os.path.realpath(
                    "src/icons/icons8/icons8-folder-50.png"
                    if self.appTheme.startswith('light') else
                    "src/icons/icons8/icons8-folder-white-50.png"
                )
            )
        ))
        self.openAction.setShortcut(QKeySequence.Open)

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
        exitAction.setShortcut(Qt.CTRL+Qt.Key_Q)
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
        settingsAction.setShortcut(Qt.ALT+Qt.SHIFT+Qt.Key_S)
        settingsAction.triggered.connect(self.onSettingsActionTriggered)

        self.backAction = QAction("Back", self)
        self.backAction.setIcon(QIcon(
            os.path.abspath(
                os.path.realpath(
                    "src/icons/icons8/icons8-back-50.png"
                    if self.appTheme.startswith('light') else
                    "src/icons/icons8/icons8-back-white-50.png"
                )
            )
        ))
        self.backAction.setShortcut(QKeySequence.Back)
        self.backAction.triggered.connect(self.onBackActionTriggered)

        self.copyAction = QAction("Copy To Clipboard", self)
        self.copyAction.setIcon(QIcon(
            os.path.abspath(
                os.path.realpath(
                    "src/icons/icons8/icons8-copy-50.png"
                    if self.appTheme.startswith('light') else
                    "src/icons/icons8/icons8-copy-white-50.png"
                )
            )
        ))
        self.copyAction.setShortcut(QKeySequence.Copy)
        self.copyAction.triggered.connect(self.onCopyActionTriggered)

        self.saveAction = QAction("Save", self)
        self.saveAction.setIcon(QIcon(
            os.path.abspath(
                os.path.realpath(
                    "src/icons/icons8/icons8-save-50.png"
                    if self.appTheme.startswith('light') else
                    "src/icons/icons8/icons8-save-white-50.png"
                )
            )
        ))
        self.saveAction.setShortcut(QKeySequence.Save)
        self.saveAction.triggered.connect(self.onSaveActionTriggered)

        self.saveAsAction = QAction("Save As", self)
        self.saveAsAction.setIcon(QIcon(
            os.path.abspath(
                os.path.realpath(
                    "src/icons/icons8/icons8-save-as-50.png"
                    if self.appTheme.startswith('light') else
                    "src/icons/icons8/icons8-save-as-white-50.png"
                )
            )
        ))
        self.saveAsAction.setShortcut(Qt.CTRL+Qt.SHIFT+Qt.Key_S)
        self.saveAsAction.triggered.connect(self.onSaveAsActionTriggered)

        self.resizeAction = QAction("Resize", self)
        self.resizeAction.setIcon(QIcon(
            os.path.abspath(
                os.path.realpath(
                    "src/icons/icons8/icons8-resize-50.png"
                    if self.appTheme.startswith('light') else
                    "src/icons/icons8/icons8-resize-white-50.png"
                )
            )
        ))
        self.resizeAction.setShortcut(Qt.CTRL+Qt.Key_R)
        self.resizeAction.triggered.connect(self.onResizeActionTriggered)

        self.rotateAction = QAction("Rotate", self)
        self.rotateAction.setIcon(QIcon(
            os.path.abspath(
                os.path.realpath(
                    "src/icons/icons8/icons8-rotate-50.png"
                    if self.appTheme.startswith('light') else
                    "src/icons/icons8/icons8-rotate-white-50.png"
                )
            )
        ))
        self.rotateAction.setShortcut(Qt.CTRL+Qt.SHIFT+Qt.Key_R)
        self.rotateAction.triggered.connect(self.onRotateActionTriggered)

        self.rotateRightAction = QAction(
            "Rotate 90 Degrees To The Right", self
        )
        self.rotateRightAction.setIcon(QIcon(
            os.path.abspath(
                os.path.realpath(
                    "src/icons/icons8/icons8-rotate-right-50.png"
                    if self.appTheme.startswith('light') else
                    "src/icons/icons8/icons8-rotate-right-white-50.png"
                )
            )
        ))
        self.rotateRightAction.setShortcut(Qt.ALT+Qt.SHIFT+Qt.Key_R)
        self.rotateRightAction.triggered.connect(
            self.onRotateRightActionTriggered
        )

        self.rotateLeftAction = QAction(
            "Rotate 90 Degrees To The Left",
            self
        )
        self.rotateLeftAction.setIcon(QIcon(
            os.path.abspath(
                os.path.realpath(
                    "src/icons/icons8/icons8-rotate-left-50.png"
                    if self.appTheme.startswith('light') else
                    "src/icons/icons8/icons8-rotate-left-white-50.png"
                )
            )
        ))
        self.rotateLeftAction.setShortcut(Qt.ALT+Qt.SHIFT+Qt.Key_L)
        self.rotateLeftAction.triggered.connect(
            self.onRotateLeftActionTriggered
        )

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

        fileMenu.addAction(newWindowAction)
        fileMenu.addAction(self.pasteAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(exitAction)

        editMenu.addAction(settingsAction)

        self.imageMenu.addAction(self.backAction)
        self.imageMenu.addAction(self.copyAction)
        self.imageMenu.addAction(self.saveAction)
        self.imageMenu.addAction(self.saveAsAction)
        self.imageMenu.addAction(self.resizeAction)
        self.imageMenu.addAction(self.rotateAction)
        self.imageMenu.addAction(self.rotateRightAction)
        self.imageMenu.addAction(self.rotateLeftAction)

        helpMenu.addAction(aboutAction)
        helpMenu.addAction(licenseAction)
        helpMenu.addAction(devInfoAction)

        menuBar.addMenu(fileMenu)
        menuBar.addMenu(editMenu)
        menuBar.addMenu(self.imageMenu)
        menuBar.addMenu(helpMenu)

        self.setMenuBar(menuBar)

    def _createWidgets(self) -> None:
        def __openImage():
            try:
                imageFile = QFileDialog.getOpenFileName(
                    self,
                    "Select An Image To Open",
                    filter=f"Image Files \
({' '.join(self.supportedExtensions)});;{';;'.join(self.supportedFormats)}\
;;All Files (*)"
                )
                self.activeImage = (
                    Image.open(imageFile[0]) if imageFile[0] else None
                )
                self.activeImagePath = imageFile[0] if imageFile[0] else None
            except UnidentifiedImageError:
                errorMessage = QMessageBox(
                    QMessageBox.Warning,
                    self.appTitle,
                    "Unidentified Image Type Found! Plase Try Another \
Extension.",
                    QMessageBox.Ok
                )
                errorMessage.setWindowIcon(QIcon(self.appIconPath))
                errorMessage.exec()
                return None
            except OSError as e:
                errorMessage = QMessageBox(
                    QMessageBox.Warning,
                    self.appTitle,
                    "Unable To Open Your Image!",
                    QMessageBox.Ok
                )
                errorMessage.setWindowIcon(QIcon(self.appIconPath))
                errorMessage.setInformativeText(str(e))
                errorMessage.exec()
                return None

        homeWidget = QWidget(self.centralWidget)

        homeLayout = QVBoxLayout(homeWidget)
        homeLayout.setAlignment(Qt.AlignCenter)

        homePasteLabel = QLabel(
            """Paste Your Image Here (Ctrl + V), Or Click The Button Below \
To Paste Your Image!

You Can Also An Existing Image File By Clicking The \"Open An Image File!\" \
Button.""", homeWidget
        )
        homePasteLabel.setAlignment(Qt.AlignCenter)

        homePasteImage = QPushButton(
            "Paste Image!", homeWidget
        )
        homePasteImage.clicked.connect(self.imagePasted)

        homeOpenImage = QPushButton(
            "Open An Image File!", homeWidget
        )
        homeOpenImage.clicked.connect(__openImage)
        self.openAction.triggered.connect(__openImage)

        homeLayout.addWidget(homePasteLabel)
        homeLayout.addSpacing(50)
        homeLayout.addWidget(homePasteImage)
        homeLayout.addSpacing(25)
        homeLayout.addWidget(homeOpenImage)

        homeWidget.setLayout(homeLayout)

        imageViewWidget = QWidget(self.centralWidget)

        imageViewLayout = QVBoxLayout(imageViewWidget)
        imageViewLayout.setAlignment(Qt.AlignCenter)

        self.imageViewScrollArea = QScrollArea(imageViewWidget)
        self.imageViewScrollArea.setWidgetResizable(True)

        self.imageViewLabel = QLabel(self.imageViewScrollArea)
        self.imageViewLabel.setAlignment(Qt.AlignCenter)

        self.imageViewScrollArea.setWidget(self.imageViewLabel)

        imageViewLayout.addWidget(self.imageViewScrollArea)

        imageViewWidget.setLayout(imageViewLayout)

        self.centralWidget.addWidget(homeWidget)
        self.centralWidget.addWidget(imageViewWidget)
        self.centralWidget.setCurrentIndex(0)

    def _createToolBar(self):
        self.toolBar = QToolBar(self)
        self.toolBar.setMovable(False)
        self.toolBar.addAction(self.backAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.copyAction)
        self.toolBar.addAction(self.saveAction)
        self.toolBar.addAction(self.saveAsAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.resizeAction)
        self.toolBar.addAction(self.rotateAction)
        self.toolBar.addAction(self.rotateRightAction)
        self.toolBar.addAction(self.rotateLeftAction)

        self.addToolBar(self.toolBar)

    def _createStatusBar(self):
        self.statusBar = QStatusBar(self)
        self.imageDimensions = QLabel(self.statusBar)
        self.imageFormat = QLabel(self.statusBar)
        self.statusBar.addPermanentWidget(QLabel("Ready", self.statusBar))
        self.statusBar.insertPermanentWidget(0, self.imageDimensions)
        self.statusBar.insertPermanentWidget(1, self.imageFormat)
        self.setStatusBar(self.statusBar)

    def _createSignalBindings(self) -> None:
        self.activeImageChanged.connect(self.onActiveImageChanged)
        self.activeImagePathChanged.connect(self.onActiveImagePathChanged)

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
            try:
                if os.path.exists(settingsFilePath):
                    with open(settingsFilePath, "r") as settingsFile:
                        try:
                            tomlObject = toml.load(settingsFile)
                        except toml.TomlDecodeError as e:
                            errorMessage = QMessageBox(
                                QMessageBox.Warning,
                                self.appTitle,
                                "Unable To Parse The Settings File!",
                                QMessageBox.Ok
                            )
                            errorMessage.setInformativeText(str(e))
                            errorMessage.setWindowIcon(QIcon(self.appIconPath))
                            errorMessage.exec()
                            return None
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
            except OSError as e:
                errorMessage = QMessageBox(
                    QMessageBox.Warning,
                    self.appTitle,
                    "Unable To Open The Settings File!",
                    QMessageBox.Ok
                )
                errorMessage.setInformativeText(str(e))
                errorMessage.setWindowIcon(QIcon(self.appIconPath))
                errorMessage.exec()
                return None

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
    def onBackActionTriggered(self):
        backConfirmation = QMessageBox(
            QMessageBox.Warning,
            self.appTitle,
            "Are You Sure You Want To Go Back?",
            QMessageBox.Yes | QMessageBox.No,
            self
        )
        backConfirmation.setInformativeText(
            "Your Image Will Get Deleted Unless You Saved It!"
        )
        backConfirmationResponse = backConfirmation.exec()
        if backConfirmationResponse == QMessageBox.Yes:
            self.activeImage = None
            self.activeImagePath = None

    @pyqtSlot()
    def onCopyActionTriggered(self):
        self.app.clipboard().setPixmap(QPixmap.fromImage(
            ImageQt.ImageQt(self.activeImage.convert("RGBA"))
        ))
        self.statusBar.showMessage("Image Copied To Clipboard", 2000)

    @pyqtSlot()
    def onSaveActionTriggered(self):
        if self.activeImagePath is not None:
            try:
                with open(self.activeImagePath, "wb") as imageFile:
                    self.activeImage.save(imageFile, self.activeImage.format)
            except UnidentifiedImageError as e:
                errorMessage = QMessageBox(
                    QMessageBox.Warning,
                    self.appTitle,
                    "Unidentified Image Type Found! Please Try Another \
Extension.",
                    QMessageBox.Ok
                )
                errorMessage.setInformativeText(str(e))
                errorMessage.setWindowIcon(QIcon(self.appIconPath))
                errorMessage.exec()
                return None
            except OSError as e:
                errorMessage = QMessageBox(
                    QMessageBox.Warning,
                    self.appTitle,
                    "Unable To Save Your Image!",
                    QMessageBox.Ok
                )
                errorMessage.setInformativeText(str(e))
                errorMessage.setWindowIcon(QIcon(self.appIconPath))
                errorMessage.exec()
                return None
            self.statusBar.showMessage("Image Saved", 2000)
        else:
            self.onSaveAsActionTriggered()

    @pyqtSlot()
    def onSaveAsActionTriggered(self):
        fileFormatList = [
            f for f in self.supportedFormats if not f.startswith(
                self.activeImage.format.upper()
            )
        ]
        saveFilePath = QFileDialog.getSaveFileName(
            self,
            "Save Your Image As",
            filter=f"{self.activeImage.format} Image \
(*.{self.activeImage.format.lower()});;{';;'.join(fileFormatList)};;\
All Files (*)"
        )
        if (f := saveFilePath[0]) is not None:
            try:
                with open(f, "wb")as imageFile:
                    self.activeImage.save(imageFile)
            except UnidentifiedImageError as e:
                errorMessage = QMessageBox(
                    QMessageBox.Warning,
                    self.appTitle,
                    "Unidentified Image Type Found! Please Try Another \
Extension.",
                    QMessageBox.Ok
                )
                errorMessage.setInformativeText(str(e))
                errorMessage.setWindowIcon(QIcon(self.appIconPath))
                errorMessage.exec()
                return None
            except OSError as e:
                errorMessage = QMessageBox(
                    QMessageBox.Warning,
                    self.appTitle,
                    "Unable To Save Your Image!",
                    QMessageBox.Ok
                )
                errorMessage.setInformativeText(str(e))
                errorMessage.setWindowIcon(QIcon(self.appIconPath))
                errorMessage.exec()
                return None
            self.activeImagePath = f
            self.statusBar.showMessage(
                f"Image Saved As {self.activeImagePath}", 2000
            )

    @pyqtSlot()
    def onResizeActionTriggered(self):
        def __resizeImage():
            oldDimensions = self.imageDimensions.text()

            try:
                newWidth = int(round(float(resizeDialogWidthField.text())))
                newHeight = int(round(float(resizeDialogHeightField.text())))
            except ValueError as e:
                errorMessage = QMessageBox(
                    QMessageBox.Warning,
                    self.appTitle,
                    "Invalid Value Entered! Plase Enter A Valid Value.",
                    QMessageBox.Ok
                )
                errorMessage.setInformativeText(str(e))
                errorMessage.setWindowIcon(QIcon(self.appIconPath))
                errorMessage.exec()
                return None

            maintainAspect = resizeDialogAspectRatio.isChecked()

            if maintainAspect:
                if resizeDialogRespectWidth.isChecked():
                    widthPercent = (newWidth / self.activeImage.size[0])
                    realHeight = int(float(newHeight) * float(widthPercent))
                    imgFormat = self.activeImage.format
                    self.activeImage = self.activeImage.resize(
                        (newWidth, realHeight,), Image.ANTIALIAS
                    )
                    self.activeImage.format = imgFormat
                    self.imageFormat.setText(imgFormat)
                else:
                    heightPercent = (newHeight / self.activeImage.size[1])
                    realWidth = int(float(newWidth) * float(heightPercent))
                    imgFormat = self.activeImage.format
                    self.activeImage = self.activeImage.resize(
                        (realWidth, newHeight,), Image.ANTIALIAS
                    )
                    self.activeImage.format = imgFormat
                    self.imageFormat.setText(imgFormat)
            else:
                imgFormat = self.activeImage.format
                self.activeImage = self.activeImage.resize(
                    (newWidth, newHeight,), Image.ANTIALIAS
                )
                self.activeImage.format = imgFormat
                self.imageFormat.setText(imgFormat)

            self.imageDimensions.setText(
                f"{self.activeImage.size[0]} × {self.activeImage.size[1]}"
            )

            resizeDialog.close()
            self.statusBar.showMessage(
                f"Image Resized ({oldDimensions} To \
{self.imageDimensions.text()})",
                2000
            )

        resizeDialog = QDialog(self)

        resizeDialogLayout = QVBoxLayout(resizeDialog)

        resizeDialogWidth = QWidget(resizeDialog)
        resizeDialogWidthLayout = QHBoxLayout(resizeDialogWidth)

        resizeDialogWidthLabel = QLabel("Width:", resizeDialogWidth)
        resizeDialogWidthField = QLineEdit(resizeDialogWidth)
        resizeDialogWidthField.setText(str(self.activeImage.size[0]))

        resizeDialogWidthLayout.addWidget(resizeDialogWidthLabel)
        resizeDialogWidthLayout.addSpacing(10)
        resizeDialogWidthLayout.addWidget(resizeDialogWidthField)
        resizeDialogWidthLayout.addWidget(QLabel("px", resizeDialogWidth))

        resizeDialogWidth.setLayout(resizeDialogWidthLayout)

        resizeDialogHeight = QWidget(resizeDialog)
        resizeDialogHeightLayout = QHBoxLayout(resizeDialogHeight)

        resizeDialogHeightLabel = QLabel("Height:", resizeDialogHeight)
        resizeDialogHeightField = QLineEdit(resizeDialogHeight)
        resizeDialogHeightField.setText(str(self.activeImage.size[1]))

        resizeDialogHeightLayout.addWidget(resizeDialogHeightLabel)
        resizeDialogHeightLayout.addSpacing(10)
        resizeDialogHeightLayout.addWidget(resizeDialogHeightField)
        resizeDialogHeightLayout.addWidget(QLabel("px", resizeDialogHeight))

        resizeDialogHeight.setLayout(resizeDialogHeightLayout)

        resizeDialogAspectRatio = QCheckBox(
            "Maintain Aspect Ratio", resizeDialog
        )
        resizeDialogAspectRatio.setChecked(True)
        resizeDialogAspectRatio.stateChanged.connect(
            lambda: resizeDialogRespect.setEnabled(
                resizeDialogAspectRatio.isChecked()
            )
        )

        resizeDialogRespect = QWidget(resizeDialog)
        resizeDialogRespect.setEnabled(resizeDialogAspectRatio.isChecked())

        resizeDialogRespectLayout = QHBoxLayout(resizeDialogRespect)

        resizeDialogRespectLabel = QLabel("Respect:", resizeDialogRespect)

        resizeDialogRespectWidth = QRadioButton("Width", resizeDialogRespect)
        resizeDialogRespectWidth.setChecked(True)

        resizeDialogRespectHeight = QRadioButton("Height", resizeDialogRespect)

        resizeDialogRespectLayout.addWidget(resizeDialogRespectLabel)
        resizeDialogRespectLayout.addSpacing(10)
        resizeDialogRespectLayout.addWidget(resizeDialogRespectWidth)
        resizeDialogRespectLayout.addWidget(resizeDialogRespectHeight)

        resizeDialogRespect.setLayout(resizeDialogRespectLayout)

        resizeDialogButtons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, resizeDialog
        )
        resizeDialogButtons.accepted.connect(__resizeImage)
        resizeDialogButtons.rejected.connect(resizeDialog.close)

        resizeDialogWidthField.returnPressed.connect(
            resizeDialogButtons.accepted.emit
        )
        resizeDialogHeightField.returnPressed.connect(
            resizeDialogButtons.accepted.emit
        )

        resizeDialogLayout.addWidget(resizeDialogWidth)
        resizeDialogLayout.addWidget(resizeDialogHeight)
        resizeDialogLayout.addWidget(resizeDialogAspectRatio)
        resizeDialogLayout.addWidget(resizeDialogRespect)
        resizeDialogLayout.addSpacing(25)
        resizeDialogLayout.addWidget(resizeDialogButtons)

        resizeDialog.setWindowTitle(self.appTitle)
        resizeDialog.setWindowIcon(QIcon(self.appIconPath))
        resizeDialog.setLayout(resizeDialogLayout)

        resizeDialog.resize(400, 200)
        resizeDialog.exec()

    @pyqtSlot()
    def onRotateActionTriggered(self):
        def __rotateImage():
            try:
                angle = int(rotateDialogAngleField.text())
                imgFormat = self.activeImage.format

                if self.rotatedImgColor == "alpha":
                    self.activeImage = self.activeImage.rotate(
                        angle, fillcolor=(255, 255, 255, 0,),
                        expand=True, resample=Image.BICUBIC
                    )
                else:
                    self.activeImage = self.activeImage.rotate(
                        angle, fillcolor=self.rotatedImgColor,
                        expand=True, resample=Image.BICUBIC
                    )

                self.activeImage.format = imgFormat
                self.imageFormat.setText(imgFormat)
            except ValueError as e:
                errorMessage = QMessageBox(
                    QMessageBox.Warning,
                    self.appTitle,
                    "Invalid Value Entered! Plase Enter A Valid Value.",
                    QMessageBox.Ok
                )
                errorMessage.setInformativeText(str(e))
                errorMessage.setWindowIcon(QIcon(self.appIconPath))
                errorMessage.exec()
                return None

            rotateDialog.close()
            self.statusBar.showMessage(f"Image Rotated {angle} Degrees", 2000)

        def __preview(color: str = "#ffffff") -> ImageQt.ImageQt:
            preview = Image.new("RGBA", (60, 25,), color)
            preview = ImageOps.expand(preview, border=4, fill="black")
            return ImageQt.ImageQt(preview)

        def __pickColor():
            self.rotatedImgColor = QColorDialog.getColor().name()
            rotateDialogColorPreview.setVisible(True)
            rotateDialogColorPreview.setPixmap(QPixmap.fromImage(
                __preview(self.rotatedImgColor))
            )

        def __transparent():
            self.rotatedImgColor = "alpha"
            rotateDialogColorPreview.setVisible(False)

        self.rotatedImgColor = "#ffffff"

        rotateDialog = QDialog(self)

        rotateDialogLayout = QVBoxLayout(rotateDialog)

        rotateDialogAngle = QWidget(rotateDialog)

        rotateDialogAngleLayout = QHBoxLayout(rotateDialogAngle)

        rotateDialogAngleLabel = QLabel("Angle:", rotateDialogAngle)
        rotateDialogAngleField = QLineEdit(rotateDialogAngle)

        rotateDialogAngleLayout.addWidget(rotateDialogAngleLabel)
        rotateDialogAngleLayout.addSpacing(10)
        rotateDialogAngleLayout.addWidget(rotateDialogAngleField)
        rotateDialogAngleLayout.addWidget(QLabel("Degrees", rotateDialogAngle))

        rotateDialogAngle.setLayout(rotateDialogAngleLayout)

        rotateDialogColor = QWidget(rotateDialog)

        rotateDialogColorLayout = QHBoxLayout(rotateDialogColor)

        rotateDialogColorLabel = QLabel("Background Color:", rotateDialogColor)

        rotateDialogColorPreview = QLabel(rotateDialogColor)
        rotateDialogColorPreview.setPixmap(QPixmap.fromImage(__preview()))

        rotateDialogColorPicker = QPushButton("Select", rotateDialogColor)
        rotateDialogColorPicker.clicked.connect(__pickColor)

        rotateDialogColorAlpha = QPushButton("Transparent", rotateDialogColor)
        rotateDialogColorAlpha.clicked.connect(__transparent)

        rotateDialogColorLayout.addWidget(rotateDialogColorLabel)
        rotateDialogColorLayout.addSpacing(10)
        rotateDialogColorLayout.addWidget(rotateDialogColorPreview)
        rotateDialogColorLayout.addWidget(rotateDialogColorPicker)
        rotateDialogColorLayout.addWidget(rotateDialogColorAlpha)

        rotateDialogColor.setLayout(rotateDialogColorLayout)

        rotateDialogButtons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            rotateDialog
        )
        rotateDialogButtons.accepted.connect(__rotateImage)
        rotateDialogButtons.rejected.connect(rotateDialog.close)

        rotateDialogAngleField.returnPressed.connect(
            rotateDialogButtons.accepted.emit
        )

        rotateDialogLayout.addWidget(rotateDialogAngle)
        rotateDialogLayout.addWidget(rotateDialogColor)
        rotateDialogLayout.addSpacing(25)
        rotateDialogLayout.addWidget(rotateDialogButtons)

        rotateDialog.setWindowTitle(self.appTitle)
        rotateDialog.setWindowIcon(QIcon(self.appIconPath))
        rotateDialog.setLayout(rotateDialogLayout)

        rotateDialog.resize(400, 150)
        rotateDialog.exec()

    @pyqtSlot()
    def onRotateRightActionTriggered(self):
        imgFormat = self.activeImage.format
        self.activeImage = self.activeImage.transpose(Image.ROTATE_270)
        self.activeImage.format = imgFormat
        self.imageFormat.setText(imgFormat)
        self.statusBar.showMessage("Image Rotated To The Right", 2000)

    @pyqtSlot()
    def onRotateLeftActionTriggered(self):
        imgFormat = self.activeImage.format
        self.activeImage = self.activeImage.transpose(Image.ROTATE_90)
        self.activeImage.format = imgFormat
        self.imageFormat.setText(imgFormat)
        self.statusBar.showMessage("Image Rotated To The Left", 2000)

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
        pipModulesStr = "(package - version)<br>"

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
<b><code><b>pip</code> packages:</b> <i><code>{pipModulesStr}</code></i><br>
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
            for action in self.imageMenu.actions():
                action.setEnabled(True)

            self.pasteAction.setEnabled(False)
            self.openAction.setEnabled(False)

            self.toolBar.setEnabled(True)

            self.imageDimensions.setText(
                f"{self.activeImage.size[0]} × {self.activeImage.size[1]}"
            )
            self.imageFormat.setText(self.activeImage.format)
            self.statusBar.insertPermanentWidget(0, self.imageDimensions)
            self.statusBar.insertPermanentWidget(1, self.imageFormat)
            self.imageDimensions.show()
            self.imageFormat.show()

            self.imageViewLabel.setPixmap(
                QPixmap.fromImage(
                    ImageQt.ImageQt(self.activeImage.convert("RGBA"))
                )
            )

            self.imageViewScrollArea.setWidgetResizable(False)
            self.imageViewScrollArea.setWidgetResizable(True)

            self.centralWidget.setCurrentIndex(1)
            self.statusBar.showMessage(
                f"Image Opened ({self.imageDimensions.text()}, \
{self.imageFormat.text()})",
                2000
            )
        else:
            self.imageMenu.setEnabled(False)
            for action in self.imageMenu.actions():
                action.setEnabled(False)

            self.pasteAction.setEnabled(True)
            self.openAction.setEnabled(True)

            self.toolBar.setEnabled(False)
            self.statusBar.removeWidget(self.imageDimensions)
            self.statusBar.removeWidget(self.imageFormat)
            self.centralWidget.setCurrentIndex(0)

    @pyqtSlot()
    def onActiveImagePathChanged(self):
        if (path := self.activeImagePath) is not None:
            self.setWindowTitle(f"{self.appTitle} {self.appVersion} - {path}")
        else:
            self.setWindowTitle(f"{self.appTitle} {self.appVersion}")

    @pyqtSlot()
    def imagePasted(self) -> None:
        try:
            image = ImageGrab.grabclipboard()
            if type(image) is list:
                image = Image.open(image[0])
            else:
                if not isinstance(image, Image.Image):
                    errorMessage = QMessageBox(
                        QMessageBox.Warning,
                        self.appTitle,
                        "Unable To Find An Image In Your Clipboard! \
Please Make Sure You Have Copied An Image Or Click The \"Open An Image \
File!\" Buttton!",
                        QMessageBox.Ok
                    )
                    errorMessage.setWindowIcon(QIcon(self.appIconPath))
                    errorMessage.exec()
                    return None
            self.activeImage = image
        except UnidentifiedImageError:
            errorMessage = QMessageBox(
                QMessageBox.Warning,
                self.appTitle,
                "Unable To Open Your Image! Plase Try Another One.",
                QMessageBox.Ok
            )
            errorMessage.setWindowIcon(QIcon(self.appIconPath))
            errorMessage.exec()
            return None

    @pyqtProperty(Image.Image, notify=activeImageChanged)
    def activeImage(self) -> Image.Image:
        return self._activeImage

    @activeImage.setter
    def activeImage(self, image: Image.Image) -> None:
        self._activeImage = image
        self.activeImageChanged.emit()

    @pyqtProperty(str, notify=activeImagePathChanged)
    def activeImagePath(self) -> str:
        return self._activeImagePath

    @activeImagePath.setter
    def activeImagePath(self, path: str) -> None:
        self._activeImagePath = path
        self.activeImagePathChanged.emit()
