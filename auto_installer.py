import os
import subprocess
import sys

def install_dependencies():
    print("Installing SafwanBuddy dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def setup_directories():
    directories = [
        "config", "assets", "data", "logs", "plugins", 
        "data/profiles", "data/models", "data/templates", 
        "data/workflows", "data/cache"
    ]
    for d in directories:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"Created directory: {d}")

def main():
    setup_directories()
    install_dependencies()
    print("Setup complete! You can now run SafwanBuddy using main.py")

if __name__ == "__main__":
    main()
