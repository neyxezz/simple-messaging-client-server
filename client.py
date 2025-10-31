# client.py

import traceback
import aioconsole
import asyncio
import struct
import time

from protocol import *
from colors import *

name = input("Enter your name: ")

def printinfo(text):
	print(f"\r\033[K{text}")

def printpadd(text):
	print(f"\r\033[K{text}\n> ", end="")

class Client:
	def __init__(self, host='127.0.0.1', port=8888):
		self.host = host
		self.port = port
		self.reader = None
		self.writer = None
		self.last_ping = time.time()

	async def unpack_int(self, data):
		return int.from_bytes(data, 'little')

	async def pack_and_send(self, PACKETTYPE, *data):
		to_send = bytes([PACKETTYPE])
		if PACKETTYPE == PACKETTYPE_INFO:
			# name
			name_encoded = name.encode('utf-8')
			name_encoded_length = struct.pack("<B", len(name_encoded))

			self.writer.write(bytes([PACKETTYPE_INFO]) + name_encoded_length + name_encoded)
			await self.writer.drain()

		if PACKETTYPE == PACKETTYPE_PING: # ping
			self.last_ping = time.time()
			self.writer.write(bytes([PACKETTYPE_PING]))
			await self.writer.drain()

		if PACKETTYPE == PACKETTYPE_UPTIME: # uptime
			self.writer.write(bytes([PACKETTYPE_UPTIME]))
			await self.writer.drain()

		if PACKETTYPE == PACKETTYPE_MSG: # msg
			message_encoded = data[0].encode('utf-8')
			message_encoded_length = struct.pack("<I", len(message_encoded))

			self.writer.write(bytes([PACKETTYPE_MSG]) + message_encoded_length + message_encoded)
			await self.writer.drain()

		if PACKETTYPE == PACKETTYPE_CLIENT_LIST:
			self.writer.write(bytes([PACKETTYPE_CLIENT_LIST]))
			await self.writer.drain()

	async def unpack_packet(self, PACKETTYPE):
		if PACKETTYPE == PACKETTYPE_INFO_STATUS:
			status = await self.reader.readexactly(1)
			status = struct.unpack("<B", status)[0]
			if status == INFO_STATUS_OK:
				printpadd(to_green("Successfully connected! Type \"*help\" for help"))
			if status == INFO_STATUS_NAME_TAKEN:
				printinfo(to_red("Your name matches the existing one"))
			if status == INFO_STATUS_INVALID_NAME:
				printinfo(to_red("Your name is shorter/longer than 1-255 symbols"))
			if status == INFO_STATUS_SERVER_FULL:
				max_clients = await self.reader.readexactly(1)
				max_clients = struct.unpack("<B", max_clients)[0]
				printinfo(to_red(f"Server is full, try connect later ({max_clients}/{max_clients})"))
			if status == INFO_STATUS_TOO_MANY_CLIENTS_PER_IP:
				max_clients = await self.reader.readexactly(1)
				max_clients = struct.unpack("<B", max_clients)[0]
				printinfo(to_red(f"Only {max_clients} clients per IP allowed"))

		if PACKETTYPE == PACKETTYPE_PING:
			printpadd(f"Latency - {(time.time()-self.last_ping)*1000:.2f} ms")

		if PACKETTYPE == PACKETTYPE_UPTIME:
			uptime = await self.reader.readexactly(8)
			uptime = await self.unpack_int(uptime) / 100
			printpadd(f"Uptime - {uptime} s")

		if PACKETTYPE == PACKETTYPE_MSG:
			message_length = struct.unpack("<I", await self.reader.readexactly(4))[0]
			message = await self.reader.readexactly(message_length)
			message = message.decode('utf-8')
			printpadd(message)

		if PACKETTYPE == PACKETTYPE_CL_MSG:
			name_length = struct.unpack("<B", await self.reader.readexactly(1))[0]
			name = await self.reader.readexactly(name_length)
			name = name.decode('utf-8')

			message_length = struct.unpack("<B", await self.reader.readexactly(1))[0]
			message = await self.reader.readexactly(message_length)
			message = message.decode('utf-8')

			printpadd(f"{to_cyan(name + ':')} {message}")

		if PACKETTYPE == PACKETTYPE_CL_CONNECT:
			name_length = struct.unpack("<B", await self.reader.readexactly(1))[0]
			name = await self.reader.readexactly(name_length)
			name = name.decode('utf-8')
			printpadd(to_yellow(f"'{name}' has connected"))

		if PACKETTYPE == PACKETTYPE_CL_DISCONNECT:
			name_length = struct.unpack("<B", await self.reader.readexactly(1))[0]
			name = await self.reader.readexactly(name_length)
			name = name.decode('utf-8')
			printpadd(to_yellow(f"'{name}' has disconnected"))

		if PACKETTYPE == PACKETTYPE_CLIENT_LIST:
			names_count = struct.unpack("<B", await self.reader.readexactly(1))[0]
			max_names_count = struct.unpack("<B", await self.reader.readexactly(1))[0]

			clients = ""
			for x in range(names_count):
				name_length = struct.unpack("<B", await self.reader.readexactly(1))[0]
				client_name = await self.reader.readexactly(name_length)
				client_name = client_name.decode('utf-8')
	
				if x == 0:
					clients += f"{names_count}/{max_names_count}\n"
				clients += f"- {client_name}\n"
		
			printpadd(to_purple(clients[:-1]))

	async def process_packets(self):
		await asyncio.sleep(0.01)
		while True:
			#await asyncio.sleep(0.01)

			try:
				msg_type = await self.unpack_int(await self.reader.readexactly(1))
				await self.unpack_packet(msg_type)

			except asyncio.IncompleteReadError:
				print("Server closed connection.")
				break
			except Exception as e:
				print(f"Error: {e}")
				break

	async def process_commands(self, message):
		need_continue = False
		need_break = False
		if message.lower() == '*help':
			printinfo(to_purple("*ping - get latency\n*uptime - server uptime\n*clients - client list\n*exit - disconnect from server"))
		elif message.lower() == '*ping':
			await self.pack_and_send(PACKETTYPE_PING)
			need_continue = True
		elif message.lower() == '*uptime':
			await self.pack_and_send(PACKETTYPE_UPTIME)
			need_continue = True
		elif message.startswith("*file"):
			file = " ".join(message.split()[1:])
			printinfo(file)
		elif message.lower() == "*clients":
			await self.pack_and_send(PACKETTYPE_CLIENT_LIST)
			need_continue = True
		elif message.lower() == '*exit':
			need_break = True
		if message.strip() == '':
			need_continue = True
		return need_continue, need_break

	async def handle_user_input(self, prompt):
		return await aioconsole.ainput(prompt)

	async def run(self):
		self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

		printinfo('Connecting...')
		periodic_task = asyncio.create_task(self.process_packets())
		await self.pack_and_send(PACKETTYPE_INFO, name)

		try:
			while True:
				user_input_task = asyncio.create_task(self.handle_user_input("> "))
				done, pending = await asyncio.wait(
					[user_input_task, periodic_task],
					return_when=asyncio.FIRST_COMPLETED
				)

				if user_input_task in done:
					message = user_input_task.result()
					if message.startswith("*"):
						need_continue, need_break = await self.process_commands(message)
						if need_continue:
							continue
						if need_break:
							break
					else:
						await self.pack_and_send(PACKETTYPE_MSG, message)

				if periodic_task in done:
					break

		except Exception as e:
			printinfo(f"Error: {e}")
		finally:
			printinfo('Connection closed.')
			self.writer.close()
			await self.writer.wait_closed()

			periodic_task.cancel()
			try:
				await periodic_task
			except asyncio.CancelledError:
				pass

if __name__ == "__main__":
	client = Client("localhost", 8888)
	try:
		asyncio.run(client.run())
	except KeyboardInterrupt as e:
		pass
