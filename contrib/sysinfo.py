from clusto.scripthelpers import init_script
from clusto.drivers import PenguinServer
from paramiko import SSHClient, MissingHostKeyPolicy
import clusto
import sys
import re

from pprint import pprint

class SilentPolicy(MissingHostKeyPolicy):
    def missing_host_key(self, client, hostname, key): pass

def discover_hardware(ip):
    client = SSHClient()

    try:
        client.load_system_host_keys()
        client.set_missing_host_key_policy(SilentPolicy())
        client.connect(ip, username='root')
        stdout = client.exec_command('cat /proc/partitions')[1].read()
    except:
        return None

    disks = []
    for line in stdout.split('\n'):
        if not line: continue
        line = [x for x in line.split(' ') if x]
        if not line[0].isdigit(): continue
        if not re.match('^sd[a-z]$', line[3]): continue
        name = line[3]
        blocks = int(line[2])
        blocks *= 1024
        disks.append({'osname': name, 'size': str(blocks)})

    stdout = client.exec_command('dmidecode -t memory')[1].read()
    memory = []
    mem = {}
    for line in stdout.split('\n'):
        if not line and mem:
            memory.append(mem)
            mem = {}
            continue
        if not line.startswith('\t'): continue

        key, value = line.lstrip('\t').split(': ', 1)
        if key in ('Locator', 'Type', 'Speed', 'Size'):
            mem[key.lower()] = value

    stdout = client.exec_command('cat /proc/cpuinfo')[1].read()
    processors = []
    cpu = {}
    for line in stdout.split('\n'):
        if not line and cpu:
            processors.append(cpu)
            cpu = {}
            continue
        if not line: continue

        key, value = line.split(':', 1)
        key = key.strip(' \t')
        if key in ('model name', 'cpu MHz', 'cache size', 'vendor_id'):
            key = key.lower().replace(' ', '-').replace('_', '-')
            cpu[key] = value.strip(' ')
    cpucount = len(processors)

    serial = client.exec_command('/usr/sbin/dmidecode --string=system-serial-number')[1].read().rstrip('\r\n')
    hostname = client.exec_command('/bin/hostname -s')[1].read().rstrip('\r\n')

    stdout = client.exec_command('/sbin/ifconfig -a')[1].read()
    iface = {}
    for line in stdout.split('\n'):
        line = line.rstrip('\r\n')
        if not line: continue
        line = line.split('  ')
        if line[0]:
            name = line[0]
            iface[name] = []
            del line[0]
        line = [x for x in line if x]
        iface[name] += line

    for name in iface:
        attribs = {}
        value = None
        for attr in iface[name]:
            value = None
            if attr.startswith('Link encap') or \
                attr.startswith('inet addr') or \
                attr.startswith('Bcast') or \
                attr.startswith('Mask') or \
                attr.startswith('MTU') or \
                attr.startswith('Metric'):
                key, value = attr.split(':', 1)
            if attr.startswith('HWaddr'):
                key, value = attr.split(' ', 1)
            if attr.startswith('inet6 addr'):
                key, value = attr.split(': ', 1)
            if not value: continue
            attribs[key.lower()] = value
        iface[name] = attribs

    client.close()

    return {
        'disk': disks,
        'memory': memory,
        'processor': processors,
        'network': iface,
        'system': [{
            'serial': serial,
            'cpucount': cpucount,
            'hostname': hostname,
        }],
    }

def update_server(server, info):
    clusto.begin_transaction()
    for itemtype in info:
        if itemtype == 'network': continue
        for i, item in enumerate(info[itemtype]):
            for subkey, value in item.items():
                server.set_attr(key=itemtype, subkey=subkey, value=value, number=i)
    clusto.commit()

    clusto.begin_transaction()
    for ifnum in range(0, 2):
        ifname = 'eth%i' % ifnum
        if server.attrs(subkey='mac', value=info['network'].get(ifname, {}).get('hwaddr', '')):
            continue
        server.set_port_attr('nic-eth', ifnum + 1, 'mac', info['network'][ifname]['hwaddr'])

        try:
            if 'inet addr' in info['network'][ifname]:
                server.bind_ip_to_osport(info['network'][ifname]['inet addr'], ifname)
        except:
            pass
    clusto.commit()

def main():
    if len(sys.argv) < 2:
        servers = clusto.get_entities(clusto_types=['server'])
    else:
        servers = [clusto.get_by_name(sys.argv[1])]
    for server in servers:
        if server.attrs(key='system', subkey='serial'): continue

        ip = server.get_ips()
        if not ip:
            print 'Unable to find IP for', server.name
            continue
        ip = ip[0]

        info = discover_hardware(ip)
        if not info:
            print 'Unable to discover', server.name
            continue
        print 'Discovered', server.name

        update_server(server, info)
        print 'Updated', server.name


if __name__ == '__main__':
    init_script()
    main()
