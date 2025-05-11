import socket
import json
import sys


def send_message(router_ip, mensagem):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(json.dumps(mensagem).encode(), (router_ip, 55151))
    sock.close()


def send_data(router_ip, source, dest, payload):
    mensagem = {
        "type": "data",
        "source": source,
        "destination": dest,
        "payload": payload,
    }
    send_message(router_ip, mensagem)


def send_trace(router_ip, source, dest):
    mensagem = {"type": "trace", "source": source, "destination": dest, "routers": []}
    send_message(router_ip, mensagem)


def send_update(router_ip, source, dest, distances):
    mensagem = {
        "type": "update",
        "source": source,
        "destination": dest,
        "distances": distances,
    }
    send_message(router_ip, mensagem)


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Uso: python client.py <tipo> <router_ip> <source> <dest> [<mensagem>]")
        sys.exit(1)

    tipo = sys.argv[1]
    router_ip = sys.argv[2]
    source = sys.argv[3]
    dest = sys.argv[4]

    if tipo == "data":
        if len(sys.argv) < 6:
            print(
                "Uso para data: python client.py data <router_ip> <source> <dest> <mensagem>"
            )
            sys.exit(1)
        payload = sys.argv[5]
        send_data(router_ip, source, dest, payload)
    elif tipo == "trace":
        send_trace(router_ip, source, dest)
    elif tipo == "update":
        if len(sys.argv) < 6:
            print(
                "Uso para update: python client.py update <router_ip> <source> <dest> <json_distances>"
            )
            sys.exit(1)
        try:
            distances = json.loads(sys.argv[5])
        except json.JSONDecodeError:
            print("Erro: distances deve ser um JSON válido")
            sys.exit(1)
        send_update(router_ip, source, dest, distances)
    else:
        print("Tipo de mensagem inválido: data, trace ou update")
