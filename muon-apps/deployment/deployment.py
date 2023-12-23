from muon_utils import MuonUtils
from typing import Dict, List
import json
import os
from libp2p.crypto.secp256k1 import Secp256k1PublicKey
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

        # TODO: handle the total_node_number.
        total_node_number = 1
        all_nodes = list(nodes_data)[:total_node_number]

        calculated_party = MuonUtils.get_new_random_subset(
            all_nodes, int(seed, 16), n)
        if not set(party).issubset(set(calculated_party)):
            raise Exception(
                'Deployment: Calculated party is not subset of the given party.')

        dkg_data: Dict = params.get('dkg_data')
        threshold = params.get('threshold')
        verified_peer_ids = []
        for peer_id, data in dkg_data.items():
            data_bytes = json.dumps(data['data']).encode('utf-8')
            validation = bytes.fromhex(data['validation'])
            public_key_bytes = bytes.fromhex(nodes_data[peer_id]['public_key'])
            public_key = Secp256k1PublicKey.deserialize(public_key_bytes)
            if public_key.verify(data_bytes, validation):
                verified_peer_ids.append(peer_id)

        if len(verified_peer_ids) >= threshold:
            return {
                'verified_peer_ids': verified_peer_ids
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
            {'type': 'string', 'value': json.dumps(
                result['verified_peer_ids'])}
        ]
    else:
        raise Exception(f'Unknown method {method}')
