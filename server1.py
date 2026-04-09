import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from networking.socket_server import start_server

if __name__ == "__main__":

    print("Starting Ringer Server...")

    start_server()