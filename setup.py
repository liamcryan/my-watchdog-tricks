from setuptools import setup, find_packages

setup(
    name='my-watchdog-tricks',
    description='learning how to use & apply watchdog',
    install_requires=['watchdog[watchmedo]', 'rever'],
    packages=find_packages()
)
