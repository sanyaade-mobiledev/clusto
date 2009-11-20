from clusto.scripthelpers import init_script
from clusto.drivers import PenguinServer, IPManager
import clusto

ATTR_MAP = {
    'tftp-server': 'next-server',
    'tftp-filename': 'filename',
    'nfsroot': 'option root-path',
}

def main():
    for server in clusto.get_entities(clusto_drivers=[PenguinServer]):
        out = 'host %s { ' % server.name

        try:
            mac = server.get_port_attr('nic-eth', 1, 'mac')
            if not mac:
                continue
            out += 'hardware ethernet %s; ' % mac
        except: continue

        ip = IPManager.get_ips(server)
        if ip:
            ip = ip[0]
            out += 'fixed-address %s; ' % ip

        options = {}
        for attr in server.attrs(key='dhcp', merge_container_attrs=True):
            if attr.subkey in options: continue
            if not attr.subkey in ATTR_MAP:
                print 'Unknown subkey:', attr.subkey
                continue
            options[ATTR_MAP[attr.subkey]] = attr.value

        for key, value in options.items():
            out += '%s %s; ' % (key, value)

        out += '}'

        print out

if __name__ == '__main__':
    init_script()
    main()
