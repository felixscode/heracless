from distutils.core import setup

setup(
    name="Heracles",
    version="0.1",
    author="Felix Schelling",
    packages=["heracles"],
    url="http://pypi.python.org/pypi/Heracles/",
    license="LICENSE.txt",
    description="YAML Config Parser and Manager",
    long_description=open("README.txt").read(),
    install_requires=[
        "Django >= 1.1.1",
        "caldav == 0.1.4",
    ],
)
