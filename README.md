# Optimize Images X
[![Github commits (since latest release)](https://img.shields.io/github/commits-since/victordomingos/optimize-images-x/latest.svg)](https://github.com/victordomingos/optimize-images-x) ![PyPI](https://img.shields.io/pypi/v/optimize-images-x)  [![PyPI Python Versions](https://img.shields.io/pypi/pyversions/optimize-images-x.svg)](https://pypi.org/project/optimize-images-x/)  ![https://badgen.net/github/contributors/victordomingos/optimize-images-x](https://badgen.net/github/contributors/victordomingos/optimize-images-x) [![PyPI Downloads](https://static.pepy.tech/personalized-badge/optimize-images-x?period=monthly&units=NONE&left_color=GREY&right_color=ORANGE&left_text=monthly+downloads)](https://pepy.tech/projects/optimize-images-x) [![GitHub License](https://img.shields.io/github/license/victordomingos/optimize-images-x.svg)](https://github.com/victordomingos/optimize-images-x/blob/master/LICENSE) 

A desktop app written in Python, that exposes and unlocks the full power of 
[Optimize Images](https://github.com/victordomingos/optimize-images) in a nice 
graphical user interface, to help you reduce the file size of images.

![Optimize Images X - Main Window](https://github.com/victordomingos/optimize-images-x/blob/main/screenshots/optimize-images-x_main-window.png?raw=true)

Optimize Images X and its CLI companion `optimize-images` offer some useful 
features that are not always present in a single package, like batch downsizing 
of images within a folder (and recursively though its 
subfolders) based on specified maximum width and/or height.

If you were just looking for the original (and slightly faster) command-line 
user interface (CLI) version of this application, it's a separate project: 
[Optimize Images](https://github.com/victordomingos/optimize-images). 

## Installation and dependencies:

To install and run this application, you need to have a working
Python 3.10+ installation. We try to keep the external dependencies at a minimum, 
in order to keep compatibility with different environments. At this moment, we 
require:

  - optimize-images==2.0.0

This single dependency is installed automatically when you install Optimize 
Images X and will also fetch Pillow and other dependencies.

There are a few ways to install Optimize Images X. The simplest, if you don't
use Python yourself, is to download a prebuilt application from the project's
[GitHub releases](https://github.com/victordomingos/optimize-images-x/releases)
page, when available for your system.

If you have Python on your system, you can also install the most recent release
from the PyPI repository using `pip`:

```
python3 -m pip install optimize-images-x
```

It can be a good idea to keep this kind of Python app isolated in its own
virtual environment. Two convenient third-party tools for that are
[pipx](https://pypa.github.io/pipx) and [uv](https://docs.astral.sh/uv/).
Instead of the command indicated above, you could then use one of these:

```
pipx install optimize-images-x
```

```
uv tool install optimize-images-x
```

After that, to run the application, just type `optimize-images-x` in the 
Terminal and press `Enter`.

Please note that, being a graphical application, Optimize Images X needs a
Python installation that includes Tcl/Tk support. This is normally the case for
the official Python distributions and most system packages. If you let a tool
manage and download its own Python for you and the window fails to open, that
particular build may be missing Tcl/Tk; in that case, install it against a
Python that includes it.


## How to use

To start compressing images, just add one or more files, or a folder. The 
process starts as soon as the files are added to the list.

After launching the application for the first time, make sure all settings are 
configured as desired. The application's default settings are similar to the 
ones in Optimize Images. Whenever you change a setting, it is applied 
immediately, and it's saved in the app's database, so that it will be can be 
used again the next time you run the app, without any need to go through all the 
settings. 

In simple terms, always make sure you have configured Optimize Images X as you 
want it, but if you just want to use the same settings from last time, just add 
images.

## Preferences

If you have used Optimize Images before, you probably already know what options 
are available. If not, please take a few minutes to take a look at the 
Preferences window and its tabs. You will find a description of each option on 
the original documentation for the command-line based Optimize Images. 

### General preferences
![Optimize Images X - Preferences Window: General](https://github.com/victordomingos/optimize-images-x/raw/main/screenshots/optimize-images-x_prefs_general.png)

### JPEG specific preferences
![Optimize Images X - Preferences Window: General](https://github.com/victordomingos/optimize-images-x/raw/main/screenshots/optimize-images-x_prefs_jpeg.png)

### PNG specific preferences
![Optimize Images X - Preferences Window: General](https://github.com/victordomingos/optimize-images-x/raw/main/screenshots/optimize-images-x_prefs_png.png)


### More options
![Optimize Images X - Preferences Window: General](https://github.com/victordomingos/optimize-images-x/raw/main/screenshots/optimize-images-x_prefs_more.png)


#### User interface options

You can choose the graphical user interface theme in the `More…` tab of the 
Settings Window. The list of available themes will vary depending on your 
operating system, as well as Python and TK/tcl versions. Just click each one of 
the radio buttons, and it will be appplied immediately as you click.


#### Restoring default settings

One important feature of Optimize Images X is its opinionated choice of default 
app and task settings, which have been defined with the web in mind and are 
probably just fine when you just want to apply some compression to the final 
images to be deployed with your website. So, being able to restore them is also 
possible. You will find the `Reset all settings` button in the `More…` tab of 
the Settings Window. 

Restoring default settings requires that the application is restarted, which is 
done automatically. So, before resetting, you should make sure you there are no 
more tasks pending or being processed.

Its worth noting that this process will also reset previous choices regarding 
confirmation dialog boxes, so they will be shown up again even if you had chosen 
not to see them.

**DISCLAIMER:  
Please note that the operation is done DESTRUCTIVELY, by replacing the
original files with the processed ones. You definitely should duplicate the
source file or folder before using this utility, in order to be able to
recover any eventual damaged files or any resulting images that don't have the
desired quality.**
  
  
## Building a standalone application

If you would like to build a standalone, double-clickable application (a `.app`
on macOS, an `.exe` on Windows, or an executable on Linux), you can do so with
[PyInstaller](https://pyinstaller.org). The repository includes a ready-to-use
build recipe, `optimize-images-x.spec`.

A couple of things to know before you start. PyInstaller is not a
cross-compiler, so you need to run the build on the same kind of system you are
targeting: build the macOS app on a Mac, the Windows executable on Windows, and
so on. Also, at the time of writing, PyInstaller does not yet support Python
3.15, so the build should be done with a supported version (for example, the
standard, GIL-enabled Python 3.14). This does not affect which Python you use
for everyday development; it only matters for the build.

It is a good idea to use a dedicated virtual environment for building:

```
python3.14 -m venv venv-build
source venv-build/bin/activate
pip install .
pip install pyinstaller
python -m PyInstaller optimize-images-x.spec
```

On Windows, activate the environment with `venv-build\Scripts\activate`
instead.

The result is placed in the `dist` folder: on macOS you get
`dist/Optimize Images X.app`, and on Windows and Linux you get a folder
containing the executable. The `build` and `dist` folders are build artifacts
and are not meant to be committed to the repository.

The application currently ships without a custom icon; you can add one by
editing the `icon` entries near the top of `optimize-images-x.spec` (use a
`.icns` file on macOS and a `.ico` file on Windows).


## Did you find a bug or do you have a suggestion?

Please let me know, by opening a new issue, or a pull request.