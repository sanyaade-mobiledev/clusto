#!/home/synack/src/clusto/env/bin/python
import simplejson as json
import xmlrpclib
import cPickle
import yaml

import new
import re

from webob import Request, Response
from ncore.daemon import become_daemon
from clusto.scripthelpers import get_clusto_config
from clusto.drivers import Driver
import clusto

config = get_clusto_config()
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
    return loadfunc(obj)

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
        kwargs = dict(request.params.items())
        self.obj.add_attr(**kwargs)
        clusto.commit()
        return self.show(request)

    def delattr(self, request):
        '''
        Delete an attribute from this object.

        Requires HTTP parameter "key"
        '''
        self.obj.del_attrs(request.params['key'])
        clusto.commit()
        return self.show(request)

    def attrs(self, request):
        '''
        Query attributes from this object.
        '''
        result = {
            'attrs': []
        }
        kwargs = dict(request.params.items())
        for attr in self.obj.attrs(**kwargs):
            result['attrs'].append(unclusto(attr))
        return Response(status=200, body=dumps(request, result))

    def insert(self, request):
        '''
        Insert an object into this object

        Requires a "device" attribute, which is the absolute URL path to the
        object to be inserted.

        For example: /pool/examplepool/insert?object=/server/exampleserver
        '''
        device = request.params['object'].strip('/').split('/')[1]
        device = clusto.get_by_name(device)
        self.obj.insert(device)
        clusto.commit()
        return self.show(request)

    def remove(self, request):
        '''
        Remove a device from this object.

        Requires a "device" attribute, which is the absolute URL path to the
        object to be removed.

        For example: /pool/examplepool/remove?object=/server/exampleserver
        '''
        device = request.params['object'].strip('/').split('/')[1]
        device = clusto.get_by_name(device)
        self.obj.remove(device)
        clusto.commit()
        return self.show(request)

    def show(self, request):
        '''
        Returns attributes and actions available for this object.
        '''
        result = {}
        result['object'] = self.url

        attrs = []
        for x in self.obj.attrs(ignore_hidden=False):
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
        for port in self.obj.port_info_tuples:
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

        Example: /rack/examplerack/insert?object=/server/exampleserver&ru=6
        '''
        device = request.params['object'].strip('/').split('/')[1]
        device = clusto.get_by_name(device)
        self.obj.insert(device, int(request.params['ru']))
        clusto.commit()
        return self.contents(request)

class ResourceAPI(EntityAPI):
    def allocate(self, request):
        '''
        Allocate a new object of the given type
        '''
        driver = clusto.DRIVERLIST[request.params['driver']]
        device = self.obj.allocate(driver)
        clusto.commit()
        return Response(status=201, body=dumps(request, unclusto(device)))

class QueryAPI(object):
    @classmethod
    def get_entities(self, request):
        kwargs = {}
        for k, v in request.POST.items():
            v = loads(request, v)
            kwargs[k] = v
        result = [unclusto(x) for x in clusto.get_entities(**kwargs)]
        return Response(status=200, body=dumps(request, result))

    @classmethod
    def get_by_name(self, request):
        if not 'name' in request.params:
            return Response(status=400, body='400 Bad Request\nYou must specify a "name" parameter\n')
        name = request.params['name']
        obj = clusto.get_by_name(name)
        api = EntityAPI(obj)
        return api.show(request)

class ClustoApp(object):
    def __init__(self):
        self.urls = [
            ('^/search$',
                self.search),
            ('^/query/(?P<querytype>[a-z_]+)',
                self.query_delegate),
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
            'resource': ResourceAPI,
        }

    def default_delegate(self, request, match):
        return Response(status=200, body=dumps(request, ['/' + x for x in clusto.typelist.keys()]))

    def types_delegate(self, request, match):
        objtype = match.groupdict()['objtype']
        result = []
        for obj in clusto.get_entities(clusto_types=(objtype,)):
            result.append(unclusto(obj))
        return Response(status=200, body=dumps(request, result))

    def action_delegate(self, request, match):
        if request.method == 'GET':
            return self.get_action(request, match)

        if request.method == 'POST':
            return self.post_action(request, match)

        if request.method == 'DELETE':
            return self.delete_action(request, match)

        return Response(status=501, body='501 Not Implemented\n')

    def query_delegate(self, request, match):
        querytype = match.groupdict()['querytype']

        if hasattr(QueryAPI, querytype):
            method = getattr(QueryAPI, querytype)
            return method(request)
        else:
            return Response(status=400, body='400 Bad Request\nThere is no such query\n')

    def post_action(self, request, match):
        name = request.path_info.strip('/')
        if name.count('/') != 1:
            return Response(status=400, body='400 Bad Request\nYou may only create objects, not types or actions\n')
        objtype, objname = name.split('/', 1)

        try:
            obj = clusto.get_by_name(objname)
            if obj:
                return Response(status=409, body='409 Conflict\nObject already exists\n')
        except LookupError: pass

        obj = clusto.typelist[objtype](objname)
        clusto.commit()

        obj = EntityAPI(obj)
        response = obj.show(request)
        response.status = 201
        return response

    def delete_action(self, request, match):
        name = request.path_info.strip('/')
        if name.count('/') != 1:
            return Response(status=400, body='400 Bad Request\nYou may only delete objects, not types or actions\n')
        objtype, objname = name.split('/', 1)

        try:
            obj = clusto.get_by_name(objname)
        except LookupError:
            return Response(status=404, body='404 Not Found\n')

        clusto.delete_entity(obj.entity)
        clusto.commit()
        return Response(status=200, body='200 OK\nObject deleted\n')

    def get_action(self, request, match):
        group = match.groupdict()
        try:
            obj = clusto.get_by_name(group['name'])
        except LookupError:
            return Response(status=404, body='404 Not Found\n')

        if obj.type != group['objtype']:
            response = Response(status=302)
            response.headers.add('Location', str('/%s/%s/%s' % (obj.type, obj.name, group.get('action', ''))))
            return response

        action = group.get('action', 'show')
        handler = self.types.get(group['objtype'], EntityAPI)
        if not obj:
            obj = clusto.get_by_name(group['name'])
        h = handler(obj)
        if hasattr(h, action):
            f = getattr(h, action)
            response = f(request)
        else:
            response = Response(status=404, body='404 Not Found\nInvalid action\n')
        return response

    def search(self, request, match):
        query = request.params.get('q', None)
        if not query:
            return Response(status=400, body='400 Bad Request\nNo query specified\n')

        result = []
        for obj in clusto.get_entities():
            if obj.name.find(query) != -1:
                result.append(unclusto(obj))
        return Response(status=200, body=dumps(request, result))

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
    #become_daemon(out_log='/tmp/cweb.log', err_log='/tmp/cweb.log')

    app = ClustoApp()
    
    # Disable reverse DNS upon request. It's just stupid.
    wsgi = WSGIRequestHandler
    def address_string(self):
        return self.client_address[0]
    wsgi.address_string = address_string

    server = make_server(conf('server.bind_address'), conf('server.bind_port'), app, handler_class=wsgi)
    server.serve_forever()
