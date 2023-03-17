import os
import sys
import time
from datetime import datetime
from bs4 import BeautifulSoup
from termcolor import colored, cprint

import json

from multiprocessing import Queue, Process

import streamlink

# driver seleniumbase
# https://stackoverflow.com/questions/74188360/selenium-cloudflare-colab-and-json
from seleniumbase import Driver
from seleniumbase import page_actions
driver = Driver(uc=True)

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def writestreamtofile(queue):
    item = queue.get()
    # getting variables from queue witout brackets
    broadcaster_stream = str(item[0]).replace("'",'')
    broadcaster_hls = str(item[1]).replace("'",'')
    print(colored((broadcaster_stream + ' successfully added to queue'), 'cyan'))
    directory = './streamcapture/' + broadcaster_stream + '/' + str(datetime.now().strftime("%d-%m-%Y")) + '/'
    os.makedirs(directory, mode=0o777, exist_ok=True)
    filename = directory + str(datetime.now().strftime("%d-%m-%Y_%H-%M-%S")) + "_" + broadcaster_stream + '.mp4'
    filename_log = directory + str(datetime.now().strftime("%d-%m-%Y_%H-%M-%S")) + "_" + broadcaster_stream + '.log'

    if os.path.exists('broadcasters.m3u'):
            with open('broadcasters.m3u', 'r') as broadcasterm3ufile:
                broadcasterm3u = broadcasterm3ufile.read().splitlines()

    if str(broadcaster_stream) or str(broadcaster_hls) not in broadcasterm3ufile:
        with open('broadcasters.m3u','a', encoding='utf-8') as outputfile:
            os.chmod('broadcasters.m3u', 0o666)
            channel = '#EXTINF:-1 group-title="chaturbate",'+ broadcaster_stream + '\n' + broadcaster_hls
            outputfile.write(channel)
            outputfile.write('\n')
    try:
        session = streamlink.Streamlink()
        session.set_option('subprocess-errorlog', 'true')
        session.set_option('subprocess-errorlog-path', 'filename_log')
        session.set_option('ffmpeg-verbose', 'true')
        session.set_option('ffmpeg-verbose-path', 'filename_log')
        
        # General timeout used by all HTTP/HTTPS requests, except the ones covered by other options
        session.set_option('http-timeout', 60)
                
        # Max number of HLS playlist reload attempts before giving up
        session.set_option('hls-playlist-reload-attempts', 10)
        # Override the HLS playlist reload time, either in seconds (float) or as a str keyword
        #   segment:      duration of the last segment
        #   live-edge:    sum of segment durations of the hls-live-edge value minus one
        #   default:      the playlist's target duration):
        session.set_option('hls-playlist-reload-time', 'segment')
 
        streams = session.streams(broadcaster_hls)

        try: 
            stream = streams['480p']
        except:
            try:
                print(colored(broadcaster_stream + ' 480p not available, switching to 360p', 'yellow'))
                stream = streams['360p']
            except:
                print(colored(broadcaster_stream + ' 360p not available, switching to worst', 'yellow'))
                stream = streams['worst']

        fd = stream.open()

        if fd != 0:
            with open(filename, 'wb') as f:
                os.chmod(filename, 0o666)
                try:
                    while(fd):
                        data = fd.read(1024)
                        f.write(data)
                except:
                    f.close()
        else: already_in_queue.remove(broadcaster_stream)

    except streamlink.exceptions.StreamlinkError as streamlink_error:
        if '403 Client Error' in str(streamlink_error):
            print(colored(broadcaster_stream + ' Streamlink error: 403 Client Error. Broadcaster is probably offline, in a ticket show or private', 'red'))
        elif 'Unable to open URL' in str(streamlink_error):
            print(colored(broadcaster_stream + ' Streamlink error: Unable to open URL (Read-Timeout). Broadcaster is probably offline', 'red'))
        else:
            print(colored(broadcaster_stream + ' Streamlink error: ' + str(streamlink_error), 'red'))

    except Exception as e:
        already_in_queue.remove(broadcaster_stream)
        if 'ssl' in str(e):
            #print(e)
            print(colored(broadcaster_stream + ' some ssl error opening the stream', 'red'))
        else: 
            print(colored(broadcaster_stream + ' some network error occured', 'red'))
            print(e)

def check_if_online(broadcaster):
    apiurl = ('https://chaturbate.com/api/chatvideocontext/' + broadcaster)
    try:
        driver.get(apiurl)
        r = driver.page_source
        soup = BeautifulSoup(r, 'html.parser')
        souptext = soup.text
        j = json.loads(souptext)
        hls_url = ''
        model = ''
        if j['hls_source']:
            hls_url = j['hls_source']
            directory = './streamcapture/' + broadcaster+ '/'
            filename = directory + broadcaster + '.json'
            if broadcaster not in already_in_queue:
                if (len(already_in_queue) < maxqueue):
                    os.makedirs(directory, mode=0o777, exist_ok=True)
                    with open(filename,'w', encoding='utf-8') as t:
                        os.chmod(filename, 0o666)
                        t.write(str(j))
                    already_in_queue.append(broadcaster)
                    showinfos()
                    print(colored(broadcaster, 'green') + colored( ' is online', 'green'))
                    queue.put((broadcaster, hls_url))
                    consumer_process = Process(target=writestreamtofile, args=(queue,))
                    consumer_process.start()
        else:
            if broadcaster in already_in_queue:
                already_in_queue.remove(broadcaster)
                print(colored(broadcaster, 'red') + colored(' is offline', 'red'))
    except Exception as e:
        if broadcaster in already_in_queue:
            already_in_queue.remove(broadcaster)
            print(colored(broadcaster + ' is offline, removing from queue (EXCEPT)', 'red'))
    except KeyboardInterrupt:
        print('KeyboardInterrupt in check_if_online')
        if stream:
            stream.close()
        if driver:
            driver.close()
        sys.exit(1)

def checkwantlist():
    try:
        while True:
            with open('wanted.txt', 'r') as wantlistfile:
                wantlist = wantlistfile.read().splitlines()
            for broadcaster in wantlist:
                check_if_online(broadcaster)
    except KeyboardInterrupt:
        print('KeyboardInterrupt in checkwantlist')
        if stream:
            stream.close()
        if driver:
            driver.close()
        pool.terminate()
        sys.exit(1)

def showinfos():
    cls()
    print(str(str(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))) + ' Queue [actual: '+str(len(already_in_queue)) +'/maximum: ' + str(maxqueue)+']: ' + str(already_in_queue))
    print('Checking online broadcasters from wantlist.txt')
    if len(already_in_queue) >= maxqueue:
        print(colored('queue is full', 'red'))

if __name__=='__main__':
    try:
        cls()
        maxqueue = 35
        stream = 0
        fd = 0
        already_in_queue = []
        broadcasterm3ufile = []
        broadcasterm3u = 0
        queue = Queue(maxsize=maxqueue)
        checkwantlist()
    except KeyboardInterrupt:
        print('KeyboardInterrupt in main')
        if stream:
            stream.close()
        if driver:
            driver.close()
        pool.terminate()
        sys.exit(1)