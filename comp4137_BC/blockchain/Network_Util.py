#this file is not using
import requests
import json

api_getchain = "/get_chain"

def getblock(blockchain, node):
    response = requests.get(node + api_getchain)
    data = response.text
    data = json.loads(data)
    node_chain = data.chain.length
