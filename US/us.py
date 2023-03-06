import socket
import requests
from flask import Flask
from flask import request

app = Flask(__name__)

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

DNS_MESSAGE = "TYPE=A\r\nNAME="


def get_ip_from_dns_response(response: str):
    response = response.split("\r\n")
    for field in response:
        if "VALUE=" in field:
            return field.split("=")[1]


def dns_query(hostname: str, as_ip: str, as_port: int):
    msg = DNS_MESSAGE + hostname
    udp_socket.sendto(msg.encode("utf-8"), (as_ip, as_port))
    as_response, _ = udp_socket.recvfrom(2048)
    as_response = as_response.decode("utf-8")
    if as_response == "fail":
        return "fail"
    return get_ip_from_dns_response(as_response)


@app.get('/fibonacci')
def fibonacci():
    hostname = request.args.get("hostname")
    fs_port = request.args.get("fs_port")
    number = request.args.get("number")
    as_ip = request.args.get("as_ip")
    as_port = request.args.get("as_port")
    if not (hostname and fs_port and number and as_ip and as_port):
        return "", 400
    ip = dns_query(hostname, as_ip, int(as_port))
    if ip == "fail":
        return f"failed to get IP of {hostname}", 400
    fs_response = requests.get(f"http://{ip}:{fs_port}/fibonacci", params={"number": number})
    return fs_response.text, fs_response.status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
