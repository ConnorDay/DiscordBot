import os
import discord
import asyncio
import time
import commands
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
		task = asyncio.create_task(helper(client))
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
				await com.run() #this can potentially be changed to create a new task. This would handle large tasks being run concurrently

			

client = Bot()
client.run(TOKEN)
