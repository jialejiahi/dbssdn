import json

MAX_HOST_NUM = 10000
MAX_SWITCH_NUM = 1000


class Controller():
    def __init__(self, data):
        self.data = data
        # print("class Controller instance create url %s %s" \
        #        % self.data["ip"], self.data["port"])

    def get_ctl_ip(self):
        return self.data["ip"]

    def get_ctl_port(self):
        return self.data["port"]


class Softsw():
    def __init__(self, data):
        self.data = data
        uplink_port_no = -1
        tun_uplink_port_no = -1
        print("class Softsw instance create id %s" % self.data["id"])

    def get_mac_from_id(self):
        mac = hex(int(self.data["id"], 10))
        mac = mac[2:]
        while len(mac) < 12:
            mac = '0' + mac
        mac = mac[0:2] + ':' + mac[2:4] + ':' + mac[4:6] + ':' \
            + mac[6:8] + ':' + mac[8:10] + ':' + mac[10:]
        return mac

    def get_id(self):
        return self.data["id"]

    def set_id(self, swid):
        self.data["id"] = swid

    def get_uplink_name(self):
        return self.data["uplink_port_name"]

    def set_uplink_name(self, port_name):
        self.data["uplink_port_name"] = port_name

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def get_port_by_mac(self, mac):
        for port in self.portdesc:
            if mac[3:] == port["hw_addr"][3:]:
                return port["port_no"]
        return -1

    def get_uplink_portno(self):
        for port in self.portdesc:
            if port["name"] == self.data["uplink_port_name"]:
                self.uplink_port_no = port["port_no"]

        return self.uplink_port_no

    def get_tun_uplink_portno(self):
        for port in self.portdesc:
            if port["name"] == "ovs-to-tun":
                self.tun_uplink_port_no = port["port_no"]
        return self.tun_uplink_port_no

    def get_portdesc(self):
        return self.portdesc

    def set_portdesc(self, portdesc):
        self.portdesc = portdesc


class Endpoint():
    def __init__(self, data):
        self.data = data
        print("class Endpoints instance create id %s" % self.data["id"])

    def get_id(self):
        return self.data["id"]

    def set_id(self, epid):
        self.data["id"] = epid

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def get_in_mac(self):
        return self.data["in"]

    def set_in_mac(self, in_port):
        self.data["in"] = in_port

    def get_out_mac(self):
        return self.data["out"]

    def set_out_mac(self, out_port):
        self.data["out"] = out_port

    def get_sw_id(self):
        return self.data["to_ovs_id"]

    def set_sw_id(self, sw_id):
        self.data["to_ovs_id"] = sw_id


class Topo():
    def __init__(self, fname="topo.json", nm="Topo"):
        self.soft_switchs = []
        self.ep_list = []
        self.controller = None
        self.fname = fname
        self.name = nm
        print("class %s instance create instance" % self.name)

    def add_controller(self, data):
        self.controller = Controller(data)

    def get_controller(self):
        return self.controller

    def get_controller_ip(self):
        return self.controller.get_ctl_ip()

    def get_controller_port(self):
        return self.controller.get_ctl_port()

    def add_softsw(self, data):
        self.soft_switchs.append(Softsw(data))

    def set_softsw(self, swid, data):
        for i, sw in enumerate(self.soft_switchs):
            if sw.get_id() == swid:
                self.soft_switchs[i].set_data(data)

    def del_softsw(self, swid):
        self.soft_switchs = [sw for sw in self.soft_switchs
                             if sw.get_id() != swid]

    def get_softsw(self, swid):
        for i, sw in enumerate(self.soft_switchs):
            if sw.get_id() == swid:
                return self.soft_switchs[i]

    def get_softsw_uplink_portno(self, swid):
        sw = self.get_softsw(swid)
        return sw.get_uplink_portno()

    def get_softsw_tun_uplink_portno(self, swid):
        sw = self.get_softsw(swid)
        return sw.get_tun_uplink_portno()

    def get_softsw_portno_by_mac(self, swid, mac):
        sw = self.get_softsw(swid)
        return sw.get_port_by_mac(mac)

    def get_softsw_portdesc(self, swid):
        sw = self.get_softsw(swid)
        return sw.get_portdesc()

    def set_softsw_portdesc(self, swid, portdesc):
        sw = self.get_softsw(swid)
        return sw.set_portdesc(portdesc)

    def add_ep(self, data):
        self.ep_list.append(Endpoint(data))

    def del_ep(self, epid):
        self.ep_list = [ep for ep in self.ep_list
                        if ep.get_id() != epid]

    def get_ep(self, epid):
        for i, ep in enumerate(self.ep_list):
            if ep.get_id() == epid:
                return self.ep_list[i]

    def set_ep(self, epid, data):
        for i, ep in enumerate(self.ep_list):
            if ep.get_id() == epid:
                self.ep_list[i].set_data(data)

    def get_ep_in_mac(self, epid):
        ep = get_ep(epid)
        return ep.get_in_mac()

    def get_ep_out_mac(self, epid):
        ep = get_ep(epid)
        return ep.get_out_mac()

    def get_ep_sw_id(self, epid):
        ep = get_ep(epid)
        return ep.get_sw_id()

    def get_ep_in_port(self, epid):
        mac = get_ep_in_mac(epid)
        swid = get_ep_sw_id(epid)
        return get_softsw_portno_by_mac(swid, mac)

    def get_ep_out_port(self, epid):
        mac = get_ep_out_mac(epid)
        swid = get_ep_sw_id(epid)
        return get_softsw_portno_by_mac(swid, mac)

    def load_topo_from_file(self):
        with open(self.fname, 'r+') as f:
            self.data = json.load(f)

        self.add_controller(self.data["controller"])
        for i, ssw in enumerate(self.data["softsw"]):
            self.add_softsw(ssw)

        for i, ep in enumerate(self.data["endpoints"]):
            self.add_ep(ep)

    def save_topo_to_file(self):
        for ssw in soft_switchs:
            self.data["softsw"][ssw.get_id()] = ssw.get_data()
        for ep in ep_list:
            self.data["endpoints"][ep.get_id()] = ep.get_data()

        with open(self.fname, 'r+') as f:
            f.write(json.dumps(data))
