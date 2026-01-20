import argparse
import sys
from src.safwanbuddy.core import event_bus, logger

def main():
    parser = argparse.ArgumentParser(description="SafwanBuddy Ultimate++ v7.0 CLI")
    parser.add_argument("command", nargs="*", help="Command to execute")
    args = parser.parse_args()

    if args.command:
        command_text = " ".join(args.command)
        logger.info(f"CLI Command: {command_text}")
        event_bus.emit("voice_command", command_text)
    else:
        print("SafwanBuddy CLI. Please provide a command.")

if __name__ == "__main__":
    main()
