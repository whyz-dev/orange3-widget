# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

# README 파일 읽기
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="orange3-example",  # PyPI 등록 이름
    version="0.1.13",
    description="Orange3 LLM 기반 사용자 정의 예제 위젯입니다.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Gangjun Jo",
    url="https://github.com/whyz-dev/orange3-widget",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Orange3>=3.32.0",
        "openai",
        "python-dotenv",
        "pyserial",
        "opencv-python-headless==4.9.0.80",
    ],
    entry_points={
        "orange3.addon": (
            "orange3example = orangecontrib.orange3example",
        ),
        "orange.widgets": (
            "Example Widgets = orangecontrib.orange3example.widgets",
        ),
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe=False,
)


