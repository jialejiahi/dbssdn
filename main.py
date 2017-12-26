import json
from vpc import Vpclist, Vpc, Vchain, Vtenant
from topo import Topo, Controller, Softsw, Endpoint
from rule import Rule


topo = Topo("topo.json")
topo.load_topo_from_file()
with open("portdesc.json", 'r+') as f:
    pdesc = json.load(f)
for i, ssw in pdesc.items():
    topo.set_softsw_portdesc(i, ssw)

vpclist = Vpclist("vpc.json")
vpclist.load_vpcs_from_file()

rule = Rule("path.json", "rule.json", "cmd.sh")
rule.add_vpclist_rules(vpclist, topo)
rule.save_rules_to_file()
rule.gen_add_cmds(topo)
