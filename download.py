#!/usr/bin/env python
# -*- coding: utf-8 -*-
import jsonlines
import os
import time
import urllib
from urlparse import urlparse
from os.path import splitext
import shutil
import wget
from urllib import FancyURLopener
import sys
import threading
from threading import Thread, Lock

from PIL import Image
import re

import signal
import sys
import imghdr
from threading import Thread
from multiprocessing.pool import ThreadPool
# from Queue import Queue

from multiprocessing import Process, Lock

pattern = re.compile(r'fuskator') # some url seems blocked

temp_i=0
dir_name = ""
image_type= ["&jpg"]
mutex = Lock()
max_thread_count = 0
list = [] #all the url and name are stored in the list

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
    base_dir=u"Down/"
# get all the list, with path and name
    def __init__(self):
        self.percent = 0
        self.total = 0
        self.downloaded = 0
        self.base_dir=u"Down/"
    def check_make_dir(self, dir_name):
        if not os.path.exists(dir_name): # if folder exist, make it
            if os.name=='nt':
                shutil.rmtree(dir_name)
            else:
                os.mkdir(dir_name)
        else:
            pass

    def get_folder_name(self,obj):
        dir_name=self.base_dir+ u''.join(e for e in obj["t_title"] if e.isalnum())
        if dir_name.endswith("poweredbyphpwindnet"):  # remove php title
            dir_name=dir_name[:-19]
            if len(dir_name) > 100:
                dir_name=dir_name[:100]
                print type(dir_name)
            print dir_name
            return unicode(dir_name)

    def verify_image(self,image_name):
        try:
            v_image = Image.open(image_name)
            # print "v_image.verify() " +str(v_image.verify())
            # if  v_image.verify():
            # v_image.verify()
            # return True
            # else:
                # print "image is wrong"
        except Exception, e:
            print "verify_image  ERROR_CODE:"+":"+unicode(e)
            return False
        print "image is ok"
        return True

    def check_if_to_downloas(self, image):
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
                v_image = Image.open(image)
            except Exception, e:
                print "verify_image  ERROR_CODE:"+":"+unicode(e)
                os.remove(image)
                # return True
            return False
        else:
            #temp_i += 1
            return True

    def get_all_boj_image(self, obj):
        dirname = self.get_folder_name(obj) # get dir name
        # self.check_make_dir(dirname) # mkdir
        image_list = obj["t_image_list"] # get image list
        l = len(image_list)
        if l:
            while l:
                link= image_list[l-1]
                # filename  = dirname+'/'+str(l)+u'.jpg'
                filename  = dirname+str(l)+u'.jpg'
                print  filename
                if self.check_if_to_downloas(filename):
                    self.get_image_from_link(link, filename)
                l = l-1
    def parse_jsonlines(self):
        with jsonlines.open('XinShiDai.jsonlines') as reader:
        #with jsonlines.open(sys.argv[1]+'.jsonlines') as reader:
            for obj in reader:# title & image list
                list.append(obj.copy())
		# get item number
        self.total = len(list)

	# get download percentage
    def print_progress(self):
        self.percent = self.downloaded*10/(self.total*0.1)
        print "%.4f%%  downloaded  %s/%s" % (self.percent, self.downloaded, self.total)

    def get_all_links(self,lock):
        #lock.acquire(1)
        obj = list.pop()
                # remove special character for the name and path
                # title as the folder name
        #lock.release()
        self.get_all_boj_image(obj)
        self.downloaded = self.downloaded + 1
        self.print_progress()


    def get_ext(url):
        """Return the filename extension from url, or ''."""
        parsed = urlparse(url)
        root, ext = splitext(parsed.path)
        return ext  # or ext[1:] if you don't want the leading '.'

    def get_image_from_link(self, link, name):
        # get_folder_name(obj)
        try:
            myopener = MyOpener()
            print "downloading",link
            myopener.retrieve(link,name)
            # if imghdr.what('bass.gif')
            # downloaded = downloaded+1
        except Exception, e:
            print "myopener EORROR name:" + name +" ERROR_CODE:"+":"+unicode(e)
    def thread_down(self):
        while threading.threading.activeCount()() >12:
            pass
        print "temp_i = " +str(temp_i), "len = " +str(length)
        if pattern.search(image):
            #temp_i += 1
            print "blocked url"
            pass # blocked url
        else:
            threads = threading.Thread(target=fetch_url, args=(image,name))
            threads.start()
        print "active thread count  = " + str(count)
        #downloaded

class Downloader:
    def __init__(self):
        pass
    def threading_download2(image_list):
        global temp_i
        global pattern
        length = len(image_list)
        while temp_i < length:
            image = image_list[temp_i]
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


class MyOpener(FancyURLopener, object):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'

def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)

def worker():
    while True:
        item = q.get()
        do_work(item)
        q.task_done()

def main():
    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C')
    # signal.pause()
    #make_del_dir()
    #max_thread_count = sys.argv[2]
    #print "max_thread_count = " + str(max_thread_count)
    p = Producer()
    p.parse_jsonlines()
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

    pool = ThreadPool(2)

	# can not use CTRL+C, blocking
	#pool.map(p.get_all_links, list)
	# can use CTRL+C, non blocking
    pool.map_async(p.get_all_links, range(500)).get(9999999)
    #pool.close()
    #pool.join()

if __name__ == "__main__":
    main()


