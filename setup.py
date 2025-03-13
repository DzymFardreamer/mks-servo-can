from setuptools import setup, find_packages

setup(
    name="mks-servo-can",
    version="0.2.2",
    packages=find_packages(include=["mks_servo_can"]),
    install_requires=["python-can"],
    # Optional metadata
    author="Dzym Fardreamer",
    author_email="anakinlokkin@gmail.com",
    description="This Python library provides an easy-to-use interface for communicating with MKS-Servo57D, MKS-Servo42D devices using the CAN protocol.",
    license="GNU-GPL",
    keywords="can mks servo",
    url="https://github.com/DzymFardreamer/mks-servo-can/",
)
