from setuptools import setup, find_packages

setup(
    name='mks_servo_can',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        "python-can"
    ],
    # Optional metadata
    author='Dzym Fardreamer',
    author_email='anakinlokkin@gmail.com',
    description='This Python library provides an easy-to-use interface for communicating with MKS-Servo57D, MKS-Servo42D devices using the CAN protocol.',
    license='GNU-GPL',
    keywords='can mks servo',
    url='https://github.com/DzymFardreamer/mks-servo-can/',
)