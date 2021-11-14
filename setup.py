from setuptools import setup
import re
import sys

versionInfo = sys.version_info

if (versionInfo.major < 3) and (versionInfo.minor < 8):
    sys.exit('Cannot install ACord on python version below 3.8, Please upgrade!')

version = ""

with open("acord/__init__.py") as f:
    contents = f.read()

    _match = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', contents, re.MULTILINE
    )

    version = _match.group(1)

if not version:
    raise RuntimeError("Cannot resolve version")


classifiers = [
    "Development Status :: 1 - Planning",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "License :: OSI Approved :: GNU License",
    
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: 3",
]

packages = [
    "acord",
    "acord.core",
]

setup(
    name="ACord",
    version=version,
    description="An object orientated math library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Mecha-Karen/acord",
    project_urls={
        "Documentation": "https://docs.mechakaren.xyz/acord",
        "Issue tracker": "https://github.com/Mecha-Karen/acord/issues",
        "Organisation": "https://github.com/Mecha-Karen",
    },
    author="Mecha Karen",
    author_email="admin@mechakaren.xyz",
    license="GNU License",
    classifiers=classifiers,
    packages=packages,
    install_requires=["aiohttp", "pydantic"],
)