from setuptools import setup, find_packages

setup(
    name="web_scanner",
    version="0.1.0",
    description="A web application security scanner",
    author="Harshwardhan Patil",
    author_email="harshwardhanp49@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "flask",
        # ... other dependencies
    ],
    entry_points={
        'console_scripts': [
            'web-scanner=web_scanner.ui.app:main',
        ],
    }
)
