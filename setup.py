from setuptools import find_packages, setup

setup(
    name="life_dashboard",
    version="0.1",
    author="Nigel",
    author_email="nigel@example.com",
    description="A personal dashboard for tracking life stats, quests, and habits.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/life_dashboard",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "django>=5.0.2",
        "pytest>=8.0.2",
        "pytest-django>=4.8.0",
        "selenium>=4.18.1",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 5.0",
    ],
    python_requires=">=3.8",
)
