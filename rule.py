import json
from vpc import Vpclist, Vpc, Vchain, Vtenant
from topo import Topo, Controller, Softsw, Endpoint

MAX_RULE_NUM=64000
VPC_PRIO_STEP=1000
CHAIN_PRIO_STEP=50
MAX_VPC_NUM=MAX_RULE_NUM/VPC_PRIO_STEP
MAX_CHAIN_NUM=VPC_PRIO_STEP/CHAIN_PRIO_STEP

# The routing of one chain includes two paths: ingress and egress
# ingress: client->server; egress: server->client
# h for half, p for path, r for rule
class Chain_hprlist():
    def __init__(self):
        self.seq = 0
        self.ruleid = 0
        self.pnodes = []
        self.rnodes = []

    def get_pnodes(self):
        return self.pnodes
        
    def set_pnodes(self, pnodes):
        self.pnodes = pnodes
    
    def add_pnode(self, pnode):
        pnode["seq"] = self.seq
        self.pnodes.append(pnode)
        self.seq += 1
        
    def get_pnode(self, seq):
        for i, pnode in enumerate(self.pnodes):
            if pnode["seq"] == seq:
                return self.pnodes[i]
        
    def set_pnode(self, seq, data):
        for i, pnode in enumerate(self.pnodes):
            if pnode["seq"] == seq:
                self.pnodes[i] = data

    def get_rnodes(self):
        return self.rnodes

    def add_rnode(self, rnode):
        rnode["ruleid"] = self.ruleid
        self.rnodes.append(rnode)
        self.ruleid += 1
        
    def get_rnode(self, ruleid):
        for i, rnode in enumerate(self.rnodes):
            if rnode["ruleid"] == ruleid:
                return self.rnodes[i]
        
    def set_rnode(self, ruleid, data):
        for i, rnode in enumerate(self.rnodes):
            if rnode["ruleid"] == ruleid:
                self.rnodes[i] = data

    def add_sw_path_node(self, data_id, in_port, out_port):
        node = {"type":"switch", "dpid":data_id, "in":in_port, "out":out_port}
        self.add_pnode(node)

    def add_ep_path_node(self, epid, in_mac, out_mac):
        node = {"type":"endpoint", "epid":epid, "in":in_mac, "out":out_mac}
        self.add_pnode(node)

    def get_rule_table_and_prio(self, vpcid, chainid, dpid):
        prio = int(vpcid) * 1000 + int(chainid) * 50 + 100
        return 0, prio

    def add_rule(self, vpcid, chainid, epid, dpid, match, actions):
        table_id, prio = self.get_rule_table_and_prio(vpcid, chainid, dpid)
        rule = {"dpid":dpid, "table_id":table_id, "priority":prio,
                 "match":match, "actions":actions}
        rnode = {"vpcid":vpcid, "chainid":chainid, "epid": epid, "rule":rule} 
        self.add_rnode(rnode)


