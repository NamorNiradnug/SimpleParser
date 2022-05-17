import setuptools

with open("README.md") as readme:
    long_description = readme.read()

setuptools.setup(
    name="simpleparser",
    version="0.1.3",
    author="NamorNiradnug",
    author_email="roma57linux@gmail.com",
    packages=["simpleparser"],
    tests_require=["test.py"],
    description="Simple library with simple parser which parses simple expressions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/NamorNiradnug/SimpleParser",
    project_urls={
        "Bug Tracker": "https://github.com/NamorNiradnug/SimpleParser/issues",
        "Source": "https://github.com/NamorNiradnug/SimpleParser",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7"
)
