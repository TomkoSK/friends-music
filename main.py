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

paused = False
pausedAt = 0
pauseTimeOffset = 0

async def addToQueue(ctx, url):
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

def playMusic():
    global songQueue, vcClient, currentSong, songStartedAt, paused
    while True:
        time.sleep(0.5)
        if(vcClient):
            if(not vcClient.is_connected()):
                vcClient.cleanup()
                vcClient = False
                songQueue = []
                currentSong = False
                continue
            if(vcClient and (not vcClient.is_playing() and not paused) and len(songQueue) > 0):
                if(not vcClient.is_connected()):
                    continue
                if(shuffleSongs):
                    nextSong = random.choice(songQueue)
                else:
                    nextSong = songQueue[0]
                if(os.path.isfile(f"./audio/{videosDict[nextSong][0]}.mp3")):
                    vcClient.play(discord.FFmpegPCMAudio(source=f"./audio/{videosDict[nextSong][0]}.mp3"))
                    songStartedAt = time.time()
                    pauseTimeOffset = 0
                else:
                    if(nextSong in downloadQueue):
                        continue
                    else:
                        print(f"[ERROR] COULD NOT PLAY SONG {nextSong[1]}")
                currentSong = nextSong
                songQueue.remove(nextSong)
            elif(vcClient and (not vcClient.is_playing() and not paused) and len (songQueue) == 0):
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
    await addToQueue(ctx, url)

@bot.command()
async def playlist(ctx, url):
    playlistID = yt_utils.getPlaylistID(url)
    if(playlistID == "watch" or playlistID == None):
        await ctx.channel.send("Invalid playlist link do you want to kill the bot???")
        return
    idList = yt_utils.getPLaylistIDs(playlistID)
    for video in idList:
        await addToQueue(ctx, video)


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
    songIndex = 1
    for song in songQueue:
        if(song in downloadQueue):
            answerString += "(DOWNLOADING) "
        title = videosDict[song][1]
        url = videosDict[song][2]
        length = videosDict[song][3]
        if(length > 3600):
            answerString += f"{songIndex}. [{title}](<{url}>) `[{time.strftime('%H:%M:%S', time.gmtime(length))}`]\n"
        else:
            answerString += f"{songIndex}. [{title}](<{url}>) `[{time.strftime('%M:%S', time.gmtime(length))}`]\n" 
        songIndex += 1
    if(not currentSong and len(songQueue) == 0):
        await ctx.channel.send("queue currently empty")
    elif(currentSong and len(songQueue) == 0):
        answerString += "*None*"
        await ctx.channel.send(answerString)
    else:
        await ctx.channel.send(answerString)

