

import sys
sys.path.append('deps')
sys.path.append('../deps')
import pituophis


port = 70 #this is the default port for gopher
path = '/'
query = ''
binary = False
menu = False
tls = False

def get_content(url):

    #Workaround start#
    urllist = url.split("/")
    result = ["/"] * (len(urllist) * 2 - 1)
    result[0::2] = urllist
    urllist = result
    urllist.insert(5, "/")
    url = ""
    for element in urllist:
        url += element
    #Workaround stop#
    '''
    for some reason the line below deletes the first letter after
    the second and only the second "/" even if I pass in everything directly.
    I think that is not an issue on our side so I decided to workarround it
    '''
    response = pituophis.get(url, port=port, path=path, query=query, tls=tls)
    content = ""
    for line in response.text().splitlines():
        if line.startswith("i") or line.startswith("!"):
            line = line[1:]
            line = line.split("\t")[0]
            content += line + "<br>"
        elif line.startswith("0") or line.startswith("1"):
            line = line[1:]
            line = line.split("\t")
            line = '<br><a style="color: #FFC0CB" href="gopher://'+line[-2]+line[-3] +'">'+line[0]+'</a><br>'
            content += line + "<br>"
        else:
            content += line + "<br>"
    return content


'''
0 Text Datei
1 Verzeichnis
3 Fehlermeldung
5 Archive Datei (zip, tar etc)
7 Suchabfrage
8 Telnet Session
9 Binäre Datei
g GIF (Bilder)
h HTML Dateien
i Info Text
I andere Bilddateien (außer GIF)
d Dokumente (ps, pdf, doc etc)
s sound file
; video file
c calendar file
M MIME file (mbox, emails etc)
'''
