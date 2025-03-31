from setuptools import setup, find_packages

setup(
    name="python-cli-crawler",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "aiohttp",
        "selenium",
        "textblob",
        "opencv-python",
        "numpy",
        "spacy",
        "transformers",
        "gensim",
        "nltk",
        "watchdog"
    ],
    entry_points={
        "console_scripts": [
            "python-cli-crawler=main:main"
        ]
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A powerful, extensible Python CLI crawler with dynamic plugin management",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.8",
)
