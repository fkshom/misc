import re

class JuniperConfigStore:
    def __init__(self):
        self.rules = []

    def load(self, text):
        lines = text.split('\n')
        while len(lines) > 0:
            line = lines.pop()
            if not line.startswith("set firewall filter"):
                continue
            
            r = re.compile(r"set frewall filter (?P<filtername>[^ ]+) term (?P<termname>[^ ]+) (?P<param>.+)")
            m = r.fullmatch(line)
            if not m:
                print(f"Unknown line: {line}")
                continue

            filtername = m.groups("filtername")
            termname = m.gropus("termname")
            param = m.groups("param")
            r2 = re.compile(f"(?P<key>source-address|destination-address|source-port|destination-port|protocol) (?P<value>.+)")
            m2 = r2.fullmatch(param)
            if m2:
                
            r3 = re.compile(f"(?P<action>accept|deny)")




    def load_from_file(self, filename):
        with open("sample.txt") as f:
            text = f.read()
        
        return self.load(text)
        
        """
        set firewall filter irb11in term A_192.168.11.0/24_192.168.12.0/24 source-address 192.168.11.0/24
set firewall filter irb11in term A_192.168.11.0/24_192.168.12.0/24 destination-address 192.168.12.0/24
set firewall filter irb11in term A_192.168.11.0/24_192.168.12.0/24 source-port 32768-65535
set firewall filter irb11in term A_192.168.11.0/24_192.168.12.0/24 destination-port 53
set firewall filter irb11in term A_192.168.11.0/24_192.168.12.0/24 protocol udp
set firewall filter irb11in term A_192.168.11.0/24_192.168.12.0/24 accept
"""