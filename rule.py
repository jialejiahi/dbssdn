import json
from user import User, Userlist
from topo import Softsw, Topo
from path import Path, Pathlist

class Rule():
    def __init__(self, *args, **kwargs):
        print("class Rule create instance")
        self.userlist = Userlist("userlist")
        self.topo = Topo("topo")
        self.pathlist = Pathlist("pathlist")
        self.rulelist = []
    
        
    def load_config_from_file(self):
        self.userlist.load_users_from_file()
        self.topo.load_topo_from_file()

    def save_rules_to_file(self):
        with open("rules_w.json", 'w') as f:
            f.write(json.dumps(self.rulelist))

    def gen_cmd_file_by_rules(self):
        with open("cmds_w.sh", 'w') as f:
            for rule in self.rulelist:
                f.write("curl -X POST -d '")
                f.write(json.dumps(rule))
                f.write("' http://10.11.88.1:8080/stats/flowentry/add\n")

    def construct_rule(self, dpid, table_id, prio, match, actions):
        # we should check the fields firstly
        rule = {"dpid":dpid, "table_id":table_id, "priority":prio, "match":match, "actions":actions}

        return rule

    def construct_rule_field_match(self, eth_type, eth_dst, eth_src, nw_dst, nw_src, in_port):
        m = {}
        if eth_type != None:
            m["eth_type"] = eth_type
        if eth_dst != None:
            m["eth_dst"] = eth_dst
        if eth_src != None:
            m["eth_src"] = eth_src
        if nw_dst != None:
            m["nw_dst"] = nw_dst
        if nw_src != None:
            m["nw_src"] = nw_src
        if in_port != None:
            m["in_port"] = in_port

        return m

    def construct_vlan_rule_field_match(self, eth_type, eth_dst, eth_src, dl_vlan, nw_dst, nw_src, in_port):
        m = {}
        if eth_type != None:
            m["eth_type"] = eth_type
        if eth_dst != None:
            m["eth_dst"] = eth_dst
        if eth_src != None:
            m["eth_src"] = eth_src
        if dl_vlan != None:
            m["dl_vlan"] = dl_vlan
        if nw_dst != None:
            m["nw_dst"] = nw_dst
        if nw_src != None:
            m["nw_src"] = nw_src
        if in_port != None:
            m["in_port"] = in_port

        return m

    def construct_rule_field_match_dir_wrapper(self, dire, ip, eth_dst, eth_src, in_port):
        m = {}

        if dire == "ingress":
            m = self.construct_rule_field_match(2048, eth_dst, eth_src, ip, None, in_port)
        elif dire == "egress":
            m = self.construct_rule_field_match(2048, eth_dst, eth_src, None, ip, in_port)
        else:
            print("param error")

        return m

    def construct_vlan_rule_field_match_dir_wrapper(self, dire, ip, eth_dst, eth_src, vlan_id, in_port):
        m = {}

        if dire == "ingress":
            m = self.construct_vlan_rule_field_match(2048, eth_dst, eth_src, vlan_id, ip, None, in_port)
        elif dire == "egress":
            m = self.construct_vlan_rule_field_match(2048, eth_dst, eth_src, vlan_id, None, ip, in_port)
        else:
            print("param error")

        return m

    def construct_rule_field_action(self, out_port, field_src, value_src,
                    field_dst, value_dst):
        act = []

        if out_port == None:
            print("no output port, error")
            return act
        if field_src != None:
            act.append({"type":"SET_FIELD", "field":field_src, "value":value_src})
        if field_dst != None:
            act.append({"type":"SET_FIELD", "field":field_dst, "value":value_dst})
        act.append({"type":"OUTPUT", "port": out_port})

        return act

    def construct_vlan_rule_field_action(self, out_port, field_src, value_src,
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
                act.append({"type":"SET_FIELD", "field":"vlan_vid", "value":vlan_id})
            elif act_vlan == "POP_VLAN":
                act.append({"type":"POP_VLAN"})
            elif act_vlan == "SET_VLAN":
                vlan_id = value_vlan + 0x1000
                act.append({"type":"SET_FIELD", "field":"vlan_vid", "value":vlan_id})
        
        act.append({"type":"OUTPUT", "port": out_port})

        return act
   
    def calc_path_for_user(self, id):
        print("calc path for user %d" % id)
        path_data = {}
        path_data_ingress = []
        path_data_egress = []
        
        path = Path(id, path_data)
        user = self.userlist.get_user(id)
        user_public = user.get_public()
        user_private = user.get_private()
        hosts = self.userlist.users[id].get_hosts()

        # construct the user node of ingress and egress firstly
        ing_user_node = {}
        if user.get_type() == "server_ip":
            ing_user_node = path.construct_user_node(0, "user_server_ip", user_public["server_ip"], user_public["router_ip"], user_public["router_mac"], None, None, None, None, user_public["router_to_sw"])
        elif user.get_type() == "server_ip_vlan":
            ing_user_node = path.construct_user_node(0, "user_server_ip_vlan", user_public["server_ip"], user_public["router_ip"], user_public["router_mac"], user_public["router_vlan"], None, None, None, user_public["router_to_sw"])
        elif user.get_type() == "server_ip_vxlan":
            ing_user_node = path.construct_user_node(0, "user_server_ip_vxlan", user_public["server_ip"], user_public["router_ip"], user_public["router_mac"], None, user_public["router_vni"], user_public["router_outer_ip"], user_public["router_outer_mac"],user_public["router_to_sw"])
        egr_user_node = ing_user_node
        path_data_ingress.append(ing_user_node)
        path_data_egress.append(egr_user_node)

        # find all the nodes of path_ing and path_egr, we construct the nodes by the seq of
        # path_in, so we should treat path_data_ingress as a queue while path_data_egress as a stack
        seq = 1
        for user_host in hosts:
            print("host seq %d" % user_host["seq"])
            topo_host = self.topo.get_host(user_host["id"])
            topo_host_id = topo_host.get_id()
            topo_host_type = topo_host.get_type()
            topo_host_in = topo_host.get_in_port()
            topo_host_out = topo_host.get_out_port()
            topo_host_insw = topo_host.get_in_sw()
            topo_host_outsw = topo_host.get_out_sw()
            # the host node's seq is not ZERO, it is computed in the next logic, it will be changed
            ing_host_node = path.construct_host_node(0, topo_host_insw, topo_host_in, topo_host_out)
            egr_host_node = path.construct_host_node(0, topo_host_insw, topo_host_out, topo_host_in)

            if user_host["type"] == "serial":
                print("host type serial")
                if user_host["id"] == topo_host_id:
                    print("host id %d" % topo_host_id)
                    # ----the first host of path_ing, also the last one for path_egr
                    # add the prev switch nodes to the path
                    if user_host["seq"] == 0:
                        print("add first host and prev switch nodes")
                        # the host is connected to the direct switch
                        if topo_host_insw == user_public["router_to_sw"]:                                                        
                            in_sw = self.topo.get_softsw_by_data_id(topo_host_insw)
                            if user.get_type() == "server_ip":
                                uplink_port = in_sw.get_uplink_port("server_ip")
                            elif user.get_type() == "server_ip_vlan":
                                uplink_port = in_sw.get_uplink_port("server_ip_vlan")
                            elif user.get_type() == "server_ip_vxlan":
                                uplink_port = in_sw.get_uplink_port("server_ip_vxlan")
                            # add direct switch node
                            ing_direct_node = path.construct_sw_node(1,
                                topo_host_insw, uplink_port,
                                in_sw.get_port_by_mac(topo_host_in))
                            egr_direct_node = path.construct_sw_node(1,
                                topo_host_insw, in_sw.get_port_by_mac(topo_host_in),
                                uplink_port)
                            # change the host node seq and add these node to path
                            ing_host_node["seq"] = 2
                            egr_host_node["seq"] = 2
                            path_data_ingress.append(ing_direct_node)
                            path_data_egress.append(egr_direct_node)
                            path_data_ingress.append(ing_host_node)
                            path_data_egress.append(egr_host_node)
                            seq = 2
                        else:
                            # the host is NOT connected to the direct switch(which the direct host connect to)
                            # just add the input switch node

                            direct_sw =  self.topo.get_softsw_by_data_id(user_public["router_to_sw"])
                            if user.get_type() == "server_ip":
                                uplink_port = direct_sw.get_uplink_port("server_ip")
                            elif user.get_type() == "server_ip_vlan":
                                uplink_port = direct_sw.get_uplink_port("server_ip_vlan")
                            elif user.get_type() == "server_ip_vxlan":
                                uplink_port = direct_sw.get_uplink_port("server_ip_vxlan")
                            
                            ing_direct_node = path.construct_sw_node(1,
                                direct_sw.get_data_id(), uplink_port,
                                direct_sw.get_uplink_port("server_ip"))
                            egr_direct_node = path.construct_sw_node(1,
                                direct_sw.get_data_id(), direct_sw.get_uplink_port("server_ip"),
                                uplink_port)
                            
                            in_sw =  self.topo.get_softsw_by_data_id(topo_host_insw)
                            uplink_port = in_sw.get_uplink_port("server_ip")
                            
                            ing_sw_node = path.construct_sw_node(2,
                                topo_host_insw, uplink_port,
                                in_sw.get_port_by_mac(topo_host_in))
                            egr_sw_node = path.construct_sw_node(2,
                                topo_host_insw, in_sw.get_port_by_mac(topo_host_in),
                                uplink_port)

                            ing_host_node["seq"] = 3
                            egr_host_node["seq"] = 3

                            path_data_ingress.append(ing_direct_node)
                            path_data_egress.append(egr_direct_node)
                            path_data_ingress.append(ing_sw_node)
                            path_data_egress.append(egr_sw_node)
                            path_data_ingress.append(ing_host_node)
                            path_data_egress.append(egr_host_node)
                            seq = 3
                    # ----all hosts except the first one is handled here
                    # add the prev switchs to the path
                    else:
                        print("add appending host and their prev switches nodes")
                        prev_user_host = hosts[user_host["seq"] - 1]
                        prev_topo_host = self.topo.get_host(prev_user_host["id"])
                        prev_topo_host_id = prev_topo_host.get_id()
                        prev_topo_host_type = prev_topo_host.get_type()
                        prev_topo_host_in = prev_topo_host.get_in_port()
                        prev_topo_host_out = prev_topo_host.get_out_port()
                        prev_topo_host_insw = prev_topo_host.get_in_sw()
                        prev_topo_host_outsw = prev_topo_host.get_out_sw()

                        # this host and the prev host are connected to same switch
                        if prev_topo_host_outsw == topo_host_insw:
                            in_sw =  self.topo.get_softsw_by_data_id(topo_host_insw)
                            seq += 1
                            ing_sw_node = path.construct_sw_node(seq,
                                topo_host_insw, in_sw.get_port_by_mac(prev_topo_host_out),
                                in_sw.get_port_by_mac(topo_host_in))
                            egr_sw_node = path.construct_sw_node(seq,
                                topo_host_insw, in_sw.get_port_by_mac(topo_host_in),
                                in_sw.get_port_by_mac(prev_topo_host_out))
                            seq += 1
                            ing_host_node["seq"] = seq
                            egr_host_node["seq"] = seq

                            path_data_ingress.append(ing_sw_node)
                            path_data_egress.append(egr_sw_node)
                            path_data_ingress.append(ing_host_node)
                            path_data_egress.append(egr_host_node)
                        # this host and the prev host are NOT on same switch
                        else:
                            prev_out_sw =  self.topo.get_softsw_by_data_id(prev_topo_host_outsw)
                            uplink_port = prev_out_sw.get_uplink_port("server_ip")
                            seq += 1
                            prev_out_sw_ing_node = path.construct_sw_node(seq,
                                prev_topo_host_outsw, prev_out_sw.get_port_by_mac(prev_topo_host_out),
                                uplink_port)
                            prev_out_sw_egr_node = path.construct_sw_node(seq,
                                prev_topo_host_outsw, uplink_port,
                                prev_out_sw.get_port_by_mac(prev_topo_host_out))
                            in_sw =  self.topo.get_softsw_by_data_id(topo_host_insw)
                            uplink_port = in_sw.get_uplink_port("server_ip")
                            seq += 1
                            ing_sw_node = path.construct_sw_node(seq,
                                topo_host_insw, uplink_port,
                                in_sw.get_port_by_mac(topo_host_in))
                            egr_sw_node = path.construct_sw_node(seq,
                                topo_host_insw, in_sw.get_port_by_mac(topo_host_in),
                                uplink_port)
                            seq += 1
                            ing_host_node["seq"] = seq
                            egr_host_node["seq"] = seq
                            path_data_ingress.append(prev_out_sw_ing_node)
                            path_data_egress.append(prev_out_sw_egr_node)
                            path_data_ingress.append(ing_sw_node)
                            path_data_egress.append(egr_sw_node)
                            path_data_ingress.append(ing_host_node)
                            path_data_egress.append(egr_host_node)

                    # now we reach the last host, add the output switches
                    if user_host["seq"] == (len(hosts) - 1):
                        print("add the last switch nodes for the path")
                        if topo_host_outsw == user_public["router_to_sw"]:
                            seq += 1
                            egr_sw =  self.topo.get_softsw_by_data_id(topo_host_outsw)
                            if user.get_type() == "server_ip":
                                uplink_port = direct_sw.get_uplink_port("server_ip")
                            elif user.get_type() == "server_ip_vlan":
                                uplink_port = direct_sw.get_uplink_port("server_ip_vlan")
                            elif user.get_type() == "server_ip_vxlan":
                                uplink_port = direct_sw.get_uplink_port("server_ip_vxlan")
                            
                            ing_last_node = path.construct_sw_node(seq,
                                topo_host_outsw, egr_sw.get_port_by_mac(topo_host_out),
                                uplink_port)
                            egr_last_node = path.construct_sw_node(seq,
                                topo_host_outsw, uplink_port,
                                egr_sw.get_port_by_mac(topo_host_out))
                            path_data_ingress.append(ing_last_node)
                            path_data_egress.append(egr_last_node)
                        else:
                            egr_sw =  self.topo.get_softsw_by_data_id(topo_host_outsw)
                            uplink_port = egr_sw.get_uplink_port("server_ip")
                            seq += 1
                            ing_last_node = path.construct_sw_node(seq,
                                topo_host_outsw, egr_sw.get_port_by_mac(topo_host_out),
                                uplink_port)
                            egr_last_node = path.construct_sw_node(seq,
                                topo_host_outsw, uplink_port,
                                egr_sw.get_port_by_mac(topo_host_out))
                            path_data_ingress.append(ing_last_node)
                            path_data_egress.append(egr_last_node)

                            direct_sw =  self.topo.get_softsw_by_data_id(user_public["router_to_sw"])
                            if user.get_type() == "server_ip":
                                uplink_port = direct_sw.get_uplink_port("server_ip")
                            elif user.get_type() == "server_ip_vlan":
                                uplink_port = direct_sw.get_uplink_port("server_ip_vlan")
                            elif user.get_type() == "server_ip_vxlan":
                                uplink_port = direct_sw.get_uplink_port("server_ip_vxlan")
                            seq += 1
                            ing_last_direct_node = path.construct_sw_node(5,
                                 direct_sw.get_data_id(), uplink_port,
                                 uplink_port)
                            egr_last_direct_node = path.construct_sw_node(5,
                                 direct_sw.get_data_id(), uplink_port,
                                 uplink_port)
                            path_data_ingress.append(ing_last_direct_node)
                            path_data_egress.append(egr_last_direct_node)
                        
                        if user.get_type() == "server_ip":
                            ing_user_node = path.construct_user_node(seq +1, "user_server_ip", user_public["server_ip"], user_public["router_ip"], user_public["router_mac"], None, None, None, None, user_public["router_to_sw"])
                        elif user.get_type() == "server_ip_vlan":
                            ing_user_node = path.construct_user_node(seq +1, "user_server_ip_vlan", user_public["server_ip"], user_public["router_ip"], user_public["router_mac"], user_public["router_vlan"], None, None, None, user_public["router_to_sw"])
                        elif user.get_type() == "server_ip_vxlan":
                            ing_user_node = path.construct_user_node(seq +1, "user_server_ip_vxlan", user_public["server_ip"], user_public["router_ip"], user_public["router_mac"], None, user_public["router_vni"], user_public["router_outer_ip"], user_public["router_outer_mac"],user_public["router_to_sw"])
                        egr_user_node = ing_user_node
                        path_data_ingress.append(ing_user_node)
                        path_data_egress.append(egr_user_node)

                else:
                    print("host id error, user host id not the same with topo host id!")
        path_data_egress.reverse()
        path.set_ingress(path_data_ingress)
        path.set_egress(path_data_egress)
        # print("we got path ingress for user %d" % id)
        # print(json.dumps(path_data_ingress))

        # print("we got path egress for user %d" % id)
        # print(json.dumps(path_data_egress))

        return path

    def calc_path_list(self):
        for user in self.userlist.users:
            path = self.calc_path_for_user(user.get_id())
            self.pathlist.add_path(path)
        self.pathlist.save_paths_to_file()

    def calc_rule_one_direction(self, dir, path):
        #dir should be "ingress" or "egress"
        if dir == "ingress":
            print("calc ingress rules for one user")
        elif dir == "egress":
            print("calc egress rules for one user")
        else:
            print("param error")

        rule = {}
        rules =[]
        direct_sw = self.topo.get_softsw_by_data_id(path[0]["router_to_sw"])
        # iterate path and egress in one loop
        for i in xrange(len(path)):
            if path[i]["type"] == "switch":
                print("find a switch node on the path")
                print(json.dumps(path[i]))

                if path[i]["out"] == path[i]["in"]:
                    out_port = "IN_PORT"
                else:
                    out_port = path[i]["out"]

                if path[i-1]["type"][0:4] == "user":
                    if path[i-1]["type"] == "user_server_ip_vlan":
                        if path[i+1]["type"][0:4] == "user":
                            print("no host in the path, error")
                        elif path[i+1]["type"] == "switch":
                            print("this is the direct switch, sending to a host that connect to another switch")
                            
                            sw = self.topo.get_softsw_by_data_id(path[i]["id"])
                            match_field = self.construct_vlan_rule_field_match_dir_wrapper(dir, path[i-1]["server_ip"],
                                                direct_sw.data["uplink_port_mac"],path[i-1]["router_mac"], path[i-1]["router_vlan"], path[i]["in"])
                            
                            action_field = self.construct_vlan_rule_field_action(out_port, "eth_src",
                                          sw.data["uplink_port_mac"], "eth_dst", path[i+2]["in"], "POP_VLAN", None)
                            rule = self.construct_rule(path[i]["id"], 0, 11111, match_field, action_field)
                        elif path[i+1]["type"] == "host":
                            print("this is the direct switch, to a host that connect to this switch")
                            match_field = self.construct_vlan_rule_field_match_dir_wrapper(dir, path[i-1]["server_ip"],
                                                direct_sw.data["uplink_port_mac"],path[i-1]["router_mac"], path[i-1]["router_vlan"], path[i]["in"])
                            action_field = self.construct_vlan_rule_field_action(out_port, None,
                                          None, "eth_dst", path[i+1]["in"], "POP_VLAN", None)
                            rule = self.construct_rule(path[i]["id"], 0, 11111, match_field, action_field)
                    else:
                        if path[i+1]["type"][0:4] == "user":
                            print("no host in the path, error")
                        elif path[i+1]["type"] == "switch":
                            print("this is the direct switch, sending to a host that connect to another switch")
                            
                            sw = self.topo.get_softsw_by_data_id(path[i]["id"])
                            match_field = self.construct_rule_field_match_dir_wrapper(dir, path[i-1]["server_ip"], direct_sw.data["uplink_port_mac"],path[i-1]["router_mac"], path[i]["in"])
                            action_field = self.construct_rule_field_action(out_port, "eth_src",
                                          sw.data["uplink_port_mac"], "eth_dst", path[i+2]["in"])
                            rule = self.construct_rule(path[i]["id"], 0, 11111, match_field, action_field)
                        elif path[i+1]["type"] == "host":
                            print("this is the direct switch, to a host that connect to this switch")
                            match_field = self.construct_rule_field_match_dir_wrapper(dir, path[i-1]["server_ip"], direct_sw.data["uplink_port_mac"], path[i-1]["router_mac"], path[i]["in"])
                            action_field = self.construct_rule_field_action(out_port, None,
                                          None, "eth_dst", path[i+1]["in"])
                            rule = self.construct_rule(path[i]["id"], 0, 11111, match_field, action_field)
                elif path[i-1]["type"] == "switch":
                    if path[i+1]["type"][0:4] == "user":
                        print("this is the last direct switch")
                        # prev switch
                        psw = self.topo.get_softsw_by_data_id(path[i-1]["id"])
                        match_field = self.construct_rule_field_match_dir_wrapper(dir, path[i+1]["server_ip"], direct_sw.data["uplink_port_mac"],psw.data["uplink_port_mac"],  path[i]["in"])
                        if path[i+1]["type"] == "user_server_ip_vlan":
                            action_field = self.construct_vlan_rule_field_action(out_port, "eth_src", direct_sw.data["uplink_port_mac"], "eth_dst", path[0]["router_mac"], "PUSH_VLAN", path[0]["router_vlan"])
                        else:
                            action_field = self.construct_rule_field_action(out_port, "eth_src", direct_sw.data["uplink_port_mac"], "eth_dst", path[0]["router_mac"])
                        rule = self.construct_rule(path[i]["id"], 0, 11111, match_field, action_field)
                    elif path[i+1]["type"] == "switch":
                        print("three switchs in a row,\
                        this is only possible when the ovs switchs tree has two layer, \
                        which means ovs switches has a shared root")
                    elif path[i+1]["type"] == "host":
                        print("this is not direct switch, direct switch send pkts to me")
                        match_field = self.construct_rule_field_match_dir_wrapper(dir, path[0]["server_ip"], path[i+1]["in"],
                                      None,  path[i]["in"])
                        action_field = self.construct_rule_field_action(out_port, None,
                                      None, None, None)
                        rule = self.construct_rule(path[i]["id"], 0, 11111, match_field, action_field)
                elif path[i-1]["type"] == "host":
                    if path[i+1]["type"][0:4] == "user":
                        print("this is the last direct switch, sending pkts to user")
                        match_field = self.construct_rule_field_match_dir_wrapper(dir, path[i+1]["server_ip"], None,
                                      None, path[i]["in"])
                        if path[i+1]["type"] == "user_server_ip_vlan":
                            action_field = self.construct_vlan_rule_field_action(out_port, "eth_src",
                                      direct_sw.data["uplink_port_mac"], "eth_dst", path[0]["router_mac"], "PUSH_VLAN", path[0]["router_vlan"])
                        else:
                            action_field = self.construct_rule_field_action(out_port, "eth_src",
                                      direct_sw.data["uplink_port_mac"], "eth_dst", path[0]["router_mac"])
                        rule = self.construct_rule(path[i]["id"], 0, 11111, match_field, action_field)
                    elif path[i+1]["type"] == "switch":
                        print("this is not direct switch, send pkts to direct switch")
                        sw = self.topo.get_softsw_by_data_id(path[i]["id"])
                        nsw = self.topo.get_softsw_by_data_id(path[i+1]["id"])
                        match_field = self.construct_rule_field_match_dir_wrapper(dir, path[0]["server_ip"], None,
                                      None,  path[i]["in"])
                        if(path[i+2]["type"][0:4] == "user"):
                            action_field = self.construct_rule_field_action(out_port, "eth_src",
                                          sw.data["uplink_port_mac"], "eth_dst", nsw.data["uplink_port_mac"])
                        elif(path[i+2]["type"] == "host"):
                            action_field = self.construct_rule_field_action(out_port, "eth_src",
                                          sw.data["uplink_port_mac"], "eth_dst", path[i+2]["in"])
                        else:
                            print("currently not handled")
                        rule = self.construct_rule(path[i]["id"], 0, 11111, match_field, action_field)
                    elif path[i+1]["type"] == "host":
                        print("two hosts connect to me are sending pkts to each other")
                        match_field = self.construct_rule_field_match_dir_wrapper(dir, path[0]["server_ip"], None,
                                      None,  path[i]["in"])
                        action_field = self.construct_rule_field_action(out_port, None,
                                      None, "eth_dst", path[i+1]["in"])
                        rule = self.construct_rule(path[i]["id"], 0, 11111, match_field, action_field)
                if rule != None:
                    rules.append(rule)
                    # print(json.dumps(rule))
        return rules
    
    def calc_rule_list(self):
        for path in self.pathlist.paths:
            path_ing = path.get_ingress()
            path_egr = path.get_egress()
            rule_ing = []
            rule_egr = []

            rule_ing = self.calc_rule_one_direction("ingress", path_ing)
            rule_egr = self.calc_rule_one_direction("egress", path_egr)

            self.rulelist.extend(rule_ing)
            self.rulelist.extend(rule_egr)
        
        print(json.dumps(self.rulelist))


# rule = Rule()
# rule.load_config_from_file()
# rule.calc_path_list()
# rule.calc_rule_list()
# rule.save_rules_to_file()
# rule.gen_cmd_file_by_rules()

