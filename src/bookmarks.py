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

class Bookmark:
    def __init__(self):
        self.makeDirs()
        # Load Bookmarks
        bookmark_data = self.read_file("bookmarks.dat")
        self.bookmarks = bookmark_data if bookmark_data != None else []
        print(self.bookmarks)

    def makeDirs(self):
        try:
            os.mkdir(storage_dir)
            open("{}/bookmarks.dat".format(storage_dir), "wb").close()
        except:
            pass

    def read_file(self, filename):
        filepath = "{}/{}".format(storage_dir, filename)
        print(filepath)

        if os.path.exists(filepath):
            print("here")
            file = self.open_file(filepath, "rb")
            return pickle.load(file)


        return None

    def open_file(self, filename, mode="r+"):
        try:
            f = open(filename, mode)
        except:
            file_path = "{}/{}".format(storage_dir, filename)
            f = open(file_path, mode)

        return f

    def add(self, url, name):
        newBookmark = url+","+name
        if newBookmark in self.bookmarks:
            print("double")
        else:
            print(newBookmark)
            self.bookmarks.append(newBookmark)
        self.save_data()
    def remove(self, url, name):
        self.bookmarks.remove(url+","+name)
        self.save_data()

    def returnvalues(self, url, name): #returns a list of all names/urls
        list = []
        for marks in self.bookmarks:
            print(marks)
            marks = marks.split(",")
            if url == True and name == True:
                return self.bookmarks
            elif url == True:
                list.append(marks[0])
            elif name == True:
                list.append(marks[1])
            else:
                print("return: please specify what values you wish to read")
        return list

    def allocate(self, value):
        for marks in self.bookmarks:
            if value == marks.split(",")[0]:
                return marks.split(",")[1]
            elif value == marks.split(",")[1]:
                return marks.split(",")[0]
            else:
                pass

    def save_data(self):
        print("Persisting")
        bookmark_file = self.open_file("bookmarks.dat", "wb")
        pickle.dump(self.bookmarks, bookmark_file)


bookmark = Bookmark()
