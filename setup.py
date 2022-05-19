setup(
    name="mtgio-gui",
    version="0.01",
    description="Program that visually displays information from the mtgio.com API",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/GickiAnarchy/mtgio",
    author="GickiAnarchy,
    author_email="fatheranarchy@programmer.net",
    license="None",
    packages=["mtgio"],
    include_package_data=True,
    install_requires=[
        "mtgsdk", "PySimpleGUI", "pillow"
    ],
)
