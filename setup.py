from distutils.core import setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="heraclesss",
    version="0.1",
    author="Felix Schelling",
    packages=["heraclesss"],
    url="http://pypi.python.org/pypi/heraclesss/",
    license="LICENSE.txt",
    description="YAML Config Parser and Manager",
    long_description=open("README.txt").read(),
    install_requires=requirements,
)
