# for networking
import socket
# for secure connection
import ssl

# create a socket
# socket is 👉 a communication endpoint (a door) 
# AF_INET → IPv4
# SOCK_STREAM → TCP
# it means: “Create a TCP communication endpoint using IPv4”
client_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# create SSL context
# Do we need to create a normal socket first?
# YES because SSL does NOT replace socket, SSL wraps socket
sslContext= ssl.create_default_context()

# Disabled verification: No real certificate → skip verification
sslContext.check_hostname = False
sslContext.verify_mode = ssl.CERT_NONE

# You must pass your socket into SSL
# SSL does identity verification (like checking ID 🪪)
# Even if you're using:
# "127.0.0.1"
# SSL still wants:
# 👉 a hostname to verify against the certificate
secure_socket= sslContext.wrap_socket(client_socket, server_hostname="127.0.0.1")

try: 
    # connect to server
    # host = IP address
    # port = number (e.g., 5000)
    secure_socket.connect(("127.0.0.1", 5000))

    # receive → print → receive → print → forever
    # keep listening forever until connection is closed
    while True:
        # receive data
        # 1024 = buffer size (how much data you read at once)
        data= secure_socket.recv(1024)
        # When server closes connection:
        # return: b'' (empty bytes)

        # if server stops, or connection closes. program will break
        # if no data -> stop loop
        if not data:
            break

        # decode data
        # Data comes as bytes, not text.
        message= data.decode()

        # print message
        print(message)

except Exception as e:
    print("Error: ", e)

# try:
#     # risky code
# except:
#     # handle error
# finally:
#     # ALWAYS runs
finally:
    secure_socket.close()

# 1. import
# 2. define host + port
# 3. create socket
# 4. wrap socket with SSL
# 5. connect
# 6. receive
# 7. decode
# 8. print

# Understand SSL (simple explanation)
# Right now your connection is like:
# Client  -----------  Server
#         (plain text)

# With SSL:
# Client  =====🔒=====  Server
#         (encrypted)

# 🧠 Key idea
# We don’t replace the socket
# 👉 we wrap it

# Concept
# normal socket → SSL context → secure socket

# ⚠️ VERY IMPORTANT (this will save you hours later)
# When using:
# ssl.create_default_context()
# 👉 Python expects:
# a valid SSL certificate from server