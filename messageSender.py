import socket
import threading
import sys

HOST = "127.0.0.1"
PORT = 5000

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            sys.stdout.write("\nClient2: " + data.decode() + "\n> ")
            sys.stdout.flush()
        except:
            break

def send_messages(sock):
    while True:
        try:
            msg = input("> ")
            sock.sendall(msg.encode("utf-8"))
            if msg.lower() == "quit":
                break
        except:
            break

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    t1 = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
    t1.start()
    send_messages(sock)
    sock.close()

if __name__ == "__main__":
    main()
