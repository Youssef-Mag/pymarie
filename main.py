import time
import json

ac = 0
memStart = 4096 # 0x1000 looks cool in addresses, can change it in your code with org
memory = [] #all our memory objects
opcodes = ["add", "subt", "store", "load", "set", "jump", "skipcond", "input", "output", "outputc", "jns", "halt", "clear", "org"]
dataTypes = ["dec", "hex"]
instructions = [] #our formatted and split up assembly file
delay = 0.2 #time between out outputs
live = False #if true shows your program running in real time (outputing every instruction)

def main():
	global memory, instructions, memStart, ac, live
	while True:
		#get file name
		print("Input file name (leave empty for assembly.txt, type c to close)")
		filename = input("> ")
		if filename == "":
			filename = "assembly.txt"
		if filename == 'c':
			return
		#reset everything
		memory = []
		instructions = []
		memStart = 4096
		ac = 0
		#load config so you can change values in runtime
		loadConfig()
		#fetch and run our file
		try:
			run(filename)
		except Exception as e:
			print(str(e))
			continue
		if input("Dump memory? (y/n)") == "y":
			dumpmem()

def run(filename):
	global ac, memStart, instructions, delay, live
	instructions = loadData(filename) #load our instructions
	makeTables() #generate our memory addresses and format our instructions
	pc = 0 #program counter
	while pc < len(instructions): #loop until we reach the last instruction
		
		instruction = list(part for part in instructions[pc].split(' ') if part!='' and "," not in part) #parse the line at pc ()
		arg = 0
		opcode = ""
		printable = ""
		
		if len(instruction) > 0:
				opcode = instruction[0]
				printable = instruction[0]
		if len(instruction) > 1: #finding our operand
			try:
				arg = int(instruction[1])
			except:
				arg = instruction[1]
			printable += " " + str(arg)
		if live:
			print(ac, printable)
			time.sleep(delay)
		if opcode == "add": #add operand to ac
			ac += getArg(arg)
		if opcode == "addi": #add value at operand value in memory to ac 
			ac += getAtAddress(getAtLabel(arg).getValue()).getValue()
		if opcode == "subt": #subtract operand from ac
			ac -= getArg(arg)
		if opcode == "store": #save operand to label
			setMemoryValue(arg, int(ac))
		if opcode == "storei": #save operand to label
			setMemoryValueAddress(getAtLabel(arg).getValue(), ac)
		if opcode == "load": #load operand from label
			ac = getArg(arg)
			if live:
				print("ac ->", ac)
		if opcode == "loadi": #load operand from label
			ac = getAtAddress(getAtLabel(arg).getValue()).getValue()
			if live:
				print("ac ->", ac)
		if opcode == "jump": #jump to label address
			pc = getAtLabel(arg).getAddress()
			continue
		if opcode == "jumpi": #jump to value of label in memory
			pc = getAtLabel(arg).getValue()
			continue
		if opcode == "skipcond": #our conditional statement
			if arg == 000: #if you pass 000 it checks if ac < 0
				if ac < 0:
					pc+=2
					continue
			if arg == 400: #if you pass 400 it checks if ac = 0
				if ac == 0:
					pc+=2
					continue
			if arg == 800: #if you pass 800 it checks if ac > 0
				if ac > 0:
					pc+=2
					continue
		if opcode == "output": #display ac
			print(ac)
			time.sleep(delay)
		if opcode == "outputc": #display ac
			print(chr(ac))
			time.sleep(delay)
		if opcode == "input": #input to ac
			ac = eval(input("AC> "))
		if opcode == "jns":	#jump to label and save the return address to the label's value
			setMemoryValue(arg, pc+1)
			pc = getAtLabel(arg).getAddress()
		if opcode == "clear": #set ac=0
			ac = 0
		if opcode == "org": #set starting memory address
			memStart = arg
		pc += 1
		if opcode == 'halt': #stop when we reach the halt keyword
			break

#Stores all the info about each address
class Memory:
	label = ""
	value = 0 
	type = ""
	address = ""
	def __init__(self, label, value, type, address):
		super(Memory, self).__init__()
		self.label = label
		self.value = value
		self.type = type
		self.address = address

	def getValue(self):
		if self.type == "hex": #turn hex to decimal for internal use
			return int(self.value, 16)
		return int(self.value)

	def getAddress(self):
		return int(str(self.address), 16) #addresses are always saved in hex

	def display(self):
		return str(hex(int(self.address, 16) + memStart)) + " " + str(self.label) + " " + str(self.type) + " " + str(self.value)

#Generate the tables for the lables and jumps
def makeTables():
	i = 0
	for instruction in instructions:
		instruction = instruction.replace("\n", "").replace("\t", " ").lower() #remove newlines that windows makes
		instruction = instruction.split("/")[0] #ignore comments
		instructions[i] = instruction

		split = list(part for part in instruction.split(' ') if part!='') #remove all empty strings in our list
		if len(split) < 1:
			memory.append(Memory(hex(0), hex(0), "hex", hex(i))) #save empty addresses to memory (so we can jumpi to them)
			i+=1
			continue

		label = split[0].split(',')[0] #format the line to our label and argument
		if label in dataTypes:
			split.insert(0, str(hex(0))) #insert 0 if we dont give our labels a name
			label = split[0]

		type = "hex"
		addr = hex(i)
		arg = 0
		if len(split) > 1: #check if it's a proper label
			if split[1] in dataTypes: 
				type = split[1]
				arg = split[2]

		if type == "hex":
			arg = hex(int(str(arg), 16)) #format our address value to hex
		if arg in opcodes or label == addr: #assign a 0 value to proper opcodes 
			arg = 0
		#add to memory
		memory.append(Memory(label, arg, type, addr))
		i+=1

#get our operand
def getArg(arg):
	for mem in memory: #looks for it in memory
		if mem.label == arg:
			return mem.getValue()
	try:
		return int(arg) 
	except:
		return 0

#Set the value at label
def setMemoryValue(label, val):
	global memory
	i = 0
	for mem in memory:
		if mem.label == label:
			if memory[i].type == "hex":
				val = hex(val)
			memory[i].value = val
			if live:
				print(label, "->", val)
			return
		i+=1

#Set the value at label
def setMemoryValueAddress(address, val):
	global memory
	i = 0
	for mem in memory:
		if mem.getAddress()-1 == address:
			if memory[i].type == "hex":
				val = hex(val)
			memory[i].value = val
			if live:
				print(str(hex(address)), "->", val)
			return
		i+=1

#get memory at address
def getAtAddress(address):
	for mem in memory:
		if mem.getAddress()-1 == address:
			return mem
	return memory[0]

#get memory at label
def getAtLabel(label):
	for mem in memory:
		if mem.label == label:
			return mem
	return label

#displays and writes the memory to a file
def dumpmem():
	print("AC:"+str(ac))
	print("memory: ")
	dump = ""
	for mem in memory:
		dump += mem.display() + "\n"
	print(dump)
	f = open("dump.txt", "w")
	f.write(dump)
	f.close()

#reads the file
def loadData(filename):
	f = open(filename, 'r')
	instructions = f.readlines()
	f.close()
	instructionsCopy = instructions.copy()
	i = 0
	for instruction in instructionsCopy:
		instruction = instruction.replace("\t", " ").replace("\n", "").replace(" ", "")
		if instruction == '' or instruction.startswith("/"):
			instructions.pop(i)

			continue
		i+=1
	
	return instructions

#load our config
def loadConfig():
	global delay, live

	f = open("config.json", "r")
	config = json.loads(f.read())
	f.close()
	delay = config['delay']
	live = config['live']



main()