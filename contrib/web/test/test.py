from rest import request
from pprint import pprint

status, headers, data = request('POST', 'http://localhost:9999/server', body={'object': '/server/test'})
pprint((status, headers, data))
