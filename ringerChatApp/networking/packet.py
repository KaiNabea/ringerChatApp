# this file is responsible for creating and reading packets that are sent over the network
import json 

# this creates a packet that is sent over the network
def create_packet(
        sender,
        receiver,
        message,
        ip,
        mac,
        port):

# this takes the parameters and creates a dictionary of key-value pairs to make a json out of 
    packet = {

        "sender":sender,

        "receiver":receiver,

        "message":message,

        "ip":ip,

        "mac":mac,

        "port":port

    }

# this converts the dictionary to a json string and returns it
    return json.dumps(packet)

# this takes the json string and converts it back to a dictionary and returns it
def read_packet(data):

# this is the function that takes the json string and converts it back to a dictionary and returns it
    return json.loads(data)