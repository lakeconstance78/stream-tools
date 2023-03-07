# stream-tools

cblogin.py - example how to login on cb
  - dependencies: seleniumbase, selenium, BeautifulSoup, datetime, time, random, os, re, sys
  - execute: python3 cblogin.py
  - login with your cb account (nothing will be saved)
  - your followed cams will be saved in cbfollowed.txt


cbstreamsave.py - example how to download cb streams
  - dependencies: streamlink, seleniumbase, multiprocessing, json, termcolor, BeautifulSoup, datetime, os, sys
  - put your favorite broadcaster in cbfollowed.txt (only the name) or use cblogin.py above
  - execute: python3 cbstreamsave.py
  - streams will be saved as mp4
  - json will be saved
  - all online broadcasters will be saved to broadcasters.m3u
