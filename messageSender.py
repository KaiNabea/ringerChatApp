# importing socket, threading, sys and ssl classes
import socket
import threading
import sys
import ssl

#import encryption and packet files from module
from networking.encryption import text_to_binary, binary_to_text
from networking.packet import create_packet, read_packet

# HOST and PORT numbers to connect the client to the server
# HOST and PORT numbers to connect the client to the server
HOST = "127.0.0.1"
PORT = 5000

# USERNAME and RECEIVER variables to store sender and receiver info
USERNAME = input("Enter your username: ")
RECEIVER = input("Enter the receiver's username: ")


# receive_messages function that allows the client to responses from the message_receiver.py
# use while loop to continue the conversation after sending or receiving messages
# try-catch block for exception handling
# try block: store received networking info in the data variable, break from loop if connection fails
# print format: Client2: <message> displayed in terminal
# except block: break from loop and closes chat
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


# send_messages function that allows client to send messages to message_receiver.py
# use while loop to continue conversation after sending or receiving messages
# try-catch block for error-handling
# try block: msg variable takes user input
# sock.sendall method sends the encoded msg variable to server
# if statement checks if quit was entered, breaks loop and closes chat if so
# except block: breaks loop and closes chat
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


# main function to setup the socket
# sock variable stores info: socket.AF_INET (IPv4) and socket.SOCK_STREAM (TCP method)
# sock.connect attempts to connect to the server using the HOST and PORT numbers
# t1 variable stores thread that uses the receive_messages variable, sock variable as arg, setup auto-close to True
# t1.start begins the thread that allows this client to receive messages
# send_messages function uses sock as parameter
# when send_messages function finishes and t1 thread ends, sock.close ends the connection
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

# only executes this file when called directly from terminal/command prompt, won't execute from import
if __name__ == "__main__":
    main()