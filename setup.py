from setuptools import setup
import re
import sys
import os
import platform

version_info = sys.version_info
sys_arch = platform.architecture()[0]
u_sys = platform.system()

if (version_info.major < 3) and (version_info.minor < 8):
    sys.exit("Cannot install ACord on python version below 3.8, Please upgrade!")

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
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: 3",
]

packages = [
    "acord",
    "acord.bases",
    "acord.bases.flags",
    "acord.bases.enums",
    "acord.client",
    "acord.client.caches",
    "acord.core",
    "acord.core.signals",
    "acord.models",
    "acord.models.channels",
    "acord.webhooks",
    "acord.voice",
    "acord.voice.transports",
    "acord.ext",
    "acord.ext.application_commands",
    "acord.rest",
]

extra_requires = {
    "speedup": ["orjson>=3.5.4", "aiodns>=1.1", "brotli", "cchardet"],
    "voice": ["pynacl", "git+https://github.com/TeamPyOgg/PyOgg"],
}
# Using git+ for pyogg PyPi doesn't seem to install correct version

if not os.name == "nt":
    extra_requires["speedup"].append("uvloop")

try:
    import wheel
except ImportError:
    # Wheel lib needed for binaries
    extra_requires["voice"].append("wheel")

if sys_arch == "32bit":
    package_data = ["bin/libopus-0.x86.dll"]
else:
    package_data = ["bin/libopus-0.x64.dll"]
ZIP_SAFE = False

setup(
    name="ACord",
    version=version,
    description="An API wrapper for discord",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Mecha-Karen/acord",
    project_urls={
        "Documentation": "https://acord.rtfd.io",
        "Issue tracker": "https://github.com/Mecha-Karen/acord/issues",
        "Organisation": "https://github.com/Mecha-Karen",
    },
    author="Mecha Karen",
    author_email="admin@mechakaren.xyz",
    license="GNU License",
    classifiers=classifiers,
    packages=packages,
    package_data={
        "acord": package_data
    },
    zip_safe=ZIP_SAFE,
    install_requires=["aiohttp", "pydantic"],
    extra_requires=extra_requires,
)
