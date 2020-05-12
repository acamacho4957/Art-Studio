## Table of Contents
* [lib](https://github.com/acamacho4957/Art-Studio/tree/master/lib)
  * [angry.mp3](https://github.com/acamacho4957/Art-Studio/blob/master/lib/angry.mp3) - music played for "Angry" emotion
  * [happy.mp3](https://github.com/acamacho4957/Art-Studio/blob/master/lib/happy.mp3) - music played for "Happy" emotion
  * [neutral.mp3](https://github.com/acamacho4957/Art-Studio/blob/master/lib/neutral.mp3) - music played for "Neutral" emotion, default
  * [main_image.png](https://github.com/acamacho4957/Art-Studio/blob/master/lib/main_image.png) - image on home screen
* [models](https://github.com/acamacho4957/Art-Studio/tree/master/models)
  * [emotion_model.h5](https://github.com/acamacho4957/Art-Studio/blob/master/models/emotion_model.h5) - default emotion recognition keras model
* [src](https://github.com/acamacho4957/Art-Studio/tree/master/src)
  * [pyleap](https://github.com/acamacho4957/Art-Studio/tree/master/src/pyleap) - python3 support for leap motion controller, [original source](https://github.com/eranegozy/pyleap)
  * [main.py](https://github.com/acamacho4957/Art-Studio/blob/master/src/main.py) - source code for application
* [training_data](https://github.com/acamacho4957/Art-Studio/tree/master/training_data) - folder to store the captured training images, contains an empty text file to create this directory
* [README.md](https://github.com/acamacho4957/Art-Studio/blob/master/README.md) - readme file
* [requirements.txt](https://github.com/acamacho4957/Art-Studio/blob/master/requirements.txt) - necessary packages
  
## Requirements
* [Python 3.6.0 or greater](https://www.python.org/downloads/release/python-3610/)
* [Microsoft C++ Build Tools 14.0 or greater](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
* [Leap Motion Controller SDK V2](https://developer.leapmotion.com/setup/desktop)
  * For Windows 10 users, be sure to apply the neccessary fix from the [Leap forums](https://forums.leapmotion.com/t/resolved-windows-10-fall-creators-update-bugfix/6585).
* [Ghostscript](https://www.ghostscript.com/download/gsdnld.html)
  * Once installed, make sure that `C:\Program Files\gs\gs9.52\bin\` is added to the PATH environment variable. Then, a restart is necessary. NOTE: This is only necessary if you want to save a drawing as a JPG image.

## Install
1. Clone repo and cd into the "Art-Studio" directory.

```
git clone https://github.com/acamacho4957/Art-Studio.git
cd Art-Studio
```

2. Create a virtual environment.
```
py -m venv venv
```
3. Upgrade pip.
```
py -m pip install -U pip
```
4. Activate the virtual environment.
```
venv\Scripts\activate.bat
```
5. Install the required packages.
```
pip install -r requirements.txt
```
## Run
```
py src\main.py
```
