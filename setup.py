from setuptools import setup, find_packages

setup(
    name="safwanbuddy",
    version="7.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PyQt6",
        "pyyaml",
        "vosk",
        "pyttsx3",
        "numpy",
        "moderngl",
        "PyOpenGL",
        "Pillow",
        "selenium",
        "requests",
        "beautifulsoup4",
        "python-docx",
        "openpyxl",
        "reportlab",
        "python-pptx",
        "pytesseract",
        "mss",
        "opencv-python",
        "psutil",
        "cryptography",
        "pyautogui",
        "keyboard",
        "mouse"
    ],
    entry_points={
        "console_scripts": [
            "safwanbuddy=run_safwaan_buddy:main",
        ],
    },
)
