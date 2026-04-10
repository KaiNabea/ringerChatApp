# this gets the client manager to get the client for the current request
from ringerChatApp.networking.client_manager import get_client

# this function takes the receiver and the message as parameters and routes the message to the correct client based on the receiver's username
def route_message(receiver, message):

    # this gets the client information based on the receiver's username
    client = get_client(receiver)

    # this checks if the client exists and if it does, it sends the message to the client's socket
    if client:

    # this gets the socket from the client 
        sock = client["socket"]

    # this sends the message to the client's socket by encoding it to bytes and sending it over the network
        sock.send(message.encode())

        print("Message sent to " + receiver)

    # this returns true if the message was sent successfully and false if the client was not found
        return True
    
    else:

        print("User not found")

        return False