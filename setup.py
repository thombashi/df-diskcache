import os.path
from typing import Dict, Final, List, Type

import setuptools


MODULE_NAME: Final = "project_name"
OWNER: Final = "thombashi"
REPOSITORY_URL: Final = f"https://github.com/{OWNER}/{MODULE_NAME}"
REQUIREMENT_DIR: Final = "requirements"
ENCODING: Final = "utf8"

pkg_info: Dict[str, str] = {}


def get_release_command_class() -> Dict[str, Type[setuptools.Command]]:
    try:
        from releasecmd import ReleaseCommand
    except ImportError:
        return {}

    return {"release": ReleaseCommand}


with open(os.path.join(MODULE_NAME.replace("-", "_"), "__version__.py")) as f:
    exec(f.read(), pkg_info)

with open("README.rst", encoding=ENCODING) as f:
    LONG_DESCRIPTION: Final = f.read()

with open(os.path.join(REQUIREMENT_DIR, "requirements.txt")) as f:
    INSTALL_REQUIRES: Final[List[str]] = [line.strip() for line in f if line.strip()]

with open(os.path.join(REQUIREMENT_DIR, "test_requirements.txt")) as f:
    TESTS_REQUIRES: Final[List[str]] = [line.strip() for line in f if line.strip()]

setuptools.setup(
    name=MODULE_NAME,
    version=pkg_info["__version__"],
    url=REPOSITORY_URL,
    author=pkg_info["__author__"],
    author_email=pkg_info["__email__"],
    description="DESCRIPTION",
    include_package_data=True,
    keywords=["library"],
    license=pkg_info["__license__"],
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/x-rst",
    packages=setuptools.find_packages(exclude=["tests*"]),
    package_data={MODULE_NAME: ["py.typed"]},
    project_urls={
        "Changlog": f"{REPOSITORY_URL:s}/releases",
        "Source": REPOSITORY_URL,
        "Tracker": f"{REPOSITORY_URL:s}/issues",
    },
    python_requires=">=3.8",
    install_requires=INSTALL_REQUIRES,
    extras_require={"test": TESTS_REQUIRES},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    cmdclass=get_release_command_class(),
    zip_safe=False,
)
