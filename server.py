import traceback
import asyncio
import struct
import time

from protocol import *

from colors import YELLOW, RESET

start_time = time.time()

class Server:
	def __init__(self, host='127.0.0.1', port=8888):
		self.host = host
		self.port = port
		self.clients = {} # {writer: name}

	async def unpack_int(self, data):
		return int.from_bytes(data, 'little')

	async def pack_and_send_msg(self, PACKETTYPE, writer, *data):
		if PACKETTYPE == PACKETTYPE_INFO_STATUS:
			message_to_send = bytes([PACKETTYPE_INFO_STATUS]) + bytes([data[0]])
			if(len(data) > 1):
				message_to_send += bytes([data[1]])
			writer.write(message_to_send)
			await writer.drain()

		if PACKETTYPE == PACKETTYPE_CL_MSG:
			name_encoded = data[0].encode('utf-8')
			name_encoded_length = struct.pack("<B", len(name_encoded))

			message_encoded = data[1].encode('utf-8')
			message_encoded_length = struct.pack("<B", len(message_encoded))

			message_to_send = bytes([PACKETTYPE_CL_MSG]) + name_encoded_length + name_encoded + message_encoded_length + message_encoded
			await self.send_to_all(writer, message_to_send)

		if PACKETTYPE == PACKETTYPE_CL_CONNECT:
			name_encoded = data[0].encode('utf-8')
			name_encoded_length = struct.pack("<B", len(name_encoded))

			message_to_send = bytes([PACKETTYPE_CL_CONNECT]) + name_encoded_length + name_encoded
			await self.send_to_all(writer, message_to_send)

		if PACKETTYPE == PACKETTYPE_CL_DISCONNECT:
			name_encoded = data[0].encode('utf-8')
			name_encoded_length = struct.pack("<B", len(name_encoded))

			message_to_send = bytes([PACKETTYPE_CL_DISCONNECT]) + name_encoded_length + name_encoded
			await self.send_to_all(writer, message_to_send)

	async def process_packets(self, PACKETTYPE, reader, writer, addr, name):
		if PACKETTYPE == PACKETTYPE_PING:
			writer.write(bytes([PACKETTYPE_PING]))
			await writer.drain()

		if PACKETTYPE == PACKETTYPE_UPTIME:
			uptime = struct.pack("<Q", int((time.time()-start_time)*100))
			writer.write(bytes([PACKETTYPE_UPTIME]) + uptime)
			await writer.drain()

		if PACKETTYPE == PACKETTYPE_MSG:
			await self.handle_message(reader, writer, addr, name)

		if PACKETTYPE == PACKETTYPE_CLIENT_LIST:
			names_count = struct.pack("<B", len(self.clients.items()))
			max_names_count = struct.pack("<B", MAX_CLIENTS)
			names = bytes()
			for w, clname in self.clients.items():
				try:
					name_encoded = clname[:250].encode('utf-8')
					name_encoded_length = struct.pack("<B", len(name_encoded))
					
					names += name_encoded_length
					names += name_encoded

				except Exception as e:
					print(traceback.format_exc())

			writer.write(bytes([PACKETTYPE_CLIENT_LIST]) + names_count + max_names_count + names)
			await writer.drain()

	async def handle_message(self, reader, writer, addr, name):
		message_length = struct.unpack("<I", await reader.readexactly(4))[0]
		message = await reader.readexactly(message_length)
		message = message.decode('utf-8')
		if not message:
			return
		print(f"{addr} - {name}: {message}")

		# message for all clients
		await self.pack_and_send_msg(PACKETTYPE_CL_MSG, writer, name, message)

	async def send_to_all(self, writer, message_to_send):
		for w, name in self.clients.items():
			if w != writer:
				try:
					w.write(message_to_send)
					await w.drain()
				except Exception as e:
					print(f"Error sending message to client: {e}")
					del self.clients[w] # remove from dict

	async def process_client_info(self, reader, writer, addr):
		msg_type = await self.unpack_int(await reader.readexactly(1))

		same_ip = 1
		for w, name in self.clients.items():
			try:
				if writer.get_extra_info('peername')[0] == w.get_extra_info('peername')[0]:
					same_ip += 1
			except Exception as e:
				pass

		if same_ip > MAX_CLIENTS_PER_IP:
			await self.pack_and_send_msg(PACKETTYPE_INFO_STATUS, writer, INFO_STATUS_TOO_MANY_CLIENTS_PER_IP, MAX_CLIENTS_PER_IP)
			return None, f"only {MAX_CLIENTS_PER_IP} clients per IP allowed"

		if len(self.clients.items()) >= MAX_CLIENTS:
			await self.pack_and_send_msg(PACKETTYPE_INFO_STATUS, writer, INFO_STATUS_SERVER_FULL, MAX_CLIENTS)
			return None, "server is full"

		if msg_type == PACKETTYPE_INFO:
			name_length = struct.unpack("<B", await reader.readexactly(1))[0]
			name = await reader.readexactly(name_length)
			name = name.decode('utf-8')

			for w, clname in self.clients.items():
				if name == clname:
					await self.pack_and_send_msg(PACKETTYPE_INFO_STATUS, writer, INFO_STATUS_NAME_TAKEN)
					return None, "name already exists"
			if not name or not name.strip():
				await self.pack_and_send_msg(PACKETTYPE_INFO_STATUS, writer, INFO_STATUS_INVALID_NAME)
				return None, "invalid name"

			print(f"Client {addr} logged as \"{name}\"")
			await self.pack_and_send_msg(PACKETTYPE_INFO_STATUS, writer, INFO_STATUS_OK)
			self.clients[writer] = name

			await self.pack_and_send_msg(PACKETTYPE_CL_CONNECT, writer, name)

			return name, "unknown"
		else:
			return None, "did not send start info"

	async def handle_client(self, reader, writer):
		addr = writer.get_extra_info('peername')
		print(f"Connected client: {addr}")

		disconnect_reason = "unknown"
		name = None

		try:
			name, disconnect_reason = await self.process_client_info(reader, writer, addr)
			if not name:
				return

			while True:
				msg_type = await self.unpack_int(await reader.readexactly(1))
				await self.process_packets(msg_type, reader, writer, addr, name)

		except asyncio.IncompleteReadError:
			print(f"Client {addr} disconnected. reason: {disconnect_reason}")
		except Exception as e:
			print(traceback.format_exc())
		finally:
			if writer in self.clients:
				if name:
					await self.pack_and_send_msg(PACKETTYPE_CL_DISCONNECT, writer, name)
				del self.clients[writer] # remove from dict
			writer.close()
			await writer.wait_closed()
			print(f"Connection with {addr} closed.")

	async def run(self):
		server = await asyncio.start_server(
			self.handle_client, self.host, self.port
		)

		addr = server.sockets[0].getsockname()
		print(f"Server started on {addr}")

		async with server:
			await server.serve_forever()

if __name__ == "__main__":
	server = Server("localhost", 8888)
	try:
		asyncio.run(server.run())
	except KeyboardInterrupt:
		print("Server shutting down...")
