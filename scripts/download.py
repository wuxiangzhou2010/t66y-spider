#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import jsonlines
import os
# import time
# import urllib
import urlparse2
from os.path import splitext
import shutil
# import wget
from urllib.request import FancyURLopener
# import sys
# import threading
# from threading import Thread, Lock

from PIL import Image
import re

import signal
import sys
# import imghdr
# from threading import Thread
from multiprocessing.pool import ThreadPool

# from Queue import Queue

# from multiprocessing import Process, Lock

pattern = re.compile(r'fuskator')  # some url seems blocked

temp_i = 0
dir_name = ""
image_type = ["&jpg"]
# mutex = Lock()
max_thread_count = 0

# with jsonlines.open(sys.argv[1]+'.jsonlines') as reader:
#     for obj in reader:
#         image_list = obj["t_image_list"] # get image list
#         if image_list: # if image list not NULL
#             for image in image_list:
#                 total=total+1


class Producer:
    total = 0
    downloaded = 0
    percent = 0
    base_dir = u"Down/"
    file = u""
    # all the url and name are stored in the list
    m_list = []

    # get all the list, with path and name
    def __init__(self):
        self.percent = 0
        self.total = 0
        self.downloaded = 0
        self.base_dir = u"Down/"

    @staticmethod
    def check_make_dir(m_dir):
        if not os.path.exists(m_dir):  # if folder exist, make it
            if os.name == 'nt':
                shutil.rmtree(m_dir)
            else:
                os.mkdir(m_dir, mode=0o777)
        else:
            pass

    # this is a static method
    @staticmethod  # get the title
    def get_title_name(obj):
        title = u''.join(e for e in obj["t_title"] if e.isalnum())  # title
        title = title.replace(" ", "")  # remove white space

        if title.endswith(u"poweredbyphpwindnet"):  # remove php title
            title = title[:-19]

        if len(title) > 50:  # limit the title length
            title = title[:50]
            print("title = " + title)
        return title

    @staticmethod
    def verify_image(image_name):
        try:
            Image.open(image_name)
            # print "v_image.verify() " +str(v_image.verify())
            # if  v_image.verify():
            # v_image.verify()
            # return True
            # else:
            # print "image is wrong"
        except Exception as e:
            print("verify_image  ERROR_CODE:" + ":" + str(e))
            return False
        print("image is ok")
        return True

    @staticmethod
    def check_if_to_download(image):
        # global temp_i
        # global downloaded
        # global dir_name
        # global image_type
        # i = temp_i
        # ext = str(image[-4:])
        # if ext in image_type:
        #     pass
        # else:
        #     image_type.append(ext)
        # ext= str(get_ext(image)) ## get image type
        # if str(ext) == ".php" or str(image[-4:]) =="&jpg":
        #     ext=".jpg"
        # name= dir_name + "/"+ str(i) +ext
        # print "downloading",image
        if os.path.exists(image):
            try:
                # try to open the image, if file is ok,
                #  then it will not through exception
                Image.open(image)
            except Exception as e:
                print("verify_image  ERROR_CODE:" + ":" + str(e))
                os.remove(image)
            return False
        else:
            return True

    @staticmethod
    def down_torrent(m_hash, path):
        cmd = "cao/rmdown.pl "+m_hash+" "+path
        print(cmd)
        os.system(cmd)  # download torrent file
        cmd = "transmission-remote -n " \
              "'transmission:transmission' -a " + path + m_hash + ".torrent"# + " -w " + path
        # cmd = "deluge-console  add " + path + m_hash + ".torrent"
        os.system(cmd)  # download file

    def get_image_from_obj(self, image_list, abs_path):
        l = len(image_list)
        if l:
            while l:
                link = image_list[l - 1]
                real_name = str(l) + u'.jpg'
                filename = abs_path + real_name
                print(filename)
                if self.check_if_to_download(filename):
                    self.get_image_from_link(link, filename)
                l = l - 1

    # download image
    def get_torrent_from_obj(self, torrent_list, abs_path):
        l = len(torrent_list)
        if l:
            while l:
                m_hash = str(torrent_list[l - 1]).split("hash=")
                l -= 1
                if not os.path.exists(abs_path + m_hash[-1] + ".torrent"):
                    self.down_torrent(m_hash[-1], abs_path)

    # download torrent
    def get_all_obj_image_torrent(self, obj):
        path = self.get_title_name(obj)  # title name
        #print("abs_path =" + path)
        if path is not None:
            abs_path = self.base_dir + path #+ "/"
            print("abs_path = " + abs_path)

            #self.check_make_dir(abs_path)
            self.check_make_dir(self.base_dir)

            image_list = obj["t_image_list"]  # for images
            self.get_image_from_obj(image_list, abs_path)

            # torrent_list = obj["t_torrent_list"]  # for torrent file
            # self.get_torrent_from_obj(torrent_list, abs_path)

    # parse the  file
    def parse_file(self):
        with jsonlines.open(self.file) as reader:
            for obj in reader:  # title & image list
                self.m_list.append(obj.copy())
        # get item number
        self.total = len(self.m_list)

    def print_progress(self):
        self.percent = self.downloaded * 10 / (self.total * 0.1)
        print('%.4f%%  downloaded  %s/%s' % (self.percent, self.downloaded, self.total))

    # get download percentage
    def get_all_links(self, item):
        self.get_all_obj_image_torrent(item)
        self.downloaded = self.downloaded + 1
        self.print_progress()

    @staticmethod
    def get_image_from_link(link, name):
        try:
            m_opener = MyOpener()
            print("downloading", link)
            m_opener.retrieve(link, name)
        except Exception as e:
            print("m_opener EORROR name:" + name + " ERROR_CODE:" + ":" + str(e))

    @staticmethod
    def get_ext(url):
        """Return the filename extension from url, or ''."""
        parsed = urlparse2.urlparse(url)
        root, ext = splitext(parsed.path)
        return ext  # or ext[1:] if you don't want the leading '.'

