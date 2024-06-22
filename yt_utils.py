import yt_dlp
import string
import random
from urllib.parse import urlparse, parse_qs
import pyyoutube

ytClient = pyyoutube.Client(api_key="API-KEY")

def download(url, filename):
    ydl_opts = {"outtmpl" : f"./audio/{filename}.mp3", "format" : "ba"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def getTitle(url):
    return ytClient.videos.list(video_id=getID(url)).items[0].snippet.title

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