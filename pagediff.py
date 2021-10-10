#!/usr/bin/env python3
import os
import glob
from datetime import datetime
from urllib.request import urlopen
from urllib.parse import quote_plus

PAGES_FILE='pages.txt'
ROOT_DIR=os.getcwd()
PAGES_DIR=os.path.join(ROOT_DIR, 'pages')
NOW=datetime.now().strftime("%Y-%b-%d_%H:%M:%S")

def get_url_dir(url):
    return os.path.join(PAGES_DIR, quote_plus(url))

def ensure_url_dir(url):
  dirname = get_url_dir(url)
  if not os.path.isdir(dirname):
      print(f'  creating dir {dirname}')
      os.makedirs(dirname, exist_ok=True)

def get_last_url_state(url):
    dirname = get_url_dir(url)
    captures = glob.glob(os.path.join(dirname, '*.html'))
    if not captures: return b''

    latest_capture = max(captures, key=os.path.getctime)
    print(f'  >> loading latest capture: {latest_capture}')
    return open(latest_capture, 'rb').read() if latest_capture else b''

def get_current_url_state(url):
    # TODO: handle error
    f = urlopen(url)
    return f.read()

def write_new_state(url, state):
    dirname = get_url_dir(url)
    capture = os.path.join(dirname, f'{NOW}.html')
    print(f'  >> writing new capture: {capture}')
    with open(capture, 'wb') as FOUT:
        FOUT.write(state)

def states_differ(last_state, current_state):
    last_state = (last_state.split(b'<body') + [b''])[1]
    last_state = (last_state.split(b'</body') + [b''])[0]
    current_state = (current_state.split(b'<body') + [b''])[1]
    current_state = (current_state.split(b'</body') + [b''])[0]
    return last_state != current_state



with open(PAGES_FILE) as file:
  urls = file.readlines()
  urls = [url for _url in urls
              for url in [_url.rstrip()]
              if url]

for url in urls:
  print(f'Handling :: {url}')
  ensure_url_dir(url)
  last_state = get_last_url_state(url)
  current_state = get_current_url_state(url)
  if states_differ(last_state, current_state):
      print(f'  >> differences found!')
      write_new_state(url, current_state)
