import parser
import json
import os
import discord

def getJson(guild : int):
	path = f"servers/{guild}/data"
	if os.path.exists(path):
		with open(path, "r") as f:
			data = json.loads(f.read())
	return data

def setJson(guild : int, data):
	path = f"servers/{guild}/data"
	if os.path.exists(path):
		with open(path, "w") as f:
			f.write(json.dumps(data))

async def printGameMessage( game : str, guild ):
	data = getJson( guild.id )
	if 'assign' not in data:
		return

	res = discord.utils.find( lambda x : x.id == data['assign'], guild.text_channels )

	mes = await res.send(f"Game: `{game}`\nReact to this if you would like to join")
	await mes.add_reaction(data['reactions']['join'])

	role = discord.utils.find( lambda x : x.name == game, guild.roles )
	if not role:
		role = await guild.create_role( name = game )
	data["assign_messages"][mes.id] = role.id
	print(mes.id)

	setJson( guild.id, data )
	
	

class command:
	def __init__(self, message, cont):
		self.formats = []
		self.definitions = []

		self.args = []

		self.valid = False
		self.overloaded = None

		self.message = message
		self.content = cont
		
		self.access = 0
	
	def getAccess(self, name):
		data = getJson(self.message.guild.id)
		if data:
			if name in data['commands']:
				self.access = data['commands'][name]
		
		
	def parse(self):
		message = self.content
		for i, form in enumerate(self.formats):
			copy = message
			self.args = []
			for mode in form:
				if not copy:
					break
				res, copy = mode(copy)
				if res == "":
					break
				self.args.append(res)

			else:
				#successfully got through all modes in $form
				if not copy:
					#there are no more leftover arguments
					self.valid = True
					self.overloaded = self.definitions[i]
					break
	
	def validate(self):
		if not self.valid:
			return

		#admins can always run all commands
		if self.message.author.top_role.permissions.administrator:
			return

		access = 0
		target = self.message.author.id
		data = getJson(self.message.guild.id)
		if data:

			#check if user has an access level
			if target in data['users']:
				access = data['users'][target]

			#get the highest access role that the user has
			for role in self.message.author.roles:
				if role.id in data['roles']:
					access = max( access, data['roles'][role.id] )


		if access < self.access:
			self.valid = False
			self.reason = "User not authorized for that command"


	async def run(self):
		if not self.valid:
			await self.message.channel.send("Could not interpret use of command")
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

		self.getAccess('ping')
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


class setLevel(command):
	def __init__(self, message, cont):
		super().__init__(message, cont)
		self.formats = [
			[parser.user, parser.integer],
			[parser.role, parser.integer],
			[parser.word, parser.integer],
			[parser.channel, parser.word],
			[parser.word, parser.word, parser.word]
		]
		self.definitions=[
			self.set_user,
			self.set_role,
			self.set_command,
			self.set_channel,
			self.set_reaction
		]
		self.getAccess('set')
	async def confirmation( self, overload : str, name , level : int ):
		if type(name) == int:
			res = discord.utils.find( lambda x : x.id == name, self.message.guild.members )
			if res:
				name = res.mention
			else:
				self.message.channel.send(f"Unable to find {overload} with id: {res}")
		await self.message.channel.send(f"Successfully changed {overload} {name}'s access level to {level}")

	async def set_user( self, user : int, level : int ):
		data = getJson(self.message.guild.id)
		if data:
			data['users'][user] = level
			setJson(self.message.guild.id,data)
			await self.confirmation( "user", user, level )

	async def set_role( self, role : int, level : int ):
		data = getJson(self.message.guild.id)
		if data:
			data['roles'][role] = level
			setJson(self.message.guild.id,data)
			await self.confirmation( "role", role, level )

	async def set_command( self, command : str, level : int):
		data = getJson(self.message.guild.id)
		if data:
			data['commands'][command] = level
			setJson(self.message.guild.id,data)
			await self.confirmation( "command", command, level )

	async def set_channel( self, channel : int, key : str):
		types = ["assign", "admin", "logging"]
		if key.lower() not in types:
			await self.message.channel.send(f"Unknown channel type: {key}")
			return

		data = getJson(self.message.guild.id)
		data[key.lower()] = channel
		setJson(self.message.guild.id,data)
		
		res = discord.utils.find( lambda x : x.id == channel, self.message.guild.text_channels )
		if key.lower() == "assign":
			for game in data['games']:
				await printGameMessage( game, self.message.guild )

		temp = await self.message.channel.send(f"Successfully set {res.mention} to {key.lower()}")
	
	async def set_reaction( self, command, arg1, arg2 ):
		data = getJson(self.message.guild.id)
		if command == "reaction":
			types = list(data['reactions'].keys())
			specifier = arg1.lower()
			if specifier not in types:
				await self.message.channel.send(f"Unknown specifier {arg1}. Pleas choose from `{' '.join(types)}`")
				return

			try:
				await self.message.add_reaction(arg2)
			except:
				await self.message.channel.send(f"Cannot use `{arg2}` as an emoji")
				return
			else:
				data['reactions'][specifier] = arg2
				setJson(self.message.guild.id, data)
				await self.message.channel.send(f"Successfully added `{arg2}` as `{specifier}`")

