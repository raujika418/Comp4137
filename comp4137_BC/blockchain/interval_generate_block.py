import time
import requests

def gen():
    requests.get('http://127.0.0.1:8000/mine_block')
while True:
    gen()
    time.sleep(30)
