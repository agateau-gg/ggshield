import io
import os
import re
import subprocess
from typing import Any

from setuptools import find_packages, setup


VERSION_RE = re.compile(r"__version__\s*=\s*\"(.*?)\"")
GIT_DESCRIBE_RE = re.compile(r"^v\d+\.\d+\.\d+-(\d+)-g([0-9a-fA-F]+)$")
HERE = os.path.abspath(os.path.dirname(__file__))


def read(*args: Any) -> str:
    """Reads complete file contents."""
    return str(io.open(os.path.join(HERE, *args), encoding="utf-8").read())


def get_version() -> str:
    """Reads the version from this module."""
    init = read("ggshield", "__init__.py")
    match = VERSION_RE.search(init)
    assert match
    version = match.group(1)

    if os.path.exists(os.path.join(HERE, ".git")):
        # `git describe` output is <tag>-<n_commits>-g<sha>, unless we are on a tag, in
        # which case the output is just <tag>.
        # If we are not on a tag, then add <n_commits> and <sha> to the version number
        # so that users installing from git know which version they are running.
        out = (
            subprocess.check_output(["git", "describe"], cwd=HERE)
            .strip()
            .decode("utf-8")
        )
        match = GIT_DESCRIBE_RE.match(out)
        if match:
            n_commits, sha = match.groups()
            version = f"{version}+{n_commits}.{sha}"
    return version


setup(
    name="ggshield",
    version=get_version(),
    packages=find_packages(exclude=["tests"]),
    description="Detect secrets from all sources using GitGuardian's brains",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/GitGuardian/ggshield",
    author="GitGuardian",
    author_email="support@gitguardian.com",
    maintainer="GitGuardian",
    entry_points={"console_scripts": ["ggshield=ggshield.cmd.main:main"]},
    install_requires=[
        "appdirs>=1.4.4,<1.5.0",
        "click>=8.0,<8.1",
        "oauthlib>=3.2,<3.3",
        "marshmallow>=3.15.0,<3.16.0",
        "marshmallow-dataclass>=8.5.8,<8.6.0",
        "pygitguardian>=1.3.4,<1.4.0",
        "python-dotenv>=0.19.1,<0.20.0",
        "pyyaml>=6.0,<6.1",
    ],
    include_package_data=True,
    zip_safe=True,
    license="MIT",
    keywords="cli devsecops secrets-detection security-tools gitguardian",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Topic :: Security",
    ],
)
