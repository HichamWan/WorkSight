import json
import urllib.parse
import urllib.request

BASE = 'http://127.0.0.1:8000/api'


def rq(path, body=None, token=None):
    h = {'Content-Type': 'application/json'}
    if token:
        h['Authorization'] = 'Bearer ' + token
    data = json.dumps(body).encode() if body else None
    return json.load(urllib.request.urlopen(urllib.request.Request(BASE + path, data, h)))


tk = rq('/hr/auth/login', {'username': 'alice', 'password': 'password'})['access_token']

for q in ['', 'leo fi', 'leo', 'chloe', 'engineering', 'hr specialist', 'zzz']:
    params = {'search': q} if q else {}
    res = rq('/hr/employees?' + urllib.parse.urlencode(params), token=tk)
    names = ['%s %s (%s)' % (e['first_name'], e['last_name'], e['department']) for e in res['employees']]
    print('%-15s -> %d: %s' % (repr(q), res['total'], '; '.join(names[:5])))

dept = rq('/hr/employees?' + urllib.parse.urlencode({'department': 'Engineering'}), token=tk)
print('department=Engineering ->', [f"{e['first_name']} {e['last_name']}" for e in dept['employees']])
