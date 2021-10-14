#!/usr/bin/env python3
import os
import re
from io import BytesIO
from datetime import datetime
from urllib.request import urlopen

import lxml
from lxml.html.clean import Cleaner

PAGES_FILE='pages.txt'
ROOT_DIR=os.getcwd()
PAGES_DIR=os.path.join(ROOT_DIR, 'pages')
NOW=datetime.now().strftime("%Y-%b-%d_%H:%M:%S")

cleaner = Cleaner()
cleaner.javascript = True
cleaner.style = True
cleaner.safe_attrs_only = True

re_class_attrs = br'class=".*?"'

def get_capture_path(url):
    return os.path.join(PAGES_DIR, url.lstrip('http://').lstrip('https://'))

def ensure_dir(dir):
  if not os.path.isdir(dir):
      print(f'  creating dir {dir}')
      os.makedirs(dir, exist_ok=True)

def get_last_url_state(url):
    capture_path = get_capture_path(url)
    if not os.path.isfile(capture_path): return b''
    print(f'  >> loading latest capture: {capture_path}')
    return open(capture_path, 'rb').read()

def get_current_url_state(url):
    # TODO: handle error
    f = urlopen(url)
    return f.read()

def write_new_state(url, state):
    capture = get_capture_path(url)
    capture_dir = '/'.join(capture.split('/')[:-1])
    ensure_dir(capture_dir)
    print(f'  >> writing new capture: {capture}')
    with open(capture, 'wb') as FOUT:
        FOUT.write(state)

def states_differ(last_state, current_state):
    last_state = lxml.html.tostring(cleaner.clean_html(lxml.html.parse(BytesIO(last_state))))
    last_state = re.sub(re_class_attrs, b'', last_state)
    current_state = lxml.html.tostring(cleaner.clean_html(lxml.html.parse(BytesIO(current_state))))
    current_state = re.sub(re_class_attrs, b'', current_state)
    return last_state != current_state

####### Main script

with open(PAGES_FILE) as file:
  urls = file.readlines()
  urls = [url for _url in urls
              for url in [_url.rstrip()]
              if url]

for url in urls:
  print(f'Handling :: {url}')
  ensure_dir(PAGES_DIR)
  last_state = get_last_url_state(url)
  current_state = get_current_url_state(url)
  if not last_state or states_differ(last_state, current_state):
      print(f'  >> differences found!')
      write_new_state(url, current_state)
