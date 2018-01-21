#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'aiohttp>=2.3.6',
    'trafaret>=0.12.0',
]

setup_requirements = [
    'pytest-runner>=3.0',
]

test_requirements = [
    'pytest>=3.3.1',
]

setup(
    name='powerrelay',
    version='0.1.0',
    description="REST API to control power relays.",
    long_description=readme + '\n\n' + history,
    author="Henrik Nymann Jensen",
    author_email='hnje@prevas.dk',
    url='https://github.com/prevas-hnje/powerrelay',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'powerrelay=powerrelay.main:powerrelay'
        ]
    },
    python_requires='>=3.5.0',
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='powerrelay',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    data_files=[('/etc/',['config.yaml'])],
    package_data={'powerrelay.views': ['*.j2']},
)
