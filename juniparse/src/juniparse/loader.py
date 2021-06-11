import re
from pprint import pprint as pp
from collections import OrderedDict


class JuniperConfigStore:
    def __init__(self):
        self._rules = OrderedDict()

    def filternames(self):
        return self._rules.keys()

    def termnames(self, filternames):
        return self._rules[filternames].keys()

    def rules_with_dict(self):
        return self._rules

    def rules(self, filtername=None):
        result = []
        target_filternames = []
        if filtername:
            target_filternames.append(filtername)
        else:
            target_filternames = self.filternames()

        for filtername in target_filternames:
            terms = self._rules[filtername]
            for termname, params in terms.items():
                rule = {}
                rule["filtername"] = filtername
                rule["termname"] = termname
                for key, value in params.items():
                    rule[key] = value
                result.append(rule)
        return result

    def _parse_firewallfilter(self, line):
        r = re.compile(r"(?P<command>set|deactivate) firewall filter (?P<filtername>[^ ]+) term (?P<termname>[^ ]+) (?P<param>.+)")
        m = r.fullmatch(line)
        if not m:
            print(f"Unknown line: {line}")
            raise Exception()

        command = m.group("command") # 扱いに困っている
        filtername = m.group("filtername")
        termname = m.group("termname")
        param = m.group("param")
        r2 = re.compile(f"(?P<key>source-address|destination-address|source-port|destination-port|protocol) (?P<value>.+)")
        m2 = r2.fullmatch(param)
        if m2:
            key = m2.group("key")
            value = m2.group("value")
            self._rules.setdefault(filtername, OrderedDict())
            self._rules[filtername].setdefault(termname, {})
            self._rules[filtername][termname].setdefault(key, [])
            self._rules[filtername][termname][key].append(value)

        r3 = re.compile(f"(?P<action>accept|deny)")
        m3 = r3.fullmatch(param)
        if m3:
            action = m3.group("action")
            self._rules.setdefault(filtername, OrderedDict())               
            self._rules[filtername].setdefault(termname, {})
            self._rules[filtername][termname]["action"] = action
        
        return True

    def _parse_interface(self, line):
        r = re.compile(r"(?P<command>set|deactivate) interface (?P<interface>[^ ]+) unit (?P<unit>[^ ]+) family inet filter (?P<direction>[^ ]+) (?P<filtername>.+)")
        m = r.fullmatch(line)
        if not m:
            print(f"Unknown line: {line}")
            raise Exception()
        
        command = m.group("command") # 扱いに困っている
        interface = m.group("interface")
        unit = m.group("unit")
        direction = m.group("direction")
        filtername = m.group("filtername")
        self._interface.setdefault(interface, OrderedDict())
        self._interface[interface].setdefault(unit, OrderedDict())
        self._interface[interface][unit][direction] = filtername

        return True

    def load(self, text):
        rules = OrderedDict()
        lines = text.split('\n')
        while len(lines) > 0:
            line = lines.pop(0)
            if line.startswith("set firewall filter"):
                self._parse_firewallfilter(line)
            elif line.startswith("deactivate firewall filter"):
                self._parse_firewallfilter(line)
            elif line.startswith("set interface irb unit"):
                self._parse_interface(line)
            elif line.startswith("deactivate interface irb unit"):
                self._parse_interface(line)

    def load_from_file(self, filename):
        with open("sample.txt") as f:
            text = f.read()
        
        return self.load(text)
        

text = """
set firewall filter irb11in term B_192.168.11.0/24_192.168.12.0/24 source-address 192.168.11.0/24
set firewall filter irb11in term B_192.168.11.0/24_192.168.12.0/24 destination-address 192.168.12.0/24
set firewall filter irb11in term B_192.168.11.0/24_192.168.12.0/24 destination-address 192.168.12.0/24
set firewall filter irb11in term B_192.168.11.0/24_192.168.12.0/24 source-port 32768-65535
set firewall filter irb11in term B_192.168.11.0/24_192.168.12.0/24 source-port 32768-65535
set firewall filter irb11in term B_192.168.11.0/24_192.168.12.0/24 destination-port 53
set firewall filter irb11in term B_192.168.11.0/24_192.168.12.0/24 protocol udp
set firewall filter irb11in term B_192.168.11.0/24_192.168.12.0/24 accept
set firewall filter irb11in term A_192.168.11.0/24_192.168.12.0/24 source-address 192.168.11.0/24
set firewall filter irb11in term A_192.168.11.0/24_192.168.12.0/24 destination-address 192.168.12.0/24
set firewall filter irb11in term A_192.168.11.0/24_192.168.12.0/24 destination-address 192.168.12.0/24
set firewall filter irb11in term A_192.168.11.0/24_192.168.12.0/24 source-port 32768-65535
set firewall filter irb11in term A_192.168.11.0/24_192.168.12.0/24 source-port 32768-65535
set firewall filter irb11in term A_192.168.11.0/24_192.168.12.0/24 destination-port 53
set firewall filter irb11in term A_192.168.11.0/24_192.168.12.0/24 protocol udp
set firewall filter irb11in term A_192.168.11.0/24_192.168.12.0/24 accept
"""

jcs = JuniperConfigStore()
jcs.load(text)

for rule in jcs.rules():
    pp(rule)