class Vpc_prlist():
    def __init__(self, nm="Vpc_prlist"):
        self.name = nm
        self.data = []
        print("class %s instance create instance" % self.name)

    def create_vpc_path(self, vpcid):
        if self.get_vpc_path(vpcid) == None:
            vpc_path = {"vpcid":vpcid, "chain":[]}
            self.data.append(vpc_path)

    def add_vpc_path(self, vpcpath):
        self.data.append(vpcpath)

    def del_vpc_path(self, vpcid):
		self.data = [vpc for vpc in self.data
                             if vpc.get_id() != vpcid]
        
    def get_vpc_path(self, vpcid):
        for i, path in enumerate(self.data):
            if path["vpcid"] == vpcid:
                return self.data[i]
        return None
        
    def set_vpc_path(self, vpcid, vpcpath):
        for i, path in enumerate(self.data):
            if path["vpcid"] == vpcid:
                self.data[i] = vpcpath

    def create_chain_path(self, vpcid, chainid):
        vpc = None
        for i, path in enumerate(self.data):
            if path["vpcid"] == vpcid:
                vpc = self.data[i]
                break
        if vpc == None:
            self.create_vpc_path(vcpid)
            for i, path in enumerate(self.data):
                if path["vpcid"] == vpcid:
                    vpc = self.data[i]
                    break
        
        if self.get_chain_path(vpcid, chainid) == None:
            chain_path = {"chainid":chainid, "ingress":{}, "egress":{}}
            self.data[i]["chain"].append(chain_path)

    def add_chain_path(self, vpcid, chain):
        vpc = None
        i = 0
        for i, path in enumerate(self.data):
            if path["vpcid"] == vpcid:
                vpc = self.data[i]
                break
        if vpc != None:
            self.data[i]["chain"].append(chain)

    def del_chain_path(self, vpcid, chainid):
        vpc = None
        i = 0
        for i, path in enumerate(self.data):
            if path["vpcid"] == vpcid:
                vpc = self.data[i]
                break
        if vpc != None:
		    self.data[i]["chain"] = [chain for chain in self.data[i]["chain"]
                                             if chain.get_id() != chainid]

    def get_chain_path(self, vpcid, chainid):
        vpc = None
        i = 0
        for i, path in enumerate(self.data):
            if path["vpcid"] == vpcid:
                vpc = self.data[i]
                break
        if vpc != None:
            for j, path in enumerate(self.data[i]["chain"]):
                if path["chainid"] == chainid:
                    return self.data[i]["chain"][j]
        return None

    def set_chain_path(self, vpcid, chainid, chain):
        vpc = None
        i = 0
        for i, path in enumerate(self.data):
            if path["vpcid"] == vpcid:
                vpc = self.data[i]
                break
        if vpc != None:
            for j, path in enumerate(self.data[i]["chain"]):
                if path["chainid"] == chainid:
                    self.data[i]["chain"][j] = chain

    def set_ingress(self, vpcid, chainid, chain_ing):
        vpc = None
        i = 0
        for i, path in enumerate(self.data):
            if path["vpcid"] == vpcid:
                vpc = self.data[i]
                break
        if vpc != None:
            for j, path in enumerate(self.data[i]["chain"]):
                if path["chainid"] == chainid:
                    self.data[i]["chain"][j]["ingress"]["pnodes"] = chain_ing.get_pnodes()
                    self.data[i]["chain"][j]["ingress"]["rnodes"] = chain_ing.get_rnodes()

    def set_egress(self, vpcid, chainid, chain_egr):
        vpc = None
        i = 0
        for i, path in enumerate(self.data):
            if path["vpcid"] == vpcid:
                vpc = self.data[i]
                break
        if vpc != None:
            for j, path in enumerate(self.data[i]["chain"]):
                if path["chainid"] == chainid:
                    self.data[i]["chain"][j]["egress"]["pnodes"] = chain_egr.get_pnodes()
                    self.data[i]["chain"][j]["egress"]["rnodes"] = chain_egr.get_rnodes()



    def save_rules_to_file(self, fname):
        with open(fname, 'w') as f:
            f.write(json.dumps(self.data))

    def gen_add_cmds(self, fname, topo):
        with open(fname, 'w') as f:
            for i, path in enumerate(self.data):
                for j, chain in enumerate(path["chain"]):
                    for rule in chain["ingress"]["rnodes"]:
                        f.write("curl -X POST -d '")
                        f.write(json.dumps(rule["rule"]))
                        f.write("' " + "http://" + \
                            topo.get_controller_ip() + ":" + \
                            topo.get_controller_port() + \
                            "/stats/flowentry/add\n")
                    for rule in chain["egress"]["rnodes"]:
                        f.write("curl -X POST -d '")
                        f.write(json.dumps(rule["rule"]))
                        f.write("' " + "http://" + \
                            topo.get_controller_ip() + ":" + \
                            topo.get_controller_port() + \
                            "/stats/flowentry/add\n")
    def gen_del_cmds(self, fname, topo):
        print("gen del cmds")
    
