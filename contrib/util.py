from clusto.drivers import BasicDatacenter, BasicRack, BasicServer, BasicNetworkSwitch, PowerTowerXM, SimpleEntityNameManager
from clusto.scripthelpers import getClustoConfig
import clusto

from traceback import format_exc
from subprocess import Popen, PIPE
from xml.etree import ElementTree
from pprint import pprint
import yaml
import socket
import sys
import re

def get_or_create(objtype, name):
    try:
        return clusto.getByName(name)
    except LookupError:
        return objtype(name)

def get_snmp_hostname(ipaddr, community='digg1t'):
    proc = Popen(['scli', '-c', 'show system info', '-x', ipaddr, community], stdout=PIPE)
    xmldata = proc.stdout.read()
    xmltree = ElementTree.fromstring(xmldata)
    hostname = list(xmltree.getiterator('name'))
    if len(hostname) > 0:
        hostname = hostname[0].text
    else:
        hostname = None
    return hostname

def get_ssh_hostname(ipaddr, username='root'):
    proc = Popen(['ssh', '%s@%s' % (username, ipaddr), 'hostname'], stdout=PIPE)
    output = proc.stdout.read()
    return output.rstrip('\r\n')

def get_hostname(ipaddr):
    hostname = get_snmp_hostname(ipaddr)
    if not hostname:
        try:
            hostname = getfqdn(ipaddr)
        except: pass
    if not hostname:
        try:
            hostname = get_ssh_hostname(ipaddr)
        except: pass
    hostname = hostname.split('.', 1)[0]
    return hostname

def discover_interfaces(ipaddr, server=None, ssh_user='root'):
    #if not server:
    #    server = get_server(ipaddr)
    proc = Popen(['ssh', '-o', 'StrictHostKeyChecking no', '%s@%s' % (ssh_user, ipaddr), '/sbin/ip addr show up'], stdout=PIPE)
    output = proc.stdout.read()
    iface = {}
    for line in output.split('\n'):
        line = line.rstrip('\r\n')
        if not line: continue
        if line[0].isdigit():
            num, line = line.split(':', 1)
            iface[num] = []
        iface[num].append(line.strip())

    patterns = [
        re.compile('^(?P<name>[A-z0-9]+): \<(?P<flags>[A-Z0-9\,]+)\> mtu (?P<mtu>[0-9]+) (?P<linkflags>.*)$'),
        re.compile('^link/(?P<linktype>[a-z]+) (?P<mac>[A-z0-9\:]+) brd (?P<broadcastmac>[A-z0-9\:]+)$'),
        re.compile('^inet (?P<ip>[0-9\.]+)/(?P<netmask>[0-9]+) brd (?P<broadcastip>[0-9\.]+) (?P<v4flags>.*)$'),
        re.compile('^inet6 (?P<ip6>[A-z0-9\:]+)/(?P<netmask6>[0-9]+) scope (?P<scope6>[\w]+)$'),
        re.compile('^inet (?P<ip>[0-9\.]+)/(?P<netmask>[0-9]+) scope (?P<scope>[\w]+) (?P<v4flags>.*)$'),
    ]
    ifdict = {}
    for num in iface:
        ifdict[num] = {}
        for line in iface[num]:
            for pattern in patterns:
                match = pattern.match(line)
                if match:
                    d = match.groupdict()
                    for key, value in d.items():
                        if not key in ifdict[num]:
                            ifdict[num][key] = []
                        ifdict[num][key].append(value)
                    break
            if not match:
                if not 'extra' in ifdict[num]:
                    ifdict[num]['extra'] = ''
                ifdict[num]['extra'] += line

    pprint(ifdict)
    return

def get_server(ipaddr, fqdn_base='digg.internal'):
    server = None
    fqdn = None

    names = get_or_create(SimpleEntityNameManager, 'servernames')
    hostname = get_hostname(ipaddr)
    if hostname:
        if hostname.endswith(fqdn_base):
            fqdn = hostname
        hostname = hostname.split('.', 1)[0]

        try:
            server = clusto.getByName(hostname)
        except LookupError:
            print "Server %s doesn't exist in clusto... Creating it"
            server = names.allocate(BasicServer, hostname)
    else:
        print 'Unable to determine hostname for %s... Assuming this is a new server' % ipaddr
        server = names.allocate(BasicServer)

    if fqdn:
        server.addFQDN(fqdn)

    return server

def main():
    discover_interfaces('10.2.128.16', ssh_user='synack')

if __name__ == '__main__':
    config = getClustoConfig()
    clusto.connect(config.get('clusto', 'dsn'))
    clusto.initclusto()
    main()
