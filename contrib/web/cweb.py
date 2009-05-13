import simplejson as json
import xmlrpclib
import cPickle
import yaml

import new
import re

from webob import Request, Response
from clusto.scripthelpers import getClustoConfig
from clusto.drivers import Driver, PortMixin, BasicRack
import clusto

config = getClustoConfig()
clusto.connect(config.get('clusto', 'dsn'))

config = json.load(file('web.conf', 'r'))

def xmldumps(obj, **kwargs):
    return xmlrpclib.dumps((obj,), **kwargs)

formats = {
    'json': (json.dumps, json.loads, {'indent': 4}),
    'yaml': (yaml.dump, yaml.load, {'indent': 4}),
    'pickle': (cPickle.dumps, cPickle.loads, {}),
    'xml': (xmldumps, xmlrpclib.loads, {'methodresponse': True, 'allow_none': True}),
}

def conf(key):
    obj = config
    for k in key.split('.'):
        obj = obj[k]
    return obj

def unclusto(obj):
    '''
    Convert an object to a representation that can be safely serialized into
    JSON.
    '''
    if type(obj) in (str, unicode, int) or obj == None:
        return obj
    if isinstance(obj, clusto.Attribute):
        return {
            'key': obj.key,
            'value': unclusto(obj.value),
            'subkey': obj.subkey,
            'number': obj.number,
            'datatype': obj.datatype
        }
    if issubclass(obj.__class__, Driver):
        return '/%s/%s' % (obj.type, obj.name)
    return str(obj)

def dumps(request, obj):
    format = request.params.get('format', 'json')
    dumpfunc, loadfunc, kwargs = formats[format]
    result = dumpfunc(obj, **kwargs)
    if format == 'json' and 'callback' in request.params:
        callback = request.params['callback']
        result = '%s(%s)' % (callback, result)
    return result

def loads(request, obj):
    format = request.params.get('format', 'json')
    dumpfunc, loadfunc, kwargs = formats[format]
    return loadfunc(obj, **kwargs)

class EntityAPI(object):
    def __init__(self, obj):
        self.obj = obj
        self.url = '/%s/%s' % (self.obj.type, self.obj.name)

    def addattr(self, request):
        '''
        Add an attribute to this object.

        Requires HTTP parameters "key" and "value"
        Optional parameters are "subkey" and "number"
        '''
        self.obj.addAttr(request.params['key'], request.params['value'], request.params.get('subkey', None), request.params.get('number', None))
        return self.show(request)

    def delattr(self, request):
        '''
        Delete an attribute from this object.

        Requires HTTP parameter "key"
        '''
        self.obj.delAttrs(request.params['key'])
        return self.show(request)

    def insert(self, request):
        '''
        Insert an object into this object

        Requires a "device" attribute, which is the absolute URL path to the
        object to be inserted.

        For example: /pool/examplepool/insert?device=/server/exampleserver
        '''
        device = request.params['device'].strip('/').split('/')[1]
        device = clusto.getByName(device)
        self.obj.insert(device)
        return self.contents(request)

    def remove(self, request):
        '''
        Remove a device from this object.

        Requires a "device" attribute, which is the absolute URL path to the
        object to be removed.

        For example: /pool/examplepool/remove?device=/server/exampleserver
        '''
        device = request.params['device'].strip('/').split('/')[1]
        device = clusto.getByName(device)
        self.obj.remove(device)
        return self.contents(request)

    def show(self, request):
        '''
        Returns attributes and actions available for this object.
        '''
        result = {}
        result['object'] = self.url

        attrs = []
        for x in self.obj.attrs():
            attrs.append(unclusto(x))
        result['attrs'] = attrs
        result['contents'] = [unclusto(x) for x in self.obj.contents()]
        result['parents'] = [unclusto(x) for x in self.obj.parents()]
        result['actions'] = [x for x in dir(self) if not x.startswith('_') and callable(getattr(self, x))]

        return Response(status=200, body=dumps(request, result))

