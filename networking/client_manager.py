clients = {}

# same idea as the packet but for clients
def add_client(username, socket, ip, port):

# this takes the parameters and creates a dictionary of key-value pairs to make a json out of
    clients[username] = {
        "socket" : socket,
        "ip" : ip,
        "port" : port
    }

    print("Client added: " + username)

# this one removes the client from the dictionary using the username as the key
def remove_client(username):
    if username in clients:
        del clients[username]
        print("Client removed: " + username)
    else:
        print("Client not found: " + username)

# this one returns the client information based on the username key
def get_client(username):
    return clients.get(username)

# this one lists all the clients in the dictionary

def list_clients():
    return clients

