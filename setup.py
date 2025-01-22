from setuptools import setup, find_packages

setup(
    name="web-scanner",
    version="1.0.0",
    description="Advanced web application security scanner with comprehensive vulnerability detection",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Harshwardhan Patil",
    author_email="harshwardhanp49@gmail.com",
    url="https://github.com/Etrama0/web-scanner",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.0.0",
        "aiohttp>=3.8.0",
        "reportlab>=3.6.0",
        "beautifulsoup4>=4.9.0",
        "pyyaml>=5.4.0",
        "python-dotenv>=0.19.0",
        "scapy>=2.4.0",
        "requests>=2.26.0",
        "jinja2>=3.0.0",
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-asyncio>=0.15.0',
            'black>=21.0.0',
            'flake8>=3.9.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'webscan=web_scanner.main:main',
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
    ],
    keywords="security scanner web vulnerability assessment pentest",
)
