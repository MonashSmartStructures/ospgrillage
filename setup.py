import os
from setuptools import setup, find_packages
from ospgrillage import __version__ as version


# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="osp-grillage",
    version=version,
    description=("A bridge deck grillage wrapper for OpenSeesPy"),
    license="MIT",
    keyword="bridge grillage openseespy",
    author="Monash Smart Structures",
    author_email="colin.caprani@monash.edu",
    url="https://monashsmartstructures.github.io/ospgrillage/",
    packages=find_packages(include=["ospgrillage"]),
    long_description=read("README.md"),
    classifiers=[
        "Development Status " " 3 - Alpha",
        "Topic :: Scientific/Engineering",
        "Programming Language :: Python",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=["openseespy", "xarray","opsvis","openseespyvis"],
    tests_require=["pytest"],
)
