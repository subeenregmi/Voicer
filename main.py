import asyncio
import os
import json
import discord
from discord import FFmpegPCMAudio
from elevenlabs import voices, generate, play, save, set_api_key
from discord.ext import commands

configf = open('config.json', "r")
configf = json.load(configf)
token = configf["discord_token"]
eleven_token = configf["eleven_token"]
TEXT_LIMIT = int(configf["character_per_say"])
TOTAL_SESSION_LIMIT = int(configf["total_session_chars"])
totalsessionchars = 0 

set_api_key(eleven_token)
voices = voices()
allowed = [] 
for x in voices:
	if x.category == "cloned":
		allowed.append(x)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.command()
async def ping(ctx):
	await ctx.send("pong")

@bot.command(pass_context = True)
async def say(ctx, voice:str, text:str):
	global totalsessionchars
	if totalsessionchars + len(text) > TOTAL_SESSION_LIMIT:
		await ctx.send("Limit of total characters in a session has been reached")
		return 

	if len(text) > TEXT_LIMIT:
		await ctx.send(f"Maximum text is set at {TEXT_LIMIT} characters")
		return 

	selectedVoice = None
	for x in allowed:
		if voice.lower() == x.name.lower():
			selectedVoice = x
	if selectedVoice is None:
		await ctx.send("Not a valid voice - use /helper to get voices")
		return

	audio = generate(text=text, voice=selectedVoice)
	save(audio, filename='audio.wav')

	if ctx.author.voice:
		if not ctx.voice_client:
			voicer = await ctx.message.author.voice.channel.connect()
			voicer.play(FFmpegPCMAudio('audio.wav'))
			totalsessionchars += len(text)
		else:
			ctx.voice_client.play(FFmpegPCMAudio('audio.wav'))
	else:
		await ctx.send("You are not in a voice channel.")
		return
	
@bot.command(pass_context = True)
async def leave(ctx):
	if ctx.voice_client:
		await ctx.guild.voice_client.disconnect()	

@bot.command()
async def helper(ctx):
	await ctx.send("Voices that are ready to use:")
	paragraph = ""
	for x in allowed:
		paragraph += (f"* {x.name}\n")
	await ctx.send(paragraph)
	await ctx.send("Use /say {one of the names above} {text in double quotations} in a voice channel to here a deepfaked message")

bot.run(token)
