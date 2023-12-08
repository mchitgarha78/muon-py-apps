from muon_utils import MuonUtils
from typing import Dict, List
import requests

def on_request(request: Dict):
    method = request['method']
    params = request['data']['params']
    if method == 'price':
        token = params.get('token')
        unit  = params.get('unit')
        response = requests.get(f'https://api.coinbase.com/v2/exchange-rates?currency={token}').json()
        price = response['data']['rates'][unit]
        return {
            'price': price
        }
    else:
        raise Exception(f'Unknown method {method}')

def sign_params(request, result):
    method = request['method']
    params = request['data']['params']
    
    if method == 'price':
        price = result['price']
        sa_price = request.get('data',{}).get('result',{}).get('price',None)
        if sa_price is None:
            sa_price = result['price']
        if (100 * abs(price - sa_price) / price > 0.5):
            raise Exception('Invalid price')
        
        return [
            {'type': "uint256", 'value': result['app_id'] },
            {'type': "string" , 'value': params['app_name'] }
        ]
    else:
        raise Exception(f'Unknown method {method}')