from setuptools import setup, find_packages

setup(
    name="blackjack-simulator",
    version="1.0.0",
    author="VijayKumaro7",
    description="Monte Carlo blackjack simulator with strategy and card counting",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/VijayKumaro7/blackjack-simulator",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[],
    extras_require={
        "analysis": ["matplotlib>=3.7", "numpy>=1.24", "jupyter>=1.0"],
        "dev":      ["pytest>=7.4", "pytest-cov>=4.1"],
    },
    entry_points={
        "console_scripts": [
            "blackjack-sim=main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
)