class game(command):
	def __init__(self, message, cont):
		super().__init__(message, cont)
		self.formats = [
			[parser.word, parser.word]
		]
		self.definitions = [
			self.manageGame
		]
		self.getAccess('set')
	
	async def manageGame( self, cmd : str, game : str ):
		commands = {
			"add" : self.addGame,
			"remove" : self.removeGame
		}
		if cmd.lower() not in commands:	
			await self.message.channel.send( f"Unknown specifier {cmd}" )
			return

		await commands[cmd.lower()]( game, getJson(self.message.guild.id) )
		
	async def addGame( self, game : str, data ):
		role = discord.utils.find( lambda x : x.name == game, self.message.guild.roles )
		if not role:
			role = await self.message.guild.create_role( name = game )
		data['games'][game] = role.id
		channel = discord.utils.find( lambda x : x.name == game, self.message.guild.text_channels )
		if not channel:
			overwrites = {
				self.message.guild.default_role : discord.PermissionOverwrite(read_messages=False),
				role : discord.PermissionOverwrite(read_messages=True)
			}
			category = await self.message.guild.create_category( game, overwrites = overwrites )
			channel = await self.message.guild.create_text_channel( game, overwrites = overwrites, category = category )
			voice = await self.message.guild.create_voice_channel( game, overwrites = overwrites, category = category )
		data['game_channels'][channel.id] = game

		await printGameMessage( game, self.message.guild )

		setJson( self.message.guild.id, data )
		
	
	async def removeGame( self, game : str, data ):
		if game not in data['games']:
			await self.message.channel.send(f"`{game}` is not stored as a game")
			return

		#Find and delete role
		role = self.message.guild.get_role( data['games'][game] )
		del data['games'][game]
		roleID = role.id
		await role.delete()
		
		#Find and delete category (with child channels)
		for channel in data['game_channels']:
			if data['game_channels'][channel] == game:
				del data['game_channels'][channel]
				break

		cat = discord.utils.find( lambda x : x.name == game, self.message.guild.categories )
		if cat:
			for channel in cat.channels:
				await channel.delete()
			await cat.delete()

		#Find and delete role assign message
		for mes in data['assign_messages']:
			if data['assign_messages'][mes] == roleID:
				del data['assign_messages'][mes]
				break
		else:
			mes = None

		if data['assign'] and mes:
			assign = self.message.guild.get_channel(data['assign'])
			message = await assign.fetch_message( mes )
			await message.delete()

		setJson(self.message.guild.id, data)

		await self.message.channel.send(f"Successfully removed `{game}`")



translate = {
	"ping" : ping,
	"set" : setLevel,
	"game" : game
}
