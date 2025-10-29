# Purpose
The purpose of this project is to demonstrate the creation of a simple client and server for message exchange.
# Protocol
All packet types and their purpose are described in the `packettypes.py` file.
# Cloning
To clone the repository, use the following command:
```
https://github.com/neyxezz/simple-messaging-client-server.git
```
# Installation and Startup
* To clone the repository, use the following command:
    ```
    pip install aioconsole
    ```
* Start the server:
   - If necessary, change the IP address and port in the last lines of the server.py file (in Linux, you can find the IP address using the ip addr command).
   - Run the command:
    ```
    python3 server.py
    ```
* Connect to the server:
   - If necessary, change the IP address and port in the last lines of the client.py file.
   - Run the command:
    ```
    python3 client.py
    ```
