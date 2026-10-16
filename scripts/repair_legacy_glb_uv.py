"""One-time repair for GLBs exported with the legacy double-V conversion.
Only use for confirmed affected exports. Refuses already marked repairs.
Preserves geometry, embedded image bytes and all non-UV binary data.
"""
import argparse, json, struct
from pathlib import Path

def repair(path):
    path=Path(path);data=path.read_bytes()
    magic,version,total=struct.unpack_from('<4sII',data)
    assert magic==b'glTF' and version==2 and total==len(data)
    chunks=[];offset=12
    while offset<len(data):
        size,kind=struct.unpack_from('<II',data,offset);offset+=8
        chunks.append([kind,bytearray(data[offset:offset+size])]);offset+=size
    doc=json.loads(chunks[0][1])
    extras=doc.setdefault('extras',{})
    assert not extras.get('intelUvRepair'), 'Already repaired'
    binary=next(b for kind,b in chunks if kind==0x004e4942)
    indices={p['attributes']['TEXCOORD_0'] for m in doc['meshes'] for p in m['primitives'] if 'TEXCOORD_0' in p['attributes']}
    assert indices
    touched=set()
    for index in indices:
        a=doc['accessors'][index];assert a['componentType']==5126 and a['type']=='VEC2' and 'sparse' not in a
        view=doc['bufferViews'][a['bufferView']];assert view.get('buffer',0)==0
        start=view.get('byteOffset',0)+a.get('byteOffset',0)
        stride=view.get('byteStride',8)
        for i in range(a['count']):
            pos=start+i*stride+4
            if pos in touched:continue
            touched.add(pos);v=struct.unpack_from('<f',binary,pos)[0];struct.pack_into('<f',binary,pos,1.0-v)
        if 'min' in a and 'max' in a:
            low,high=a['min'][1],a['max'][1];a['min'][1],a['max'][1]=1-high,1-low
    extras['intelUvRepair']='legacy-double-v-2026-10-16'
    encoded=json.dumps(doc,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4)
    chunks[0][1]=encoded
    body=b''.join(struct.pack('<II',len(b),kind)+bytes(b) for kind,b in chunks)
    path.write_bytes(struct.pack('<4sII',b'glTF',2,12+len(body))+body)
    print(str(path)+': repaired '+str(len(touched))+' UV coordinates')
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('files',nargs='+')
    for p in ap.parse_args().files:repair(p)