class PortInfoAPI(EntityAPI):
    def ports(self, request):
        '''
        Returns a list of ports within this object and any information about
        connections between those ports and other devices.
        '''
        result = {}
        result['object'] = self.url
        result['ports'] = []
        for port in self.obj.portInfoTuples:
            porttype, portnum, otherobj, othernum = [unclusto(x) for x in port]
            result['ports'].append({
                'type': porttype,
                'num': portnum,
                'other': otherobj,
                'othernum': othernum,
            })

        return Response(status=200, body=dumps(request, result))

class RackAPI(EntityAPI):
    def insert(self, request):
        '''
        Insert a device into a rack.

        This method is overridden to require a "ru" parameter in addition to
        "device"

        Example: /rack/examplerack/insert?device=/server/exampleserver&ru=6
        '''
        device = request.params['device'].strip('/').split('/')[1]
        device = clusto.getByName(device)
        self.obj.insert(device, int(request.params['ru']))
        return self.contents(request)

class ClustoApp(object):
    def __init__(self):
        self.urls = [
            ('^/(?P<objtype>\w+)/(?P<name>[-\w0-9]+)/(?P<action>\w+)',
                self.action_delegate),
            ('^/(?P<objtype>\w+)/(?P<name>[-\w0-9]+)',
                self.action_delegate),
            ('^/(?P<objtype>\w+)',
                self.types_delegate),
            ('^/',
                self.default_delegate),
        ]
        self.urls = [(re.compile(pattern), obj) for pattern, obj in self.urls]

        self.types = {
            'server': PortInfoAPI,
            'consoleserver': PortInfoAPI,
            'networkswitch': PortInfoAPI,
            'powerstrip': PortInfoAPI,
            'rack': RackAPI,
        }

    def default_delegate(self, request, match):
        return Response(status=200, body=dumps(request, ['/' + x for x in clusto.typelist.keys()]))

    def types_delegate(self, request, match):
        objtype = match.groupdict()['objtype']
        result = []
        for obj in clusto.getEntities(clustoTypes=(objtype,)):
            result.append(unclusto(obj))
        return Response(status=200, body=dumps(request, result))

    def action_delegate(self, request, match):
        group = match.groupdict()
        try:
            obj = clusto.getByName(group['name'])
        except LookupError:
            return Response(status=404, body='404 Not Found\n')

        if obj.type != group['objtype']:
            response = Response(status=302)
            response.headers.add('Location', str('/%s/%s/%s' % (obj.type, obj.name, group.get('action', ''))))
            return response

        action = group.get('action', 'show')
        if request.method == 'POST':
            format = request.params.get('format', 'json')
            obj = loads(format, request.body.read())
            if len(obj['object'].strip('/').split('/')) != 2:
                return Response(status=400, body='400 Bad Request\nYou may only create objects, not types or actions\n')
            objtype, objname = obj['object'].strip('/').split('/')
            obj = clusto.typelist[objtype](objname)
            obj = EntityAPI(obj)
            return Response(status=201, body='201 Created')

        if request.method == 'DELETE':
            if len(obj['object'].strip('/').split('/')) != 2:
                return Response(status=400, body='400 Bad Request\nYou may only delete objects, not types or actions\n')
            objtype, objname = obj['object'].strip('/').split('/')
            obj = clusto.getByName(objname)
            clusto.deleteEntity(obj.entity)
            return Response(status=200, body='200 OK\nObject deleted\n')

        handler = self.types.get(group['objtype'], EntityAPI)
        if not obj:
            obj = clusto.getByName(group['name'])
        h = handler(obj)
        if hasattr(h, action):
            f = getattr(h, action)
            response = f(request)
        else:
            response = Response(status=404, body='404 Not Found\nInvalid action\n')
        return response

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = Response(status=404, body='404 Not Found\nUnmatched URL\n')

        for pattern, handler in self.urls:
            match = pattern.match(request.path_info)
            if match:
                response = handler(request, match)
                break

        return response(environ, start_response)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server, WSGIRequestHandler

    app = ClustoApp()
    
    # Disable reverse DNS upon request. It's just stupid.
    wsgi = WSGIRequestHandler
    def address_string(self):
        return self.client_address[0]
    wsgi.address_string = address_string

    server = make_server(conf('server.bind_address'), conf('server.bind_port'), app, handler_class=wsgi)
    server.serve_forever()
