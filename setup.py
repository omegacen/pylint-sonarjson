import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pylint-sonarjson",
    version="1.0.0",
    author="Teake Nutma",
    description="A PyLint plugin that can output to SonarQube-importable JSON",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/omegacen/pylint-sonarjson",
    packages=setuptools.find_packages(),
    license_file='LICENSE',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["pylint>=2.0"],
    package_dir={'': 'src'}
)
