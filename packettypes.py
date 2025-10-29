# types.py

PACKETTYPE_INFO = 0  # Used by the client to send client information
# Workflow:
# 1. The client sends this packet to the server upon connection, containing the client's name.
# 2. The server validates the name against requirements (not already taken, length within 1-255 characters).
# 3. The server sends a PACKETTYPE_INFOSTATUS to inform the client about the success or failure.

PACKETTYPE_INFOSTATUS = 1  # Used by the server to provide success information regarding client information
# Workflow:
# 1. The server sends this packet to the client in response to a PACKETTYPE_INFO.
# 2. Contains a single byte indicating whether the client's name registration was successful (True) or not (False).
# 3. The client displays the corresponding success or error message.

PACKETTYPE_PING = 2  # Client pings the server
# Workflow:
# 1. The client sends this packet to the server to measure latency (ping).
# 2. The server, upon receiving this packet, immediately sends it back to the client.
# 3. The client measures the time between sending and receiving to determine latency.

PACKETTYPE_UPTIME = 3  # Server's uptime
# Workflow:
# 1. The client sends this packet to the server to find out the server's uptime.
# 2. The server sends this packet to the client, containing the server's uptime in seconds.
# 3. The client displays the received uptime.

PACKETTYPE_MSG = 4  # Sends a message if a client sends a message
# Workflow:
# 1. The client sends this packet to the server when it wants to send a message to all other clients.
# 2. The server receives the message and broadcasts it to all connected clients, using PACKETTYPE_CL_MSG.

PACKETTYPE_CL_MSG = 5  # Someone sent a message
# Workflow:
# 1. The server sends this packet to all clients when one of the clients sends a message.
# 2. Contains the sender's name and the message text.
# 3. The client displays the message from another client.

PACKETTYPE_CL_CONNECT = 6  # Someone connected
# Workflow:
# 1. The server sends this packet to all clients when a new client has successfully connected.
# 2. Contains the name of the connected client.
# 3. The client displays a message about the new client connecting.

PACKETTYPE_CL_DISCONNECT = 7  # Someone disconnected
# Workflow:
# 1. The server sends this packet to all clients when a client has disconnected.
# 2. Contains the name of the disconnected client.
# 3. The client displays a message about the client disconnecting.
