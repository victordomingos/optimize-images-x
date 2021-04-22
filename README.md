# Optimize Images X [![Github commits (since latest release)](https://img.shields.io/github/commits-since/victordomingos/optimize-images-x/latest.svg)](https://github.com/victordomingos/optimize-images-x) ![PyPI](https://img.shields.io/pypi/v/optimize-images-x) ![PyPI - Downloads](https://img.shields.io/pypi/dm/optimize-images-x)
A desktop app written in Python, that exposes and unlocks the full power of 
[Optimize Images](https://github.com/victordomingos/optimize-images) in a nice 
graphical user interface, to help you reduce the file size of images.

![Optimize Images X - Main Window](screenshots/optimize-images-x_main-window.png)

Optimize Images X and its CLI companion `optimize-images` offer some useful 
features that are not always present in a single package, like batch downsizing 
of images within a folder (and recursively though its 
subfolders) based on specified maximum width and/or height.

If you were just looking for the original (and slightly faster) command-line 
user interface (CLI) version of this application, it's a separate project: 
[Optimize Images](https://github.com/victordomingos/optimize-images). 

## Installation and dependencies:

To install and run this application, you need to have a working
Python 3.9+ installation. We try to keep the external dependencies at a minimum, 
in order to keep compatibility with different  environments. At this moment, we 
require:

  - optimize-images>=1.4.0
  - Pillow>=8.0.1
  - piexif>=1.1.3
  - watchdog>=2.0.2
  

If you are able to swap Pillow with the faster version 
[Pillow-SIMD](https://github.com/uploadcare/pillow-simd), you should be able
to get a considerably faster speed. For that reason, we provide, as a 
friendly courtesy, an optional shell script (`replace_pillow__macOS.sh`) to 
replace Pillow with the faster Pillow-SIMD on macOS. Please notice, however, 
that it usually requires a compilation step, and it was not throughly tested 
by us, so your mileage may vary.


## How to use

To start compressing images, just add one or more files, or a folder. The 
process starts as soon as the files are added to the list.

After launching the application for the first time, make sure all settings are 
configured as desired. The application's default settings are similar to the 
ones in Optimize Images. Whenever you change a setting it is applied 
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
![Optimize Images X - Preferences Window: General](screenshots/optimize-images-x_prefs_general.jpg)

### JPEG specific preferences
![Optimize Images X - Preferences Window: General](screenshots/optimize-images-x_prefs_jpeg.jpg)

### PNG specific preferences
![Optimize Images X - Preferences Window: General](screenshots/optimize-images-x_prefs_png.jpg)


**DISCLAIMER:  
Please note that the operation is done DESTRUCTIVELY, by replacing the
original files with the processed ones. You definitely should duplicate the
source file or folder before using this utility, in order to be able to
recover any eventual damaged files or any resulting images that don't have the
desired quality.**
  
  
## Did you find a bug or do you have a suggestion?

Please let me know, by opening a new issue, or a pull request.
