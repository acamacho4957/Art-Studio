## Requirements
* [Python 3.6.0 or greater](https://www.python.org/downloads/release/python-3610/)
* [Microsoft C++ Build Tools 14.0 or greater](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
* [Leap Motion Controller SDK V2](https://developer.leapmotion.com/setup/desktop)
  * For Windows 10 users, be sure to apply the neccessary fix from the [Leap forums](https://forums.leapmotion.com/t/resolved-windows-10-fall-creators-update-bugfix/6585).
* [Ghostscript](https://www.ghostscript.com/download/gsdnld.html)
  * Once installed, make sure that `C:\Program Files\gs\gs9.52\bin\` is added to the PATH environment variable. Then, a restart is necessary.

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
