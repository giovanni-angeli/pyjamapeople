# coding: utf-8

# pylint: disable=missing-docstring
# pylint: disable=invalid-name

import os
import glob

from setuptools import setup, find_packages

__app_name__ = 'pyjamampeople'

def main():
    setup(
        name=__app_name__,
        version='0.0.1',
        description='example using asyncio, tornado and websocket together',
        url='',
        author='giovanni angeli',
        author_email='giovanni.angeli6@gmail.com',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python :: 3',
            "License :: OSI Approved :: MIT License",
            "Operating System :: POSIX :: Linux",
        ],
        packages=find_packages(where='src'),
        package_dir={'': 'src'},
        data_files=[
            ('templates', list(glob.glob('templates'))),
        ],
        include_package_data=True,
        scripts=[
            'bin/pyjamampeople',
        ],
        install_requires=[
            'tornado',
        ],
    )


if __name__ == '__main__':
    main()
