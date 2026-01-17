from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="safwaanbuddy-ultimate",
    version="7.0.0",
    author="SafwaanBuddy Team",
    description="Comprehensive Windows AI assistant with voice control and automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/safwaanbuddy/ultimate-agent",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.9",
    install_requires=[
        "PyQt6>=6.4.0",
        "PyQt6-WebEngine>=6.4.0",
        "vosk>=0.3.45",
        "pyttsx3>=2.90",
        "numpy>=1.24.0",
        "PyOpenGL>=3.1.6",
        "moderngl>=5.8.2",
        "Pillow>=10.0.0",
        "pyautogui>=0.9.54",
        "keyboard>=0.13.5",
        "mouse>=0.7.1",
        "selenium>=4.15.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "python-docx>=1.1.0",
        "openpyxl>=3.1.2",
        "reportlab>=4.0.7",
        "pdfkit>=1.0.0",
        "pytesseract>=0.3.10",
        "mss>=9.0.1",
        "opencv-python>=4.8.1",
        "pyyaml>=6.0.1",
        "python-dotenv>=1.0.0",
        "cryptography>=41.0.7",
        "psutil>=5.9.6",
        "sounddevice>=0.4.6",
        "soundfile>=0.12.1",
    ],
    entry_points={
        "console_scripts": [
            "safwaanbuddy=safwaanbuddy.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "safwaanbuddy": [
            "assets/**/*",
            "config/**/*",
        ],
    },
)
