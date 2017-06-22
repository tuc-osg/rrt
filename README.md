# rrt
Run Python test code remotely on another machine

### Installation
pip install -r requirements.txt

## Usage
Check example_client_sock.py and example_server_sock.py for details.

The client runs the test case locally and can use `self.remote()` for running
code on the server.

Connection management happens automatically in the background.

