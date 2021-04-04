# Optimize Images X
A desktop app written in Python, that unlocks the power of [Optimize Images](https://github.com/victordomingos/optimize-images) in a graphical user interface, to help you reduce the file size of images.

Like Optimize Images, this application is intended to be almost pure Python, with no special dependencies
besides Pillow, therefore ensuring compatibility with a wide range of environments. If you don't have the need
for such a strict dependency management, you may eventually be better served by any several other image optimization utilities that are based on some well known external binaries. You may find, however, that Optimize Images X and its CLI companion offer some useful features that are not always present in a single package, like batch downsizing of images within a folder (and recursively though its subfolders) based on specified maximum width and/or height.


## Full Documentation:
 * [English](https://github.com/victordomingos/optimize-images-x/blob/main/docs/docs_EN.md)
 * [Portugu&ecirc;s](https://github.com/victordomingos/optimize-images-x/blob/main/docs/docs_PT.md)

Please refer to the above links if you want to know about all the options available in this application. For a quick intro, just to get a feeling of what it can do, please keep reading below.

## Installation and dependencies:

To install and run this application, you need to have a working
Python 3.7+ installation. We try to keep the external dependencies at a minimum, in order to keep compatibility with different  environments. At this moment, we require:

  - optimize-images>=1.4.0
  - Pillow>=8.0.1
  - piexif>=1.1.3

The easiest way to install it in a single step, including any dependencies, is 
by using this command:

-- TODO --

If you are able to swap Pillow with the faster version 
[Pillow-SIMD](https://github.com/uploadcare/pillow-simd), you should be able
to get a considerably faster speed. For that reason, we provide, as a 
friendly courtesy, an optional shell script (`replace_pillow__macOS.sh`) to 
replace Pillow with the faster Pillow-SIMD on macOS. Please notice, however, 
that it usually requires a compilation step and it was not throughly tested 
by us, so your mileage may vary.


## How to use

-- TODO --


**DISCLAIMER:  
Please note that the operation is done DESTRUCTIVELY, by replacing the
original files with the processed ones. You definitely should duplicate the
source file or folder before using this utility, in order to be able to
recover any eventual damaged files or any resulting images that don't have the
desired quality.**
  
  
## Did you find a bug or do you have a suggestion?

Please let me know, by opening a new issue or a pull request.
