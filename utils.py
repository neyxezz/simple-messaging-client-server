import ipaddress
import json
from colors import *

def load_config():
	try:
		with open("config.json", "r") as f:
			return json.load(f)
	except:
		data = {"name": None, "ip_port": None}
		with open("config.json", "w") as f:
			json.dump(data, f, ensure_ascii=False)
		return data

def save_config(data):
	with open("config.json", "w") as f:
		json.dump(data, f, ensure_ascii=False)

def is_ipv4(address):
	try:
		ip_part, port_part = address.rsplit(':', 1)
		if ip_part != "localhost":
			ipaddress.IPv4Address(ip_part)
		port = int(port_part)
		if 0 <= port <= 65535:
			return True
		else:
			return False
	except:
		return False

def get_ipv4(address):
	return address.split(":")

def get_values(config):
	while (not config["name"] or not(0 < len(config["name"]) < 255)) or (not is_ipv4(config["ip_port"])):
		if not config["name"] or not(0 < len(config["name"]) < 255):
			name = input(to_yellow("1. Enter your name: "))
			if not name or not(0 < len(name) < 255):
				print("Name is empty or contains more or less 1-255 chars")
				continue
			config["name"] = name

		if not is_ipv4(config["ip_port"]):
			ip_port = input(to_yellow("2. Enter IP address and port (e.g. 255.255.255.255:65536): "))
			if not is_ipv4(ip_port):
				print("Invalid IPv4 address")
				continue
			config["ip_port"] = ip_port
	save_config(config)
	return config
