from setuptools import find_packages
from setuptools import setup

with open("requirements.txt") as fp:
    requirements = fp.read()

setup(
    name="hubs-bot",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    tests_require=["pytest", "coverage"],
    cmdclass={},
)
