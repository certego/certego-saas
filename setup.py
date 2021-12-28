"""
# certego-saas
"""
from pathlib import Path
from setuptools import setup, find_packages

# constants
GITHUB_URL = "https://github.com/certego/certego-saas"

# The directory containing this file
HERE = Path(__file__).parent
# The text of the README file
README = (HERE / "README.md").read_text()
# Define requirements
requirements = (HERE / "requirements.txt").read_text().split("\n")
requirements_dev = (HERE / "requirements.dev.txt").read_text().split("\n")
# read version
version_contents = {}
with open((HERE / "certego_saas" / "version.py"), encoding="utf-8") as f:
    exec(f.read(), version_contents)

setup(
    name="certego_saas",
    version=version_contents["VERSION"],
    author="Certego S.R.L",
    url=GITHUB_URL,
    license="GNU AGPL v3.0",
    description="Certego SaaS",
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    python_requires=">=3.6",
    include_package_data=True,
    install_requires=requirements,
    dependency_links=[
        "https://github.com/eshaan7/django-rest-durin/archive/dev-sessions-19.tar.gz",
    ],
    project_urls={
        "Documentation": GITHUB_URL,
        "Source": GITHUB_URL,
        "Tracker": f"{GITHUB_URL}/issues",
    },
    keywords="certego django rest framework saas",
    extras_require={
        "dev": requirements + requirements_dev,
    },
)
