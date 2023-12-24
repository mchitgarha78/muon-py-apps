from itertools import islice
from muon_utils import MuonUtils
from typing import Dict, List
from libp2p.crypto.secp256k1 import Secp256k1PublicKey
import json
import os

nodes_data = {}
with open('./muon-apps/deployment/nodes.json') as reader:
    nodes_data = json.loads(reader.read())


def on_request(request: Dict):
    method = request['method']
    params = request['data']['params']
    if method == 'get_random_seed':
        app_name = params.get('app_name')
        app_id = MuonUtils.get_app_id(app_name)
        timestamp = params.get('timestamp')
        if not os.path.exists(f'./muon-apps/{app_name}/{app_name}.py'):
            raise Exception('Deployment: App is not found.')
        return {
            'app_id': app_id,
            'timestamp': timestamp
        }

    elif method == 'verify_dkg_key':
        party = params.get('party')
        n = params.get('n')
        app_name = params.get('app_name')
        timestamp = params.get('timestamp')
        app_id = MuonUtils.get_app_id(app_name)

        seed = params.get('seed')

        result = {}
        for node, data in islice(nodes_data.items(), n):
            result[node] = list(data.keys())

        # TODO: Random selection
        selected_nodes = {}
        for node_id, peer_ids in result.items():
            selected_nodes[node_id] = peer_ids[0]
        calculated_party = MuonUtils.get_new_random_subset(
            selected_nodes, seed, n)
        if not set(party).issubset(set(calculated_party)):
            raise Exception(
                'Deployment: Calculated party is not subset of the given party.')

        dkg_data: Dict = params.get('dkg_data')
        threshold = params.get('threshold')
        verified_party = []
        validation_items = {}
        for id, public_share in dkg_data['public_shares'].items():
            validation_items[id] = {}
            validation_items[id]['dkg_public_key'] = dkg_data['public_key']
            validation_items[id]['public_share'] = public_share

            data_bytes = json.dumps(validation_items[id]).encode('utf-8')
            validation = bytes.fromhex(dkg_data['validations'][id])
            public_key_bytes = b''
            for node_id, data in nodes_data.items():
                result = data.get(selected_nodes[id], None)
                if result is not None:
                    public_key_bytes = bytes.fromhex(result['public_key'])
                    break
            public_key = Secp256k1PublicKey.deserialize(public_key_bytes)
            # TODO: Fix validation:
            if public_key.verify(data_bytes, validation):
                verified_party.append(selected_nodes[id])

        if len(verified_party) >= threshold:
            return {
                'verified_party': verified_party,
                'app_id': app_id
            }

        raise Exception(
            'Deployment: The number of verified peerIds is less than threshold.')

    else:
        raise Exception(f'Deployment: Unknown method {method}')


def sign_params(request, result):
    method = request['method']
    params = request['data']['params']
    if method == 'get_random_seed':
        return [
            {'type': 'uint256', 'value': result['app_id']},
            {'type': 'uint256', 'value': params['timestamp']},
        ]
    elif method == 'verify_dkg_key':
        return [
            {'type': 'uint256', 'value': result['app_id']},
            {'type': 'uint256', 'value': params['timestamp']},
            {'type': 'uint32', 'value': params['dkg_data']['public_key']},
        ]
    else:
        raise Exception(f'Unknown method {method}')
