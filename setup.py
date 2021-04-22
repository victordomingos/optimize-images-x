# encoding: utf-8
import os
import sys

from setuptools import setup, find_packages

used = sys.version_info
required = (3, 9)

if used[:2] < required:
    msg = f'Unsupported Python version: ' \
          f'{sys.version_info.major}.{sys.version_info.minor}. ' \
          f'Python 3.9 or later is required.'

    sys.stderr.write(msg)
    sys.exit(1)

short_desc = "A desktop app written in Python, that exposes and unlocks the " \
             "full power of Optimize Images in a nice graphical user interface, " \
             "to help you reduce the file size of images."


def read_readme(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name)) as f:
        return f.read()


setup(name='optimize-images-x',
      version=__import__('optimize_images_x').__version__,
      description=short_desc,
      author="Victor Domingos",
      packages=find_packages(),
      include_package_data=True,
      long_description=read_readme('README.md'),  # for PyPI
      long_description_content_type="text/markdown",
      license='MIT',
      url='https://no-title.victordomingos.com/projects/optimize-images-x/',
      project_urls={
          'Documentation': 'https://github.com/victordomingos/optimize-images-x/',
          'Source': 'https://github.com/victordomingos/optimize-images-x',
          'Bug Reports': 'https://github.com/victordomingos/optimize-images-x/issues',
      },
      python_requires='>=3.9',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: MacOS X',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: Unix',
          'Operating System :: POSIX :: Linux ',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.9',
          'Topic :: Utilities',
          'Topic :: Multimedia :: Graphics',
          'Topic :: Multimedia :: Graphics :: Graphics Conversion',
      ],

      keywords='python3 pythonista-ios pil pillow image-processing ' \
               'image-compression image-optimization image-optimisation seo '
               'seo-optimization website-performance gui recursive non-recursive',

      install_requires=[
          'optimize-images>=1.4.0',
          'pillow>=8.2.0',
          'piexif>=1.1.3',
          'watchdog>=2.0.2'
      ],

      entry_points={
          'console_scripts': ['optimize-images-x = optimize_images_x.__main__:main']
      },
      )
