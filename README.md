# Muon Runners Py

This is the implementation of Muon apps to interact with Muon nodes. 


## How to Setup

To create a virtual environment (`venv`) and install the required packages, run the following commands:

```bash
$ git clone https://github.com/mchitgarha78/muon-runner-py.git --recurse-submodules
$ cd muon-runner-py
$ virtualenv -p python3.10 venv
$ source venv/bin/activate
(venv) $ pip install requirements.txt
```

**Note:** The required Python version is `3.10`.

## How to Run

For any instance of Muon node, you should run an instance of runner app with specific local port using the following command:

```bash
(venv) $ python runner_server.py [your port number. e.g. 6000]

```

If you want to test the `simple_oracle`, you can test the runner server using this command:
```bash
(venv) $ curl -X POST -H "Content-Type: application/json" -d '{"app": "simple_oracle", "method": "price", "reqId": "12345", "data": {"params": {"unit": "USD", "token": "BNB"}, "result": {"price":267},"signParams":[{"name":"appId","type":"uint256","value":"55248038324285368712633359989377918216711324138169494581107010692219814301235"},{"name":"reqId","type":"uint256","value":"12345"},{"type":"uint32","value":227},{"type":"string","value":"BNB"},{"type":"string","value":"USD"}],"hash":"0x7e92cff17408096d2fa9c73b7a818a1c51f0eeeab5a91c19d60cf8395a5a6c53"}}' http://localhost:6000/v1/

```



