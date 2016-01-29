from setuptools import setup, find_packages

with open('README.rst', 'r') as readme:
    readme = readme.read()

setup(
    name = "beekeeper",
    version = "0.7",
    packages = ['beekeeper'],
    author = "Jesse Shapiro",
    author_email = "jesse@bedrockdata.com",
    long_description = readme
    keywords = "REST API web client wrapper",
    url = "https://github.com/haikuginger/beekeeper",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities"
    ]
)