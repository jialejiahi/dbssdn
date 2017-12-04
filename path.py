import json

# The packet route of one user, it includes two paths .aka. ingress and egress
# ingress: client->server; egress: server->client
class Path:
    def __init__(self, id, data):
        self.id = id
        self.data = data
        print("class path instance create id %d" % self.id)

    def get_data(self):
        return self.data
        
    def get_id(self):
        return self.id
        
    def get_ingress(self):
        return self.data["ingress"]
        
    def get_egress(self):
        return self.data["egress"]
        
    def set_data(self, data):
        self.data = data
        
    def set_id(self, id):
        self.id = id
        
    def set_ingress(self, ing_data):
        # ing_data is a list of path node maps
        self.data["ingress"] = ing_data 
        
    def set_egress(self, eg_data):
        # eg_data is a list of path node maps
        self.data["egress"] = eg_data
        
    def get_ingress_node_by_seq(self, seq):
        return self.data["ingress"][seq]
    
    def set_ingress_node_by_seq(self, seq, node):
        self.data["ingress"].insert(seq, node)
        
    def get_egress_node_by_seq(self, seq):
        return self.data["egress"][seq]
    
    def set_egress_node_by_seq(self, seq, node):
        self.data["egress"].insert(seq, node)
        
    def construct_user_node(self, seq,  type, server_ip, router_ip, router_mac,
                            router_vlan, router_vni, rotuer_outer_ip,rotuer_outer_mac, router_to_sw):
        node = {"seq":seq, "type":type, "server_ip":server_ip, "router_ip":router_ip, "router_mac":router_mac, "router_to_sw":router_to_sw}
        if router_vlan != None:
            node["router_vlan"] = router_vlan
        if router_vni != None:
            node["router_vni"] = router_vni
        if rotuer_outer_ip != None:
            node["rotuer_outer_ip"] = rotuer_outer_ip
        if rotuer_outer_mac != None:
            node["rotuer_outer_mac"] = rotuer_outer_mac
        return node
        
    def construct_sw_node(self, seq, data_id, in_port, out_port):
        node = {"seq":seq, "type":"switch", "id":data_id, "in":in_port, "out":out_port}
        return node
    
    def construct_host_node(self, seq,  data_id, in_mac, out_mac):
        node = {"seq":seq, "type":"host", "id":data_id, "in":in_mac, "out":out_mac}
        return node
        
class Pathlist():
    def __init__(self, nm="Pathlist"):
        self.data = []
        self.paths = []
        self.name = nm
        print("class %s instance create instance" % self.name)

    def get_data(self):
        return self.data
        
    def add_path(self, path):
        self.paths.insert(path.get_id(), path)
        
    def add_path_by_data(self, id, data):
        self.paths.insert(id, Path(id, data))
        
    def del_path(self, id):
        del self.paths[id]
        
    def get_path(self, id):
        return self.paths[id]
        
    def set_path(self, id, data):
        self.paths[id] = Path(id, data)
        
    def load_paths_from_file(self):
        with open("path.json", 'r') as f:
            self.data = json.load(f)
        i = 0
        for pdata in self.data:
            self.add_path(i, pdata)
            i += 1
    
    def save_paths_to_file(self):
        self.data = [p.data for p in self.paths]
        # print(path.get_id())
        # self.data[path.get_id()] = path.get_data()
        with open("paths_w.json", 'w') as f:
            f.write(json.dumps(self.data))

