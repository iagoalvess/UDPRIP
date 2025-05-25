import json
from udprip.utils.helpers import current_time

class MessageHandler:
    def __init__(self, router):
        self.router = router
    
    def handle_message(self, message):
        msg_type = message.get("type")
        if msg_type == "data":
            self.handle_data(message)
        elif msg_type == "update":
            self.handle_update(message)
        elif msg_type == "trace":
            self.handle_trace(message)

    def handle_data(self, message):
        dest = message["destination"]
        if dest == self.router.address:
            print(f"Mensagem recebida: {message['payload']}")
        else:
            next_hop = self.router.routing_table.get_next_hop(dest)
            if next_hop:
                self.router.send_message(next_hop, message)
            else:
                print(f"Rota não encontrada para {dest}")
    
    def handle_update(self, message):
        source = message["source"]
        distances = message["distances"]
        link_cost = self.router.neighbors.get(source)
        
        self.router.last_update[source] = 0#adicionado pro mim
        
        if link_cost is None:
            link_cost = message["distances"][source]
       
        for dest, cost in distances.items():
            new_cost = link_cost #adicionado por mim
            if dest != source:
                new_cost = cost + link_cost #adicionado por mim
            if dest == self.router.address:
                continue
            self.router.routing_table.update_route(dest, source, new_cost, source)
      
        self.router.routing_table.remove_routes_without_list_neighbor(source, [ip for ip, weight in distances.items()])
        
        self.router.received_update_from.append(source)
       

    def handle_trace(self, message):
        message.setdefault("routers", []).append(self.router.address)
        if message["destination"] == self.router.address:
            response = {
                "type": "data",
                "source": self.router.address,
                "destination": message["source"],
                "payload": json.dumps(message),
            }
            self.router.send_message(message["source"], response)
        else:
            next_hop = self.router.routing_table.get_next_hop(message["destination"])
            if next_hop:
                self.router.send_message(next_hop, message)
            else:
                print(
                    f"Não foi possível encaminhar TRACE para {message['destination']}"
                )
