from setuptools import setup, find_packages

setup(
    name = "strongchicken",
    version = "0.1",
    packages = find_packages("src"),
	package_dir = {'':'src'},
	install_requires = ['numpy>=1.0.0'],
)


