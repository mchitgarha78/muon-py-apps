import importlib
import logging
from web3.auto import w3
import hashlib
import json
import random
from typing import List
class MuonUtils:
    def __init__(self) -> None:
        pass


    @staticmethod
    def call_method(script_file: str, method_name: str, *args, **kwargs) -> None:
        try:
            module = importlib.import_module(script_file, package='muon-apps')
            method_to_call = getattr(module, method_name)
            return method_to_call(*args, **kwargs)
        except ModuleNotFoundError:
            logging.error(f"Error: {script_file} not found")
            return None
        except AttributeError:
            logging.error(
                f"Error: {method_name} not found in {script_file}")
            return None
        except Exception as e:
            logging.error(f"Unhandled error: {e}")
            return None
        
    @staticmethod
    def get_app_id(name):
        hash_obj = hashlib.sha3_256(f'{name}.py'.encode())
        hash_hex = hash_obj.hexdigest()
        appId = str(int(hash_hex, 16))
        return appId
    
    @staticmethod
    def hash_json(json_obj):
        hash_obj = hashlib.sha3_256(json.dumps(json_obj).encode())
        hash_hex = hash_obj.hexdigest()
        return hash_hex
    
    @staticmethod
    def get_new_random_subset(list: List, seed: int, subset_size: int) -> None:
        random.seed(seed)  
        random_subset = random.sample(list, subset_size)
        return random_subset
    
    
    # TODO: Implement verification of deployment signature
    @staticmethod 
    def verify_deployment_signature(signature: str, message: str):
        return True
    

