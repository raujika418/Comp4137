from django.shortcuts import render
import datetime
import hashlib
import json
from uuid import uuid4
import socket
import requests
from urllib.parse import urlparse
from datetime import datetime
from coden import hex_to_bin
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt  # New
# from blockchain import Network_Util


class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []  # New
        self.create_block(nonce=1, previous_block_hash='',
                          block_info=[], data="")
        self.nodes = set()  # New


    def calculateHash(self, block_info):
        block_information = json.dumps(block_info,sort_keys = True).encode()#
        hashed_value = hashlib.sha256(block_information).hexdigest()
        return hashed_value

    def create_block(self, nonce, previous_block_hash, data, block_info):
        current_block = {'index': len(self.chain) + 1,
                         'timestamp': datetime.now().timestamp(),
                         'nonce': nonce,
                         'previous_block_hash': previous_block_hash,
                         'hash': Blockchain.calculateHash(self, block_info),
                         'data': data,
                         'Valid': ""
                         }

        self.transactions = []  # New
        self.chain.append(current_block)
        return current_block

    def get_last_block(self):
        return self.chain[-1]

    def hashMatchesDifficulty(self, hash, difficulty):
        hashInBinary = str(hex_to_bin(hash))
        requiredPrefix = ''
        for i in range(difficulty):
            requiredPrefix += '0'
        if hashInBinary.startswith(requiredPrefix):
            return True
        else:
            return False


    def proof_of_work(self, previous_nonce):
        new_nonce = 1
        check_nonce = False
        while check_nonce is False:
            hash_operation = hashlib.sha256(
                str(new_nonce ** 2 - previous_nonce ** 2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_nonce = True
            else:
                new_nonce += 1
        return new_nonce



    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_nonce = previous_block['nonce']
            nonce = block['nonce']

            hash_operation = hashlib.sha256(
                str(nonce ** 2 - previous_nonce ** 2).encode()).hexdigest()

            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount, time):  # New
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount,
                                  'time': str(datetime.datetime.now())})
        previous_block = self.get_last_block()
        return previous_block['index'] + 1

    def add_node(self, address):  # New
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):  # New
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False


# Creating our Blockchain
blockchain = Blockchain()
# Creating an address for the node running our server
node_address = str(uuid4()).replace('-', '')  # New
root_node = '7512827ca39631df7b54e8a265ed158ab033eb50d954718aee11505dfcd5e85b'  # New


def is_block_valid(current_block, previous_block):
    if previous_block['index'] + 1 != current_block['index']:
        print('x')
        return False
    elif previous_block['hash'] != current_block['previous_block_hash']:
        print('y')

        return False
    elif blockchain.calculateHash(current_block) != current_block['hash']:
        print('g')
        return False
    else:
        return True


def mine_block(request):
    if request.method == 'GET':
        previous_block = blockchain.get_last_block()
        previous_block_hash = previous_block['hash']
        previous_nonce = previous_block['nonce']
        nonce = blockchain.proof_of_work(previous_nonce)
        data = 'testing data'
        block_info = [data, previous_block_hash, str(datetime.now().timestamp()), len(blockchain.chain) + 1]
        block = blockchain.create_block(nonce, previous_block_hash, data, block_info)
        current_block = {
            'index': block['index'],
            'nonce': block['nonce'],
            'timestamp': block['timestamp'],
            'hash': block['hash'],
            'previous_block_hash': block['previous_block_hash'],
            'Data': block['data'],
            'Valid':""
        }
        print(is_block_valid(current_block, previous_block))
        response = {}
        for node in list(blockchain.nodes):
            response_get = requests.get(f'http://{node}/replace_chain')
            if response_get.status_code != 200:
                response = {
                    'message': "error, server return error code " + str(response_get.status_code)}
                return JsonResponse(response)
            else:
                if response_get.json()['message'] == "All good. The chain is the largest one.":
                    response = current_block
                    response['message'] = 'Congratulations, you just mined a block!'
                    if(node == list(blockchain.nodes)[len(list(blockchain.nodes)) - 1]):
                        return JsonResponse(response)
                else:
                    response = {'message': 'json parse error'}
                    return JsonResponse(response)
        response = current_block
        response['message'] = 'Congratulations, you just mined a block!'
        return JsonResponse(response)



# Getting the full Blockchain
def get_chain(request):
    if request.method == 'GET':
        response = {'chain': blockchain.chain,
                    'length': len(blockchain.chain)}
    return JsonResponse(response)


# Checking if the Blockchain is valid
def is_valid(request):
    if request.method == 'GET':
        is_valid = blockchain.is_chain_valid(blockchain.chain)
        if is_valid:
            response = {'message': 'All good. The Blockchain is valid.'}
        else:
            response = {
                'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return JsonResponse(response)


# Adding a new transaction to the Blockchain


@csrf_exempt
def add_transaction(request):  # New
    if request.method == 'POST':
        received_json = json.loads(request.body)
        transaction_keys = ['sender', 'receiver', 'amount', 'time']
        if not all(key in received_json for key in transaction_keys):
            return 'Some elements of the transaction are missing', HttpResponse(status=400)
        index = blockchain.add_transaction(received_json['sender'], received_json['receiver'], received_json['amount'],
                                           received_json['time'])
        response = {
            'message': f'This transaction will be added to Block {index}'}
    return JsonResponse(response)


# Connecting new nodes


@csrf_exempt
def connect_node(request):  # New
    if request.method == 'POST':
        print(request.body)
        received_json = json.loads(request.body)
        nodes = received_json.get('nodes')
        if nodes is None:
            return "No node", HttpResponse(status=400)
        node_detail_list = []
        for node in nodes:
            blockchain.add_node(node)
            response_get = requests.get(f'{node}/get_chain')
            if response_get.status_code == 200:
                length = response_get.json()['length']
                chain = response_get.json()['chain']
                node_detail_list.append({
                    "host_ip": node,
                    "length": length,
                    "last_block": chain[length-1]
                })
            # Network_Util.getblock(blockchain, node)

        response = {'message': 'All the nodes are now connected. The Sudocoin Blockchain now contains the following nodes:',
                    'total_nodes': list(blockchain.nodes),
                    'node_detail_list': node_detail_list
                    }
    return JsonResponse(response)


# Replacing the chain by the longest chain if needed

def replace_chain(request):  # New
    if request.method == 'GET':
        is_chain_replaced = blockchain.replace_chain()
        if is_chain_replaced:
            response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                        'new_chain': blockchain.chain}
        else:
            response = {'message': 'All good. The chain is the largest one.',
                        'actual_chain': blockchain.chain}
    return JsonResponse(response)
