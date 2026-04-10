# ringerChatApp/socket_server.py
import socket
import threading
import ssl
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ringerChatApp.networking.client_manager import add_client, remove_client, get_client
from ringerChatApp.networking.packet import read_packet
from ringerChatApp.networking.router import route_message
from ringerChatApp.networking.encryption import binary_to_text

HOST = "0.0.0.0"
PORT = 5000

def handle_client(client, addr):
    print(f"New connection from {addr}")
    username = None
    
    try:
        # Receive username (first message)
        username = client.recv(1024).decode()
        add_client(username, client, addr[0], addr[1])
        print(f"User '{username}' registered from {addr}")
        
        while True:
            try:
                data = client.recv(4096)
                if not data:
                    break
                
                # FIXED: was .decodes() now .decode()
                packet = read_packet(data.decode())
                message_binary = packet["message"]
                message = binary_to_text(message_binary)
                
                print(f"\n[+] Packet from {packet['sender']} to {packet['receiver']}")
                print(f"    Message: {message}")
                print(f"    Sender IP: {packet['ip']}")
                
                # Route to receiver
                route_message(packet["receiver"], data.decode())
                
            except Exception as e:
                print(f"Error handling message: {e}")
                break
                
    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        if username:
            remove_client(username)
        client.close()
        print(f"Connection closed from {addr}")

def start_server():
    try:
        # Get the root directory (where cert.pem and key.pem are)
        # Going up from ringerChatApp/socket_server.py to RINGERCHATAPP/
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cert_path = os.path.join(base_dir, "cert.pem")
        key_path = os.path.join(base_dir, "key.pem")
        
        print(f"Looking for certificates in: {base_dir}")
        
        # Create server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # SSL Setup
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        
        # Load certificates
        if os.path.exists(cert_path) and os.path.exists(key_path):
            context.load_cert_chain(certfile=cert_path, keyfile=key_path)
            print("[✓] SSL certificates loaded")
        else:
            print("[✗] ERROR: cert.pem or key.pem not found!")
            print(f"    Looking in: {base_dir}")
            print("    Generate them with:")
            print("    openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes")
            return
        
        # Wrap socket
        server = context.wrap_socket(server_socket, server_side=True)
        
        # Bind and listen
        server.bind((HOST, PORT))
        server.listen()
        print(f"[✓] Ringer server running on {HOST}:{PORT}")
        print(f"[✓] Waiting for connections...")
        
        while True:
            client, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(client, addr))
            thread.daemon = True
            thread.start()
            print(f"[*] Active connections: {threading.active_count() - 1}")
            
    except Exception as e:
        print(f"[✗] Server error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    start_server()