from setuptools import find_packages, setup

setup(
    name="life_dashboard",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "django>=5.0.2",
        "pytest>=8.0.2",
        "pytest-django>=4.8.0",
        "selenium>=4.18.1",
    ],
)
