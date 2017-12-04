import json

class Softsw():
    uplink_port = -1
    def __init__(self, id, data):
        self.id = id
        self.data = data
        print("class Softsw instance create id %d" % self.id)
        
    def get_id(self):
        return self.id
    
    def set_id(self, id):
        self.id = id
    
    def get_data(self):
        return self.data
            
    def set_data(self, data):
        self.data = data
    
    def get_data_id(self):
        return self.data["data_id"]
        
    def set_data_id(self, data_id):
        self.data["data_id"] = data_id
            
    def get_type(self):
        return self.data["type"]
        
    def set_type(self, type):
        self.data["type"] = type
    
    def get_port_by_mac(self, mac):
        for port in self.data["portdesc"]:
            if mac[3:] == port["hw_addr"][3:]:
                return port["port_no"]
        return -1
    
    def get_uplink_port(self, type):
        # type may be "server_ip", "server_ip_vlan", "server_ip_vxlan"
        # for eth and vlan, the uplink port is set to the eth port link to the outside world
        # for vxlan a patch port to the ovs-tun bridge is returned
        if type == "server_ip":
            self.uplink_port = self.data["uplink_port_no"]
        elif type == "server_ip_vlan":
            self.uplink_port = self.data["uplink_port_no"]
        elif type == "server_ip_vxlan":
            self.uplink_port = self.data["tun_uplink_port_no"]
        else:
            # type error, not a right uplink port type
            return -1
        return self.uplink_port

    def get_portdesc(self):
        return self.data["portdesc"]
        
    def set_portdesc(self, portdesc):
        self.data["portdesc"] = portdesc
            
class Host():
    def __init__(self, id, data):
        self.id = id
        self.data = data
        print("class Hosts instance create id %d" % self.id)
        
    def get_id(self):
        return self.id
    
    def set_id(self, id):
        self.id = id
    
    def get_data(self):
        return self.data
        
    def set_data(self, data):
        self.data = data
        
    def get_type(self):
        return self.data["type"]
    
    def set_type(self, type):
        self.data["type"] = type
        
    def get_in_port(self):
        return self.data["in"]
    
    def set_in_port(self, in_port):
        self.data["in"] = in_port
    
    def get_out_port(self):
        return self.data["out"]
        
    def set_out_port(self, out_port):
        self.data["out"] = out_port
        
    def get_in_sw(self):
        return self.data["in_sw"]
    
    def set_in_sw(self, in_sw):
        self.data["in_sw"] = in_sw
    
    def get_out_sw(self):
        return self.data["out_sw"]
        
    def set_out_sw(self, out_sw):
        self.data["out_sw"] = out_sw

MAX_HOST_NUM=10000
MAX_SWITCH_NUM=1000
class Topo():
    data = {}

    soft_switchs = [None] * MAX_SWITCH_NUM
    host_list = [None] * MAX_HOST_NUM
    
    def __init__(self, nm = "Topo"):
        self.name = nm
        print("class %s instance create instance" % self.name)
                
    def add_softsw(self, id, data):
        print("add softsw %d" % id)
        self.soft_switchs.insert(id, Softsw(id, data))
        
    def add_host(self, id, data):
        self.host_list.insert(id, Host(id, data))
                        
    def del_softsw(self, id):
        del self.soft_switchs[id]
        
    def del_host(self, id):
        del self.host_list[id]
            
    def get_softsw(self, id):
        return self.soft_switchs[id]
    
    def get_softsw_by_data_id(self, data_id):
        for sw in self.soft_switchs:
            if data_id == sw.get_data_id():
                return sw
        return {}
    
    def get_host(self, id):
        return self.host_list[id]
            
    def set_softsw(self, id, data):
        self.soft_switchs[id] = Softsw(id, data)
        
    def set_host(self, id, data):
        self.host_list[id] = Host(id, data)
        
        
    def load_topo_from_file(self):
        with open("topo.json", 'r') as f:
            self.data = json.load(f)
                    
        i = 0
        for ssw in self.data["softsw"]:
            self.add_softsw(i, ssw)
            i += 1
            
        i = 0
        for host in self.data["hosts"]:
            self.add_host(i, host)
            i += 1
        
    def save_topo_to_file(self):
        for ssw in soft_switchs:
            self.data["softsw"][ssw.get_id()] = ssw.get_data()
        for host in host_list:
            self.data["hosts"][host.get_id()] = host.get_data()
        
        with open("topo_w.json", 'w') as f:
            f.write(json.dumps(data))

