import pytest
from pprint import pprint as pp
import juniparse.loader2

@pytest.fixture(scope='function', autouse=False)
def sample1():
    text = """
set firewall filter irb11in term B_192.168.11.0/24_192.168.12.0/24 from source-address 192.168.11.0/24
set firewall filter irb11in term B_192.168.11.0/24_192.168.12.0/24 from destination-address 192.168.12.0/24
set firewall filter irb11in term B_192.168.11.0/24_192.168.12.0/24 from destination-address 192.168.12.0/24
set firewall filter irb11in term B_192.168.11.0/24_192.168.12.0/24 from source-port 32768-65535
set firewall filter irb11in term B_192.168.11.0/24_192.168.12.0/24 from source-port 32768-65535
set firewall filter irb11in term B_192.168.11.0/24_192.168.12.0/24 from destination-port 53
set firewall filter irb11in term B_192.168.11.0/24_192.168.12.0/24 from protocol udp
set firewall filter irb11in term B_192.168.11.0/24_192.168.12.0/24 then accept
set firewall filter irb11in term B_192.168.11.0/24_192.168.12.0/24 from source-address 192.168.11.0/24
set firewall filter irb11in term B_192.168.11.0/24_192.168.12.0/24 from destination-address 192.168.12.0/24
set firewall filter irb11in term A_192.168.11.0/24_192.168.12.0/24 then count counter-one
set firewall filter irb11in term A_192.168.11.0/24_192.168.12.0/24 then forwarding-class expedited-forwarding
set firewall filter irb11in term A_192.168.11.0/24_192.168.12.0/24 then loss-priority high
set firewall filter irb11in term A_192.168.11.0/24_192.168.12.0/24 then discard
"""
    yield text.strip()


def test1(sample1):
    jcs = juniparse.loader2.JuniperConfigStore()
    jcs.load(sample1)
    pp(jcs._firewallfilters._filters)
    for rule in jcs._firewallfilters._filters:
        pp(rule)

    assert 1 == 2