"""
def thread_down():
    while threading.threading.activeCount()() >12:
        pass
    if pattern.search(image):
        #temp_i += 1
        print("blocked url")
        pass # blocked url

    else:
        threads = threading.Thread(target=fetch_url, args=(image,name))
        threads.start()
    print ("active thread count  = " + str(count))
    #downloaded

"""

"""
class Downloader:
    def __init__(self):
        pass

    def threading_download2(m_image_list):
        global temp_i
        global pattern
        length = len(m_image_list)
        while temp_i < length:
            image = m_image_list[temp_i]
            #global name
            (return_code, name) = check_if_to_downloas(image)
            count = threading.threading.activeCount()()
            if return_code:
                pass
            else:
                pass
            percent = downloaded*10/(total*0.1)
            print "%.4f%%  downloaded  %s/%s" % (percent, downloaded, total)
            mutex.acquire(blocking)
            temp_i += 1
            mutex.release()
"""


# use custom urllib opener
class MyOpener(FancyURLopener, object):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'


def signal_handler(a, b):
    print('You pressed Ctrl+C!')
    sys.exit(0)


"""

def worker():
    while True:
        item = q.get()
        do_work(item)
        q.task_done()
"""


def main():
    # get filename from argument
    file = sys.argv[1]

    # register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C')
    # signal.pause()
    # make_del_dir()
    # max_thread_count = sys.argv[2]
    # print "max_thread_count = " + str(max_thread_count)
    p = Producer()
    p.file = file
    p.parse_file()
    p.check_make_dir(p.base_dir)
    # p.get_all_links()

    # q = Queue()
    # for i in range(20):
    #      t = Thread(target= p.get_all_links())
    #      t.daemon = True
    #      t.start()

    # for item in source():
    #     q.put(item)

    # q.join()       # block until all tasks are done
    #################
    # lock = Lock()
    # for i in range(10):
    #     print "active cout "+ str(threading.activeCount())
    #     Process(target=p.get_all_links, args=(lock,)).start()

    pool = ThreadPool(12)

    # can not use CTRL+C, blocking
    # pool.map(p.get_all_links, list)
    # can use CTRL+C, non blocking
    # pool.map_async(p.get_all_links, range(500)).get(9999999)
    pool.map_async(p.get_all_links, p.m_list).get(9999999)
    # pool.close()
    # pool.join()

if __name__ == "__main__":
    main()