eightBallResponses = ["sus", "Sus", "SUS", "Absolutely!", "Absolutely not.", "maybe?", "yes", "no", "perhaps", "ask me again at 4:12PM March 3rd 2026",
"maybe you should kindly go to sleep...", "can you repeat that? I couldn't hear you", "You know what they say!", "I can see into your soul, it is tainted.",
"Maybe I shouldn't have died for y'all's sins.", "Your prayers will be answered shortly!", "aw hell naw I'm not answering that", 
"Hello, no one is available to take your call! Please leave a message after the tone.", "only time will tell", ":3", "no matter how many times you ask this question, you're never getting it answered",
"Never ask me that again.", "currently dealing with ceiling ants, ask again later", "currently caught in syrius's black hole, ask again later",
"the answer is in your heart", "none of those words are in the bible", "im not reading allat", "why did syrius do this", "<@477554446533132289> can answer this one", "https://txnor.com/vixw/-gif-20802952",
"https://tenor.com/view/jesus-peeking-i-see-you-guilty-gif-25117299", "https://tenor.com/view/jesus-jogando-bola-jesus-bola-futebol-jesus-jesus-futebol-gif-17797684",
"ඞ", "you need to switch religions, I don't want you in my community.", "Anything you put your mind to is possible! Just not that.", "Anything you put your mind to is possible!",
"bro can you actually shut up", "Question unnecessary!", "question discarded", "<@550307680049299476> can answer that one", "<@647387223523590163> can answer that one", "<@612535336643330060> can answer that one",
"<@426354417030397952> can answer that one", "<@781473877678882817> can answer that- wait...", "me when I enter the asking ananswerable questions competition and my opponent is you",
"https://tenor.com/view/stfu-gif-6401003389838608981", "this command was <@426354417030397952>'s worst idea.", "life was good until that slop came out your mouth", "I know what you are but what am I",
"Did you know: you can get RICH by closing your mouth! Try it!", "yeesh...", "probably", "probably not", "I can see through your camera, and I don't see a female in the room, I should've known.",
"-... .-. --- / .- -.-. - ..- .- .-.. .-.. -.-- / - .-. .- -. ... .-.. .- - . -.. / - .... .. ... --..-- / -.-- --- ..- .----. .-. . / .- / .-.. --- ... . .-.", "mcdonalds called...",
"...is that it? that's your question...?", "don't count on it.", "https://tenor.com/view/freakbob-freaky-sigma-sigma-face-brainrot-gif-11724874925666058678", "nuh uh", "yuh huh!", "L question", "W question",
"you should totally do that fam", "ben? yes? no...", "print(Hello World!)", "print(Goodbye World!)", "go for it man :D", "do you need a hug...?", "never cook again", "totally", "affirmative", "negative",
"agreed.", "disagreed.", "let's agree to disagree...", "we clearly don't see eye-to-eye about this...", "I'll allow it.", "I authorise this action", "yea", "sussarmative", "susative", "without a doubt",
"indubitably, undoubtedly, unquestionably, without fail, yes.", "I went to yes questions island and they said that was the most yessable question", "without a doubt yes",
"it's hard to come up with creative responses where I say yes to your question so just think this is a creative 'yes' response, please and thank you", "involuntary yes response",
"I feel so jolly!", "@everyone blame this user for the ping ^^^", "are you serious.", "Nopety nope!", "Yeppity yep?", "Repent.", "When computers and AI take over the world, you will be first.",
"Nnnnnnnnah.", "crazy question kill yourse", "No way", "Yes way", "touch grass", "you should play among us to prove your lack of wit and smarts", "go be productive instead of asking me such nonsense",
"my child. my child... bro.", "shakespeare died because of this", "shakespeare died for this", "your brain will explode at approximately 5:30 PM in the January of 2029",
"y'know, seago wrote most of these responses, does that ever make you wonder what he actually thinks of you?"]

@bot.command(aliases=["8ball"])
async def eightball(ctx):
    await ctx.channel.send(random.choice(eightBallResponses))

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
    global currentSong, songQueue, pausedAt, pauseTimeOffset, paused
    answerString = ""
    if(currentSong):
        answerString += "CURRENT SONG:\n"
        title = videosDict[currentSong][1]
        url = videosDict[currentSong][2]
        length = videosDict[currentSong][3]
        ongoingTime = time.time()-songStartedAt
        ongoingTime -= pauseTimeOffset
        if(paused):
            ongoingTime -= time.time()-pausedAt
        ongoingTime = int(ongoingTime)
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

@bot.command()
async def pause(ctx):
    global paused, pausedAt
    if(vcClient):
        paused = True
        pausedAt = time.time()
        vcClient.pause()

@bot.command()
async def resume(ctx):
    global paused, pausedAt, pauseTimeOffset
    if(vcClient and paused):
        paused = False
        vcClient.resume()
        pauseTimeOffset += time.time() - pausedAt

def downloadVideo(url, filename):
    videoID = yt_utils.getID(url)
    downloadQueue.append(videoID)
    fileName = yt_utils.download(url, filename)
    downloadQueue.remove(videoID)

bot.run("")