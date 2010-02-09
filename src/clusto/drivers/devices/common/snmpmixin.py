"""
SNMPMixin for objects that can be accessed with SNMP
"""

import clusto
from clusto.drivers import IPManager

import scapy

from socket import socket, AF_INET, SOCK_DGRAM

class SNMPMixin:
    """Provide SNMP capabilities to devices
    """

    def _snmp_connect(self, port=161):
        ip = IPManager.get_ips(self)
        if not ip:
            raise ValueError('Device %s does not have an IP' % self.name)
        ip = ip[0]

        community = self.attr_values(key='snmp', subkey='community', merge_container_attrs=True)
        if not community:
            raise ValueError('Device %s does not have an SNMP community attribute' % self.name)
        
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.connect((ip, port))
        return (str(community[0]), sock)

    def _snmp_get(self, oid):
        community, sock = self._snmp_connect()

        pdu = scapy.SNMPget(varbindlist=[scapy.SNMPvarbind(oid=str(oid))])
        p = scapy.SNMP(community=community, PDU=pdu)
        sock.sendall(p.build())

        r = scapy.SNMP(sock.recv(4096))
        return r.PDU.varbindlist[0].value.val

    def _snmp_set(self, oid, value):
        community, sock = self._snmp_connect()

        pdu = scapy.SNMPset(varbindlist=[scapy.SNMPvarbind(oid=str(oid), value=value)])
        p = scapy.SNMP(community=community, PDU=pdu)
        sock.sendall(p.build())

        r = scapy.SNMP(sock.recv(4096))
        return r

    def _snmp_walk(self, oid_prefix):
        community, sock = self._snmp_connect()

        nextoid = oid_prefix
        while True:
            p = scapy.SNMP(community=community, PDU=scapy.SNMPnext(varbindlist=[scapy.SNMPvarbind(oid=nextoid)]))
            sock.sendall(p.build())

            r = scapy.SNMP(sock.recv(4096))
            oid = r.PDU.varbindlist[0].oid.val
            if oid.startswith(oid_prefix):
                yield (oid, r.PDU.varbindlist[0].value.val)
            else:
                break
            nextoid = oid

        sock.close()
