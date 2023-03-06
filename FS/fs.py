from flask import Flask
from flask import request
import socket

app = Flask(__name__)

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def get_fib_x(x: int):
    if x < 2:
        return x
    a, b = 0, 1
    for i in range(2, x + 1):
        a, b = b, a + b
    return b


def get_dns_message(hostname, ip, ttl):
    return f"TYPE=A\r\nNAME={hostname}\r\nVALUE={ip}\r\nTTL={ttl}"


@app.route('/register', methods=["PUT"])
def register():
    data = request.json
    hostname = data["hostname"]
    ip = data["ip"]
    as_ip = data["as_ip"]
    as_port = data["as_port"]
    dns_msg = get_dns_message(hostname, ip, 10)
    udp_socket.sendto(dns_msg.encode("utf-8"), (as_ip, int(as_port)))
    data, AS = udp_socket.recvfrom(2048)
    data = data.decode("utf-8")
    if data == "fail":
        return "registration failed", 400
    return "registration succeeded", 201


@app.get('/fibonacci')
def get_fib():
    number = request.args.get("number")
    try:
        number = int(number)
        if number < 0:
            raise ValueError
    except (ValueError, TypeError):
        return "", 400
    return str(get_fib_x(number)), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9090, debug=True)
