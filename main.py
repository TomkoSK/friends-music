import yt_utils
import discord
from discord.ext import commands
import json
import threading
import string
import random
import os.path

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='sus', intents=intents)

downloadQueue = []
songQueue = []
currentSong = False
vcClient = False
shuffle = False

def playMusic():#TODO: BOT GETS THE LAST SONG OF THE QUEUE STUCK AS CURRENT PLAYING
    global songQueue, vcClient, currentSong
    while True:
        if(vcClient):
            if(not vcClient.is_connected()):
                vcClient.cleanup()
                vcClient = False
                songQueue = []
                currentSong = False
                continue
            if(vcClient and not vcClient.is_playing() and len(songQueue) > 0):
                if(not vcClient.is_connected()):
                    continue
                if(os.path.isfile(f"./audio/{videosDict[songQueue[0]][0]}.mp3")):
                    vcClient.play(discord.FFmpegPCMAudio(source=f"./audio/{videosDict[songQueue[0]][0]}.mp3"))
                else:
                    if(songQueue[0] in downloadQueue):
                        continue
                    else:
                        print(f"[ERROR] COULD NOT PLAY SONG {songQueue[0][1]}")
                currentSong = songQueue[0]
                songQueue = songQueue[1:]
            elif(vcClient and not vcClient.is_playing() and len (songQueue) == 0):
                if(not vcClient.is_connected()):
                    continue
                currentSong = False

musicThread = threading.Thread(target=playMusic, daemon=True)
musicThread.start()

with open("videos.json", "r") as file:
    videosDict = json.load(file)

@bot.command()
async def test(ctx, *args):
    await ctx.reply(" ".join(args))

"""
@bot.command()
async def download(ctx, url):
    videoID = yt_utils.getID(url)
    if(videoID in downloadQueue):
        await ctx.reply("Currently downloading this")
    elif(videoID in videosDict):
        await ctx.reply("This is already downloaded")
    else:
        await ctx.reply("alr downloading")
        thread = threading.Thread(target=downloadVideo, args=[url], daemon=True)
        thread.start()
"""

@bot.command()
async def play(ctx, *args):
    url = " ".join(args)
    global vcClient
    videoID = yt_utils.getID(url)
    if(not url.startswith("https://")):#if user didnt put in URL, it gets made from the video ID
        url = f"https://www.youtube.com/watch?v={videoID}"
    if(not vcClient and not ctx.author.voice):
        await ctx.reply("You aren't in a VC")
    if(not(videoID in videosDict or videoID in downloadQueue)):
        videosDict[videoID] = []
        filename = ''.join(random.choices(string.ascii_letters, k=12))
        videosDict[videoID].append(filename)
        videosDict[videoID].append(yt_utils.getTitle(url))
        videosDict[videoID].append(f"https://www.youtube.com/watch?v={videoID}")
        with open("videos.json", "w") as file:
            json.dump(videosDict, file)
        thread = threading.Thread(target=downloadVideo, args=[url, filename], daemon=True)
        thread.start()
    if(vcClient):
        songQueue.append(videoID)
        await ctx.reply(f"Added **{videosDict[videoID][1]}** to queue")
    elif(ctx.author.voice):
        vcClient = await ctx.author.voice.channel.connect()
        songQueue.append(videoID)
        await ctx.reply(f"Added **{videosDict[videoID][1]}** to queue")

@bot.command()
async def q(ctx):
    global currentSong, songQueue
    answerString = ""
    if(currentSong):
        answerString += "CURRENT SONG:\n"
        title = videosDict[currentSong][1]
        url = videosDict[currentSong][2]
        answerString += f"[{title}](<{url}>)\n"
    answerString += "NEXT SONGS:\n"
    for song in songQueue:
        if(song in downloadQueue):
            answerString += "(DOWNLOADING) "
        title = videosDict[song][1]
        url = videosDict[song][2]
        answerString += f"[{title}](<{url}>)\n"
    if(not currentSong and len(songQueue) == 0):
        await ctx.reply("queue currently empty")
    elif(currentSong and len(songQueue) == 0):
        answerString += "*None*"
        await ctx.reply(answerString)
    else:
        await ctx.reply(answerString)

@bot.command()
async def np(ctx):
    global currentSong, songQueue
    answerString = ""
    if(currentSong):
        answerString += "CURRENT SONG:\n"
        title = videosDict[currentSong][1]
        url = videosDict[currentSong][2]
        answerString += f"[{title}](<{url}>)\n"
    if(answerString == ""):
        await ctx.reply("not playing anything")
    else:
        await ctx.reply(answerString)

@bot.command()
async def kindlygotosleep(ctx):
    if(vcClient):
        await vcClient.disconnect()
        if(vcClient and vcClient.is_playing()):#double checking vcClient because multi threaded code can be annoying
            vcClient.stop()

@bot.command()
async def skip(ctx):
    global vcClient, currentSong
    if(vcClient and vcClient.is_connected() and currentSong):
        vcClient.stop()

@bot.command()
async def shuffle(ctx):
    global shuffle
    shuffle = not shuffle
    if(shuffle):
        await ctx.reply("song shuffling is **on** (not functional yet :yum:)")
    else:
        await ctx.reply("song shuffling is **off**")

def downloadVideo(url, filename):
    videoID = yt_utils.getID(url)
    downloadQueue.append(videoID)
    fileName = yt_utils.download(url, filename)
    downloadQueue.remove(videoID)

bot.run("BOT-TOKEN")