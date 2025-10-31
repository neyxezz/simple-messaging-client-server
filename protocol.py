# types.py

"""packets"""

PACKETTYPE_INFO = 0  # Used by the client to send client information
# Workflow:

# 1. The client sends this packet to the server upon connection, containing the client's name.
# 2. The server validates the name against requirements (not already taken, length within 1-255 characters).
# 3. The server sends a PACKETTYPE_INFOSTATUS to inform the client about the success or failure.

# Structure:

# Structure:

# [PACKETTYPE_INFO] [name_encoded_length] [name_encoded]

PACKETTYPE_INFO_STATUS = 1  # Used by the server to provide status information regarding client info
# Workflow:

# 1. The server sends this packet to the client in response to a PACKETTYPE_INFO.
# 2. Contains a single byte indicating info status, INFO_STATUS_OK, INFO_STATUS_NAME_TAKEN, INFO_STATUS_INVALID_NAME
# 3. The client displays the corresponding success or error message.

# Structure:

# [PACKETTYPE_INFO_STATUS] [INFO_STATUS_OK | INFO_STATUS_NAME_TAKEN | INFO_STATUS_INVALID_NAME | INFO_STATUS_SERVER_FULL | INFO_STATUS_ONLY_X_CLIENTS_ALLOWED]
# if INFO_STATUS_TOO_MANY_CLIENTS_PER_IP [PACKETTYPE_INFO_STATUS] [INFO_STATUS_ONLY_X_CLIENTS_ALLOWED] [max_clients_per_ip]


INFO_STATUS_OK = 0
INFO_STATUS_NAME_TAKEN = 1
INFO_STATUS_INVALID_NAME = 2
INFO_STATUS_SERVER_FULL = 3
INFO_STATUS_TOO_MANY_CLIENTS_PER_IP = 4

PACKETTYPE_PING = 2  # Client pings the server
# Workflow:

# 1. The client sends this packet to the server to measure latency (ping).
# 2. The server, upon receiving this packet, immediately sends it back to the client.
# 3. The client measures the time between sending and receiving to determine latency.

# Structure:

# [PACKETTYPE_PING]

PACKETTYPE_UPTIME = 3  # Server's uptime
# Workflow:

# 1. The client sends this packet to the server to find out the server's uptime.
# 2. The server sends this packet to the client, containing the server's uptime in seconds.
# 3. The client displays the received uptime.

# Structure:

# [PACKETTYPE_UPTIME]

PACKETTYPE_MSG = 4  # Sends a message if a client sends a message
# Workflow:

# 1. The client sends this packet to the server when it wants to send a message to all other clients.
# 2. The server receives the message and broadcasts it to all connected clients, using PACKETTYPE_CL_MSG.

# Structure:

# [PACKETTYPE_MSG] [message_encoded_length] [message_encoded]

PACKETTYPE_CL_MSG = 5  # Someone sent a message
# Workflow:

# 1. The server sends this packet to all clients when one of the clients sends a message.
# 2. Contains the sender's name and the message text.
# 3. The client displays the message from another client.

# Structure:

# [PACKETTYPE_CL_MSG] [name_encoded_length] [name_encoded] [message_encoded_length] [message_encoded]

PACKETTYPE_CL_CONNECT = 6  # Someone connected
# Workflow:

# 1. The server sends this packet to all clients when a new client has successfully connected.
# 2. Contains the name of the connected client.
# 3. The client displays a message about the new client connecting.

# Structure:

# [PACKETTYPE_CL_CONNECT] [name_encoded_length] [name_encoded]

PACKETTYPE_CL_DISCONNECT = 7  # Someone disconnected
# Workflow:

# 1. The server sends this packet to all clients when a client has disconnected.
# 2. Contains the name of the disconnected client.
# 3. The client displays a message about the client disconnecting.

# Structure:

# [PACKETTYPE_CL_DISCONNECT] [name_encoded_length] [name_encoded]

PACKETTYPE_CLIENT_LIST = 8 # Client list
# Workflow:

# 1. The client sends this packet to the server to get client list.
# 2. The server sends this packet to the client, containing the connected clients.
# 3. The client displays a list of clients.

# Structure:

# [PACKETTYPE_CLIENT_LIST] [clients_count] [max_clients_count] [name_encoded_length] [name_encoded] ... [client_n]


"""other"""

MAX_CLIENTS = 16
MAX_CLIENTS_PER_IP = 2
