'''
Great parts of this code were copied and modified from this project(https://tildegit.org/solderpunk/gemini-demo-1).
I wouldnt have been able to do this without this resource. Thanks for the awsome code.
'''


import cgi
import os
import socket
import ssl
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

        self.migrate_to_page_context()

        # cache_limit prevents all pages from being cached
        self.cache_limit = 5
        self.current_url = None

    def migrate_to_page_context(self):
        # Migrate from simple url strings in the history to dictionaries
        # The dictionaries currently contain the url and scroll height of the page.
        # In the future they can also hold other information for page context.

        self.history = [
            self.create_page_context(item, 0) if type(item) is str else item
            for item in self.history
        ]

        self.future = [
            self.create_page_context(item, 0) if type(item) is str else item
            for item in self.future
        ]

    def read_file(self, filename):
        filepath = "{}/{}".format(storage_dir, filename)
        try:
            if os.path.exists(filepath):
                file = self.open_file(filepath, "rb")
                return pickle.load(file)
        except:
            return []


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
            # Handle port numbers in the url (defaults to 1965)
            netloc_data = parsed_url.netloc.split(":")
            netloc = netloc_data[0]
            port_number = int(netloc_data[1]) if len(netloc_data) > 1 else 1965

            s = socket.create_connection((netloc, port_number))
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            s = context.wrap_socket(s, server_hostname = netloc)
            s.sendall((url + '\r\n').encode("UTF-8"))
            # Get header and check for redirects
            fp = s.makefile("rb")
            header = fp.readline()
            header = header.decode("UTF-8").strip()
            status, meta = header.split()[:2]
            # Handle input requests
            if status.startswith("1"):
                # Prompt with message from server (in meta)
                is_secret = status == "11"

                pyotherside.send('requestInput', meta, is_secret)

                self.current_url = url
                break
                # Follow redirects
            elif status.startswith("3"):
                url = self.absolutise_url(url, meta)
                parsed_url = urllib.parse.urlparse(url)
            # Otherwise, we're done.
            else:
                mime, mime_opts = cgi.parse_header(meta)
                body = fp.read()
                body = body.decode(mime_opts.get("charset","UTF-8"))
                return str(body)

    def handle_input(self, inputText):
        new_url = self.current_url
        new_url += "?" + urllib.parse.quote(inputText)

        self.current_url = None
        self.goto(new_url)

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
        inside_pre_block = False
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
            elif "```" in line:
                print(line, flush=True)
                if inside_pre_block:
                    mdBody += "</pre>"
                    inside_pre_block = False
                else:
                    mdBody += "<pre style='font-size: 12px'>"
                    inside_pre_block = True

            else:
                mdBody += line
                mdBody += "\n"
                if not inside_pre_block:
                #print("nolink")
                    mdBody += "<br>"
        return mdBody

    def top(self, stack):
        stack_size = len(stack)

        if stack_size == 0:
            return None

        return stack[stack_size - 1]

    def create_page_context(self, url, scroll_height):
        return {
            "url": url,
            "scroll_height": scroll_height
        }

    def update_scroll_height(self, scroll_height):
        # Record scroll height for current page (top page on the stack)
        current_page = self.top(self.history)
        current_page["scroll_height"] = scroll_height
        self.history.pop()
        self.history.append(current_page)

    def back(self, scroll_height):
        if len(self.history) == 1:
            return self.load(self.history[0], True)

        self.update_scroll_height(scroll_height)

        self.future.append(self.history.pop())
        page = self.top(self.history)

        if len(self.future) > 0:
            pyotherside.send('showForward')

        return self.load(page, True)

    def forward(self, scroll_height):
        self.update_scroll_height(scroll_height)

        self.history.append(self.future.pop())
        page = self.top(self.history)

        if len(self.future) == 0:
            pyotherside.send('hideForward')

        return self.load(page, True)

    def goto(self, _url, scroll_height=0):
        if "://" not in _url:
            url = "gemini://" + _url
        else:
            url = _url

        if url.split(':')[0] in ["https", "http:"]:
            return pyotherside.send('externalUrl', url)

        self.update_scroll_height(scroll_height)

        page = self.create_page_context(url, 0)
        self.history.append(page)

        # Reset the future.
        self.remove_from_cache(self.future)
        self.future = []
        pyotherside.send('hideForward')

        return self.load(page)

    def reload(self, url, scroll_height):
        page = self.create_page_context(url, scroll_height)

        return self.load(page)

    def load_initial_page(self):
        if len(self.history) > 0:
            page = self.top(self.history)
            self.load(page)
        else:
            home_page = self.create_page_context("gemini://gemini.circumlunar.space/servers/", 0)
            self.load(home_page)
            self.history.append(home_page)

    def cache_page(self, url, content):
        cache_obj = {}

        if url in self.page_cache:
            cache_obj = self.page_cache[url]


        cache_obj["content"] =  content
        cache_obj["timestamp"] =  time.time()

        self.page_cache[url] = cache_obj

    def prune_cache(self):
        # Find urls that are too old to be cached
        old_history = self.history[self.cache_limit:]
        old_future = self.future[self.cache_limit:]
        old_urls = old_history.extend(old_future)

        if old_urls:
            self.remove_from_cache(old_urls)

    def remove_from_cache(self, context_list):
        url_list = [page['url'] for page in context_list]

        # Removes cached values for the provided list of urls
        for url in url_list:
            if url in self.page_cache:
                del self.page_cache[url]

    def load(self, page_context, using_cache = False):
        url = page_context["url"]
        scroll_height = page_context['scroll_height'] if 'scroll_height' in page_context else 0

        if len(self.history) > self.cache_limit or len(self.future) > self.cache_limit:
            self.prune_cache()

        pyotherside.send('loading', url)

        if using_cache and url in self.page_cache:
            cache_obj = self.page_cache[url]

            return pyotherside.send('onLoad', cache_obj['content'], scroll_height)


        if "gopher://" in url or "Gopher://" in url:
            try:
                gophsite = gopher.get_content(url)
                self.cache_page(url, gophsite)
                pyotherside.send('onLoad', gophsite, scroll_height)
            except Exception as e:
                print("Error:", e)
                pyotherside.send('onLoad', "uhm... seems like this site does not exist, it might also be bug <br> ¯\_( ͡❛ ͜ʖ ͡❛)_/¯")
            return;


        try:

            gemsite = self.get_site(url)

            if gemsite is None:
                return

            gemsite = self.instert_html_links(gemsite, self.get_links(gemsite, url))
            self.cache_page(url, gemsite)

            pyotherside.send('onLoad', gemsite, scroll_height)
        except Exception as e:
            print("Error:", e)
            pyotherside.send('onLoad', "uhm... seems like this site does not exist, it might also be bug <br> ¯\_( ͡❛ ͜ʖ ͡❛)_/¯")

        return;

gemini = Gemini()
pyotherside.atexit(gemini.save_data)
