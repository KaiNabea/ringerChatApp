import socket
import threading
import ssl

from networking.client_manager import add_client, remove_client
from networking.packet import read_packet
from networking.router import route_message
from networking.encryption import binary_to_text



HOST = "127.0.0.1"
PORT = 5000


def handle_client(conn, addr):

    print("🔌 New connection from", addr)

    username = None

    try:
        # receive username first
        username = conn.recv(1024).decode()
        ip, port = addr
        add_client(username, conn, ip, port)

        print(f"👤 User registered: {username}")

        while True:

            data = conn.recv(4096)

            if not data:
                break

            # parse packet
            packet = read_packet(data.decode())

            print("\n📦 Packet received")

            print("From:", packet["sender"])
            print("To:", packet["receiver"])
            print("IP:", packet["ip"])
            print("MAC:", packet["mac"])

            print("Encrypted:", packet["message"])

            # decrypt message
            message = binary_to_text(packet["message"])
            print("Decrypted:", message)

            # route message
            route_message(packet["receiver"], message)

    except Exception as e:
        print("⚠️ Error handling client:", e)

    finally:
        remove_client(username)
        conn.close()
        print("❌ Connection closed:", addr)


def start_server():

    # create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    # SSL setup
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    secure_server = context.wrap_socket(server_socket, server_side=True)

    print("🔒 Secure Ringer Server running on port", PORT)

    while True:
        conn, addr = secure_server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(conn, addr)
        )

        thread.start()