# run_server.py (in RINGERCHATAPP/ root)
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Starting Ringer Chat Server...")
    print(f"Working directory: {os.getcwd()}")
    
    try:
        from ringerChatApp.socket_server import start_server
        start_server()
    except ImportError as e:
        print(f"Import error: {e}")
        print("\nMake sure you're running from the RINGERCHATAPP directory")
        print("Current directory:", os.getcwd())
        print("Expected structure:")
        print("  RINGERCHATAPP/")
        print("  ├── ringerChatApp/")
        print("  │   ├── socket_server.py")
        print("  │   └── networking/")
        print("  ├── cert.pem")
        print("  ├── key.pem")
        print("  └── run_server.py")
        sys.exit(1)