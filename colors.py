# colors.py

COLOR = "\033[{}m"

RESET = COLOR.format(0)

RED = COLOR.format(31)
GREEN = COLOR.format(32)
YELLOW = COLOR.format(33)
BLUE = COLOR.format(34)
PURPLE = COLOR.format(35)
CYAN = COLOR.format(36)

def to_red(string):
	return f"{RED}{string}{RESET}"

def to_green(string):
	return f"{GREEN}{string}{RESET}"

def to_yellow(string):
	return f"{YELLOW}{string}{RESET}"

def to_blue(string):
	return f"{BLUE}{string}{RESET}"

def to_purple(string):
	return f"{PURPLE}{string}{RESET}"

def to_cyan(string):
	return f"{CYAN}{string}{RESET}"
