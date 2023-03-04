import os
import sys
import time
import random
import datetime
from time import sleep
from datetime import date
from datetime import datetime
from bs4 import BeautifulSoup
from termcolor import colored, cprint

import json
import schedule

from multiprocessing import Queue, Process

import streamlink

# driver seleniumbase
# https://stackoverflow.com/questions/74188360/selenium-cloudflare-colab-and-json
from seleniumbase import Driver
from seleniumbase import page_actions
driver = Driver(uc=True)

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def randomwaiting():
    time.sleep(random.randint(2,4))

def writestreamtofile(queue):
    item = queue.get()
    # getting variables from queue witout brackets
    broadcaster_stream = str(item[0]).replace("'",'')
    broadcaster_hls = str(item[1]).replace("'",'')
    print(colored((broadcaster_stream + ' successfully added to queue'), 'cyan'))
    directory = './streamcapture/' + broadcaster_stream + '/' + str(datetime.now().strftime("%d-%m-%Y")) + '/'
    os.makedirs(directory, mode=0o777, exist_ok=True)
    filename = directory + str(datetime.now().strftime("%d-%m-%Y_%H-%M-%S")) + "_" + broadcaster_stream + '.mp4'
    
    if str(broadcaster_stream) or str(broadcaster_hls) not in broadcasterm3ufile:
        with open('broadcasters.m3u','a', encoding='utf-8') as outputfile:
            os.chmod('broadcasters.m3u', 0o666)
            channel = '#EXTINF:-1 group-title="chaturbate",'+ broadcaster_stream + '\n' + broadcaster_hls
            outputfile.write(channel)
            outputfile.write('\n')
    try:
        session = streamlink.Streamlink()
        #https://streamlink.github.io/cli.html#cmdoption-http-no-ssl-verify
        session.set_option('http-header', {'User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'})
        session.set_option('http-header', {'referer=https://chaturbate.eu/'})
        session.set_option('http-no-ssl-verify', 'true')
        session.set_option('default-stream', {'480p,360p'})
        # TEST OPTIONS
        #--stream-timeout TIMEOUT
        #Timeout for reading data from streams
        session.set_option('stream-timeout', 10)
        #--stream-segment-threads THREADS
        #The size of the thread pool used to download segments. Minimum value is 1 and maximum is 10
        session.set_option('stream-segment-thread', 3)
        #--stream-segment-timeout TIMEOUT
        #Segment connect and read timeout.
        session.set_option('stream-segment-timeout', 10)
        #--stream-segment-attempts ATTEMPTS
        #How many attempts should be done to download each segment before giving up.
        session.set_option('stream-segment-attempts', 2)
        #--ringbuffer-size SIZE
        #The maximum size of the ringbuffer. Mega- or kilobytes can be specified via the M or K suffix respectively.
        #The ringbuffer is used as a temporary storage between the stream and the player. 
        #This allows Streamlink to download the stream faster than the player which reads the data from the ringbuffer.
        #session.set_option('ringbuffer-size', '8192k')
        #--retry-streams DELAY
        #Retry fetching the list of available streams until streams are found while waiting DELAY second(s) between each attempt. 
        #If unset, only one attempt will be made to fetch the list of streams available.
        session.set_option('retry-streams', 10)
        #--retry-max COUNT
        #When using --retry-streams, stop retrying the fetch after COUNT retry attempt(s). 
        #Fetch will retry infinitely if COUNT is zero or unset.
        session.set_option('retry-max', 2)
        #--retry-open ATTEMPTS
        #After a successful fetch, try ATTEMPTS time(s) to open the stream until giving up.
        session.set_option('retry-open', 2)
        #--hls-playlist-reload-attempts ATTEMPTS
        #How many attempts should be done to reload the HLS playlist before giving up.
        session.set_option('hls-playlist-reload-attempts', 2)
        # TEST OPTIONS
        #session.set_option('hls-playlist-stream-data', 'true')        
        #session.set_option('http-timeout', 30)

        streams = session.streams(broadcaster_hls)
        stream = streams['480p']
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
    #except streamlink.exceptions.StreamlinkError as e:
    except BaseException as e:
        already_in_queue.remove(broadcaster_stream)
        if 'ssl' in str(e):
            #print(e)
            print(colored(broadcaster_stream + ': some ssl error opening the stream', 'red'))
        elif 'Unable to open URL' in str(e):
            print(colored(broadcaster_stream + ': unable to open URL. Broadcaster is probably offline', 'red'))
        #elif '404' in str(e):
            #print(colored(broadcaster_stream + ': failed to reload playlist. Broadcaster is probably offline', 'red'))
        else: 
            print(colored(broadcaster_stream + ': some network error occured', 'red'))
            print(e)
            
def check_if_online(broadcaster):
    apiurl = ('https://chaturbate.com/api/chatvideocontext/' + broadcaster)
    try:
        driver.get(apiurl)
        r = driver.page_source
        # parsing json with soup
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
                print(colored(broadcaster, 'red') + colored(' is offilne, removing from queue (ELSE)', 'cyan'))
    except: #Exception as e:
        #if 'hls_source' not in e: 
        #print(e)
        if broadcaster in already_in_queue:
            already_in_queue.remove(broadcaster)
            print(colored(broadcaster, 'red') + colored(' is offilne, removing from queue (EXCEPT)', 'cyan'))

def checkwantlist():
    try:
        start_time = datetime.now()
        while True:
            #start_time = datetime.now()
            print('Checking online broadcasters from wantlist.txt')
            for broadcaster in wantlist:
                check_if_online(broadcaster)
            end_time = datetime.now()
            duration = int((end_time - start_time).total_seconds())
            time.sleep(duration/100)
    except KeyboardInterrupt:
        print('keyboard interrupt')
        if stream:
            stream.close()
        if driver:
            driver.close()
        pool.terminate()
        sys.exit(1)

def showinfos():
    cls()
    print(str(str(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))) + ' Queue [actual: '+str(len(already_in_queue)) +'/maximum: ' + str(maxqueue)+']: ' + str(already_in_queue) + ' Duration: ' + str(duration) + 's')
    if len(already_in_queue) >= maxqueue:
        print(colored('queue is full', 'red'))

if __name__=='__main__':
    try:
        cls()
        maxqueue = 5
        stream = 0
        fd = 0
        already_in_queue = []
        broadcasterm3ufile = []
        broadcasterm3u = 0
        duration = 600
        queue = Queue(maxsize=maxqueue)
        queue2 = Queue(maxsize=maxqueue)
        with open('wanted.txt', 'r') as wantlistfile:
            wantlist = wantlistfile.read().splitlines()
        if os.path.exists('broadcasters.m3u'):
            with open('broadcasters.m3u', 'r') as broadcasterm3ufile:
                broadcasterm3u = broadcasterm3ufile.read().splitlines()
        checkwantlist()
    except KeyboardInterrupt:
        if stream:
            stream.close()
        if driver:
            driver.close()
        pool.terminate()
        sys.exit(1)
