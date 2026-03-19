#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="xianyu-search",
    version="1.0.5",
    author="OpenClaw用户",
    author_email="",
    description="基于Selenium的闲鱼自动化搜索工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/xianyu-search",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "selenium>=4.0.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=5.0.0",
    ],
    entry_points={
        "console_scripts": [
            "xianyu-search=xianyu_clickable_links:main",
        ],
    },
    keywords="闲鱼, xianyu, goofish, 搜索, 自动化, selenium, 二手, 购物",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/xianyu-search/issues",
        "Source": "https://github.com/yourusername/xianyu-search",
    },
)