import socket
import ssl

from networking.packet import read_packet
from networking.encryption import binary_to_text

HOST = "127.0.0.1"
PORT = 5000


def start_receiver():

    # create normal socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # create SSL context
    context = ssl.create_default_context()

    # disable verification (for local testing)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # wrap socket with SSL
    secure_socket = context.wrap_socket(
        client_socket,
        server_hostname="127.0.0.1"
    )

    try:
        # connect to server
        secure_socket.connect((HOST, PORT))
        print("Connected to secure server")

        # send username (IMPORTANT for server)
        username = input("Enter your username: ")
        secure_socket.sendall(username.encode())

        print("Listening for messages...\n")

        while True:

            data = secure_socket.recv(4096)

            if not data:
                break

            # decode packet
            packet = read_packet(data.decode())

            print("\n📩 Message received from:", packet["sender"])

            print("Encrypted:", packet["message"])

            # decrypt message
            decrypted = binary_to_text(packet["message"])
            print("Decrypted:", decrypted)

    except Exception as e:
        print("Error:", e)

    finally:
        secure_socket.close()
        print("Connection closed")


if __name__ == "__main__":
    start_receiver()