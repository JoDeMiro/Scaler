# deadline.py

from termcolor import colored

def printTest(value):

	print(colored('---------------------------------------', 'yellow'))

	print(colored(value, 'yellow'))

	print(colored('---------------------------------------', 'yellow'))


def printToDo(value):

	print(colored('---------------------------------------', 'cyan'))

	print(colored(value, 'cyan'))

	print(colored('---------------------------------------', 'cyan'))

def printColor(text, color):

	print(colored('---------------------------------------', color))

	print(colored(text, color))

	print(colored('---------------------------------------', color))


def printBlink(text, color):

	print(colored('---------------------------------------', color))

	print(colored(text, color, attrs=["reverse", "blink"]))

	print(colored('---------------------------------------', color))

# https://pypi.org/project/termcolor
