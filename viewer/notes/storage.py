import os,json,tempfile,time,fcntl
from contextlib import contextmanager

@contextmanager
def file_lock(directory):
 with open(directory/".notes.lock","a") as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  try:yield
  finally:fcntl.flock(lock,fcntl.LOCK_UN)

def now():return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
def atomic(path,text):
 fd,tmp=tempfile.mkstemp(prefix='.notes-',dir=path.parent)
 try:
  with os.fdopen(fd,'w') as f:f.write(text);f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def markdown(doc):
 out=['# Intel 3D Studio — part annotations','',f"Updated: {doc['updatedAt']}",'']
 for note in doc['notes']:
  out.extend(['## '+note['model']['name'].replace('\n',' ')+' / '+note['part']['name'].replace('\n',' '),'',
   'Model ID: '+json.dumps(note['model']['id']),'Part ID: '+json.dumps(note['part']['id']),
   'CAD name: '+json.dumps(note['part'].get('cadName')),'Node path: '+json.dumps(note['part'].get('nodePath')),
   'Geometry SHA-256: '+note['part'].get('geometryFingerprint','unknown'),
   'Source CAD point (mm, X/Y/Z): '+json.dumps(note.get('anchor',{}).get('sourceCadPointMm')),
   'Reviewed: '+str(note.get('reviewed',False)),
   'Review history (JSON): '+json.dumps(note.get('history',[]),ensure_ascii=False),
   'Review response: '+json.dumps(note.get('reviewResponse',''),ensure_ascii=False),
   'User note (JSON string): '+json.dumps(note['text'],ensure_ascii=False),''])
 return '\n'.join(out)
