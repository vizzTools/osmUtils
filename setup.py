import pathlib
import setuptools

# The directory containing this file
HERE = pathlib.Path(__file__).parent
with open('README.md', 'r') as fh:
    README = fh.read()

# # The text of the README file
# README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setuptools.setup(
    name="osmUtils",
    version="0.0.1",
    description="Provides library functions to interface overpass API",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/vizzTools/osmUtils",
    author="Elena Palao",
    author_email="elena.palao@vizzuality.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    packages=['osmUtils'],
    install_requires=['requests>=2.2.0', 'folium==0.8.3'],
    entry_points={
        "console_scripts": [
            "vizzpython=osmUtils.__main__:main",
        ]
    },
)
