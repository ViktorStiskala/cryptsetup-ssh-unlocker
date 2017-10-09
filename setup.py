import os

import sys
from setuptools import setup
from unlocker import __version__

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

if sys.version_info[:2] < (3, 5):
    sys.exit('ssh-unlocker requires Python 3.5 or higher, sorry. Please consider using `pyenv` if your distribution does not provide Python 3.5+')

setup(
    name='ssh-unlocker',
    version=__version__,
    packages=['unlocker'],
    package_data={'unlocker': ['unlock.py', 'unlocker/*.py']},
    entry_points={
        'console_scripts': [
            'ssh-unlocker=unlock:main',
        ],
    },
    include_package_data=True,
    license='MIT',
    description='Django session sharing across multiple domains running same application',
    url='https://github.com/ViktorStiskala/cryptsetup-ssh-unlocker',
    author='Viktor Stískala',
    author_email='viktor@stiskala.cz',
    install_requires=['asyncssh>=1.11', 'bcrypt>=3.1'],
    classifiers=[
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Framework :: AsyncIO',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ],
)
