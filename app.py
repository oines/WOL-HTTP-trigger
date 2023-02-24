from json import load, dump
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST
from flask import Flask, request

app = Flask(__name__)

try:
    with open('config.json', 'r') as f:
        config = load(f)
except FileNotFoundError:
    config = {
        'auth_token': 'token',
        'host': '0.0.0.0',
        'port': 5000
    }
    with open('config.json', 'w') as f:
        dump(config, f)

@app.before_request
def check_auth():
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f'Bearer {config["auth_token"]}':
        return 'Unauthorized', 401

@app.route('/wakeonlan', methods=['GET'])
def wake_on_lan():
    mac_address = request.args.get('mac_address')
    mac_bytes = bytes.fromhex(mac_address.replace(':', ''))
    magic_packet = b'\xff' * 6 + mac_bytes * 16
    with socket(AF_INET, SOCK_DGRAM) as sock:
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        sock.sendto(magic_packet, ('<broadcast>', 9))
    return 'Wake-on-LAN packet sent'

if __name__ == '__main__':
    app.run(host=config['host'], port=config['port'])
