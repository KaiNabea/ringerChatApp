import socket

import threading

import ssl

from networking.client_manager import add_client

from networking.packet import read_packet

from networking.router import route_message

from networking.encryption import binary_to_text

HOST="0.0.0.0"

PORT=5000

def handle_client(client, addr):

    print("New connection from " + str(addr))

    username = client.recv(1024).decode()

    add_client(
        username, 
        client, 
        addr[0], 
        addr[1])
    
    while True:

        try:

            data = client.recv(4096)

            if not data:

                break

            packet = read_packet(
                
                data.decodes()
                
            )

            message_binary = packet["message"]

            message = binary_to_text(message_binary)

            print("Packet received")

            print("Sender IP: ", packet["ip"])

            print("Sender MAC: ", packet["mac"])

            print("Encrypted: ", message_binary)

            print("Decrypted: ", message)

            route_message(

                packet["receiver"], 
                
                data.decode()
                
                )
            
        except:

            break

        client.close()

def start_server():

    server = socket.socket(

        socket.AF_INET,

        socket.SOCK_STREAM

    )

    context = ssl.create_default_context(
        
        ssl.Purpose.CLIENT_AUTH
        
        )
    
    context.load_cert_chain(

    certfile="cert.pem", 
    
    keyfile="key.pem"

    )

    server = context.wrap_socket(
        
        server, 
        
        server_side=True)

    server.bind((HOST, PORT))

    server.listen()

    print("Ringer socket server running on " + HOST + ":" + str(PORT))

    while True:

        client, addr = server.accept()

        thread = threading.Thread(
            
            target=handle_client, 
            
            args=(client, addr)
            
            )

        thread.start()
    