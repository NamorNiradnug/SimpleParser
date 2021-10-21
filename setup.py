import setuptools

setuptools.setup(
    name="simple-parser",
<<<<<<< HEAD
    version="0.1.1",
    author="NamorNiradnug",
    author_email="roma57linux@gmail.com",
    packages=["simpleparser"],
=======
    version="0.1",
    author="NamorNiradnug",
    author_email="roma57linux@gmail.com",
    packages=["parser"],
>>>>>>> origin/main
    tests_require=["test.py"],
    description="Simple library with simple parser which parses simple expressions.",
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
