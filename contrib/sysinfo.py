from clusto.scripthelpers import init_script
from clusto.drivers import PenguinServer
from paramiko import SSHClient, MissingHostKeyPolicy
import clusto
import re

from pprint import pprint

class SilentPolicy(MissingHostKeyPolicy):
    def missing_host_key(self, client, hostname, key): pass

def discover_hardware(server):
    ip = server.get_ips()
    if not ip:
        return None
    ip = ip[0]

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

    serial = client.exec_command('/usr/sbin/dmidecode --string=system-serial-number')[1].read()

    client.close()

    return (server, {
        'disk': disks,
        'memory': memory,
        'processor': processors,
        'system': [{'serial': serial}],
    })

def main():
    for server in clusto.get_entities(clusto_drivers=[PenguinServer]):
        print server.name

        #if server.attrs(key='memory'): continue

        server = discover_hardware(server)
        if not server: continue
        server, info = server

        clusto.begin_transaction()

        for itemtype in info:
            for i, item in enumerate(info[itemtype]):
                for subkey, value in item.items():
                    server.set_attr(key=itemtype, subkey=subkey, value=value, number=i)

        clusto.commit()

if __name__ == '__main__':
    init_script()
    main()
