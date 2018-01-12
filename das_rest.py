import logging
import json
import ast

from ryu.app.dbssdn.vpc import Vpclist
from ryu.app.dbssdn.topo import Topo
from ryu.app.dbssdn.rule import Rule

from ryu.base import app_manager
# from ryu.controller import ofp_event
from ryu.controller import dpset
# from ryu.controller.handler import MAIN_DISPATCHER
# from ryu.controller.handler import set_ev_cls
from ryu.exception import RyuException
from ryu.ofproto import ofproto_v1_0
from ryu.ofproto import ofproto_v1_2
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ofproto_v1_4
from ryu.ofproto import ofproto_v1_5
from ryu.lib import ofctl_v1_0
from ryu.lib import ofctl_v1_2
from ryu.lib import ofctl_v1_3
from ryu.lib import ofctl_v1_4
from ryu.lib import ofctl_v1_5
from ryu.app.wsgi import ControllerBase
from ryu.app.wsgi import Response
from ryu.app.wsgi import WSGIApplication

LOG = logging.getLogger('ryu.app.das_rest')

# supported ofctl versions in this restful app
supported_ofctl = {
    ofproto_v1_0.OFP_VERSION: ofctl_v1_0,
    ofproto_v1_2.OFP_VERSION: ofctl_v1_2,
    ofproto_v1_3.OFP_VERSION: ofctl_v1_3,
    ofproto_v1_4.OFP_VERSION: ofctl_v1_4,
    ofproto_v1_5.OFP_VERSION: ofctl_v1_5,
}


class CommandNotFoundError(RyuException):
    message = 'No such command : %(cmd)s'


class PortNotFoundError(RyuException):
    message = 'No such port info: %(port_no)s'


class VpcNotFoundError(RyuException):
    message = 'No such vpc: %(vpc)'


def das_get_method(method):
    def wrapper(self, req, *args):
        # Parse request json body
        try:
            if req.body:
                body = ast.literal_eval(req.body.decode('utf-8'))
            else:
                body = {}
        except SyntaxError:
            LOG.exception('Invalid syntax: %s', req.body)
            return Response(status=400)

        # Invoke DasController method
        try:
            ret = method(self, req, body, *args)
            return Response(content_type='application/json',
                            body=json.dumps(ret))
        except ValueError:
            LOG.exception('Invalid syntax: %s', req.body)
            return Response(status=400)
        except AttributeError:
            LOG.exception('Unsupported OF request in this version')
            return Response(status=501)
        except CommandNotFoundError as e:
            LOG.exception(e.message)
            return Response(status=404)
        except PortNotFoundError as e:
            LOG.exception(e.message)
            return Response(status=404)
        except VpcNotFoundError as e:
            LOG.exception(e.message)
            return Response(status=404)

    return wrapper


def das_set_method(method):
    def wrapper(self, req, *args):
        # Parse request json body
        try:
            if req.body:
                body = ast.literal_eval(req.body.decode('utf-8'))
            else:
                body = {}
        except SyntaxError:
            LOG.exception('Invalid syntax: %s', req.body)
            return Response(status=400)

        # Invoke DasController method
        try:
            ret = method(self, req, body, *args)
            if ret is None:
                return Response(status=200)
            else:
                return Response(content_type='application/json', body=json.dumps(ret))
        except ValueError:
            LOG.exception('Invalid syntax: %s', req.body)
            return Response(status=400)
        except AttributeError:
            LOG.exception('Unsupported OF request in this version')
            return Response(status=501)
        except CommandNotFoundError as e:
            LOG.exception(e.message)
            return Response(status=404)
        except PortNotFoundError as e:
            LOG.exception(e.message)
            return Response(status=404)
        except VpcNotFoundError as e:
            LOG.exception(e.message)
            return Response(status=404)

    return wrapper


