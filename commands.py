import parser

class command:
	def __init__(self, message, cont):
		self.formats = []
		self.valid = False
		self.args = []
		self.definitions = []
		self.overloaded = None
		self.message = message
		self.content = cont
		
	def parse(self):
		message = self.content
		for i, form in enumerate(self.formats):
			copy = message
			self.args = []
			for mode in form:
				if not copy:
					break
				res, copy = mode(copy)
				if not res:
					break
				self.args.append(res)

			else:
				#successfully got through all modes in $form

				if not copy:
					#there are no more leftover arguments
					self.valid = True
					self.overloaded = self.definitions[i]
					break

	async def run(self):
		if not self.valid:
			print("attempted to run an invalid command")
			return
		await self.overloaded(*self.args)

		

	
class ping(command):
	def __init__(self, message, cont):
		super().__init__(message, cont)
		self.formats = [
			[parser.integer, parser.integer],
			[parser.user, parser.integer],
			[parser.role],
			[parser.channel]
		]
		self.definitions = [
			self.handle1,
			self.handle_user,
			self.handle_role,
			self.handle_channel
		]
	async def handle1(self, arg : int , arg2 : int):
		await self.message.channel.send("this should have been an int")
		print(arg, arg2)
	async def handle2(self, arg : str ):
		await self.message.channel.send("this should have been a string: " + arg)
		print(arg)
		print(type(arg))
	async def handle_user(self, arg : int, arg2 : int):
		await self.message.channel.send("you mentioned someone with id: " + str(arg) )
		await self.message.channel.send(str(arg2))
		print(arg)
	async def handle_channel(self, arg : int):
		await self.message.channel.send("you mentioned a channel with id: " + str(arg) )
		print(arg)
	async def handle_role(self, arg : int):
		await self.message.channel.send("you mentioned a role with id: " + str(arg) )
		print(arg)


translate = {
	"ping" : ping
}
