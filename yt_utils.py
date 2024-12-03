import yt_dlp
import string
import random
from urllib.parse import urlparse, parse_qs
import pyyoutube

ytClient = pyyoutube.Client(api_key="AIzaSyAJgzdx8Ix89RoKz7Ek-167LY6SgmeIc9I")

def download(url, filename):
    ydl_opts = {"outtmpl" : f"./audio/{filename}.mp3", "format" : "ba"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def getTitle(url):
    return ytClient.videos.list(video_id=getID(url)).items[0].snippet.title

def getLength(url):#Returns the length of a youtube video by url in a format of seconds
    durationString = ytClient.videos.list(video_id=getID(url)).items[0].contentDetails.duration
    durationSeconds = 0
    try:
        hourIndex = durationString.index("H")
        lengthString = ""
        while True:
            hourIndex -= 1
            if(durationString[hourIndex].isdigit()):
                lengthString += durationString[hourIndex]
            else:
                durationSeconds += int(lengthString[::-1])*3600
                print(durationSeconds)
                break
    except ValueError:
        pass
    try:
        minuteIndex = durationString.index("M")
        lengthString = ""
        while True:
            minuteIndex -= 1
            if(durationString[minuteIndex].isdigit()):
                lengthString += durationString[minuteIndex]
            else:
                durationSeconds += int(lengthString[::-1])*60
                break
    except ValueError:
        pass
    try:
        secondIndex = durationString.index("S")
        lengthString = ""
        while True:
            secondIndex -= 1
            if(durationString[secondIndex].isdigit()):
                lengthString += durationString[secondIndex]
            else:
                durationSeconds += int(lengthString[::-1])
                break
    except ValueError:
        pass
    return durationSeconds

def getID(url):
    if(url.startswith("https://")):
        u_pars = urlparse(url)
        quer_v = parse_qs(u_pars.query).get('v')
        if quer_v:
            return quer_v[0]
        pth = u_pars.path.split('/')
        if pth:
            return pth[-1]
    else:
        ydl_opts = {"extract_flat": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            videoID = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0]["id"]
            return videoID