class DasController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(DasController, self).__init__(req, link, data, **config)
        self.dpset = data['dpset']
        self.waiters = data['waiters']
        self.topo = data['topo']
        self.vpclist = data['vpclist']
        self.rule = data['rule']

    @das_set_method
    def topo_switch_add(self, req, cfg):
        for sw in cfg:
            self.topo.del_softsw(sw["id"])
            self.topo.add_softsw(sw)
        return None

    @das_set_method
    def topo_switch_del(self, req, ids):
        swids = []

        if ids is []:
            for sw in self.topo.soft_switchs:
                swids.append(sw.get_id())
        else:
            swids = ids

        for swid in swids:
            self.topo.del_softsw(swid)

        return None

    @das_get_method
    def topo_switch_lookup(self, req, ids):
        ret = []
        swids = []

        if ids is []:
            for sw in self.topo.soft_switchs:
                swids.append(sw.get_id())
        else:
            swids = ids

        for swid in swids:
            sw = self.topo.get_softsw(swid)
            ret.append(sw.data)

        return ret

    @das_get_method
    def flow_switch_lookup(self, req, ids):
        ret = []
        for swid in ids:
            ret.append(self.rule.get_topo_switch_rules(swid))

        return ret

    @das_set_method
    def topo_ep_add(self, req, cfg):
        for ep in cfg:
            self.topo.del_ep(ep["id"])
            self.topo.add_ep(ep)
        return None

    @das_set_method
    def topo_ep_del(self, req, ids):
        epids = []

        if ids is []:
            for ep in self.topo.ep_list:
                epids.append(ep.get_id())
        else:
            epids = ids

        for epid in epids:
            # 1. make sure no vpc is using this ep
            ep = self.topo.get_ep(epid)
            if ep.ep_vpc_refcnt == 0:
                self.topo.del_ep(epid)
            else:
                print("endpoint %s still in use cann't delete" % epid)


        return None

    @das_get_method
    def topo_ep_lookup(self, req, ids):
        epids = []
        ret = []

        if ids is []:
            for ep in self.topo.ep_list:
                epids.append(ep.get_id())
        else:
            epids = ids

        for epid in epids:
            ep = self.topo.get_ep(epid)
            ret.append(ep.data)

        return ret

    @das_set_method
    def vpc_add(self, req, cfg):
        for vpc in cfg:
            self.vpclist.del_vpc(vpc["id"])
            self.vpclist.add_vpc(vpc)
        return None

    @das_set_method
    def vpc_del(self, req, ids):
        vpcids = []

        if ids is []:
            for vpc in self.vpclist.vpcs:
                vpcids.append(vpc.get_id())
        else:
            vpcids = ids

        for vpcid in vpcids:
            # 1. check that all the ep of this vpc are deleted
            vpc = self.vpclist.get_vpc(vpcid)
            if vpc.get_endpoints() is None:
                self.vpclist.del_vpc(vpcid)
            else:
                print("there are endpoints in vpc %s, cann't delete" % vpcid)

        return None

    @das_get_method
    def vpc_lookup(self, req, ids):
        vpcids = []
        ret = []

        if ids is []:
            for vpc in self.vpclist.vpcs:
                vpcids.append(vpc.get_id())
        else:
            vpcids = ids

        for vpcid in vpcids:
            vpc = self.vpclist.get_vpc(vpcid)
            ret.append({"id": vpc.get_id(), "subnets": vpc.get_tenant_subnets(),
                        "cutin": vpc.get_tenant_cutin()})

        return ret

    @das_get_method
    def flow_vpc_lookup(self, req, ids):
        ret = []
        for vpcid in ids:
            ret.append(self.rule.get_vpc_rules(vpcid))

        return ret

    @das_set_method
    def vpc_ep_add(self, req, cfg):
        vpc = self.vpclist.get_vpc(cfg["vpcid"])
        if vpc is None:
            raise VpcNotFoundError
        for epid in cfg["epids"]:
            if epid not in vpc.data["endpoints"]:
                ep = self.topo.get_ep(epid)
                ep.ep_vpc_refcnt += 1
                vpc.data["endpoints"].append(epid)
        return None

    @das_set_method
    def vpc_ep_del(self, req, cfg):
        vpc = self.vpclist.get_vpc(cfg["vpcid"])
        if vpc is None:
            raise VpcNotFoundError
        for epid in cfg["epids"]:
            if epid in vpc.data["endpoints"]:
                # 1. check that all chains using this ep is deleted
                if vpc.ep_chain_refcnt[epid] == 0:
                    vpc.data["endpoints"].remove(epid)
                    ep = self.topo.get_ep(epid)
                    ep.ep_vpc_refcnt -= 1
        return None

    @das_get_method
    def vpc_ep_lookup(self, req, cfg):
        ret = []
        vpc = self.vpclist.get_vpc(cfg["vpcid"])
        if vpc is None:
            raise VpcNotFoundError
        if cfg["epids"] is []:
            ret = vpc.data["endpoints"]
            return ret

        for epid in cfg["epids"]:
            if epid in vpc.data["endpoints"]:
                ret.append(epid)
        return ret

    @das_set_method
    def vpc_chain_add(self, req, cfg):
        vpc = self.vpclist.get_vpc(cfg["vpcid"])
        if vpc is None:
            raise VpcNotFoundError
        for chain in cfg["chains"]:
            # 1. firstly delete all the rules and flows of this chain
            self.rule.del_vpc_chain_rules(vpc.get_id(), chain["id"])
            vpc.del_chain(chain["id"])
            # 2. add the chain and it's rules
            vpc.add_chain(chain)
            self.rule.add_vpc_chain_rules(vpc, vpc.get_chain(chain["id"]), self.topo)

        return None

    @das_set_method
    def vpc_chain_del(self, req, cfg):
        chainids = []
        vpc = self.vpclist.get_vpc(cfg["vpcid"])
        if vpc is None:
            raise VpcNotFoundError
        if cfg["chainids"] is []:
            for chain in vpc.chain_list:
                chainids.append(chain.get_id())
        else:
            chainids = cfg["chainids"]

        for chainid in chainids:
            # 1. firstly delete all the rules and flows of this chain
            self.rule.del_vpc_chain_rules(vpc.get_id(), chainid)

            # 2. delete this chain
            vpc.del_chain(chainid)

        return None

    @das_get_method
    def vpc_chain_lookup(self, req, ids):
        chainids = []
        ret = []

        vpc = self.vpclist.get_vpc(ids["vpcid"])
        if vpc is None:
            raise VpcNotFoundError

        if ids["chainids"] is []:
            for chain in vpc.chain_list:
                chainids.append(chain.get_id())
        else:
            chainids = ids["chainids"]

        for chain in chainids:
            ret.append(vpc.get_chain(chain).data)

        return ret

    @das_get_method
    def flow_vpc_chain_lookup(self, req, ids):
        ret = []
        for chainid in ids["chainids"]:
            ret.append(self.rule.get_vpc_chain_rules(ids["vpcid"], chainid))

        return ret


