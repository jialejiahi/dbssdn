import json
# from ryu.app.dbssdn.topo import Topo, Softsw

MAX_RULE_NUM = 64000
VPC_PRIO_STEP = 1000
CHAIN_PRIO_STEP = 50
MAX_VPC_NUM = MAX_RULE_NUM / VPC_PRIO_STEP
MAX_CHAIN_NUM = VPC_PRIO_STEP / CHAIN_PRIO_STEP


class Vtenant:
    def __init__(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def get_subnets(self):
        return self.data["subnets"]

    def set_subnets(self, subnets):
        self.data["subnets"] = subnets

    def get_cutin(self):
        return self.data["cutin"]

    def set_cutin(self, cutin):
        self.data["cutin"] = cutin

    def get_cutin_type(self):
        return self.data["cutin"]["type"]

    def set_cutin_type(self, ctype):
        self.data["cutin"]["type"] = ctype

    def get_cutin_router_ip(self):
        return self.data["cutin"]["router_ip"]

    def set_cutin_router_ip(self, router_ip):
        self.data["cutin"]["router_ip"] = router_ip

    def get_cutin_router_mac(self):
        return self.data["cutin"]["router_mac"]

    def set_cutin_router_mac(self, router_mac):
        self.data["cutin"]["router_mac"] = router_mac

    def get_cutin_to_node_id(self):
        return self.data["cutin"]["to_node_id"]

    def set_cutin_to_node_id(self, to_node_id):
        self.data["cutin"]["to_node_id"] = to_node_id

    def get_cutin_to_node_ip(self):
        return self.data["cutin"]["to_node_ip"]

    def set_cutin_to_node_ip(self, to_node_ip):
        self.data["cutin"]["to_node_ip"] = to_node_ip

    def get_cutin_vid(self):
        ctype = self.get_cutin_type()
        if ctype != "vlan+route":
            print("error, try to get vid while it's not vlan type")
            return None
        return self.data["cutin"]["vid"]

    def set_cutin_vid(self, vid):
        ctype = self.get_cutin_type()
        if ctype != "vlan+route":
            print("error, try to get vid while it's not vlan type")
            return None
        self.data["cutin"]["vid"] = vid

    def get_cutin_vni(self):
        ctype = self.get_cutin_type()
        if ctype != "vxlan+route":
            print("error, try to get vni while it's not vxlan type")
            return None
        return self.data["cutin"]["vni"]

    def set_cutin_vni(self, vni):
        ctype = self.get_cutin_type()
        if ctype != "vxlan+route":
            print("error, try to get vni while it's not vxlan type")
            return None
        self.data["cutin"]["vni"] = vni

    def get_cutin_router_outer_ip(self):
        ctype = self.get_cutin_type()
        if ctype != "vxlan+route":
            print("error, try to get router_outer_ip while it's not vxlan type")
            return None
        return self.data["cutin"]["router_outer_ip"]

    def set_cutin_router_outer_ip(self, router_outer_ip):
        ctype = self.get_cutin_type()
        if ctype != "vxlan+route":
            print("error, try to get router_outer_ip while it's not vxlan type")
            return None
        self.data["cutin"]["router_outer_ip"] = router_outer_ip

    def get_cutin_router_outer_mac(self):
        ctype = self.get_cutin_type()
        if ctype != "vxlan+route":
            print("error, try to get router_outer_mac while it's not vxlan type")
            return None
        return self.data["cutin"]["router_outer_mac"]

    def set_cutin_router_outer_mac(self, router_outer_mac):
        ctype = self.get_cutin_type()
        if ctype != "vxlan+route":
            print("error, try to get router_outer_mac while it's not vxlan type")
            return None
        self.data["cutin"]["router_outer_mac"] = router_outer_mac


class Vchain:
    def __init__(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def get_id(self):
        return self.data["id"]

    def set_id(self, chainid):
        self.data["id"] = chainid

    def get_match(self):
        return self.data["match"]

    def set_match(self, match):
        self.data["match"] = match

    def get_match_subnet(self):
        return self.data["match"]["subnet"]

    def set_match_subnet(self, subnet):
        self.data["match"]["subnet"] = subnet

    def get_match_ethtype(self):
        return self.data["match"]["ethtype"]

    def set_match_ethtype(self, ethtype):
        self.data["match"]["ethtype"] = ethtype

    def get_match_proto(self):
        return self.data["match"]["proto"]

    def set_match_proto(self, proto):
        self.data["match"]["proto"] = proto

    def get_match_l4port(self):
        return self.data["match"]["l4port"]

    def set_match_l4port(self, l4port):
        self.data["match"]["l4port"] = l4port

    def get_pass_through(self):
        return self.data["pass_through"]

    def set_pass_through(self, pass_through):
        self.data["pass_through"] = pass_through


class Vpc:
    version = 0.1

    def __init__(self, data):
        self.data = data
        self.chain_list = []
        self.ep_chain_refcnt = {}

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def get_id(self):
        return self.data["id"]

    def set_id(self, vpcid):
        self.data["id"] = vpcid

    def get_tenant(self):
        return self.data["tenant"]

    def set_tenant(self, tenant):
        self.data["tenant"] = tenant

    def get_tenant_subnets(self):
        return self.data["tenant"]["subnets"]

    def set_tenant_subnets(self, subnets):
        self.data["tenant"]["subnets"] = subnets

    def get_tenant_cutin(self):
        return self.data["tenant"]["cutin"]

    def set_tenant_cutin(self, cutin):
        self.data["tenant"]["cutin"] = cutin

    def get_tenant_cutin_type(self):
        return self.data["tenant"]["cutin"]["type"]

    def set_tenant_cutin_type(self, ctype):
        self.data["tenant"]["cutin"]["type"] = ctype

    def get_tenant_cutin_router_ip(self):
        return self.data["tenant"]["cutin"]["router_ip"]

    def set_tenant_cutin_router_ip(self, router_ip):
        self.data["tenant"]["cutin"]["router_ip"] = router_ip

    def get_tenant_cutin_router_mac(self):
        return self.data["tenant"]["cutin"]["router_mac"]

    def set_tenant_cutin_router_mac(self, router_mac):
        self.data["tenant"]["cutin"]["router_mac"] = router_mac

    def get_tenant_cutin_to_node_id(self):
        return self.data["tenant"]["cutin"]["to_node_id"]

    def get_tenant_to_ovs_id(self, topo):
        node_id = self.get_tenant_cutin_to_node_id()
        ovsid = topo.get_ovs_id_by_node(node_id)

        return ovsid

    def get_tenant_to_ovs_mac(self, topo):
        ovsid = self.get_tenant_to_ovs_id(topo)
        mac = hex(int(ovsid, 10))
        mac = mac[2:]
        while len(mac) < 12:
            mac = '0' + mac
        mac = mac[0:2] + ':' + mac[2:4] + ':' + mac[4:6] + ':' \
            + mac[6:8] + ':' + mac[8:10] + ':' + mac[10:]
        return mac

    def set_tenant_cutin_to_node_id(self, to_node_id):
        self.data["tenant"]["cutin"]["to_node_id"] = to_node_id

    def get_tenant_cutin_to_node_ip(self):
        return self.data["tenant"]["cutin"]["to_node_ip"]

    def set_tenant_cutin_to_node_ip(self, to_node_ip):
        self.data["tenant"]["cutin"]["to_node_ip"] = to_node_ip

    def get_tenant_cutin_vid(self):
        ctype = self.get_tenant_cutin_type()
        if ctype != "vlan+route":
            print("error, try to get vid while it's not vlan type")
            return None
        return self.data["tenant"]["cutin"]["vid"]

    def set_tenant_cutin_vid(self, vid):
        ctype = self.get_tenant_cutin_type()
        if ctype != "vlan+route":
            print("error, try to get vid while it's not vlan type")
            return None
        self.data["tenant"]["cutin"]["vid"] = vid

    def get_tenant_cutin_vni(self):
        ctype = self.get_tenant_cutin_type()
        if ctype != "vxlan+route":
            print("error, try to get vni while it's not vxlan type")
            return None
        return self.data["tenant"]["cutin"]["vni"]

    def set_tenant_cutin_vni(self, vni):
        ctype = self.get_tenant_cutin_type()
        if ctype != "vxlan+route":
            print("error, try to get vni while it's not vxlan type")
            return None
        self.data["tenant"]["cutin"]["vni"] = vni

    def get_tenant_cutin_router_outer_ip(self):
        ctype = self.get_tenant_cutin_type()
        if ctype != "vxlan+route":
            print("error, try to get router_outer_ip while it's not vxlan type")
            return None
        return self.data["tenant"]["cutin"]["router_outer_ip"]

    def set_tenant_cutin_router_outer_ip(self, router_outer_ip):
        ctype = self.get_tenant_cutin_type()
        if ctype != "vxlan+route":
            print("error, try to get router_outer_ip while it's not vxlan type")
            return None
        self.data["tenant"]["cutin"]["router_outer_ip"] = router_outer_ip

    def get_tenant_cutin_router_outer_mac(self):
        ctype = self.get_tenant_cutin_type()
        if ctype != "vxlan+route":
            print("error, try to get router_outer_mac while it's not vxlan type")
            return None
        return self.data["tenant"]["cutin"]["router_outer_mac"]

    def set_tenant_cutin_router_outer_mac(self, router_outer_mac):
        ctype = self.get_tenant_cutin_type()
        if ctype != "vxlan+route":
            print("error, try to get router_outer_mac while it's not vxlan type")
            return None
        self.data["tenant"]["cutin"]["router_outer_mac"] = router_outer_mac

    def get_endpoints(self):
        return self.data["endpoints"]

    def set_endpoints(self, endpoints):
        for ep in endpoints:
            self.ep_chain_refcnt[ep] = 0
        self.data["endpoints"] = endpoints

    # limit chain id to 0~MAX_CHAIN_NUM, now 0~19
    def add_chain(self, data):
        for ep in data["pass_through"]:
            self.ep_chain_refcnt[ep] += 1
        self.chain_list.append(Vchain(data))

    def del_chain(self, chainid):
        i = 0
        for chain in self.chain_list:
            if chain.get_id() == chainid:
                for ep in chain.get_pass_through():
                    self.ep_chain_refcnt[ep] -= 1
                break
            i += 1
        del self.chain_list[i]

    def get_chain(self, chainid):
        for i, chain in enumerate(self.chain_list):
            if chain.get_id() == chainid:
                return self.chain_list[i]

    def set_chain(self, chainid, data):
        for i, chain in enumerate(self.chain_list):
            if chain.get_id() == chainid:
                self.chain_list[i].set_data(data)

    def get_chain_match(self, chainid):
        chain = self.get_chain(chainid)
        return chain.get_match()

    def set_chain_match(self, chainid, data):
        chain = self.get_chain(chainid)
        chain.set_match(data)

    def get_chain_match_subnet(self, chainid):
        chain = self.get_chain(chainid)
        return chain.get_match_subnet()

    def set_chain_match_subnet(self, chainid, data):
        chain = self.get_chain(chainid)
        chain.set_match_subnet(data)

    def get_chain_match_ethtype(self, chainid):
        chain = self.get_chain(chainid)
        return chain.get_match_ethtype()

    def set_chain_match_ethtype(self, chainid, data):
        chain = self.get_chain(chainid)
        chain.set_match_ethtype(data)

    def get_chain_match_proto(self, chainid):
        chain = self.get_chain(chainid)
        return chain.get_match_proto()

    def set_chain_match_proto(self, chainid, data):
        chain = self.get_chain(chainid)
        chain.set_match_proto(data)

    def get_chain_match_l4port(self, chainid):
        chain = self.get_chain(chainid)
        return chain.get_match_l4port()

    def set_chain_match_l4port(self, chainid, data):
        chain = self.get_chain(chainid)
        chain.set_match_l4port(data)

    def get_chain_pass_through(self, chainid):
        chain = self.get_chain(chainid)
        return chain.get_pass_through()

    def set_chain_pass_through(self, chainid, data):
        chain = self.get_chain(chainid)
        chain.set_pass_through(data)


class Vpclist:
    def __init__(self, fname="vpc.json", nm="Vpclist"):
        self.fname = fname
        self.vpcs = []
        self.data = []
        self.name = nm
        print("class %s instance create instance" % self.name)

    def get_data(self):
        return self.data

    # limit vpc num to 0~MAX_VPC_NUM, now 0~63
    def add_vpc(self, data):
        self.vpcs.append(Vpc(data))

    def del_vpc(self, vpcid):
        self.vpcs = [vpc for vpc in self.vpcs
                     if vpc.get_id() != vpcid]

    def get_vpc(self, vpcid):
        for i, vpc in enumerate(self.vpcs):
            if vpc.get_id() == vpcid:
                return self.vpcs[i]

    def set_vpc(self, vpcid, data):
        for i, vpc in enumerate(self.vpcs):
            if vpc.get_id() == vpcid:
                self.vpcs[i].set_data(data)

    def load_vpcs_from_file(self):
        with open(self.fname, 'r+') as f:
            self.data = json.load(f)

        for vpc in self.data:
            self.add_vpc(vpc)

        for vpc in self.vpcs:
            vpc.set_endpoints(vpc.data["endpoints"])
            for chain in vpc.data["chains"]:
                vpc.add_chain(chain)

    def save_vpcs_to_file(self):
        for vpc in self.vpcs:
            self.data[vpc.get_id()] = vpc.get_data
        with open(self.fname, 'w') as f:
            f.write(json.dumps(self.data))
