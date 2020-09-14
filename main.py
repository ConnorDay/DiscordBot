import os
import discord
import asyncio
import time
import commands
import json
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

async def helper( client ):
	print("timer")
	start = time.time()
	while time.time() - start < 10:
		#print(time.time() - start)
		await asyncio.sleep(1)
	await client.close()

class Bot(discord.Client):
	async def on_ready(self):
		print(f'{client.user} has connected to Discord!')
		for g in self.guilds:
			if not os.path.exists(f"servers/{g.id}/data"):
				print(f"No data file detected for {g.name}")
				if not os.path.exists("servers"):
					os.mkdir("servers")
				if not os.path.exists(f"servers/{g.id}"):
					os.mkdir("servers/"+str(g.id))
				with open(f"servers/{g.id}/data","w") as f:
					default = {
						"roles" : {},
						"users" : {},
						"commands" : {},
						"games" : {},
						"game_channels" : {},
						"assign_messages" : {},
						"reactions" : {
							"affirmative" : "✅",
							"negative" : "❌",
							"join" : "✋"
						}
					}
					f.write(json.dumps(default))

		#task = asyncio.create_task(helper(client))
	async def on_message(self, message):
		if message.author.bot:
			#this also handles not replying to self
			return
		#if message.author.top_role.permissions.administrator:
			#print("wow you're an admin!")
			#await message.channel.send("wow you're an admin!")
		if message.content[0] == "!": #Temporary for now. There should be an isCommand function somewhere
			cmd, args = message.content[1:].split(maxsplit=1)

			if cmd in commands.translate:
				#$cmd is a valid command
				com = commands.translate[cmd](message, args)
				com.parse()
				com.validate()
				await com.run() #this can potentially be changed to create a new task. This would handle large tasks being run concurrently
		
	async def on_raw_reaction_add( self, payload ):
		if payload.member.bot:
			return
		data = commands.getJson( payload.guild_id )
		if str(payload.message_id) in data['assign_messages']:
			role = payload.member.guild.get_role( data['assign_messages'][str(payload.message_id)] )
			if role:
				await payload.member.add_roles( role )

	async def on_raw_reaction_remove( self, payload ):
		guild = discord.utils.find( lambda x : x.id == payload.guild_id, self.guilds )
		member = guild.get_member(payload.user_id)
		if member.bot:
			return

		data = commands.getJson( payload.guild_id )
		if str(payload.message_id) in data['assign_messages']:
			role = guild.get_role( data['assign_messages'][str(payload.message_id)] )
			if role:
				await member.remove_roles( role )

			

if __name__ == "__main__":
	client = Bot()
	client.run(TOKEN)
