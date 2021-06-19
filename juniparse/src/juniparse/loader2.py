import re
from pprint import pprint as pp
from collections import OrderedDict

class Interfaces():
    def __init__(self):
        self._interfaces = OrderedDict()
    
    def is_supported(self, line):
        if line.startswith("set interfaces"):
            return True
        elif line.startswith("deactivate interfaces"):
            return True
        else:
            return False

    def add(self, line):
        r = re.compile(r"(?P<command>set|deactivate) interfaces (?P<param>.+)")
        m = r.fullmatch(line)
        if not m:
            print(f"Unknown line: {line}")
            raise Exception()

        command = m.group("command") # 扱いに困っている
        param = m.group("param")
        r1 = re.compile(r"(?P<interface>[^ ]+) unit (?P<unit>[^ ]+) family inet filter (?P<direction>[^ ]+) (?P<filtername>.+)")
        m1 = r.fullmatch(param)
        r2 = re.compile(r"(?P<description>.+)")
        m2 = r.fullmatch(param)
        if m1:
            interface = m1.group("interface")
            unit = m1.group("unit")
            direction = m1.group("direction")
            filtername = m1.group("filtername")
            self._interface.setdefault(interface, OrderedDict())
            self._interface[interface].setdefault(unit, OrderedDict())
            self._interface[interface][unit][direction] = filtername
        elif m2:
            description = m2.group("description")
            self._interface.setdefault()  # ここから

class FirewallFilters():
    def __init__(self):
        self._filters = OrderedDict()

    def is_supported(self, line):
        if line.startswith("set firewall filter"):
            return True
        elif line.startswith("deactivate firewall filter"):
            return True
        else:
            return False

    def _parse_param_text(self, paramtext):
        result = {}
        param = paramtext
        r1 = re.compile(r"""
            from
            \s(?P<key>source-address|destination-address|source-port|destination-port|protocol)
            \s(?P<value>.+)
        """, re.X)
        m1 = r1.fullmatch(param)
        r2 = re.compile(f"from (?P<key>tcp-initial|tcp-established)")
        m2 = r2.fullmatch(param)
        r3 = re.compile(f"then (?P<action>count|forwarding-class|loss-priority) (?P<value>.+)")
        m3 = r3.fullmatch(param)
        r4 = re.compile(f"then (?P<action>accept|discard|syslog|log)")
        m4 = r4.fullmatch(param)
        if m1:
            key = m1.group("key")
            value = m1.group("value")
            result.setdefault(key, [])
            result[key].append(value)
        elif m2:
            key = m2.group("key")
            result[key] = True
        elif m3:
            action = m3.group("action")
            value = m3.group("value")
            result[action] = value
        elif m4:
            action = m4.group("action")
            result[action] = True
        else:
            raise Exception(f"cant parse {paramtext}")
        return result

    def add(self, line):
        r = re.compile(r"(?P<command>set|deactivate) firewall filter (?P<filtername>[^ ]+) term (?P<termname>[^ ]+) (?P<param>.+)")
        m = r.fullmatch(line)
        if not m:
            print(f"Unknown line: {line}")
            raise Exception()

        command = m.group("command")
        filtername = m.group("filtername")
        termname = m.group("termname")
        paramtext = m.group("param")
        paramdict = self._parse_param_text(paramtext)

        if command == "set":
            self._filters.setdefault(filtername, OrderedDict())
            self._filters[filtername].setdefault(termname, {})
            self._filters[filtername][termname].update(paramdict)
        else:
            self._filters[filtername][termname] = [
                _paramdict
                for _paramdict in self._filters[filtername][termname]
                if _paramdict != paramdict
            ]

class JuniperConfigStore:
    def __init__(self):
        self._interfaces = Interfaces()
        self._firewallfilters = FirewallFilters()
    
    def load(self, text):
        lines = text.split('\n')
        while len(lines) > 0:
            line = lines.pop(0)
            if self._interfaces.is_supported(line):
                self._interfaces.add(line)
            elif self._firewallfilters.is_supported(line):
                self._firewallfilters.add(line)
            else:
                print(f"Not supported. {line}")

        return self
