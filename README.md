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


