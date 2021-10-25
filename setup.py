import os
from setuptools import setup, find_packages
from ospgrillage import __version__ as version


# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="osp-grillage",
    version=version,
    description=("Bridge deck grillage analysis using OpenSeesPy"),
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
    install_requires=[
        "matplotlib",
        "numpy",
        "openseespy>=3.2.2.6",
        "opsvis~=0.95.5",
        "openseespyvis>=0.0.6",
        "pandas",
        "pytest>=6.1.1",
        "scipy>=1.5.2",
        "xarray>=0.18.2",
        "setuptools~=49.2.1",
    ],
    tests_require=["pytest"],
)
