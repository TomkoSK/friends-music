import yt_dlp
from urllib.parse import urlparse, parse_qs

arg = input()
def getID(url):
    u_pars = urlparse(url)
    quer_v = parse_qs(u_pars.query).get('v')
    if quer_v:
        return quer_v[0]
    pth = u_pars.path.split('/')
    if pth:
        return pth[-1]

print(getID(arg))
ydl_opts = {"outtmpl" : f"./audio/TESTING.mp3", "format" : "ba"}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    video = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]["id"]
print(video)