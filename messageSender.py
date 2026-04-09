import socket
import threading
import sys
import ssl

from networking.encryption import text_to_binary, binary_to_text
from networking.packet import create_packet, read_packet

HOST = "127.0.0.1"
PORT = 5000

USERNAME = input("Enter your username: ")
RECEIVER = input("Enter the receiver's username: ")


def receive_messages(sock):
    while True:
        try:
            data = sock.recv(4096)

            if not data:
                break

            packet = read_packet(data.decode())

            print("\nMessage received from " + packet["sender"])

            print("Encrypted:", packet["message"])

            # ✅ Decrypt message
            decrypted = binary_to_text(packet["message"])
            print("Decrypted:", decrypted)

        except:
            print("Connection closed")
            break


def send_message(sock):
    while True:
        try:
            msg = input("> ")

            if msg.lower() == "exit":
                break

            binary_msg = text_to_binary(msg)

            packet = create_packet(
                sender=USERNAME,
                receiver=RECEIVER,
                message=binary_msg,
                ip="127.0.0.1",   
                mac="00:AA",
                port=PORT
            )

            sock.sendall(packet.encode())

        except:
            print("Connection closed")
            break


def main():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        sock = context.wrap_socket(client_socket, server_hostname="127.0.0.1")

        sock.connect((HOST, PORT))
        print("Connected to server")

        # send username first
        sock.sendall(USERNAME.encode())

        t1 = threading.Thread(
            target=receive_messages,
            args=(sock,),
            daemon=True
        )

        t1.start()

        send_message(sock)

        sock.close()

    except Exception as e:
        print("Unable to connect to server:", e)
        sys.exit()


if __name__ == "__main__":
    main()