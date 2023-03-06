import socket
import json
import os

udp_recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_recv_socket.bind(('', 53533))
udp_send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if not os.path.exists("records.json") or os.path.getsize("records.json") == 0:
    with open("records.json", "wb") as fp:
        fp.write(json.dumps({}, ensure_ascii=False).encode("utf-8"))


def register(q_type, name, value, ttl):
    try:
        with open("records.json", "rb") as fp:
            content = json.loads(fp.read().decode("utf-8"))
        if name not in content:
            content[name] = {
                q_type: {
                    "ip": value,
                    "ttl": ttl,
                }
            }
        else:
            content[name][q_type] = {
                    "ip": value,
                    "ttl": ttl,
                }
        with open("records.json", "wb") as fp:
            fp.write(json.dumps(content, ensure_ascii=False).encode("utf-8"))
    except (IOError, KeyError, FileNotFoundError):
        return "fail"
    return "ok"


def query(q_type, name):
    try:
        with open("records.json", "rb") as fp:
            record = json.loads(fp.read().decode("utf-8"))[name][q_type]
    except FileNotFoundError:
        with open("records.json", "wb") as fp:
            fp.write(json.dumps({}, ensure_ascii=False).encode("utf-8"))
        return "fail"
    except KeyError:
        return "fail"

    return f"TYPE={q_type}\r\nNAME={name}\r\nVALUE={record['ip']}\r\nTTL={record['ttl']}"


def main():
    while True:
        try:
            data, from_addr = udp_recv_socket.recvfrom(2048)
            data = data.decode("utf-8").split("\r\n")
            dic = {}
            for field in data:
                name, value = field.split("=")
                dic[name] = value
            res = "fail"
            if len(dic) == 2:
                res = query(dic["TYPE"], dic["NAME"])
            if len(dic) == 4:
                res = register(dic["TYPE"], dic["NAME"], dic["VALUE"], dic["TTL"])
            udp_send_socket.sendto(res.encode("utf-8"), from_addr)
        except:
            res = "fail"
            udp_send_socket.sendto(res.encode("utf-8"), from_addr)


if __name__ == '__main__':
    main()
