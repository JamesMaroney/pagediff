#!/usr/bin/env python3
import os
import re
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen

PAGES_FILE='pages.txt'
ROOT_DIR=os.getcwd()
PAGES_DIR=os.path.join(ROOT_DIR, 'pages')
NOW=datetime.now().strftime("%Y-%b-%d_%H:%M:%S")

re_publish_time = re.compile(br'<meta property="article:published_time" content="(.*?)" />')

def get_capture_path(url):
    return os.path.join(PAGES_DIR, url.lstrip('http://').lstrip('https://')) + '.html'

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

def write_new_state(url, state, staged=False):
    capture = get_capture_path(url)
    if staged:
        capture += '.staged'
    capture_dir = '/'.join(capture.split('/')[:-1])
    ensure_dir(capture_dir)
    print(f'  >> writing new capture')
    with open(capture, 'wb') as FOUT:
        FOUT.write(b'<base href="https://www.uscis.gov/" />\n' + state)

def get_publish_time(html):
    # extracts meta tag value:
    # <meta property="article:published_time" content="YYYY-MM-DD" />
    matches = re_publish_time.search(html)
    if not matches: return b''
    return matches.group(1)

def states_differ(last_state, current_state):
    last_publish_dt = get_publish_time(last_state)
    current_publish_dt = get_publish_time(current_state)

    return last_publish_dt != current_publish_dt

####### Main script

with open(PAGES_FILE) as file:
  urls = file.readlines()
  urls = [url for _url in urls
              for url in [_url.rstrip()]
              if url]

for url in urls:
  try:
    print(f'Handling :: {url}')
    ensure_dir(PAGES_DIR)
    last_state = get_last_url_state(url)
    current_state = get_current_url_state(url)
    if not last_state or states_differ(last_state, current_state):
        print(f'  >> differences found!')
        Path('differences_found').touch()
        write_new_state(url, current_state, True)
    else:
        print(f'  >> no appreciable differences')
        write_new_state(url, current_state, False)
  except: pass
