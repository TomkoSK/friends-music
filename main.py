import yt_utils
import discord
from discord.ext import commands
import json
import threading
import string
import random
import os.path
import time

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='sus', intents=intents)

downloadQueue = []
songQueue = []
currentSong = False
vcClient = False
shuffleSongs = False
songStartedAt = 0

def playMusic():
    global songQueue, vcClient, currentSong, songStartedAt
    while True:
        time.sleep(0.5)
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
                if(shuffleSongs):
                    nextSong = random.choice(songQueue)
                else:
                    nextSong = songQueue[0]
                if(os.path.isfile(f"./audio/{videosDict[nextSong][0]}.mp3")):
                    vcClient.play(discord.FFmpegPCMAudio(source=f"./audio/{videosDict[nextSong][0]}.mp3"))
                    songStartedAt = time.time()
                else:
                    if(nextSong in downloadQueue):
                        continue
                    else:
                        print(f"[ERROR] COULD NOT PLAY SONG {nextSong[1]}")
                currentSong = nextSong
                songQueue.remove(nextSong)
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
    await ctx.channel.send(" ".join(args))

"""
@bot.command()
async def download(ctx, url):
    videoID = yt_utils.getID(url)
    if(videoID in downloadQueue):
        await ctx.channel.send("Currently downloading this")
    elif(videoID in videosDict):
        await ctx.channel.send("This is already downloaded")
    else:
        await ctx.channel.send("alr downloading")
        thread = threading.Thread(target=downloadVideo, args=[url], daemon=True)
        thread.start()
"""

@bot.command(aliases=["p"])
async def play(ctx, *args):
    url = " ".join(args)
    global vcClient
    videoID = yt_utils.getID(url)
    if(not url.startswith("https://")):#if user didnt put in URL, it gets made from the video ID
        url = f"https://www.youtube.com/watch?v={videoID}"
    if(not vcClient and not ctx.author.voice):
        await ctx.channel.send("You aren't in a VC")
    if(not(videoID in videosDict or videoID in downloadQueue)):
        videosDict[videoID] = []
        filename = ''.join(random.choices(string.ascii_letters, k=12))
        videosDict[videoID].append(filename)
        videosDict[videoID].append(yt_utils.getTitle(url))
        videosDict[videoID].append(f"https://www.youtube.com/watch?v={videoID}")
        videosDict[videoID].append(yt_utils.getLength(url))
        with open("videos.json", "w") as file:
            json.dump(videosDict, file)
        thread = threading.Thread(target=downloadVideo, args=[url, filename], daemon=True)
        thread.start()
    if(vcClient):
        songQueue.append(videoID)
        await ctx.channel.send(f"Added **{videosDict[videoID][1]}** to queue")
    elif(ctx.author.voice):
        vcClient = await ctx.author.voice.channel.connect()
        songQueue.append(videoID)
        await ctx.channel.send(f"Added **{videosDict[videoID][1]}** to queue")

@bot.command(aliases=["queue"])
async def q(ctx):
    global currentSong, songQueue
    answerString = ""
    if(currentSong):
        answerString += "CURRENT SONG:\n"
        title = videosDict[currentSong][1]
        url = videosDict[currentSong][2]
        length = videosDict[currentSong][3]
        if(length > 3600):
            answerString += f"[{title}](<{url}>) `[{time.strftime('%H:%M:%S', time.gmtime(length))}`]\n"
        else:
            answerString += f"[{title}](<{url}>) `[{time.strftime('%M:%S', time.gmtime(length))}`]\n" 
    answerString += "NEXT SONGS:\n"
    for song in songQueue:
        if(song in downloadQueue):
            answerString += "(DOWNLOADING) "
        title = videosDict[song][1]
        url = videosDict[song][2]
        length = videosDict[song][3]
        if(length > 3600):
            answerString += f"[{title}](<{url}>) `[{time.strftime('%H:%M:%S', time.gmtime(length))}`]\n"
        else:
            answerString += f"[{title}](<{url}>) `[{time.strftime('%M:%S', time.gmtime(length))}`]\n" 
    if(not currentSong and len(songQueue) == 0):
        await ctx.channel.send("queue currently empty")
    elif(currentSong and len(songQueue) == 0):
        answerString += "*None*"
        await ctx.channel.send(answerString)
    else:
        await ctx.channel.send(answerString)

@bot.command()
async def message(ctx, *args):
    message = " ".join(args)
    await ctx.message.delete()
    await ctx.channel.send(message)

@bot.command()
async def remove(ctx, songPlace):
    global songQueue
    index = -1
    try:
        index = int(songPlace)
    except:
        await ctx.channel.send("Invalid song number to remove")
        return
    if(index < 1 or index > len(songQueue)):
        await ctx.channel.send("Invalid song number to remove")
        return
    songQueue.pop(index-1)

@bot.command()
async def np(ctx):
    global currentSong, songQueue
    answerString = ""
    if(currentSong):
        answerString += "CURRENT SONG:\n"
        title = videosDict[currentSong][1]
        url = videosDict[currentSong][2]
        length = videosDict[currentSong][3]
        ongoingTime = int(time.time()-songStartedAt)
        if(length > 3600):
            answerString += f"[{title}](<{url}>) `[{time.strftime('%H:%M:%S', time.gmtime(ongoingTime))}/{time.strftime('%H:%M:%S', time.gmtime(length))}`]\n"
        else:
            answerString += f"[{title}](<{url}>) `[{time.strftime('%M:%S', time.gmtime(ongoingTime))}/{time.strftime('%M:%S', time.gmtime(length))}`]\n" 
    if(answerString == ""):
        await ctx.channel.send("not playing anything")
    else:
        await ctx.channel.send(answerString)

@bot.command(aliases=["leave"])
async def kindlygotosleep(ctx):
    if(vcClient):
        await vcClient.disconnect()
        if(vcClient and vcClient.is_playing()):#double checking vcClient because multi threaded code can be annoying
            vcClient.stop()

@bot.command(aliases=["s"])
async def skip(ctx):
    global vcClient, currentSong
    if(vcClient and vcClient.is_connected() and currentSong):
        vcClient.stop()

@bot.command()
async def shuffle(ctx):
    global shuffleSongs
    shuffleSongs = not shuffleSongs
    if(shuffleSongs):
        await ctx.channel.send("song shuffling is **on**")
    else:
        await ctx.channel.send("song shuffling is **off**")

def downloadVideo(url, filename):
    videoID = yt_utils.getID(url)
    downloadQueue.append(videoID)
    fileName = yt_utils.download(url, filename)
    downloadQueue.remove(videoID)

bot.run("")
