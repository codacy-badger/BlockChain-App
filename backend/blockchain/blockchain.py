#TODO:Re-word this to also explain this module function
'''
This module defines the blockchain blueprint extension to the main flask app
'''

from flask import Blueprint, request, jsonify
from uuid import uuid4
from .controller import BlockController, NodeController

# Initialize this module as a blueprint
blockchain_bp = Blueprint('blockchain_bp', __name__)

# Generate a globally unique address for this node
node_id = str(uuid4()).replace('-', '')

#TODO: Group related endpoints and name them appropritely

@blockchain_bp.route('/', methods=['GET'])
def index():
    return jsonify('Blockchain app is running....')

@blockchain_bp.route('/mine', methods=['POST'])
def mine():
    '''
    1. Calculates the Proof of Work
    2. Rewards the miner (us) by adding a transaction granting us 1 coin
    3. Forges the new Block by adding it to the chain
    4. Returns the newly forged block -> json
    '''

    # Fetch the transaction data from front-end
    values = request.get_json()

    # Check that the required fields are in the POST data
    required = ['plot_number', 'size', 'location', 'county', 'seller_id', 'buyer_id', 'amount', 'original_owner']

    if not all(k in values for k in required):
        return "Missing values", 400

    # Prepare the transfer transaction
    transaction = {
        'plot_number': values['plot_number'],
        'size': values['size'],
        'location': values['location'],
        'county': values['county'],
        'seller_id': values['seller_id'],
        'buyer_id': values['buyer_id'],
        'transfer_amount': values['amount'],
        'original_owner': values['original_owner'],
        'transfer_fee': {
            'sender': values['buyer_id'],
            'recipient': node_id,
            'amount': 10000,
        }
    }

    forged_block = BlockController().new_block(
        transactions=transaction)

    response = {
        'Message': 'New Block Forged',
        'Block': forged_block
    }

    return jsonify(response), 201

@blockchain_bp.route('/chain', methods=['GET'])
def full_chain():
    '''
    Exposes the entire blockchain -> json
    '''

    block_List = BlockController().extract_chain()

    response = {
        'chain': block_List,
        'length': len(block_List)
    }

    init = {'Message': 'Blockchain Initialized'}

    return jsonify(response) if len(block_List) != 0 else jsonify(init), 200

@blockchain_bp.route('/nodes/register', methods=['POST'])
def register_nodes():
    '''
    Accepts a new peer node in the from of {"address": "http://192.168.100.208:5002"} and returns the newly registerd node -> json
    '''

    # Fetch node data from front-end
    values = request.get_json()

    if 'http' not in values['address']:
        return jsonify({"message":"Please supply a valid node address"}), 400

    new_node = NodeController().register_node(values['address'])

    response = {
        'message': 'New node added',
        'new_node': new_node
    }

    return jsonify(response), 201

@blockchain_bp.route('/nodes/resolve', methods=['GET'])
def consensus():
    '''  Reconciles our chain with the blockchain network i.e finds the longest, valid chain in the network and replaces ours with it. If a chain longer than our is not found in the network, then our chain is considered up-to-date -> json '''

    replaced = BlockController().update_chain()
    chain = []

    for block in BlockController().extract_chain():
        chain.append(block)

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': chain
        }

    else:
        response = {
            'message': 'Our chain is King',
            'chain': chain
        }

    return jsonify(response), 200