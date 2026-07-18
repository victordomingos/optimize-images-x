# encoding: utf-8
import os
import re
import sys

from setuptools import setup
from setuptools.command.sdist import sdist


class CustomSdist(sdist):
    """Custom sdist command to ensure locale data is included."""

    def run(self):
        # Compile .po files to .mo before creating the distribution
        self.run_command('compile_catalog')
        super().run()


used = sys.version_info
required = (3, 10)

if used[:2] < required:
    msg = f'Unsupported Python version: ' \
          f'{sys.version_info.major}.{sys.version_info.minor}. ' \
          f'Python 3.10 or later is required.'

    sys.stderr.write(msg)
    sys.exit(1)

short_desc = "A desktop app written in Python, that exposes and unlocks the " \
             "full power of Optimize Images in a nice graphical user interface, " \
             "to help you reduce the file size of images."


def read_readme(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name)) as f:
        return f.read()


def read_version():
    # Parsed from source rather than imported: under an isolated PEP 517
    # build, the working directory isn't guaranteed to be on sys.path, so
    # `__import__('optimize_images_x')` can raise ModuleNotFoundError.
    init_path = os.path.join(os.path.dirname(__file__),
                             'optimize_images_x', '__init__.py')
    with open(init_path) as f:
        match = re.search(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]", f.read(), re.M)
    return match.group(1)


setup(name='optimize-images-x',
      version=read_version(),
      description=short_desc,
      author="Victor Domingos",
      cmdclass={'sdist': CustomSdist},
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
      python_requires='>=3.10',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: MacOS X',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: Unix',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Programming Language :: Python :: 3.13',
          'Programming Language :: Python :: 3.14',
          'Programming Language :: Python :: 3.15',
          'Programming Language :: Python :: Free Threading',
          'Topic :: Utilities',
          'Topic :: Multimedia :: Graphics',
          'Topic :: Multimedia :: Graphics :: Graphics Conversion',
      ],

      keywords='python3 pythonista-ios pil pillow image-processing ' \
               'image-compression image-optimization image-optimisation seo '
               'seo-optimization website-performance gui recursive non-recursive',

      install_requires=[
          'optimize-images>=2.1.0,<2.2.0',
      ],

      extras_require={
          'dnd': ['tkinterdnd2'],
          # Only needed to run `setup.py extract_messages` / `compile_catalog`
          # by hand during translation work; release builds get Babel from
          # pyproject.toml's build-system requirements instead.
          'dev': ['Babel>=2.9.0'],
      },

      entry_points={
          'console_scripts': ['optimize-images-x = optimize_images_x.__main__:main']
      },
      )
