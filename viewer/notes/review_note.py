"""Mark one reviewed annotation using the same file lock as the notes service."""
import argparse,json
from pathlib import Path
from storage import file_lock,atomic,markdown,now

def review(path,model,part,revision,response):
 path=Path(path).resolve()
 if not path.name.startswith('workspace-') or path.suffix!='.json':raise ValueError('Choose a workspace JSON file')
 with file_lock(path.parent):
  doc=json.loads(path.read_text())
  note=next((n for n in doc['notes'] if n['model']['id']==model and n['part']['id']==part),None)
  if note is None:raise ValueError('Note not found')
  if note['revision']!=revision:raise ValueError('Revision conflict: re-read and review the current note')
  if note.get('reviewed',False):raise ValueError('Note already reviewed')
  if not note['text'].strip():raise ValueError('No note text to review')
  if not response.strip() or len(response)>12000:raise ValueError('Supply a review response of 1–12000 characters')
  note.update(reviewed=True,reviewedAt=now(),reviewResponse=response,revision=revision+1)
  doc.update(schemaVersion=2,updatedAt=now())
  atomic(path,json.dumps(doc,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
  atomic(path.with_suffix('.md'),markdown(doc))
  return note

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 for name in ['file','model','part','response']:parser.add_argument('--'+name,required=True)
 parser.add_argument('--expected-revision',type=int,required=True)
 args=parser.parse_args()
 try:
  note=review(args.file,args.model,args.part,args.expected_revision,args.response)
  print(json.dumps({'reviewed':True,'revision':note['revision'],'reviewedAt':note['reviewedAt']}))
 except (ValueError,OSError,KeyError) as error:parser.exit(1,str(error)+'\n')
