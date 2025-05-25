import time
import threading
from udprip.core.routing_table import RoutingTable
from udprip.network.udp_socket import UDPSocket
from udprip.core.message_handler import MessageHandler
from udprip.utils.helpers import current_time, has_expired
import os

class Router:
    def __init__(self, address, update_period, port=55151):
        self.address = address
        self.update_period = update_period
        self.running = True
        self.updateHeighb = 0
        self.neighbors = {}
        self.neighbors_update = {}
        self.last_update = {}
        self.received_update_from = []
        self.routing_table = RoutingTable(self.address)
        self.socket = UDPSocket(self.address, port)
        self.lock = threading.Lock()

        self.handler = MessageHandler(self)

    def add_neighbor(self, ip, weight):
        with self.lock:
            #print(f'--> Add neighbor - ip:{ip} - weight: {weight}')
            self.neighbors[ip] = weight
            #self.routing_table.add_direct_route(ip, weight) // adicionado por mim, errado porque deve se mandar apenas a tabela de roteadores

    def remove_neighbor(self, ip):
        with self.lock:
            if ip in self.neighbors:
                #print(f'--> Del neighbor - ip:{ip} - weight: {self.neighbors[ip]}')
                del self.neighbors[ip]
            self.routing_table.remove_routes_from(ip)

    def limpar_tela(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def send_update(self):
        self.limpar_tela() 
        print(f'Atualização: {self.updateHeighb}')
        print(f'===================Vizinhos=============================, {self.address}')
        for ip, weight in self.neighbors.items():
            print(f'IP[{ip}]: weight:{weight}')
        
        self.updateHeighb = self.updateHeighb + 1     
        print(f'===================Roteadores Aprendidos=============================, {self.address}')
        self.print()
        print(f'\n')
   
        with self.lock:
            
            for ip, weight in self.neighbors.items():
               
                update_msg = self.routing_table.build_update_message(
                    self, ip, self.neighbors[ip]
                )
               
                self.socket.send_json(update_msg, ip)

    def receive_loop(self):
        while self.running:
            msg, sender = self.socket.receive_json()
            if msg:
                with self.lock:
                    self.handler.handle_message(msg)

    def periodic_update_loop(self):
        while self.running:
            self.send_update()
            time.sleep(self.update_period)
            self._expire_routes()

    def _expire_routes(self):
        try:
           
            for ip, data in self.routing_table.routes.items():
                if ip != data[2]: 
                    continue
                if ip not in self.received_update_from:
                    if self.last_update[ip] != None:
                        self.last_update[ip] = self.last_update[ip] - 1
                
            expired = [
                ip for ip, t in self.last_update.items()
                if self.last_update[ip] < -3
            ]
            
            for ip in expired:
                del self.last_update[ip]
                self.routing_table.remove_routes_from(ip)
            self.received_update_from = []
        except KeyError:
            return

    def send_message(self, dest_ip, message):
        self.socket.send_json(message, dest_ip)

    def update_last_heard(self, dest_ip):
        self.last_update[ip] = 0 if self.last_update[ip] == None else self.last_update[ip] + 1
        #self.last_update[ip] = current_time()
    
    def send_trace(self, dest_ip):
       
        message = {
            "type": "trace",
            "source": self.address,
            "destination":  dest_ip,
            "routers": [self.address]
        }

        if self.routing_table.routes.get(dest_ip, 'undefined') != 'undefined':
            next_dest = self.routing_table.routes[dest_ip][2]
            self.send_message(next_dest, message)
        else:
            print(f'O destino IP[{dest_ip}] não pode ser encontrado')
            return
       
    
    def input_comands(self):
        while True:
            try:
                comand = input().split(" ")
                typeComand = comand[0]
                ip = comand[1]

                weight = None
                if len(comand) > 2:
                    weight = int(comand[2])
                
                if typeComand == 'add' and weight != None:
                    self.add_neighbor(ip, weight)
                elif typeComand == 'del':
                    self.remove_neighbor(ip)
                elif typeComand == 'trace':
                    self.send_trace(ip)
                else:
                    print('Comando ou formato incorreto')
            except:
                print('Erro no processamento do comando')
            
    def print(self):
        for chave, valor in self.routing_table.routes.items():
            print(f'IP[{chave}] - data: {valor}')
            
                
        

    def run(self):
        recv_thread = threading.Thread(target=self.receive_loop, daemon=True)
        update_thread = threading.Thread(target=self.periodic_update_loop, daemon=True)
        input_thread = threading.Thread(target=self.input_comands, daemon=True)
        recv_thread.start()
        update_thread.start()
        input_thread.start()

        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.running = False
            print("\nRouter shutting down.")
