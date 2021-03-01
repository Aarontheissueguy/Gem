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
        status, mime = header.split()
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



def instert_md_links(body, links):
    mdBody = ""
    for line in body.splitlines():
        if "=>" in line:
            try:
                line =  '<a href="'+links[0]+'">'+line+'</a>'
                del links[0]
                mdBody += line
                mdBody += "<br>"
                #print("here")
            except:
                mdBody += line
                #print("err")
                pass
        else:
            #print("nolink")
            mdBody += line + "\n"
            mdBody += "<br>"
    return mdBody



def main(url):
    return instert_md_links(get_site(url),get_links(get_site(url), url))
