"""
Setup configuration for Retail Price Intelligence System.
"""
from setuptools import setup, find_packages
from pathlib import Path

readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, encoding="utf-8") as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="retail-price-intelligence",
    version="1.0.0",
    description="A comprehensive system for scraping, tracking, and analyzing product prices across multiple e-commerce websites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rafael Race",
    author_email="rhaprace@gmail.com",
    url="https://github.com/rhaprace/retail-price-intelligence-system",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.8",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Office/Business :: Financial",
    ],
    entry_points={
        "console_scripts": [
            "rpi-api=run_api:main",
            "rpi-pipeline=pipeline.runner:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

