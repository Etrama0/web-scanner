from setuptools import setup, find_packages

setup(
    name="websecurity-scanner",
    version="0.1.0",
    description="A web application security scanner",
    author="Security Team",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt").readlines()
    ],
    entry_points={
        'console_scripts': [
            'webscan=src.main:main',
        ],
    },
    python_requires=">=3.7",
    include_package_data=True,
    package_data={
        'src': [
            'config/*.yaml',
            'templates/*.html',
            'templates/*.css',
        ],
    },
) 