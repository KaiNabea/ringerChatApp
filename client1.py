# importing socket, threading and sys classes for ssl methods
import socket
import threading
import sys

# HOST and PORT numbers to connect the client to the server
HOST = "127.0.0.1"
PORT = 5000

# receive_messages function that allows the client to responses from the message_receiver.py
# use while loop to continue the conversation after sending or receiving messages
# try-catch block for exception handling
# try block: store received networking info in the data variable, break from loop if connection fails
# print format: Client2: <message> displayed in terminal
# except block: break from loop and closes chat
def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            print(f"\nClient2: {data.decode()}\n> ", end="", flush=True)
        except:
            break

# send_messages function that allows client to send messages to message_receiver.py
# use while loop to continue conversation after sending or receiving messages
# try-catch block for error-handling
# try block: msg variable takes user input
# sock.sendall method sends the encoded msg variable to server
# if statement checks if quit was entered, breaks loop and closes chat if so
# except block: breaks loop and closes chat
def send_messages(sock):
    print("Write \"quit\" to end conversation")
    while True:
        try:
            msg = input("> ")
            sock.sendall(msg.encode("utf-8"))
            if msg.lower() == "quit":
                break
        except:
            break

# main function to setup the socket
# sock variable stores info: socket.AF_INET (IPv4) and socket.SOCK_STREAM (TCP method)
# sock.connect attempts to connect to the server using the HOST and PORT numbers
# t1 variable stores thread that uses the receive_messages variable, sock variable as arg, setup auto-close to True
# t1.start begins the thread that allows this client to receive messages
# send_messages function uses sock as parameter
# when send_messages function finishes and t1 thread ends, sock.close ends the connection
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    t1 = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
    t1.start()
    send_messages(sock)
    sock.close()

# only executes this file when called directly from terminal/command prompt, won't execute from import
if __name__ == "__main__":
    main()