class Rule():
    def __init__(self, fname_path="path.json",
                       fname_rule="rule.json",
                       fname_cmd ="cmd.sh"):
        self.fname_path = fname_path
        self.fname_rule = fname_rule
        self.fname_cmd  = fname_cmd
        self.vprlist = Vpc_prlist("vprlist")

    def get_mac_by_dpid(self, ovsid):
        mac = hex(int(ovsid, 10))
        mac = mac[2:]
        while len(mac) < 12:
            mac='0'+mac
        mac = mac[0:2]+':'+mac[2:4]+':'+mac[4:6]+':' \
             +mac[6:8]+':'+mac[8:10]+':'+mac[10:]
        return mac
    
    def save_rules_to_file(self):
        self.vprlist.save_rules_to_file(self.fname_rule)

    def gen_add_cmds(self, topo):
        self.vprlist.gen_add_cmds(self.fname_cmd, topo)
        
    def construct_rule_field_match(self, in_port,
                            eth_type, eth_dst, eth_src, dl_vlan,
                            ipv6_src, ipv6_dst, ipv4_src, ipv4_dst, ip_proto,
                            tcp_src, tcp_dst, udp_src, udp_dst):
        # no direction considered        
        m = {}
        if in_port != None:
            m["in_port"] = in_port
        if eth_type != None:
            m["eth_type"] = eth_type
        if eth_dst != None:
            m["eth_dst"] = eth_dst
        if eth_src != None:
            m["eth_src"] = eth_src
        if dl_vlan != None:
            m["dl_vlan"] = dl_vlan
        if ipv4_src != None:
            m["ipv4_src"] = ipv4_src
        if ipv4_dst != None:
            m["ipv4_dst"] = ipv4_dst
        if ipv6_src != None:
            m["ipv6_src"] = ipv6_src
        if ipv6_dst != None:
            m["ipv6_dst"] = ipv6_dst
        if ip_proto != None:
            m["ip_proto"] = ip_proto
        if tcp_src != None:
            m["tcp_src"] = tcp_src
        if tcp_dst != None:
            m["tcp_dst"] = tcp_dst
        if udp_src != None:
            m["udp_src"] = udp_src
        if udp_dst != None:
            m["udp_dst"] = udp_dst


        return m

    def construct_rule_match(self, dire, in_port,
                eth_type, eth_dst, eth_src, vlan_id,
                ip, ip_proto, l4_port):
        m = {}

        if l4_port != 0:
            l4_flag = 1
        else:
            l4_flag = 0

        print("construct match: dir=%s et=%s ip_proto=%s l4_flag=%s" % \
              (dire, eth_type,  ip_proto, l4_flag))
        if dire == "ingress":
            if [str(eth_type), str(ip_proto), str(l4_flag)] == ["2048", "6", "1"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            None, None, None, ip, ip_proto,
                            None, l4_port, None, None)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["2048", "6", "0"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            None, None, None, ip, ip_proto,
                            None, None, None, None)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["2048", "17", "1"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            None, None, None, ip, ip_proto,
                            None, None, None, l4_port)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["2048", "17", "0"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            None, None, None, ip, ip_proto,
                            None, None, None, None)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["2048", "0", "1"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            None, None, None, ip, None,
                            None, None, None, None)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["2048", "0", "0"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            None, None, None, ip, None,
                            None, None, None, None)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["34525", "6", "1"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            None, ip, None, None, ip_proto,
                            None, l4_port, None, None)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["34525", "6", "0"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            None, ip, None, None, ip_proto,
                            None, None, None, None)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["34525", "17", "1"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            None, ip, None, None, ip_proto,
                            None, None, None, l4_port)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["34525", "17", "0"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            None, ip, None, None, ip_proto,
                            None, None, None, None)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["34525", "0", "1"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            None, ip, None, None, None,
                            None, None, None, None)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["34525", "0", "0"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            None, ip, None, None, None,
                            None, None, None, None)
            else:
                print("construct a match of None, not ipv4/ipv6")
        elif dire == "egress":
            if [str(eth_type), str(ip_proto), str(l4_flag)]  == ["2048", "6", "1"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            None, None, ip, None, ip_proto,
                            l4_port, None, None, None)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["2048", "6", "0"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            None, None, ip, None, ip_proto,
                            None, None, None, None)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["2048", "17", "1"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            None, None, ip, None, ip_proto,
                            None, None, l4_port, None)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["2048", "17", "0"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            None, None, ip, None, ip_proto,
                            None, None, None, None)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["2048", "0", "1"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            None, None, ip, None, None,
                            None, None, None, None)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["2048", "0", "0"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            None, None, ip, None, None,
                            None, None, None, None)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["34525", "6", "1"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            ip, None, None, None, ip_proto,
                            l4_port, None, None, None)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["34525", "6", "0"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            ip, None, None, None, ip_proto,
                            None, None, None, None)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["34525", "17", "1"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            ip, None, None, None, ip_proto,
                            None, None, l4_port, None)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["34525", "17", "0"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            ip, None, None, None, ip_proto,
                            None, None, None, None)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["34525", "0", "1"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            ip, None, None, None, None,
                            None, None, None, None)
            elif [str(eth_type), str(ip_proto), str(l4_flag)]  == ["34525", "0", "0"]:
                m = self.construct_rule_field_match(in_port,
                            eth_type, eth_dst, eth_src, vlan_id,
                            ip, None, None, None, None,
                            None, None, None, None)
            else:
                print("construct a match of None, not ipv4/ipv6")
        else:
            print("param error")

        return m

    def construct_rule_action(self, out_port, field_src, value_src,
                    field_dst, value_dst, act_vlan, value_vlan):
        act = []

        if out_port == None:
            print("no output port, error")
            return act
        if field_src is not None:
            act.append({"type":"SET_FIELD", "field":field_src, "value":value_src})
        if field_dst is not None:
            act.append({"type":"SET_FIELD", "field":field_dst, "value":value_dst})
        if act_vlan is not None:            
            if act_vlan == "PUSH_VLAN":
                vlan_id = value_vlan + 0x1000
                act.append({"type":"PUSH_VLAN", "ethertype":33024})                
                act.append({"type":"SET_FIELD",
                            "field":"vlan_vid", "value":vlan_id})
            elif act_vlan == "POP_VLAN":
                act.append({"type":"POP_VLAN"})
            elif act_vlan == "SET_VLAN":
                vlan_id = value_vlan + 0x1000
                act.append({"type":"SET_FIELD",
                            "field":"vlan_vid", "value":vlan_id})
        act.append({"type":"OUTPUT", "port": out_port})

        return act
   
    # private functions
    def calc_path_first_ep(self, dire, hprlist, first_ovs_id, topo, ep):
        if dire == "ingress":
            if first_ovs_id == ep.get_sw_id():
                hprlist.add_sw_path_node(first_ovs_id,
                                topo.get_softsw_uplink_portno(first_ovs_id), 
                                topo.get_softsw_portno_by_mac(first_ovs_id,
                                                              ep.get_in_mac()))
            else:
                hprlist.add_sw_path_node(first_ovs_id,
                                topo.get_softsw_uplink_portno(first_ovs_id), 
                                topo.get_softsw_uplink_portno(first_ovs_id))
                hprlist.add_sw_path_node(ep.get_sw_id(),
                                topo.get_softsw_uplink_portno(ep.get_sw_id()), 
                                topo.get_softsw_portno_by_mac(ep.get_sw_id(),
                                                              ep.get_in_mac()))
            hprlist.add_ep_path_node(ep.get_id(), ep.get_in_mac(), ep.get_out_mac())
        else:
            if first_ovs_id == ep.get_sw_id():
                hprlist.add_sw_path_node(first_ovs_id,
                                topo.get_softsw_uplink_portno(first_ovs_id), 
                                topo.get_softsw_portno_by_mac(first_ovs_id,
                                                              ep.get_out_mac()))
            else:
                hprlist.add_sw_path_node(first_ovs_id,
                                topo.get_softsw_uplink_portno(first_ovs_id), 
                                topo.get_softsw_uplink_portno(first_ovs_id))
                hprlist.add_sw_path_node(ep.get_sw_id(),
                                topo.get_softsw_uplink_portno(ep.get_sw_id()), 
                                topo.get_softsw_portno_by_mac(ep.get_sw_id(),
                                                              ep.get_out_mac()))
            hprlist.add_ep_path_node(ep.get_id(), ep.get_out_mac(), ep.get_in_mac())

    def calc_path_last_ep(self, dire, hprlist,
                          first_ovs_id, topo, ep, prevep):
        if prevep == None:
            # prev is None, there is only one node in this chain
            self.calc_path_first_ep(dire, hprlist, first_ovs_id, topo, ep)
        else:
            # prev is NOT None, there is more than one node in this chain
            self.calc_path_mid_ep(dire, hprlist, topo, ep, prevep)
        # add output nodes
        if dire == "ingress":
            if first_ovs_id == ep.get_sw_id():
                hprlist.add_sw_path_node(first_ovs_id,
                                topo.get_softsw_portno_by_mac(first_ovs_id,
                                                              ep.get_out_mac()),
                                topo.get_softsw_uplink_portno(first_ovs_id)) 
            else:
                hprlist.add_sw_path_node(ep.get_sw_id(),
                                topo.get_softsw_portno_by_mac(ep.get_sw_id(),
                                                              ep.get_out_mac()),
                                topo.get_softsw_uplink_portno(ep.get_sw_id()))
                hprlist.add_sw_path_node(first_ovs_id,
                                topo.get_softsw_uplink_portno(first_ovs_id), 
                                topo.get_softsw_uplink_portno(first_ovs_id))
        else:
            if first_ovs_id == ep.get_sw_id():
                hprlist.add_sw_path_node(first_ovs_id,
                                topo.get_softsw_portno_by_mac(first_ovs_id,
                                                              ep.get_in_mac()),
                                topo.get_softsw_uplink_portno(first_ovs_id))
            else:
                hprlist.add_sw_path_node(ep.get_sw_id(),
                                topo.get_softsw_portno_by_mac(ep.get_sw_id(),
                                                              ep.get_in_mac()),
                                topo.get_softsw_uplink_portno(ep.get_sw_id()))
                hprlist.add_sw_path_node(first_ovs_id,
                                topo.get_softsw_uplink_portno(first_ovs_id), 
                                topo.get_softsw_uplink_portno(first_ovs_id))
    
    def calc_path_mid_ep(self, dire, hprlist, topo, ep, prevep):
        if dire == "ingress":
            if prevep.get_sw_id() == ep.get_sw_id():
                hprlist.add_sw_path_node(prevep.get_sw_id(),
                              topo.get_softsw_portno_by_mac(prevep.get_sw_id(),
                                                            prevep.get_out_mac()),
                                topo.get_softsw_portno_by_mac(prevep.get_sw_id(),
                                                              ep.get_in_mac()))
            else:
                hprlist.add_sw_path_node(prevep.get_sw_id(),
                              topo.get_softsw_portno_by_mac(prevep.get_sw_id(),
                                                            prevep.get_out_mac()),
                                topo.get_softsw_uplink_portno(prevep.get_sw_id()))
                hprlist.add_sw_path_node(ep.get_sw_id(),
                                topo.get_softsw_uplink_portno(ep.get_sw_id()), 
                                topo.get_softsw_portno_by_mac(ep.get_sw_id(),
                                                              ep.get_in_mac()))
            hprlist.add_ep_path_node(ep.get_id(), ep.get_in_mac(), ep.get_out_mac())
        else:
            if prevep.get_sw_id() == ep.get_sw_id():
                hprlist.add_sw_path_node(prevep.get_sw_id(),
                              topo.get_softsw_portno_by_mac(prevep.get_sw_id(),
                                                            prevep.get_in_mac()),
                                topo.get_softsw_portno_by_mac(ep.get_sw_id(),
                                                              ep.get_out_mac()))
            else:
                hprlist.add_sw_path_node(prevep.get_sw_id(),
                              topo.get_softsw_portno_by_mac(prevep.get_sw_id(),
                                                            prevep.get_in_mac()),
                              topo.get_softsw_uplink_portno(prevep.get_sw_id()))
                hprlist.add_sw_path_node(ep.get_sw_id(),
                                topo.get_softsw_uplink_portno(ep.get_sw_id()), 
                                topo.get_softsw_portno_by_mac(ep.get_sw_id(),
                                                              ep.get_out_mac()))
            hprlist.add_ep_path_node(ep.get_id(), ep.get_out_mac(), ep.get_in_mac())


    def calc_path_one_dire(self, dire, vpc, topo, chain):
        hprlist = Chain_hprlist()
        length = len(chain.get_pass_through())
        if length == 0:
            print("there are no endpoints in this chain, default rule")
            return hprlist
        elif length == 1:
            pass_through = chain.get_pass_through()
            ep = topo.get_ep(pass_through[0])
            self.calc_path_last_ep(dire, hprlist,
                              vpc.get_tenant_cutin_to_ovs_id(),
                              topo, ep, None)
            return hprlist

        pass_through = chain.get_pass_through()
        if dire == "egress":
            pass_through.reverse()

        for i, epid in enumerate(pass_through):
            ep = topo.get_ep(epid)
            if i == 0:
                self.calc_path_first_ep(dire, hprlist,
                                   vpc.get_tenant_cutin_to_ovs_id(), topo, ep)
            elif i == length - 1:
                prev_epid = chain.get_pass_through()[i-1]
                self.calc_path_last_ep(dire, hprlist,
                                vpc.get_tenant_cutin_to_ovs_id(),
                                topo, ep, topo.get_ep(prev_epid))
            else:
                prev_epid = chain.get_pass_through()[i-1]
                self.calc_path_mid_ep(dire, hprlist,
                                 topo, ep, topo.get_ep(prev_epid))
        
        return hprlist

    # rule calc functions
    def calc_rule_chain_first_switch(self, dire, vpc, chain,
                                     pnode, next_snode, next_hnode, hprlist):
        if pnode["out"] == pnode["in"]:
            oport = "IN_PORT"
        else:
            oport = pnode["out"]

        if vpc.get_tenant_cutin_type() == "route":
            match = self.construct_rule_match(dire, pnode["in"],
                chain.get_match_ethtype(),
                self.get_mac_by_dpid(pnode["dpid"]),
                vpc.get_tenant_cutin_router_mac(), None,
                chain.get_match_subnet(), chain.get_match_proto(),
                chain.get_match_l4port())
            act = self.construct_rule_action(oport,
                "eth_src", self.get_mac_by_dpid(pnode["dpid"]),
                "eth_dst", next_hnode["in"], None, None)
        elif vpc.get_tenant_cutin_type() == "vlan+route":
            match = self.construct_rule_match(dire, pnode["in"],
                chain.get_match_ethtype(),
                self.get_mac_by_dpid(pnode["dpid"]),
                vpc.get_tenant_cutin_router_mac(),
                vpc.get_tenant_cutin_vid(),
                chain.get_match_subnet(), chain.get_match_proto(),
                chain.get_match_l4port())
            act = self.construct_rule_action(oport,
                "eth_src", self.get_mac_by_dpid(pnode["dpid"]),
                "eth_dst", next_hnode["in"], "POP_VLAN", None)

        elif vpc.get_tenant_cutin_type() == "vxlan+route":
            match = self.construct_rule_match(dire, pnode["in"],
                chain.get_match_ethtype(),
                self.get_mac_by_dpid(pnode["dpid"]),
                vpc.get_tenant_cutin_router_mac(), None,
                chain.get_match_subnet(), chain.get_match_proto(),
                chain.get_match_l4port())
            act = self.construct_rule_action(oport,
                "eth_src", self.get_mac_by_dpid(pnode["dpid"]),
                "eth_dst", next_hnode["in"], None, None)
        hprlist.add_rule(vpc.get_id(), chain.get_id(), next_hnode["epid"],
                      pnode["dpid"], match, act)

    def calc_rule_chain_last_switch(self, dire, vpc, chain,
                                    pnode, prev_snode, prev_hnode, hprlist):

        if prev_snode == None:
            match = self.construct_rule_match(dire, pnode["in"],
                chain.get_match_ethtype(),
                self.get_mac_by_dpid(pnode["dpid"]),
                prev_hnode["out"], None,
                chain.get_match_subnet(), chain.get_match_proto(),
                chain.get_match_l4port())
        else:
            match = self.construct_rule_match(dire, pnode["in"],
                chain.get_match_ethtype(),
                self.get_mac_by_dpid(pnode["dpid"]),
                self.get_mac_by_dpid(prev_snode["dpid"]),None,
                chain.get_match_subnet(), chain.get_match_proto(),
                chain.get_match_l4port())

        if pnode["out"] == pnode["in"]:
            oport = "IN_PORT"
        else:
            oport = pnode["out"]
        if vpc.get_tenant_cutin_type() == "route":
            act = self.construct_rule_action(oport,
                    "eth_src", self.get_mac_by_dpid(pnode["dpid"]),
                    "eth_dst", vpc.get_tenant_cutin_router_mac(),
                    None, None)
        elif vpc.get_tenant_cutin_type() == "vlan+route":
            act = self.construct_rule_action(oport,
                    "eth_src", self.get_mac_by_dpid(pnode["dpid"]),
                    "eth_dst", vpc.get_tenant_cutin_router_mac(),
                    "PUSH_VLAN", vpc.get_tenant_cutin_vid())
        elif vpc.get_tenant_cutin_type() == "vxlan+route":
            act = self.construct_rule_action(oport,
                    "eth_src", self.get_mac_by_dpid(pnode["dpid"]),
                    "eth_dst", vpc.get_tenant_cutin_router_mac(),
                    None, None)
        hprlist.add_rule(vpc.get_id(), chain.get_id(), "tenant",
                      pnode["dpid"], match, act)

    def calc_rule_chain_mid_switch(self, dire, vpc, chain, pnode,
                    prev_snode, prev_hnode, next_snode, next_hnode, hprlist):

        if pnode["out"] == pnode["in"]:
            oport = "IN_PORT"
        else:
            oport = pnode["out"]

        if prev_snode == None:
            match = self.construct_rule_match(dire, pnode["in"],
                chain.get_match_ethtype(),
                vpc.get_tenant_to_ovs_mac(),
                prev_hnode["out"], None,
                chain.get_match_subnet(), chain.get_match_proto(),
                chain.get_match_l4port())
        else:
            match = self.construct_rule_match(dire, pnode["in"],
                chain.get_match_ethtype(),
                next_hnode["in"],
                self.get_mac_by_dpid(prev_snode["dpid"]),None,
                chain.get_match_subnet(), chain.get_match_proto(),
                chain.get_match_l4port())

        if next_snode == None:
            act = self.construct_rule_action(oport,
                "eth_src", vpc.get_tenant_to_ovs_mac(),
                "eth_dst", next_hnode["in"],
                None, None)
        else:
            if next_hnode == None:
                act = self.construct_rule_action(oport,
                    "eth_src", self.get_mac_by_dpid(pnode["dpid"]),
                    "eth_dst", self.get_mac_by_dpid(next_snode["dpid"]),
                    None, None)
            else:
                act = self.construct_rule_action(oport,
                    "eth_src", self.get_mac_by_dpid(pnode["dpid"]),
                    "eth_dst", next_hnode["in"],
                    None, None)
        if next_hnode == None:
            epid = "tenant"
        else:
            epid = next_hnode["epid"]
        hprlist.add_rule(vpc.get_id(), chain.get_id(), epid,
                      pnode["dpid"], match, act)

    def calc_rule_chain_bypass(self, dire, vpc, topo, chain, hprlist):
        if vpc.get_tenant_cutin_type() == "route":
            match = self.construct_rule_match(dire,
                topo.get_softsw_uplink_portno(vpc.get_tenant_cutin_to_ovs_id()),
                chain.get_match_ethtype(),
                vpc.get_tenant_to_ovs_mac(),
                vpc.get_tenant_cutin_router_mac(), None,
                chain.get_match_subnet(), chain.get_match_proto(),
                chain.get_match_l4port())
        elif vpc.get_tenant_cutin_type() == "vlan+route":
            match = self.construct_rule_match(dire,
                topo.get_softsw_uplink_portno(vpc.get_tenant_cutin_to_ovs_id()),
                chain.get_match_ethtype(),
                vpc.get_tenant_to_ovs_mac(),
                vpc.get_tenant_cutin_router_mac(),
                vpc.get_tenant_cutin_vid(),
                chain.get_match_subnet(), chain.get_match_proto(),
                chain.get_match_l4port())
        elif vpc.get_tenant_cutin_type() == "vxlan+route":
            match = self.construct_rule_match(dire,
                topo.get_softsw_uplink_portno(vpc.get_tenant_cutin_to_ovs_id()),
                chain.get_match_ethtype(),
                vpc.get_tenant_to_ovs_mac(),
                vpc.get_tenant_cutin_router_mac(), None,
                chain.get_match_subnet(), chain.get_match_proto(),
                chain.get_match_l4port())

        act = self.construct_rule_action("IN_PORT",
            "eth_src", vpc.get_tenant_to_ovs_mac(), 
            "eth_dst", vpc.get_tenant_cutin_router_mac(),
            None, None)
        hprlist.add_rule(vpc.get_id(), chain.get_id(), "tenant",
                      vpc.get_tenant_cutin_to_ovs_id(), match, act)


    def calc_rule_chain_one_dire(self, dire, vpc, topo, chain):
        hprlist = self.calc_path_one_dire(dire, vpc, topo, chain)
        print("hpnodes: " + json.dumps(hprlist.get_pnodes()))
        length = len(hprlist.get_pnodes())
        if length == 0:
            print("pnodes number is 0, reflect the packets of this chain's match")
            self.calc_rule_chain_bypass(dire, vpc, topo, chain, hprlist)
            return hprlist
            
        #calc rule for each switch, at least three pnodes in a path
        for i, pnode in enumerate(hprlist.get_pnodes()):
            if pnode["type"] == "switch":
                if i == 0:
                    if hprlist.get_pnode(i+1)["type"] == "switch":
                        next_snode = hprlist.get_pnode(i+1)
                        next_hnode = hprlist.get_pnode(i+2)
                        self.calc_rule_chain_first_switch(dire, vpc, chain,
                                        pnode, next_snode, next_hnode, hprlist)
                    elif hprlist.get_pnode(i+1)["type"] == "endpoint":
                        next_hnode = hprlist.get_pnode(i+1)
                        self.calc_rule_chain_first_switch(dire, vpc, chain,
                                                pnode, None, next_hnode, hprlist)
                    else:
                        print("next path type not recognized")
                elif i == 1:
                    prev_snode = hprlist.get_pnode(i-1)
                    next_hnode = hprlist.get_pnode(i+1)
                    self.calc_rule_chain_mid_switch(dire, vpc, chain, pnode,
                                    prev_snode, None, None, next_hnode, hprlist)
                elif i == length - 2:
                    prev_hnode = hprlist.get_pnode(i-1)
                    next_snode = hprlist.get_pnode(i+1)
                    self.calc_rule_chain_mid_switch(dire, vpc, chain, pnode,
                                    None, prev_hnode, next_snode, None, hprlist)
                elif i == length - 1:
                    if hprlist.get_pnode(i-1)["type"] == "switch":
                        prev_snode = hprlist.get_pnode(i-1)
                        prev_hnode = hprlist.get_pnode(i-2)
                        self.calc_rule_chain_last_switch(dire, vpc, chain,
                                        pnode, prev_snode, prev_hnode, hprlist)
                    elif hprlist.get_pnode(i-1)["type"] == "endpoint":
                        prev_hnode = hprlist.get_pnode(i-1)
                        self.calc_rule_chain_last_switch(dire, vpc, chain,
                                                pnode, None, prev_hnode, hprlist)
                    else:
                        print("prev path type not recognized")
                else:
                    if hprlist.get_pnode(i-1)["type"] == "switch":
                        prev_snode = hprlist.get_pnode(i-1)
                        prev_hnode = hprlist.get_pnode(i-2)
                        next_hnode = hprlist.get_pnode(i+1)
                        self.calc_rule_chain_mid_switch(dire, vpc, chain, pnode,
                                prev_snode, prev_hnode, None, next_hnode, hprlist)
                    elif hprlist.get_pnode(i+1)["type"] == "switch":
                        prev_hnode = hprlist.get_pnode(i-1)
                        next_snode = hprlist.get_pnode(i+1)
                        next_hnode = hprlist.get_pnode(i+2)
                        self.calc_rule_chain_mid_switch(dire, vpc, chain, pnode,
                                None, prev_hnode, next_snode, next_hnode, hprlist)
                    else:
                        prev_hnode = hprlist.get_pnode(i-1)
                        next_hnode = hprlist.get_pnode(i+1)
                        self.calc_rule_chain_mid_switch(dire, vpc, chain, pnode,
                                None, prev_hnode, None, next_hnode, hprlist)
        #print(json.dumps(hprlist.get_rnodes()))
        return hprlist
    # private functions end

    def add_vpclist_rules(self, vpclist, topo):
        for vpc in vpclist.vpcs:
            for chain in vpc.chain_list:
                print("outer add chain rules for " + json.dumps(chain.get_data()))
            self.add_vpc_rules(vpc, topo)
        #print(json.dumps(self.vprlist.data))

    def get_vpclist_rules(self, vpclist):
        return self.vprlist.data

    def del_vpclist_rules(self, vpclist):
        del self.vprlist.data

    def add_vpc_rules(self, vpc, topo):
        print("add vpc rules for " + json.dumps(vpc.get_data()))
        self.vprlist.create_vpc_path(vpc.get_id())
        for chain in vpc.chain_list:
            #print("outer add chain rules for " + json.dumps(chain.get_data()))
            self.add_vpc_chain_rules(vpc, chain, topo)

    def get_vpc_rules(self, vpcid):
        return self.vprlist.get_vpc_path(vpcid)

    def del_vpc_rules(self, vpcid):
        self.vprlist.del_vpc_path(vpcid)

    def add_vpc_chain_rules(self, vpc, chain, topo):
        print("inner add chain rules for " + json.dumps(chain.get_data()))
        self.vprlist.create_chain_path(vpc.get_id(), chain.get_id())
        vprlist_ing = self.calc_rule_chain_one_dire("ingress", vpc, topo, chain)
        vprlist_egr = self.calc_rule_chain_one_dire("egress", vpc, topo, chain)
        print("ingress: " + json.dumps(vprlist_ing.get_rnodes()))
        print("egress: " + json.dumps(vprlist_egr.get_rnodes()))
        self.vprlist.set_ingress(vpc.get_id(), chain.get_id(), vprlist_ing)
        self.vprlist.set_egress(vpc.get_id(), chain.get_id(), vprlist_egr)
        print("all: " + json.dumps(self.vprlist.data))
        
    def get_vpc_chain_rules(self, vpcid, chainid):
        return self.vprlist.get_chain_path(vpcid, chainid)

    def del_vpc_chain_rules(self, vpcid, chainid):
        self.vprlist.del_chain_path(vpcid, chainid)

    #for debug purpose
    def get_vpc_chain_switch_rules(self, seq):
        print("for debug purpose")

    def get_endpoint_rules(self, seq):
        print("for debug purpose")

    def get_switch_rules(self, seq):
        print("for debug purpose")

