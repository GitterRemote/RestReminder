from setuptools import setup, find_packages
from os import path
from io import open


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="RestReminder",
    version="1.0.0",
    description="Reminds you when too long surfing Internet.",
    long_description=long_description,
    author="shuaihu.wang",
    author_email="shuaihu.w@gmail.com",
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    include_package_data=True,
    # package_data={"slots_helper.slots_mania": ["bin/*"]},
    install_requires=["pynput", "fire"],
    extras_require={  # Optional
        "dev": ["pytest", "fire"],
        "test": ["pytest"]
    },
    entry_points={
        "console_scripts": [
            "rreminder=rest_reminder:main"
        ],
    },
    classifiers=[
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7"
    ]
)
