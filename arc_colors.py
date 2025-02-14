import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import numpy as np
import os
import json
from dotenv import load_dotenv
import requests

load_dotenv()

def read_file(file_path):
  try:
      with open(file_path, 'r') as file:
          return file.read()
  except Exception as e:
      print(f'Error reading file: {e}')

# Handles reading a file every time it gets changed
class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, file_path, on_read):
        self.file_path = file_path
        self.on_read = on_read

    def on_modified(self, event):
        if event.src_path == self.file_path:
            print(f'File updated: {self.file_path}')
            self.read_file()
    
    def read_file(self):
      return self.on_read(read_file(self.file_path))

# Handles updating the bulb color via and HTTP request
class BulbController:
  def __init__(self):
    self.last_color = None

  def change_bulb_color(self, color):
    if (self.last_color != color).any():
      self.make_request(color)
      self.last_color = color

  def make_request(self, color):
    url = 'https://developer-api.govee.com/v1/devices/control'
    headers = { 'Govee-API-Key': os.getenv('GOVEE_API_KEY') }
    body = {
      "device": os.getenv('GOVEE_DEVICE_MAC'),
      "model": os.getenv('GOVEE_DEVICE_MODEL'),
      "cmd": {
        "name": "color",
        "value": {
          "r": int(color[0]),
          "g": int(color[1]),
          "b": int(color[2])
        }
      }
    }

    r = requests.put(url, headers=headers, json=body)

controller = BulbController()

# Continuously watches a file and calls on_read when the file updates
def watch_file(file_path, on_read):
    observer = Observer()
    event_handler = FileChangeHandler(file_path, on_read)
    event_handler.read_file()
    observer.schedule(event_handler, path=os.path.dirname(file_path) or '.', recursive=False)
    observer.start()

    print(f'Watching file: {file_path}')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Stopping observer...')
        observer.stop()
    observer.join()

def update_color(content):
  color = find_active_color(content)
  controller.change_bulb_color(color)

def find_active_color(content):
  active_tab = get_active_tab(content)
  sidebar_content = read_file(f'/Users/{os.getenv('HOME_DIR_NAME')}/Library/Application Support/Arc/StorableSidebar.json')
  return get_color(sidebar_content, active_tab)

# Gets the id for the current active tab
def get_active_tab(content):
  obj = json.loads(content)
  return obj['lastFocusedSpaceID']

# Gets the color of the active tab from the arc application file
def get_color(content, active_tab):
  obj = json.loads(content)
  spaces = obj['sidebar']['containers'][1]['spaces']
  active_index = spaces.index(active_tab)
  space = spaces[active_index + 1]

  print(f'Current space: {space['title']}')

  color_obj = space['customInfo']['windowTheme']['background']['single']['_0']['style']['color']['_0']
  if 'blendedSingleColor' in color_obj:
    color = color_obj['blendedSingleColor']['_0']['color']
  else:
    color = color_obj['blendedGradient']['_0']['baseColors'][0]

  extended_srgb = [color['red'], color['green'], color['blue']]
  srgb = np.clip(extended_srgb, 0, 1)
  srgb = np.round(srgb * 255).astype(np.int32)
  print_color(srgb)

  return srgb

# Used for printing out the color in the terminal
def print_color(rgb):
  print(get_color_escape(rgb, True)
      + ' ' * 20
      + RESET)

RESET = '\033[0m'
def get_color_escape(rgb, background=True):
    return '\033[{};2;{};{};{}m'.format(48 if background else 38, rgb[0], rgb[1], rgb[2])

if __name__ == '__main__':
    file_to_watch = f'/Users/{os.getenv('HOME_DIR_NAME')}/Library/Application Support/Arc/StorableWindows.json'
    watch_file(file_to_watch, update_color)