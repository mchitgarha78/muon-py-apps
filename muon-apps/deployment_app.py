from muon_utils import MuonUtils
from typing import Dict, List
import json
from node_info import NodeInfo
import os
from libp2p.crypto.secp256k1 import Secp256k1PublicKey
def on_request(request: Dict):
    method = request['method']
    params = request['data']['params']
    node_info = NodeInfo()

    if method == 'get_random_seed':
        app_name = params.get('app_name')
        app_id = MuonUtils.get_app_id(app_name)
        timestamp = params.get('timestamp')
        if not os.path.exists(f'./muon-apps/{app_name}.py'):
            return {
                'success': False,
                'app_id': app_id,
                'timestamp': timestamp
            }
        return {
            'success': True,
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
        all_nodes = node_info.get_all_nodes(3)

        message = json.dumps(
            {
                'app_id': app_id,
                'timestamp': timestamp
            }
        )
        if not MuonUtils.verify_deployment_signature(seed, message):
            return {
                'success': False,
                'verified_peer_ids' : []
            }
        calculated_party = MuonUtils.get_new_random_subset(all_nodes, int(seed, 16), n)
        if not set(party).issubset(set(calculated_party)):
            return {
                'success': False,
                'verified_peer_ids' : []
            }
        
        dkg_data: Dict = params.get('dkg_data')
        threshold = params.get('threshold')
        verified_peer_ids = []
        for peer_id, data in dkg_data.items():
            data_bytes = json.dumps(data['data']).encode('utf-8')
            validation = bytes.fromhex(data['validation'])
            public_key_bytes = bytes.fromhex(node_info.lookup_node(peer_id)['public_key'])
            public_key = Secp256k1PublicKey.deserialize(public_key_bytes)
            if public_key.verify(data_bytes, validation):
                verified_peer_ids.append(peer_id)
            if len(verified_peer_ids) >= threshold:
                return {
                'success': True,
                'verified_peer_ids': verified_peer_ids
            }
        
        return {
            'success': False,
            'verified_peer_ids' : []
        }

    else:
        raise Exception(f'Unknown method {method}')

def sign_params(request, result):
    method = request['method']
    params = request['data']['params']
    
    if method == 'get_random_seed':
        return [
            {'type': "string" , 'value': params['app_name'] },
            {'type': "uint256" , 'value': params['timestamp'] },
            {'type': "uint256", 'value': result['app_id'] },
            {'type': "uint16" , 'value': result['success']},
        ]
    elif method == 'verify_dkg_key':
        return [
            {'type': "string" , 'value': params['app_name'] },
            {'type': "uint256" , 'value': params['timestamp'] },
            {'type': "uint256" , 'value': params['seed']},
            {'type': "string", 'value': json.dumps(params['party']) },
            {'type': "uint16" , 'value': params['n']},
            {'type': "string", 'value': json.dumps(params['dkg_data']) },
            {'type': "uint32" , 'value': params['threshold']},
            {'type': "uint16" , 'value': result['success']},
            {'type': "string", 'value': json.dumps(result['verified_peer_ids']) },
        ]
    else:
        raise Exception(f'Unknown method {method}')