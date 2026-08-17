import os, uuid, io, requests
BASE_URL=os.environ['REACT_APP_BACKEND_URL'].rstrip('/')

def test_root_and_list():
    r=requests.get(BASE_URL+'/api/',timeout=20); assert r.status_code==200; assert 'message' in r.json()
    r=requests.get(BASE_URL+'/api/transactions',timeout=20); assert r.status_code==200; assert isinstance(r.json(),list)

def test_create_persist_delete():
    payload={'transaction_type':'cash_in','amount':12345,'purpose':'TEST_api_'+uuid.uuid4().hex[:8],'note':'regression','transaction_date':'2026-02-20','evidence_url':None}
    r=requests.post(BASE_URL+'/api/transactions',json=payload,timeout=20); assert r.status_code==200; d=r.json(); assert d['purpose']==payload['purpose']; assert d['id']
    found=requests.get(BASE_URL+'/api/transactions',timeout=20).json(); assert any(x['id']==d['id'] and x['amount']==12345 for x in found)
    r=requests.delete(BASE_URL+'/api/transactions/'+d['id'],timeout=20); assert r.status_code==200
    assert requests.delete(BASE_URL+'/api/transactions/'+d['id'],timeout=20).status_code==404

def test_validation_and_evidence():
    r=requests.post(BASE_URL+'/api/transactions',json={'transaction_type':'bad','amount':1,'purpose':'x','transaction_date':'2026-02-20'},timeout=20); assert r.status_code==422
    r=requests.post(BASE_URL+'/api/evidence',files={'file':('bad.txt',b'abc','text/plain')},timeout=20); assert r.status_code==400
    r=requests.post(BASE_URL+'/api/evidence',files={'file':('test.png',b'\x89PNG\r\n','image/png')},timeout=20); assert r.status_code==200; assert r.json()['url'].startswith('/uploads/')