class DasRestApi(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION,
                    ofproto_v1_2.OFP_VERSION,
                    ofproto_v1_3.OFP_VERSION,
                    ofproto_v1_4.OFP_VERSION,
                    ofproto_v1_5.OFP_VERSION]
    _CONTEXTS = {
        'dpset': dpset.DPSet,
        'wsgi': WSGIApplication
    }

    def __init__(self, *args, **kwargs):
        super(DasRestApi, self).__init__(*args)

        self.topo = Topo("topo.json")
        self.topo.load_topo_from_file()
        with open("portdesc.json", 'r+') as f:
            self.pdesc = json.load(f)
        for i, ssw in self.pdesc.items():
            self.topo.set_softsw_portdesc(i, ssw)

        self.vpclist = Vpclist("vpc.json")
        self.vpclist.load_vpcs_from_file()

        self.rule = Rule("path.json", "rule.json", "cmd.sh")

        self.dpset = kwargs['dpset']
        wsgi = kwargs['wsgi']
        self.waiters = {}
        self.data = {}
        self.data['dpset'] = self.dpset
        self.data['waiters'] = self.waiters
        self.data['topo'] = self.topo
        self.data['vpclist'] = self.vpclist
        self.data['rule'] = self.rule
        mapper = wsgi.mapper

        wsgi.registory['DasController'] = self.data
        path = '/das'

        uri = path + '/topo/switch/add'
        mapper.connect('das', uri,
                       controller=DasController, action='topo_switch_add',
                       conditions=dict(method=['POST']))

        uri = path + '/topo/switch/del'
        mapper.connect('das', uri,
                       controller=DasController, action='topo_switch_del',
                       conditions=dict(method=['POST']))

        uri = path + '/topo/switch/lookup'
        mapper.connect('das', uri,
                       controller=DasController, action='topo_switch_lookup',
                       conditions=dict(method=['POST']))

        uri = path + '/flow/switch/lookup'
        mapper.connect('das', uri,
                       controller=DasController, action='flow_switch_lookup',
                       conditions=dict(method=['POST']))

        uri = path + '/topo/ep/add'
        mapper.connect('das', uri,
                       controller=DasController, action='topo_ep_add',
                       conditions=dict(method=['POST']))

        uri = path + '/topo/ep/del'
        mapper.connect('das', uri,
                       controller=DasController, action='topo_ep_del',
                       conditions=dict(method=['POST']))

        uri = path + '/topo/ep/lookup'
        mapper.connect('das', uri,
                       controller=DasController, action='topo_ep_lookup',
                       conditions=dict(method=['POST']))

        uri = path + '/vpc/add'
        mapper.connect('das', uri,
                       controller=DasController, action='vpc_add',
                       conditions=dict(method=['POST']))

        uri = path + '/vpc/del'
        mapper.connect('das', uri,
                       controller=DasController, action='vpc_del',
                       conditions=dict(method=['POST']))

        uri = path + '/vpc/lookup'
        mapper.connect('das', uri,
                       controller=DasController, action='vpc_lookup',
                       conditions=dict(method=['POST']))

        uri = path + '/flow/vpc/lookup'
        mapper.connect('das', uri,
                       controller=DasController, action='flow_vpc_lookup',
                       conditions=dict(method=['POST']))

        uri = path + '/vpc/ep/add'
        mapper.connect('das', uri,
                       controller=DasController, action='vpc_ep_add',
                       conditions=dict(method=['POST']))

        uri = path + '/vpc/ep/del'
        mapper.connect('das', uri,
                       controller=DasController, action='vpc_ep_del',
                       conditions=dict(method=['POST']))

        uri = path + '/vpc/ep/lookup'
        mapper.connect('das', uri,
                       controller=DasController, action='vpc_ep_lookup',
                       conditions=dict(method=['POST']))

        uri = path + '/vpc/chain/add'
        mapper.connect('das', uri,
                       controller=DasController, action='vpc_chain_add',
                       conditions=dict(method=['POST']))

        uri = path + '/vpc/chain/del'
        mapper.connect('das', uri,
                       controller=DasController, action='vpc_chain_del',
                       conditions=dict(method=['POST']))

        uri = path + '/vpc/chain/lookup'
        mapper.connect('das', uri,
                       controller=DasController, action='vpc_chain_lookup',
                       conditions=dict(method=['POST']))

        uri = path + '/flow/vpc/chain/lookup'
        mapper.connect('das', uri,
                       controller=DasController, action='flow_vpc_chain_lookup',
                       conditions=dict(method=['POST']))

    def stats_reply_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath

        if dp.id not in self.waiters:
            return
        if msg.xid not in self.waiters[dp.id]:
            return
        lock, msgs = self.waiters[dp.id][msg.xid]
        msgs.append(msg)

        flags = 0
        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            flags = dp.ofproto.OFPSF_REPLY_MORE
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            flags = dp.ofproto.OFPSF_REPLY_MORE
        elif dp.ofproto.OFP_VERSION >= ofproto_v1_3.OFP_VERSION:
            flags = dp.ofproto.OFPMPF_REPLY_MORE

        if msg.flags & flags:
            return
        del self.waiters[dp.id][msg.xid]
        lock.set()

    def features_reply_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath

        if dp.id not in self.waiters:
            return
        if msg.xid not in self.waiters[dp.id]:
            return
        lock, msgs = self.waiters[dp.id][msg.xid]
        msgs.append(msg)

        del self.waiters[dp.id][msg.xid]
        lock.set()
