from flask import Flask, request, jsonify
import logging
import os
from muon_utils import MuonUtils
from typing import List
import sys

app = Flask(__name__)

@app.route('/v1/', methods=['POST'])
def handler():
    try:
        data = request.get_json()
        app_name = data.get('app')
        method = data.get('method')
        req_id = data.get('reqId')
        params = data.get('data', {}).get('params')

        if None in [app_name, method, req_id, params]:
            return jsonify({'error': 'Invalid request format'}), 400
        if not os.path.exists(f'muon-apps/{app_name}/{app_name}.py'):
            return jsonify({'error': 'App not found on the node.'}), 400

        app_id = MuonUtils.get_app_id(app_name)

        response_data = {
        }
        response_data['result'] = MuonUtils.call_method(f'{app_name}','on_request', data)

        response_data['signParams'] = MuonUtils.call_method(f'{app_name}', 'sign_params'
                                                                    , data, response_data['result'])
        response_data['signParams'].insert(0, { 'name': 'appId', 'type': 'uint256', 'value': app_id })
        response_data['signParams'].insert(1, { 'name': 'reqId', 'type': 'uint256', 'value': req_id })
        response_data['hash'] = MuonUtils.hash_json(response_data['signParams'])
        return jsonify(response_data), 200
    except Exception as e:
        logging.error(f'Flask request_sign => Exception occurred: {type(e).__name__}: {e}')
        return jsonify({'error': f'{e}'}), 500

if __name__ == '__main__':
    # TODO: use uvicorn or WSGI
    app.run(port = sys.argv[1], debug = True, use_reloader = False)