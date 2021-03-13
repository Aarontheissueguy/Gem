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
import pyotherside
import pickle
import time
import re
import gopher


storage_dir = "/home/phablet/.local/share/gem.aaron"

class Gemini:
    def __init__(self):
        self.makeDirs()
        self.page_cache = {}
        # Load history
        history_data = self.read_file("history.dat")
        self.history = history_data if history_data != None else []
        # Load future
        future_data = self.read_file("future.dat")
        self.future = future_data if future_data != None else []
        # cache_limit prevents all pages from being cached
        self.cache_limit = 5

    def read_file(self, filename):
        filepath = "{}/{}".format(storage_dir, filename)

        if os.path.exists(filepath):
            file = self.open_file(filepath, "rb")
            return pickle.load(file)


        return None

    def save_data(self):
        print("Persisting")
        future_file = self.open_file("future.dat", "wb")
        pickle.dump(self.future, future_file)

        history_file = self.open_file("history.dat", "wb")
        pickle.dump(self.history, history_file)

    def makeDirs(self):
        try:
            os.mkdir(storage_dir)
            open("{}/history.dat".format(storage_dir), "wb").close()
            open("{}/future.dat".format(storage_dir), "wb").close()
        except:
            pass

    def open_file(self, filename, mode="r+"):
        try:
            f = open(filename, mode)
        except:
            file_path = "{}/{}".format(storage_dir, filename)
            f = open(file_path, mode)

        return f

    def absolutise_url(self, base, relative):
        # Absolutise relative links
        if "://" not in relative:
            # Python's URL tools somehow only work with known schemes?
            base = re.sub("gemini://", "http://", base, flags=re.IGNORECASE)
            relative = urllib.parse.urljoin(base, relative)
            relative = re.sub("http://", "gemini://", relative, flags=re.IGNORECASE)
        return relative

    def get_site(self, url):
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
                url = self.absolutise_url(url, mime)
                parsed_url = urllib.parse.urlparse(url)
            # Otherwise, we're done.
            else:
                mime, mime_opts = cgi.parse_header(mime)
                body = fp.read()
                body = body.decode(mime_opts.get("charset","UTF-8"))
                return str(body)
                break

    def get_links(self, body, url):
        links = []
        for line in body.splitlines():
            if line.startswith("=>"):
                bits = line[2:].strip().split(maxsplit=1)
                link_url = bits[0]
                link_url = self.absolutise_url(url, link_url)
                links.append(link_url)
        return links

    def instert_html_links(self, body, links):
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

    def top(self, stack):
        stack_size = len(stack)

        if stack_size == 0:
            return None

        return stack[stack_size - 1]

    def back(self):
        if len(self.history) == 1:
            return self.load(self.history[0], True)

        self.future.append(self.history.pop())
        url = self.top(self.history)

        if len(self.future) > 0:
            pyotherside.send('showForward')

        return self.load(url, True)

    def forward(self):
        self.history.append(self.future.pop())
        url = self.top(self.history)

        if len(self.future) == 0:
            pyotherside.send('hideForward')

        return self.load(url, True)

    def goto(self, _url):
        if "://" not in _url:
            url = "gemini://" + _url
        else:
            url = _url

        if url.split(':')[0] in ["https", "http:"]:
            return pyotherside.send('externalUrl', url)



        self.history.append(url)

        # Reset the future.
        self.remove_from_cache(self.future)
        self.future = []
        pyotherside.send('hideForward')

        return self.load(url)

    def load_initial_page(self):
        if len(self.history) > 0:
            url = self.top(self.history)
            self.load(url)
        else:
            self.load("gemini://gemini.circumlunar.space/servers/")

    def cache_page(self, url, content):
        self.page_cache[url] = {
            "content": content,
            "timestamp": time.time()
        }

    def prune_cache(self):
        # Find urls that are too old to be cached
        old_history = self.history[self.cache_limit:]
        old_future = self.future[self.cache_limit:]
        old_urls = old_history.extend(old_future)

        if old_urls:
            self.remove_from_cache(old_urls)

    def remove_from_cache(self, url_list):
        # Removes cached values for the provided list of urls
        for url in url_list:
            if url in self.page_cache:
                del self.page_cache[url]

    def load(self, url, using_cache = False):
        if len(self.history) > self.cache_limit or len(self.future) > self.cache_limit:
            self.prune_cache()
        self.prune_cache()
        pyotherside.send('loading', url)

        if using_cache and url in self.page_cache:
            return pyotherside.send('onLoad', self.page_cache[url]['content'])


        if "gopher://" in url or "Gopher://" in url:
            try:
                gophsite = gopher.get_content(url)
                self.cache_page(url, gophsite)
                pyotherside.send('onLoad', gophsite)
            except Exception as e:
                print("Error:", e)
                pyotherside.send('onLoad', "uhm... seems like this site does not exist, it might also be bug <br> ¯\_( ͡❛ ͜ʖ ͡❛)_/¯")
            return;


        try:

            gemsite = self.get_site(url)
            gemsite = self.instert_html_links(gemsite, self.get_links(gemsite, url))
            self.cache_page(url, gemsite)

            pyotherside.send('onLoad', gemsite)
        except Exception as e:
            print("Error:", e)
            pyotherside.send('onLoad', "uhm... seems like this site does not exist, it might also be bug <br> ¯\_( ͡❛ ͜ʖ ͡❛)_/¯")

        return;

gemini = Gemini()
pyotherside.atexit(gemini.save_data)
