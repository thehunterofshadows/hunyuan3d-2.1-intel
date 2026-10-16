"""Run with Python against an isolated notes-service Docker instance."""
import urllib.request, urllib.error, json, http.cookiejar, os
BASE=os.environ.get('NOTES_TEST_URL','http://intel3d-notes-check:8080')
jar=http.cookiejar.CookieJar();client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
def request(path='',body=None,origin=BASE):
 raw=None if body is None else json.dumps(body).encode()
 r=urllib.request.Request(BASE+'/api/part-notes'+path,data=raw,headers={'Content-Type':'application/json','Origin':origin})
 try:
  with client.open(r) as response:return response.status,json.load(response)
 except urllib.error.HTTPError as error:return error.code,json.load(error)
assert request()[0]==200
note={'model':{'id':'api-check','name':'API check'},'part':{'id':'cad:test','name':'Test part','cadName':'test','geometryFingerprint':'ab'*32},'text':'Persistent annotation','anchor':{'sourceCadPointMm':[1,2,3]},'view':{},'expectedRevision':0}
assert request(body=note)[0]==200
assert request(body=note)[0]==409
note['expectedRevision']=1;note['text']='Updated annotation';assert request(body=note)[1]['note']['revision']==2
assert request('?model=api-check')[1]['notes'][0]['text']=='Updated annotation'
assert request('/export')[0]==200
assert request(body=note,origin='https://other.example')[0]==403
assert request(body=[])[0]==400
bad={**note,'anchor':[]};assert request(body=bad)[0]==400
bad={**note,'part':{**note['part'],'geometryFingerprint':[]}};assert request(body=bad)[0]==400
assert request(body={**note,'text':'x'*12001})[0]==400
print('PASS: persistent JSON API; revision conflict; filtered export; origin and malformed-data validation')
