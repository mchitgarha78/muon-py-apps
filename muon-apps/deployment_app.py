from muon_utils import MuonUtils
from typing import Dict, List
import json
from node_info import NodeInfo
from libp2p.crypto.secp256k1 import Secp256k1PublicKey
def on_request(request: Dict):
    method = request['method']
    params = request['data']['params']
    node_info = NodeInfo()
    if method == 'get_random_seed':
        app_name = params.get('app_name')
        app_id = MuonUtils.get_app_id(app_name)
        return {
            'app_id': app_id
        }
    elif method == 'verify_party':
        party = params.get('party')
        n = params.get('n')
        seed = params.get('seed')
        all_nodes = node_info.get_all_nodes()

        calculated_party = MuonUtils.get_new_random_subset(all_nodes, seed, n)
        if set(party).issubset(set(calculated_party)):
            return {
                'is_verified': True
            }
        else:
            return {
                'is_verified': False
            }
    
    elif method == 'verify_dkg_key':
        dkg_data = params.get('dkg_data')
        t = params.get('threshold')
        number_of_verified_nodes = 0
        for peer_id, data in dkg_data:
            data_bytes = json.dumps(data['data']).encode('utf-8')
            validation = bytes.fromhex(data['validation'])
            public_key_bytes = bytes.fromhex(node_info.lookup_node(peer_id)['public_key'])
            public_key = Secp256k1PublicKey.deserialize(public_key_bytes)
            if public_key.verify(data_bytes, validation):
                number_of_verified_nodes += 1
            if number_of_verified_nodes == t:
                return {
                'is_verified': True
            }
        
        return {
            'is_verified': False
        }

    else:
        raise Exception(f'Unknown method {method}')

def sign_params(request, result):
    method = request['method']
    params = request['data']['params']
    
    if method == 'get_random_seed':
        return [
            {'type': "uint256", 'value': result['app_id'] },
            {'type': "string" , 'value': params['app_name'] }
        ]
    elif method == 'verify_party':
        return [
            {'type': "uint16" , 'value': result['is_verified']},
            {'type': "string", 'value': json.dumps(params['party']) },
            {'type': "uint16" , 'value': params['n']},
            {'type': "uint256" , 'value': params['seed']},
        ]
    
    elif method == 'verify_dkg_key':
        return [
            {'type': "uint16" , 'value': result['is_verified']},
            {'type': "string", 'value': json.dumps(params['dkg_data']) },
            {'type': "uint16" , 'value': params['threshold']},
        ]
    else:
        raise Exception(f'Unknown method {method}')