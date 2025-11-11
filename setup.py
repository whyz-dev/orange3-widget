from setuptools import setup, find_packages

setup(
    name="orange3-example",  # PyPI 등록 이름
    version="0.1.2",
    description="Orange3 LLM 기반 사용자 정의 예제 위젯입니다.",
    author="Gangjun Jo",
    url="https://github.com/whyz-dev/Orange3-Widget",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Orange3>=3.32.0",
        "openai",
        "PyQt5",
        "python-dotenv",
        "opencv-python",
        "pyserial"
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
