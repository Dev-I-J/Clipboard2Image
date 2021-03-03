# Clipboard2Image

Clipboard2Image Is A FOSS Tool To Create Images By Copy-Pasting Them.

![Screenshot](screenshot.png)

## Features

* Get started by copy-pasting an image from a browser, an image file or open an existing image file!
* Ability to resize and rotate images.
* Wide range zooming (10% to 2000%).
* Save images in different formats.
* Copy edited image to the clipboard.

## Installation

### Using The Installer Or Zip File

Installers and zips are Windows only at this time (excluding Windows 7).

#### Installer

1. Download the [Latest Installer](https://github.com/Dev-I-J/Clipboard2Image/releases/latest). The installer has the following file name: `Clipboard2Image_<version>_Installer.exe` (&lt;version&gt; is the version of Clipboard2Image you are installing)
2. Double click the installer file.
3. Proceed with the installer wizard as you waould normaly do with any program.

#### ZIP File

1. Download the [Latest Zip](https://github.com/Dev-I-J/Clipboard2Image/releases/latest). The zip file has the following file name: `Clipboard2Image_<version>.zip` (&lt;version&gt; is the version of Clipboard2Image you are installing)
2. Extract the image to a path you prefer ([7zip](https://www.7-zip.org) is recommended).
3. Navigate to the extraction path and double click `Clipboard2Image.exe`.

### Build From Source

This is the method to use Clipboard2Image on Linux and Mac.

1. Download **Python 3.9** from [python.org](https://www.python.org/downloads/release/python-392/). For Ubuntu, follow [this guide](https://phoenixnap.com/kb/how-to-install-python-3-ubuntu)
2. Clone project: `git clone https://github.com/Dev-I-J/Clipboard2Image.git && cd Clipboard2Image`
3. Install **pipenv**: `python3 -m pip install pipenv`.
4. Install required dependencies: `python3 -m pipenv install --dev`.
5. Build app with **PyInstaller**: `python3 -m PyInstaller Clipboard2Image.spec`.
6. Run app: `dist/Clipboard2Image/Clipboard2Image`.

## Documentation

Documentation for Clipboard2Image Is Available At It's [Wiki Page](https://github.com/Dev-I-J/Clipboard2Image/wiki).

## License

Clipboard2Image Is Licensed Under The [GNU GPL License](https://www.gnu.org/licenses/gpl-3.0.en.html).
