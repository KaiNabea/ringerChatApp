# run_server.py (in RINGERCHATAPP/ root)
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the start_server function from socket_server.py
if __name__ == "__main__":
    print("Starting Ringer Chat Server...")
    print(f"Working directory: {os.getcwd()}")
    
    try:
        from ringerChatApp.socket_server import start_server
        start_server()
    except ImportError as e:
        print(f"Import error: {e}")
        sys.exit(1)