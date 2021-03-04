'''
Great parts of this code were copied and modified from this project(https://tildegit.org/solderpunk/gemini-demo-1).
I wouldnt have been able to do this without this resource. Thanks for the awsome code.
'''


import cgi
import mailcap
import os
import socket
import ssl
import tempfile
import textwrap
import urllib.parse
def makeDirs():
    try:
        os.mkdir("/home/phablet/.local/share/gem.aaron/")
    except:
        pass

def absolutise_url(base, relative):
    # Absolutise relative links
    if "://" not in relative:
        # Python's URL tools somehow only work with known schemes?
        base = base.replace("gemini://","http://")
        relative = urllib.parse.urljoin(base, relative)
        relative = relative.replace("http://", "gemini://")
    return relative

def get_site(url):
    parsed_url = urllib.parse.urlparse(url)
    while True:
        s = socket.create_connection((parsed_url.netloc, 1965))
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        s = context.wrap_socket(s, server_hostname = parsed_url.netloc)
        s.sendall((url + '\r\n').encode("UTF-8"))
        # Get header and check for redirects
        fp = s.makefile("rb")
        header = fp.readline()
        header = header.decode("UTF-8").strip()
        status, mime = header.split()[:2]
        # Handle input requests
        if status.startswith("1"):
            # Prompt
            query = input("INPUT" + mime + "> ")
            url += "?" + urllib.parse.quote(query) # Bit lazy...
            # Follow redirects
        elif status.startswith("3"):
            url = absolutise_url(url, mime)
            parsed_url = urllib.parse.urlparse(url)
        # Otherwise, we're done.
        else:
            mime, mime_opts = cgi.parse_header(mime)
            body = fp.read()
            body = body.decode(mime_opts.get("charset","UTF-8"))
            return str(body)
            break

def get_links(body, url):
    links = []
    for line in body.splitlines():
        if line.startswith("=>"):
            bits = line[2:].strip().split(maxsplit=1)
            link_url = bits[0]
            link_url = absolutise_url(url, link_url)
            links.append(link_url)
    return links



def instert_html_links(body, links):
    mdBody = ""
    for line in body.splitlines():
        if "=>" in line:
            try:
                line =  '<a style="color: #FFC0CB" href="'+links[0]+'">'+line+'</a>'
                del links[0]
                mdBody += line
                mdBody += "<br>"
                mdBody += "<br>"
                #print("here")
            except:
                mdBody += line
                #print("err")
                pass
        elif line.startswith("#"):
            if line.startswith("###"):
                line = line.replace("###", "<h3>")
                line += "</h3>"
                mdBody += line
            elif line.startswith("##"):
                line = line.replace("##", "<h2>")
                line += "</h2>"
                mdBody += line
            elif line.startswith("#"):
                line = line.replace("#", "<h1>")
                line += "</h1>"
                mdBody += line
            else:
                pass

        else:
            #print("nolink")
            mdBody += line + "\n"
            mdBody += "<br>"
            mdBody += "<br>"
    return mdBody


def where_am_I(direction):
    try:
        try:
            makeDirs()
            f = open("where_am_I.txt", "r")
        except:
            makeDirs()
            f = open("/home/phablet/.local/share/gem.aaron/where_am_I.txt", "r")
    except:
        try:
            makeDirs()
            f = open("where_am_I.txt", "w+")
        except:
            makeDirs()
            f = open("/home/phablet/.local/share/gem.aaron/where_am_I.txt", "w+")
    current = f.read()

    if direction == "forward":
        try:
            current =int(current) + 1
        except:
            current = int(0)
    if direction == "backward" and int(current) > 0:
        try:
            current =int(current) - 1
        except:
            current = int(0)

    f.close()
    try:
        f = open("where_am_I.txt", "w")
    except:
        f = open("/home/phablet/.local/share/gem.aaron/where_am_I.txt", "w")
    f.write(str(current))


    f.close()
    return current

def history(url):
    try:
        makeDirs()
        f = open("history.txt", "a")
    except:
        makeDirs()
        f = open("/home/phablet/.local/share/gem.aaron/history.txt", "a")
    f.write(","+url)
    f.close()

def back():
    index = where_am_I("backward")
    try:
        makeDirs()
        f = open("history.txt", "r")
    except:
        makeDirs()
        f = open("/home/phablet/.local/share/gem.aaron/history.txt", "r")
    history = f.read().split(",")
    url = history[index+1]
    f.close()
    try:
        makeDirs()
        f = open("history.txt", "w")
    except:
        makeDirs()
        f = open("/home/phablet/.local/share/gem.aaron/history.txt", "w")
    newHist = "" #were rewriting history lmao
    for element in history[1:index+2]:
         newHist += "," + element
    f.write(newHist)
    f.close()

    return str(url)

def main(url):
    try:
        gemsite = get_site(url)
        returnValue = instert_html_links(gemsite, get_links(gemsite, url))
#        where_am_I("forward")
#        history(url)
        return {
            'status': 'success',
            'content': returnValue
        }
    except Exception as e:
#        where_am_I("forward")
#        history(url)
        return {
            'status': 'error',
            'content': "uhm... seems like this site does not exist, it might also be bug <br> ¯\_( ͡❛ ͜ʖ ͡❛)_/¯",
            'message': str(e)
        }
        return
