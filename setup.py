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
    'gpiod>=2.2.4',
]

setup(
    name='powerrelay',
    version='0.2.0',
    description="REST API to control power relays.",
    long_description=readme + '\n\n' + history,
    author="Rasmus Villemoes",
    author_email='ravi@prevas.dk',
    url='https://github.com/prevas-dk/labgrid-powerrelay',
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
    data_files=[('/etc/powerrelay/',['config.yaml'])],
)
