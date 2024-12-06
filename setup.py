from setuptools import setup, find_packages

setup(
    name="skyarclog",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "python-json-logger",
        "azure-storage-blob",
        "opencensus",
        "opencensus-ext-azure",
    ],
    python_requires=">=3.8",
)
