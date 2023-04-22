from distutils.core import setup

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name="tklinenums",
    version="1.6.5",
    description="A simple Tkinter widget for displaying line numbers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Moosems",
    author_email="moosems.j@gmail.com",
    url="https://github.com/Moosems/TkLineNums",
    packages=["tklinenums"],
)
