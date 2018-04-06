#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import jsonlines
import os
import urlparse2
from os.path import splitext
import shutil
# from urllib.request import FancyURLopener
# import urllib2    
# import wget
import requests

from PIL import Image
import re

import signal
import sys
from multiprocessing.pool import ThreadPool

pattern = re.compile(r'fuskator')  # some url seems blocked

temp_i = 0
dir_name = ""
image_type = ["&jpg"]
max_thread_count = 0

category = ('YaZhouWuMa', 'YaZhouYouMa', 'GuoChanYuanChuang',
 'OuMeiYuanChuang', 'ZhongZiYuanChuang','YaZhouWuMaZhuanTie',
 'YaZhouYouMaZhuanTie', 'ZhuanTieJiaoLiu', 'XinShiDai')

class Producer:

    file_path = u""
    # all the url and name are stored in the list
    m_list = []

    # get all the list, with path and name
    def __init__(self,needImage, needTorrent, file_path):
        self.percent = 0
        self.total = 0
        self.file_path = file_path
        self.downloaded = 0
        self.base_dir = u"/home/pi/Down/"
        self.needImage = needImage
        self.needTorrent = needTorrent
        self.parse_file()

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
        except Exception as e:
            print("verify_image  ERROR_CODE:" + ":" + str(e))
            return False
        print("image is ok")
        return True

    @staticmethod
    def check_if_to_download(image):
        if os.path.exists(image):
            try:
                # try to open the image, if file is ok,
                #  then it will not throw exception
                Image.open(image)
            except Exception as e:
                print("verify_image  ERROR_CODE:" + ":" + str(e))
                os.remove(image)
            return False
        else:
            return True

    @staticmethod
    def down_torrent(self, m_hash, path):
        cmd = "cao/rmdown.pl "+m_hash+" "+self.base_dir#+path
        print(cmd)
        os.system(cmd)  # download torrent file
        '''
        cmd = "transmission-remote -n " \
              "'transmission:transmission' -a " + path + m_hash + ".torrent"# + " -w " + path
        # cmd = "deluge-console  add " + path + m_hash + ".torrent"
        os.system(cmd)  # download file
        '''

    def get_image_from_obj(self, image_list, abs_path):
        l = len(image_list)
        if l:
            while l:
                link = image_list[l - 1]
                real_name = str(l) + u'.jpg'
                filename = abs_path + real_name
                # print('    ', filename)
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
                    self.down_torrent(self, m_hash[-1], abs_path)

    # download torrent
    def get_all_obj_image_torrent(self, obj):
        path = self.get_title_name(obj)  # title name
        # print("abs_path =" + path)
        if path is not None:
            abs_path = self.base_dir + path #+ "/"
            # print("abs_path = " + abs_path)

            # self.check_make_dir(abs_path)
            self.check_make_dir(self.base_dir)
            if self.needImage == 1:
                image_list = obj["t_image_list"]  # for images
                self.get_image_from_obj(image_list, abs_path)
            if self.needTorrent == 1:
                torrent_list = obj["t_torrent_list"]  # for torrent file
                self.get_torrent_from_obj(torrent_list, abs_path)

    # parse the  file
    def parse_file(self):
        with jsonlines.open(self.file_path) as reader:
            for obj in reader:  # title & image list
                self.m_list.append(obj.copy())
        # get item number
        self.total = len(self.m_list)

    def print_progress(self):
        self.percent = self.downloaded * 10 / (self.total * 0.1)
        print('###### %.4f%%  downloaded  %s/%s ######' % (self.percent, self.downloaded, self.total))

    # get download percentage
    def get_all_links(self, item):
        self.get_all_obj_image_torrent(item)
        self.downloaded += 1
        self.print_progress()
# 
    @staticmethod
    def get_image_from_link(link, name):
        try:
            # m_opener = MyOpener()
            print('    ', name)
            print("     downloading", link)
            # m_opener.retrieve(link, name)
            # wget.download(link, name) ##ok
            r = requests.get(link)
            with open(name, "wb") as f:
                f.write(r.content)
           
        except Exception as e:
            print("get_image_from_link EORROR name:" + name + " ERROR_CODE:" + ":" + str(e))

    @staticmethod
    def get_ext(url):
        """Return the filename extension from url, or ''."""
        parsed = urlparse2.urlparse(url)
        root, ext = splitext(parsed.path)
        return ext  # or ext[1:] if you don't want the leading '.'

# use custom urllib opener
# class MyOpener(FancyURLopener, object):
#     version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'

# handle ctrl + c
def signal_handler(a, b):
    print('You pressed Ctrl+C!')
    sys.exit(0)

def getTorrentDownloader():
    # get torrent_downloader
    if not os.path.exists('cao'):
        cmd = "git clone https://github.com/xihajuan2010/caoliu-synchronizer.git cao"
        os.system(cmd)

def registerSignalHandler():
    # register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C')


def main():
    # getTorrentDownloader()

    # get filename from argument
    cat = sys.argv[1]
    if cat in category:
        cmd = "cd t66ySpider; scrapy crawl " + cat + " -o " + cat+".jl; cd .."
        path = "/home/pi/Xin.jsonlines"
        print(cmd, path)
        if not os.path.exists(path):
            os.system(cmd)

        needImage = int(sys.argv[2])
        needTorrent = int(sys.argv[3])

        registerSignalHandler()

        p = Producer(needImage, needTorrent, path)

        # p.parse_file()
        p.check_make_dir(p.base_dir)

        pool = ThreadPool(12)
        pool.map_async(p.get_all_links, p.m_list).get(9999999)
    else:
        pass

if __name__ == "__main__":
    main()
