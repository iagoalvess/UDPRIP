import socket
import json


class UDPSocket:
    def __init__(self, ip, port=55151):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, port))
        self.sock.settimeout(0.1)

    def send_json(self, message, ip_dest):
        try:
            data = json.dumps(message).encode()
            self.sock.sendto(data, (ip_dest, 55151))
        except Exception as e:
            print(f"Erro ao enviar mensagem para {ip_dest}: {e}")

    def receive_json(self):
        try:
            data, addr = self.sock.recvfrom(65535)
            return json.loads(data.decode()), addr
        except socket.timeout:
            return None, None
        except json.JSONDecodeError:
            print("Erro ao decodificar mensagem recebida")
            return None, None
        except ConnectionResetError:
            print("Conexão foi encerrada pelo destino")
            return None, None
