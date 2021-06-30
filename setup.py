#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# from distutils.core import setup
from setuptools import setup, find_packages
from tuya_iot import __version__

tests_require = []


def requirements():
    with open('requirements.txt', 'r') as fileobj:
        requirements = [line.strip() for line in fileobj]
        return requirements


with open("README.md", "r", encoding="utf-8") as fh:
    doc_long_description = fh.read()


setup(
    name='tuya-iot-py-sdk',
    url='https://github.com/tuya/tuya-iot-app-sdk-python',
    author="Tuya Inc.",
    author_email='developer@tuya.com',
    keywords='tuya iot app sdk python',
    long_description=doc_long_description,
    long_description_content_type="text/markdown",
    description='A Python sdk for Tuya Open API, which provides IoT capabilities, maintained by Tuya official',
    license='MIT',
    project_urls={
        "Bug Tracker": "https://github.com/tuya/tuya-iot-app-sdk-python/issues",
        "Changes": "https://github.com/tuya/tuya-iot-python-sdk/wiki/Tuya-IoT-Python-SDK-Release-Notes"
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],

    version=__version__,
    install_requires=requirements(),
    tests_require=tests_require,
    test_suite='runtests.runtests',
    extras_require={'test': tests_require},
    entry_points={'nose.plugins': []},
    packages=find_packages(),
    python_requires='>=3.0',

)
